# -*- coding: utf-8 -*-
"""Handle dashboard helpers and related logic.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
import logging
import os
import pprint
from decimal import Decimal
from enum import Enum

from django.conf import settings
from django.conf.urls.static import static
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.http import Http404, HttpResponseBadRequest, JsonResponse
from django.utils import timezone

from app.utils import get_semaphore, sync_profile
from dashboard.models import (
    Activity, Bounty, BountyDocuments, BountyFulfillment, BountyInvites, BountySyncRequest, Coupon, HackathonEvent,
    UserAction,
)
from dashboard.notifications import (
    maybe_market_to_email, maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter,
    maybe_market_to_user_discord, maybe_market_to_user_slack,
)
from dashboard.tokens import addr_to_token
from economy.utils import ConversionRateNotFoundError, convert_amount
from git.utils import get_gh_issue_details, get_url_dict
from jsondiff import diff
from marketing.mails import new_reserved_issue
from pytz import UTC
from ratelimit.decorators import ratelimit
from redis_semaphore import NotAvailable as SemaphoreExists

from .models import Profile

logger = logging.getLogger(__name__)

def load_files_in_directory(dir_name):
    path = os.path.join(settings.STATIC_ROOT, dir_name)
    images = []
    for f in os.listdir(path):
        if f.endswith('jpg') or f.endswith('png') or f.endswith('jpeg'):
            images.append("%s" % (f))
    return images


def get_bounty_view_kwargs(request):
    """Get the relevant kwargs from the request."""
    # Define lookup criteria.
    pk = request.GET.get('id') or request.GET.get('pk')
    standard_bounties_id = request.GET.get('sb_id') or request.GET.get('standard_bounties_id')
    network = request.GET.get('network', 'mainnet')
    issue_url = request.GET.get('url')
    bounty_kwargs = {}

    # Check for relevant params.
    if pk and pk.isdigit():
        bounty_kwargs['pk'] = int(pk)
    elif standard_bounties_id and standard_bounties_id.isdigit():
        bounty_kwargs['standard_bounties_id'] = int(standard_bounties_id)
        bounty_kwargs['network'] = network
    elif issue_url:
        bounty_kwargs['github_url'] = issue_url
    else:
        raise Http404

    return bounty_kwargs


def handle_bounty_views(request):
    """Handle bounty view entry.

    Attributes:
        bounty (dashboard.Bounty): The bounty object for the specified request.
        bounty_kwargs (dict): The relevant key/values from the request to be
            used for the Bounty query.

    Returns:
        dashboard.Bounty: The Bounty object.
    """
    bounty = None
    bounty_kwargs = get_bounty_view_kwargs(request)

    try:
        bounty = Bounty.objects.current().get(**bounty_kwargs)
    except Bounty.MultipleObjectsReturned:
        bounty = Bounty.objects.current().filter(**bounty_kwargs).distinct().latest('id')
    except (Bounty.DoesNotExist, ValueError):
        raise Http404
    except Exception as e:
        logger.error(f'Error in handle_bounty_views - {e}')
        raise Http404

    return bounty


@ratelimit(key='ip', rate='100/m', method=ratelimit.UNSAFE, block=True)
def amount(request):
    """Determine the value of the provided denomination and amount in ETH and USD.

    Raises:
        Http404: The exception is raised if any error is encountered.

    Returns:
        JsonResponse: A JSON response containing ETH and USDT values.

    """
    response = {}

    try:
        amount = str(request.GET.get('amount'))
        if not amount.replace('.','').isnumeric():
            return HttpResponseBadRequest('not number')
        denomination = request.GET.get('denomination', 'ETH')
        if not denomination:
            denomination = 'ETH'

        if denomination in settings.STABLE_COINS:
            denomination = 'USDT'
        if denomination == 'ETH':
            amount_in_eth = float(amount)
        else:
            amount_in_eth = convert_amount(amount, denomination, 'ETH')
        amount_in_usdt = convert_amount(amount_in_eth, 'ETH', 'USDT')
        response = {
            'eth': amount_in_eth,
            'usdt': amount_in_usdt,
        }
        return JsonResponse(response)
    except ConversionRateNotFoundError as e:
        logger.debug(e)
        raise Http404
    except Exception as e:
        logger.error(e)
        raise Http404


@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
def issue_details(request):
    """Determine the Github issue keywords of the specified Github issue or PR URL.

    Todo:
        * Modify the view to only use the Github API (remove BeautifulSoup).
        * Simplify the view logic.

    Returns:
        JsonResponse: A JSON response containing the Github issue or PR keywords.

    """
    from dashboard.utils import clean_bounty_url
    response = {}
    token = request.GET.get('token', None)
    url = request.GET.get('url')
    url_val = URLValidator()

    try:
        url_val(url)
    except ValidationError:
        response['message'] = 'invalid arguments'
        return JsonResponse(response)

    if url.lower()[:19] != 'https://github.com/':
        response['message'] = 'invalid arguments'
        return JsonResponse(response)

    try:
        url_dict = get_url_dict(clean_bounty_url(url))
        if url_dict:
            response = get_gh_issue_details(token=token, **url_dict)
        else:
            response['message'] = 'could not parse Github url'
    except Exception as e:
        logger.warning(e)
        response['message'] = 'could not pull back remote response'
    return JsonResponse(response)


def normalize_url(url):
    """Normalize the URL.

    Args:
        url (str): The URL to be normalized.

    Returns:
        str: The normalized URL.

    """
    if url[-1] == '/':
        url = url[0:-1]
    return url


def sync_bounty_with_web3(bounty_contract, url):
    """Sync the Bounty with Web3.

    Args:
        bounty_contract (Web3): The Web3 contract instance.
        url (str): The bounty URL.

    Returns:
        tuple: A tuple of bounty change data.
        tuple[0] (bool): Whether or not the Bounty changed.
        tuple[1] (dashboard.models.Bounty): The first old bounty object.
        tuple[2] (dashboard.models.Bounty): The new Bounty object.

    """
    bountydetails = bounty_contract.call().bountydetails(url)
    return process_bounty_details(bountydetails)


class BountyStage(Enum):
    """Python enum class that matches up with the Standard Bounties BountyStage enum.

    Attributes:
        Draft (int): Bounty is a draft.
        Active (int): Bounty is active.
        Dead (int): Bounty is dead.

    """

    Draft = 0
    Active = 1
    Dead = 2


class UnsupportedSchemaException(Exception):
    """Define unsupported schema exception handling."""

    pass


def bounty_did_change(bounty_id, new_bounty_details):
    """Determine whether or not the Bounty has changed.

    Args:
        bounty_id (int): The ID of the Bounty.
        new_bounty_details (dict): The new Bounty raw data JSON.

    Returns:
        bool: Whether or not the Bounty has changed.
        QuerySet: The old bounties queryset.

    """
    did_change = False
    old_bounties = Bounty.objects.none()
    network = new_bounty_details['network']
    try:
        # IMPORTANT -- if you change the criteria for deriving old_bounties
        # make sure it is updated in dashboard.helpers/bounty_did_change
        # AND
        # refresh_bounties/handle
        old_bounties = Bounty.objects.filter(
            standard_bounties_id=bounty_id, network=network
        ).nocache().order_by('-created_on')

        if old_bounties.exists():
            did_change = (new_bounty_details != old_bounties.first().raw_data)
        else:
            did_change = True
    except Exception as e:
        did_change = True
        print(f"asserting did change because got the following exception: {e}. args;"
              f"bounty_id: {bounty_id}, network: {network}")

    print('* Bounty did_change:', did_change)
    return did_change, old_bounties


def handle_bounty_fulfillments(fulfillments, new_bounty, old_bounty):
    """Handle BountyFulfillment creation for new bounties.

    Args:
        fulfillments (dict): The fulfillments data dictionary.
        new_bounty (dashboard.models.Bounty): The new Bounty object.
        old_bounty (dashboard.models.Bounty): The old Bounty object.

    Returns:
        QuerySet: The BountyFulfillments queryset.

    """
    from dashboard.utils import is_blocked
    for fulfillment in fulfillments:
        kwargs = {}
        accepted_on = None
        github_username = fulfillment.get('data', {}).get(
            'payload', {}).get('fulfiller', {}).get(
                'githubUsername', '')
        if github_username:
            if is_blocked(github_username):
                continue
            try:
                kwargs['profile_id'] = Profile.objects.get(handle__iexact=github_username).pk
            except Profile.MultipleObjectsReturned:
                kwargs['profile_id'] = Profile.objects.filter(handle__iexact=github_username).first().pk
            except Profile.DoesNotExist:
                pass
        if fulfillment.get('accepted'):
            kwargs['accepted'] = True
            accepted_on = timezone.now()
        try:
            created_on = timezone.now()
            modified_on = timezone.now()
            if old_bounty:
                old_fulfillments = old_bounty.fulfillments.filter(fulfillment_id=fulfillment.get('id')).nocache()
                if old_fulfillments.exists():
                    old_fulfillment = old_fulfillments.first()
                    created_on = old_fulfillment.created_on
                    modified_on = old_fulfillment.modified_on
                    if old_fulfillment.accepted:
                        accepted_on = old_fulfillment.accepted_on
            hours_worked = fulfillment.get('data', {}).get(
                    'payload', {}).get('fulfiller', {}).get('hoursWorked', None)
            if not hours_worked or not hours_worked.isdigit():
                hours_worked = None
            new_bounty.fulfillments.create(
                fulfiller_address=fulfillment.get(
                    'fulfiller',
                    '0x0000000000000000000000000000000000000000'),
                fulfiller_email=fulfillment.get('data', {}).get(
                    'payload', {}).get('fulfiller', {}).get('email', ''),
                fulfiller_github_username=github_username,
                fulfiller_name=fulfillment.get('data', {}).get(
                    'payload', {}).get('fulfiller', {}).get('name', ''),
                fulfiller_metadata=fulfillment,
                fulfillment_id=fulfillment.get('id'),
                fulfiller_github_url=fulfillment.get('data', {}).get(
                    'payload', {}).get('fulfiller', {}).get('githubPRLink', ''),
                fulfiller_hours_worked=hours_worked,
                created_on=created_on,
                modified_on=modified_on,
                accepted_on=accepted_on,
                **kwargs)
        except Exception as e:
            logger.error(f'{e} during new fulfillment creation for {new_bounty}')
            continue

    if new_bounty:
        return new_bounty.fulfillments.all()


def create_new_bounty(old_bounties, bounty_payload, bounty_details, bounty_id):
    """Handle new Bounty creation in the event of bounty changes.

    Possible Bounty Stages:
        0: Draft
        1: Active
        2: Dead

    Returns:
        dashboard.models.Bounty: The new Bounty object.

    """
    bounty_issuer = bounty_payload.get('issuer', {})
    metadata = bounty_payload.get('metadata', {})
    # fulfillments metadata will be empty when bounty is first created
    fulfillments = bounty_details.get('fulfillments', {})
    interested_comment_id = None
    submissions_comment_id = None
    interested_comment_id = None

    # start to process out all the bounty data
    url = bounty_payload.get('webReferenceURL')
    if url:
        url = normalize_url(url)
    else:
        raise UnsupportedSchemaException('No webReferenceURL found. Cannot continue!')

    # check conditions for private repos
    if metadata.get('repo_type', None) == 'private' and \
        bounty_payload.get('schemes', {}).get('permission_type', 'permissionless') != 'approval' and \
            bounty_payload.get('schemes', {}).get('project_type', 'traditional') != 'traditional':
            raise UnsupportedSchemaException('The project type or permission does not match for private repo')


    # Check if we have any fulfillments.  If so, check if they are accepted.
    # If there are no fulfillments, accepted is automatically False.
    # Currently we are only considering the latest fulfillment.  Std bounties supports multiple.
    # If any of the fulfillments have been accepted, the bounty is now accepted and complete.
    accepted = any([fulfillment.get('accepted') for fulfillment in fulfillments])
    print('create new bounty with payload:{}'.format(bounty_payload))

    with transaction.atomic():
        old_bounties = old_bounties.distinct().order_by('created_on')
        latest_old_bounty = None
        token_address = bounty_payload.get('tokenAddress', '0x0000000000000000000000000000000000000000')
        token_name = bounty_payload.get('tokenName', '')
        if not token_name:
            token = addr_to_token(token_address)
            if token:
                token_name = token['name']

        for old_bounty in old_bounties:
            if old_bounty.current_bounty:
                submissions_comment_id = old_bounty.submissions_comment
                interested_comment_id = old_bounty.interested_comment
            old_bounty.current_bounty = False
            old_bounty.save()
            latest_old_bounty = old_bounty

        bounty_kwargs = {
            'is_open': True if (bounty_details.get('bountyStage') == 1 and not accepted) else False,
            'raw_data': bounty_details,
            'metadata': metadata,
            'current_bounty': True,
            'accepted': accepted,
            'interested_comment': interested_comment_id,
            'submissions_comment': submissions_comment_id,
            'standard_bounties_id': bounty_id,
            'num_fulfillments': len(fulfillments),
            'value_in_token': bounty_details.get('fulfillmentAmount', Decimal(1.0)),
            'fee_tx_id': bounty_payload.get('fee_tx_id', '0x0'),
            'fee_amount': bounty_payload.get('fee_amount', 0)
        }

        coupon_code = bounty_payload.get('coupon_code', None)
        if coupon_code:
            coupon = Coupon.objects.get(code=coupon_code)
            if coupon:
                bounty_kwargs.update({
                    'coupon_code': coupon
                })

        if not latest_old_bounty:
            print("no latest old bounty")
            schemes = bounty_payload.get('schemes', {})
            unsigned_nda = None
            if bounty_payload.get('unsigned_nda', None):
                unsigned_nda = BountyDocuments.objects.filter(
                    pk=bounty_payload.get('unsigned_nda')
                ).first()
            bounty_kwargs.update({
                # info to xfr over from latest_old_bounty as override fields (this is because sometimes
                # ppl dont login when they first submit issue and it needs to be overridden)
                'web3_created': timezone.make_aware(
                    timezone.datetime.fromtimestamp(bounty_payload.get('created')),
                    timezone=UTC),
                'github_url': url,
                'token_name': token_name,
                'token_address': token_address,
                'privacy_preferences': bounty_payload.get('privacy_preferences', {}),
                'expires_date': timezone.make_aware(
                    timezone.datetime.fromtimestamp(bounty_details.get('deadline')),
                    timezone=UTC),
                'title': bounty_payload.get('title', ''),
                'issue_description': bounty_payload.get('description', ' '),
                'balance': bounty_details.get('balance'),
                'contract_address': bounty_details.get('token'),
                'network': bounty_details.get('network'),
                'bounty_type': metadata.get('bountyType', ''),
                'bounty_categories': metadata.get('bounty_categories', '').split(','),
                'funding_organisation': metadata.get('fundingOrganisation', ''),
                'project_length': metadata.get('projectLength', ''),
                'estimated_hours': metadata.get('estimatedHours'),
                'experience_level': metadata.get('experienceLevel', ''),
                'project_type': schemes.get('project_type', 'traditional'),
                'permission_type': schemes.get('permission_type', 'permissionless'),
                'attached_job_description': bounty_payload.get('hiring', {}).get('jobDescription', None),
                'is_featured': metadata.get('is_featured', False),
                'featuring_date': timezone.make_aware(
                    timezone.datetime.fromtimestamp(metadata.get('featuring_date', 0)),
                    timezone=UTC),
                'repo_type': metadata.get('repo_type', 'public'),
                'unsigned_nda': unsigned_nda,
                'bounty_owner_github_username': bounty_issuer.get('githubUsername', ''),
                'bounty_owner_address': bounty_issuer.get('address', ''),
                'bounty_owner_email': bounty_issuer.get('email', ''),
                'bounty_owner_name': bounty_issuer.get('name', ''),
                'admin_override_suspend_auto_approval': not schemes.get('auto_approve_workers', True),
                'fee_tx_id': bounty_payload.get('fee_tx_id', '0x0'),
                'fee_amount': bounty_payload.get('fee_amount', 0)
            })
        else:
            print('latest old bounty found {}'.format(latest_old_bounty))
            latest_old_bounty_dict = latest_old_bounty.to_standard_dict(
                fields=[
                    'web3_created', 'github_url', 'token_name', 'token_address', 'privacy_preferences', 'expires_date',
                    'title', 'issue_description', 'balance', 'contract_address', 'network', 'bounty_type',
                    'bounty_categories', 'project_length', 'experience_level', 'project_type', 'permission_type',
                    'attached_job_description', 'bounty_owner_github_username', 'bounty_owner_address',
                    'bounty_owner_email', 'bounty_owner_name', 'github_comments', 'override_status', 'last_comment_date',
                    'snooze_warnings_for_days', 'admin_override_and_hide', 'admin_override_suspend_auto_approval',
                    'admin_mark_as_remarket_ready', 'funding_organisation', 'bounty_reserved_for_user', 'is_featured',
                    'featuring_date', 'fee_tx_id', 'fee_amount', 'repo_type', 'unsigned_nda', 'coupon_code',
                    'admin_override_org_name', 'admin_override_org_logo'
                ],
            )
            if latest_old_bounty_dict['bounty_reserved_for_user']:
                latest_old_bounty_dict['bounty_reserved_for_user'] = Profile.objects.get(pk=latest_old_bounty_dict['bounty_reserved_for_user'])
            if latest_old_bounty_dict.get('bounty_owner_profile'):
                latest_old_bounty_dict['bounty_owner_profile'] = Profile.objects.get(pk=latest_old_bounty_dict['bounty_owner_profile'])
            if latest_old_bounty_dict['unsigned_nda']:
                latest_old_bounty_dict['unsigned_nda'] = BountyDocuments.objects.filter(
                    pk=latest_old_bounty_dict['unsigned_nda']
                ).first()
            if latest_old_bounty_dict.get('coupon_code'):
                latest_old_bounty_dict['coupon_code'] = Coupon.objects.get(pk=latest_old_bounty_dict['coupon_code'])

            bounty_kwargs.update(latest_old_bounty_dict)

        try:
            print('new bounty with kwargs:{}'.format(bounty_kwargs))
            new_bounty = Bounty.objects.create(**bounty_kwargs)
            merge_bounty(latest_old_bounty, new_bounty, metadata, bounty_details)

        except Exception as e:
            print(e, 'encountered during new bounty creation for:', url)
            logger.error(f'{e} encountered during new bounty creation for: {url}')
            new_bounty = None

    return new_bounty


# merges the bounties
def merge_bounty(latest_old_bounty, new_bounty, metadata, bounty_details, verbose=True):
    if verbose:
        print('new bounty is:{}'.format(new_bounty.to_standard_dict()))
    new_bounty.fetch_issue_item()
    try:
        issue_kwargs = get_url_dict(new_bounty.github_url)
        new_bounty.github_issue_details = get_gh_issue_details(**issue_kwargs)

    except Exception as e:
        logger.error(e)

    event_tag = metadata.get('eventTag', '')
    if event_tag:
        try:
            evt = HackathonEvent.objects.filter(name__iexact=event_tag).latest('id')
            new_bounty.event = evt
            new_bounty.save()
        except Exception as e:
            logger.error(e)

    bounty_invitees = metadata.get('invite', '')
    if bounty_invitees and not latest_old_bounty:
        from marketing.mails import share_bounty
        from dashboard.utils import get_bounty_invite_url
        emails = []
        inviter = Profile.objects.get(handle=new_bounty.bounty_owner_github_username)
        invite_url = get_bounty_invite_url(inviter, new_bounty.id)
        msg = "Check out this bounty that pays out " + \
            str(new_bounty.get_value_true) + new_bounty.token_name + invite_url
        for keyword in new_bounty.keywords_list:
            msg += " #" + keyword
        for user_id in bounty_invitees:
            profile = Profile.objects.get(id=int(user_id))
            bounty_invite = BountyInvites.objects.create(
                status='pending'
            )
            bounty_invite.bounty.add(new_bounty)
            bounty_invite.inviter.add(inviter.user)
            bounty_invite.invitee.add(profile.user)
            emails.append(profile.email)
        try:
            share_bounty(emails, msg, inviter, invite_url, False)
            response = {
                'status': 200,
                'msg': 'email_sent',
            }
        except Exception as e:
            logging.exception(e)
            response = {
                'status': 500,
                'msg': 'Email not sent',
            }
    # migrate data objects from old bounty
    if latest_old_bounty:
        # Pull the interested parties off the last old_bounty
        for interest in latest_old_bounty.interested.all().nocache():
            new_bounty.interested.add(interest)

        # pull the activities off the last old bounty
        for activity in latest_old_bounty.activities.all().nocache():
            new_bounty.activities.add(activity)


    bounty_reserved_for_user = metadata.get('reservedFor', '')
    if bounty_reserved_for_user:
        new_bounty.reserved_for_user_handle = bounty_reserved_for_user
        new_bounty.save()
        if new_bounty.bounty_reserved_for_user:
            # notify a user that a bounty has been reserved for them
            new_reserved_issue('founders@gitcoin.co', new_bounty.bounty_reserved_for_user, new_bounty)

    # set cancel date of this bounty
    canceled_on = latest_old_bounty.canceled_on if latest_old_bounty and latest_old_bounty.canceled_on else None
    if not canceled_on and new_bounty.status == 'cancelled':
        canceled_on = timezone.now()
    if canceled_on:
        new_bounty.canceled_on = canceled_on
        new_bounty.save()

    # migrate fulfillments, and only take the ones from 
    # fulfillments metadata will be empty when bounty is first created
    fulfillments = bounty_details.get('fulfillments', {})
    if fulfillments:
        handle_bounty_fulfillments(fulfillments, new_bounty, latest_old_bounty)
        url = normalize_url(new_bounty.github_url)
        for inactive in Bounty.objects.filter(
            current_bounty=False, github_url=url
        ).nocache().order_by('-created_on'):
            BountyFulfillment.objects.filter(bounty_id=inactive.id).nocache().delete()

    # preserve featured status for bounties where it was set manually
    new_bounty.is_featured = True if latest_old_bounty and latest_old_bounty.is_featured is True else False
    if new_bounty.is_featured == True:
        new_bounty.save()
    
    if latest_old_bounty:
        latest_old_bounty.current_bounty = False
        latest_old_bounty.save()


def process_bounty_details(bounty_details):
    """Process bounty details.

    Args:
        bounty_details (dict): The Bounty details.

    Raises:
        UnsupportedSchemaException: Exception raised if the schema is unknown
            or unsupported.

    Returns:
        tuple: A tuple of bounty change data.
        tuple[0] (bool): Whether or not the Bounty changed.
        tuple[1] (dashboard.models.Bounty): The first old bounty object.
        tuple[2] (dashboard.models.Bounty): The new Bounty object.

    """
    from dashboard.utils import get_bounty_semaphore_ns
    # See dashboard/utils.py:get_bounty from details on this data
    print(bounty_details)
    bounty_id = bounty_details.get('id', {})
    bounty_data = bounty_details.get('data') or {}
    bounty_payload = bounty_data.get('payload', {})
    meta = bounty_data.get('meta', {})

    # what schema are we working with?
    schema_name = meta.get('schemaName', 'Unknown')
    schema_version = meta.get('schemaVersion', 'Unknown')
    if not schema_name or schema_name != 'gitcoinBounty':
        logger.info('Unknown Schema: %s - Version: %s', schema_name, schema_version)
        return (False, None, None)

    # Create new bounty (but only if things have changed)
    did_change, old_bounties = bounty_did_change(bounty_id, bounty_details)
    latest_old_bounty = old_bounties.nocache().order_by('-pk').first()

    if not did_change:
        return (did_change, latest_old_bounty, latest_old_bounty)

    semaphore_key = get_bounty_semaphore_ns(bounty_id)
    semaphore = get_semaphore(semaphore_key)

    try:
        with semaphore:
            new_bounty = create_new_bounty(old_bounties, bounty_payload, bounty_details, bounty_id)

            if new_bounty:
                return (did_change, latest_old_bounty, new_bounty)
            return (did_change, latest_old_bounty, latest_old_bounty)
    except SemaphoreExists:
        return (did_change, latest_old_bounty, latest_old_bounty)


def get_bounty_data_for_activity(bounty):
    """Get data from bounty to be saved in activity records.

    Args:
        bounty (dashboard.models.Bounty): The Bounty object.

    Returns:
        dict: The Bounty data represented as a dictionary.

    """
    data = {
        'id': bounty.pk,
        'value_in_eth': str(bounty.value_in_eth),
        'value_in_usdt_now': str(bounty.value_in_usdt_now),
        'value_in_token': str(bounty.value_in_token),
        'token_name': bounty.token_name,
        'token_value_time_peg': str(bounty.token_value_time_peg),
        'token_value_in_usdt': str(bounty.token_value_in_usdt),
        'title': bounty.title,
    }
    return data


def get_fulfillment_data_for_activity(fulfillment):
    """Get data from fulfillment to be saved in activity records.

    Args:
        fulfillment (dashboard.models.BountyFulfillment): The BountyFulfillment.

    Returns:
        dict: The BountyFulfillment data represented as a dictionary.

    """
    data = {
        'id': fulfillment.pk,
        'fulfiller_address': fulfillment.fulfiller_address,
        'fulfiller_email': fulfillment.fulfiller_email,
        'fulfiller_github_username': fulfillment.fulfiller_github_username,
        'fulfiller_name': fulfillment.fulfiller_name,
        'fulfiller_metadata': fulfillment.fulfiller_metadata,
        'fulfillment_id': fulfillment.fulfillment_id,
        'fulfiller_hours_worked': str(fulfillment.fulfiller_hours_worked),
        'fulfiller_github_url': fulfillment.fulfiller_github_url,
        'accepted': fulfillment.accepted,
        'accepted_on': str(fulfillment.accepted_on)
    }
    return data


def record_bounty_activity(event_name, old_bounty, new_bounty, _fulfillment=None):
    """Records activity based on bounty changes

    Args:
        event_name (string): the event
        old_bounty (dashboard.models.Bounty): The old Bounty object.
        new_bounty (dashboard.models.Bounty): The new Bounty object.

    Raises:
        Exception: Log all exceptions that occur during fulfillment checks.

    Returns:
        dashboard.Activity: The Activity object if user_profile is present or None.

    """
    user_profile = None
    fulfillment = _fulfillment
    try:
        user_profile = Profile.objects.filter(handle__iexact=new_bounty.bounty_owner_github_username).first()
        funder_actions = ['new_bounty',
                          'worker_approved',
                          'killed_bounty',
                          'increased_bounty',
                          'worker_rejected',
                          'bounty_changed']
        if event_name not in funder_actions:
            if not fulfillment:
                fulfillment = new_bounty.fulfillments.order_by('-pk').first()
                if event_name == 'work_done':
                    fulfillment = new_bounty.fulfillments.filter(accepted=True).latest('fulfillment_id')
            if fulfillment:
                user_profile = Profile.objects.filter(handle__iexact=fulfillment.fulfiller_github_username).first()
                if not user_profile:
                    user_profile = sync_profile(fulfillment.fulfiller_github_username)

    except Exception as e:
        logger.error(f'{e} during record_bounty_activity for {new_bounty}')

    if user_profile:
        return Activity.objects.create(
            profile=user_profile,
            activity_type=event_name,
            bounty=new_bounty,
            metadata={
                'new_bounty': get_bounty_data_for_activity(new_bounty) if new_bounty else None,
                'old_bounty': get_bounty_data_for_activity(old_bounty) if old_bounty else None,
                'fulfillment': get_fulfillment_data_for_activity(fulfillment) if fulfillment else None,
            })
    return None


def record_user_action(event_name, old_bounty, new_bounty):
    """Record a user action.

    Args:
        event_name (str): The event to be recorded.
        old_bounty (Bounty): The old Bounty object.
        new_bounty (Bounty): The new Bounty object.

    Raises:
        Exception: Log all exceptions that occur during fulfillment checks.

    """
    user_profile = None
    fulfillment = None
    try:
        user_profile = Profile.objects.filter(handle__iexact=new_bounty.bounty_owner_github_username).first()
        fulfillment = new_bounty.fulfillments.order_by('pk').first()

    except Exception as e:
        logger.error(f'{e} during record_user_action for {new_bounty}')
        # TODO: create a profile if one does not exist already?

    if user_profile:
        UserAction.objects.create(
            profile=user_profile,
            action=event_name,
            metadata={
                'new_bounty': new_bounty.pk if new_bounty else None,
                'old_bounty': old_bounty.pk if old_bounty else None,
                'fulfillment': fulfillment.to_json if fulfillment else None,
            })


def process_bounty_changes(old_bounty, new_bounty):
    """Process Bounty changes.

    Args:
        old_bounty (dashboard.models.Bounty): The old Bounty object.
        new_bounty (dashboard.models.Bounty): The new Bounty object.

    """
    from dashboard.utils import build_profile_pairs
    profile_pairs = None
    # process bounty sync requests
    did_bsr = False
    for bsr in BountySyncRequest.objects.filter(processed=False, github_url=new_bounty.github_url).nocache():
        did_bsr = True
        bsr.processed = True
        bsr.save()

    # get json diff
    json_diff = diff(old_bounty.raw_data, new_bounty.raw_data) if (old_bounty and new_bounty) else None

    # new bounty
    if not old_bounty or (not old_bounty and new_bounty and new_bounty.is_open) or (not old_bounty.is_open and new_bounty and new_bounty.is_open):
        is_greater_than_x_days_old = new_bounty.web3_created < (timezone.now() - timezone.timedelta(hours=24))
        if is_greater_than_x_days_old and not settings.IS_DEBUG_ENV:
            msg = f"attempting to create a new bounty ({new_bounty.standard_bounties_id}) when is_greater_than_x_days_old = True"
            print(msg)
            raise Exception(msg)
        event_name = 'new_bounty'
    elif old_bounty.num_fulfillments < new_bounty.num_fulfillments:
        event_name = 'work_submitted'
    elif old_bounty.is_open and not new_bounty.is_open:
        if new_bounty.status in ['cancelled', 'expired']:
            event_name = 'killed_bounty'
        else:
            event_name = 'work_done'
    elif old_bounty.value_in_token < new_bounty.value_in_token:
        event_name = 'increased_bounty'
    else:
        event_name = 'unknown_event'
        logger.info(f'got an unknown event from bounty {old_bounty.pk} => {new_bounty.pk}: {json_diff}')

    print(f"- {event_name} event; diff => {json_diff}")

    # record a useraction for this
    record_user_action(event_name, old_bounty, new_bounty)
    record_bounty_activity(event_name, old_bounty, new_bounty)


    # Build profile pairs list
    if new_bounty.fulfillments.exists():
        profile_pairs = build_profile_pairs(new_bounty)

    # marketing
    if event_name != 'unknown_event':
        print("============ posting ==============")
        did_post_to_twitter = maybe_market_to_twitter(new_bounty, event_name)
        did_post_to_slack = maybe_market_to_slack(new_bounty, event_name)
        did_post_to_user_slack = maybe_market_to_user_slack(new_bounty, event_name)
        did_post_to_user_discord = maybe_market_to_user_discord(new_bounty, event_name)
        did_post_to_github = maybe_market_to_github(new_bounty, event_name, profile_pairs)
        did_post_to_email = maybe_market_to_email(new_bounty, event_name)
        print("============ done posting ==============")

        # what happened
        what_happened = {
            'did_bsr': did_bsr,
            'did_post_to_email': did_post_to_email,
            'did_post_to_github': did_post_to_github,
            'did_post_to_slack': did_post_to_slack,
            'did_post_to_user_slack': did_post_to_user_slack,
            'did_post_to_user_discord': did_post_to_user_discord,
            'did_post_to_twitter': did_post_to_twitter,
        }

        print("changes processed: ")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(what_happened)
    else:
        print('No notifications sent - Event Type Unknown = did_bsr: ', did_bsr)
