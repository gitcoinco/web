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
import pprint
from enum import Enum
import datetime
import calendar

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.utils.html import escape

from app.utils import sync_profile
from dashboard.models import Activity, Bounty, BountyFulfillment, BountySyncRequest, UserAction
from dashboard.notifications import (
    maybe_market_to_email, maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter,
    maybe_market_to_user_discord, maybe_market_to_user_slack,
)
from dashboard.tokens import addr_to_token
from economy.utils import convert_amount
from git.utils import get_gh_issue_details, get_url_dict, issue_number, org_name, repo_name
from jsondiff import diff
from pytz import UTC
from ratelimit.decorators import ratelimit
from math import ceil

from .models import Profile

logger = logging.getLogger(__name__)


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
        amount = request.GET.get('amount')
        denomination = request.GET.get('denomination', 'ETH')
        if denomination == 'DAI':
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
    except Exception as e:
        print(e)
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
    from .utils import clean_bounty_url
    response = {}

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
            response = get_gh_issue_details(**url_dict)
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
        old_bounties = Bounty.objects.filter(standard_bounties_id=bounty_id, network=network).order_by('-created_on')

        if old_bounties.exists():
            did_change = (new_bounty_details != old_bounties.first().raw_data)
        else:
            did_change = True
    except Exception as e:
        did_change = True
        print(f"asserting did change because got the following exception: {e}. args; bounty_id: {bounty_id}, network: {network}")

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
    for fulfillment in fulfillments:
        kwargs = {}
        accepted_on = None
        github_username = fulfillment.get('data', {}).get(
            'payload', {}).get('fulfiller', {}).get(
                'githubUsername', '')
        if github_username:
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
                old_fulfillments = old_bounty.fulfillments.filter(fulfillment_id=fulfillment.get('id'))
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
            logging.error(f'{e} during new fulfillment creation for {new_bounty}')
            continue
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

    # Check if we have any fulfillments.  If so, check if they are accepted.
    # If there are no fulfillments, accepted is automatically False.
    # Currently we are only considering the latest fulfillment.  Std bounties supports multiple.
    # If any of the fulfillments have been accepted, the bounty is now accepted and complete.
    accepted = any([fulfillment.get('accepted') for fulfillment in fulfillments])

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
        try:
            new_bounty = Bounty.objects.create(
                is_open=True if (bounty_details.get('bountyStage') == 1 and not accepted) else False,
                raw_data=bounty_details,
                metadata=metadata,
                current_bounty=True,
                accepted=accepted,
                interested_comment=interested_comment_id,
                submissions_comment=submissions_comment_id,
                # These fields are after initial bounty creation, in bounty_details.js
                standard_bounties_id=bounty_id,
                num_fulfillments=len(fulfillments),
                value_in_token=bounty_details.get('fulfillmentAmount'),
                # info to xfr over from latest_old_bounty as override fields (this is because sometimes ppl dont login when they first submit issue and it needs to be overridden)
                web3_created=timezone.make_aware(
                    timezone.datetime.fromtimestamp(bounty_payload.get('created')),
                    timezone=UTC) if not latest_old_bounty else latest_old_bounty.web3_created,
                github_url=url if not latest_old_bounty else latest_old_bounty.github_url,
                token_name=token_name if not latest_old_bounty else latest_old_bounty.token_name,
                token_address=token_address if not latest_old_bounty else latest_old_bounty.token_address,
                privacy_preferences=bounty_payload.get('privacy_preferences', {}) if not latest_old_bounty else latest_old_bounty.privacy_preferences,
                expires_date=timezone.make_aware(
                    timezone.datetime.fromtimestamp(bounty_details.get('deadline')),
                    timezone=UTC) if not latest_old_bounty else latest_old_bounty.expires_date,
                title=bounty_payload.get('title', '') if not latest_old_bounty else latest_old_bounty.title,
                issue_description=bounty_payload.get('description', ' ') if not latest_old_bounty else latest_old_bounty.issue_description,
                balance=bounty_details.get('balance') if not latest_old_bounty else latest_old_bounty.balance,
                contract_address=bounty_details.get('token') if not latest_old_bounty else latest_old_bounty.contract_address,
                network=bounty_details.get('network') if not latest_old_bounty else latest_old_bounty.network,
                bounty_type=metadata.get('bountyType', '') if not latest_old_bounty else latest_old_bounty.bounty_type,
                project_length=metadata.get('projectLength', '') if not latest_old_bounty else latest_old_bounty.project_length,
                experience_level=metadata.get('experienceLevel', '') if not latest_old_bounty else latest_old_bounty.experience_level,
                project_type=bounty_payload.get('schemes', {}).get('project_type', 'traditional') if not latest_old_bounty else latest_old_bounty.project_type,
                permission_type=bounty_payload.get('schemes', {}).get('permission_type', 'permissionless') if not latest_old_bounty else latest_old_bounty.permission_type,
                attached_job_description=bounty_payload.get('hiring', {}).get('jobDescription', None) if not latest_old_bounty else latest_old_bounty.attached_job_description,
                bounty_owner_github_username=bounty_issuer.get('githubUsername', '') if not latest_old_bounty else latest_old_bounty.bounty_owner_github_username,
                bounty_owner_address=bounty_issuer.get('address', '') if not latest_old_bounty else latest_old_bounty.bounty_owner_address,
                bounty_owner_email=bounty_issuer.get('email', '') if not latest_old_bounty else latest_old_bounty.bounty_owner_email,
                bounty_owner_name=bounty_issuer.get('name', '') if not latest_old_bounty else latest_old_bounty.bounty_owner_name,
                # info to xfr over from latest_old_bounty
                github_comments=latest_old_bounty.github_comments if latest_old_bounty else 0,
                override_status=latest_old_bounty.override_status if latest_old_bounty else '',
                last_comment_date=latest_old_bounty.last_comment_date if latest_old_bounty else None,
                snooze_warnings_for_days=latest_old_bounty.snooze_warnings_for_days if latest_old_bounty else 0,
                admin_override_and_hide=latest_old_bounty.admin_override_and_hide if latest_old_bounty else 0,
                admin_override_suspend_auto_approval=latest_old_bounty.admin_override_suspend_auto_approval if latest_old_bounty else 0,
                admin_mark_as_remarket_ready=latest_old_bounty.admin_mark_as_remarket_ready if latest_old_bounty else 0,
            )
            new_bounty.fetch_issue_item()
            try:
                issue_kwargs = get_url_dict(new_bounty.github_url)
                new_bounty.github_issue_details = get_gh_issue_details(**issue_kwargs)
            except Exception as e:
                logger.error(e)

            # migrate data objects from old bounty
            if latest_old_bounty:
                # Pull the interested parties off the last old_bounty
                for interest in latest_old_bounty.interested.all():
                    new_bounty.interested.add(interest)

                # pull the activities off the last old bounty
                for activity in latest_old_bounty.activities.all():
                    new_bounty.activities.add(activity)

            # set cancel date of this bounty
            canceled_on = latest_old_bounty.canceled_on if latest_old_bounty and latest_old_bounty.canceled_on else None
            if not canceled_on and new_bounty.status == 'cancelled':
                canceled_on = timezone.now()
            if canceled_on:
                new_bounty.canceled_on = canceled_on
                new_bounty.save()

        except Exception as e:
            print(e, 'encountered during new bounty creation for:', url)
            logging.error(f'{e} encountered during new bounty creation for: {url}')
            new_bounty = None

        if fulfillments:
            handle_bounty_fulfillments(fulfillments, new_bounty, latest_old_bounty)
            for inactive in Bounty.objects.filter(current_bounty=False, github_url=url).order_by('-created_on'):
                BountyFulfillment.objects.filter(bounty_id=inactive.id).delete()
    return new_bounty


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
    # See dashboard/utils.py:get_bounty from details on this data
    bounty_id = bounty_details.get('id', {})
    bounty_data = bounty_details.get('data') or {}
    bounty_payload = bounty_data.get('payload', {})
    meta = bounty_data.get('meta', {})

    # what schema are we workign with?
    schema_name = meta.get('schemaName')
    schema_version = meta.get('schemaVersion', 'Unknown')

    if not schema_name or schema_name != 'gitcoinBounty':
        raise UnsupportedSchemaException(
            f'Unknown Schema: Unknown - Version: {schema_version}')

    # Create new bounty (but only if things have changed)
    did_change, old_bounties = bounty_did_change(bounty_id, bounty_details)
    latest_old_bounty = old_bounties.order_by('-pk').first()

    if not did_change:
        return (did_change, latest_old_bounty, latest_old_bounty)

    new_bounty = create_new_bounty(old_bounties, bounty_payload, bounty_details, bounty_id)

    if new_bounty:
        return (did_change, latest_old_bounty, new_bounty)
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
        funder_actions = ['new_bounty', 'worker_approved', 'killed_bounty', 'increased_bounty', 'worker_rejected']
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
        logging.error(f'{e} during record_bounty_activity for {new_bounty}')

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
        logging.error(f'{e} during record_user_action for {new_bounty}')
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
    for bsr in BountySyncRequest.objects.filter(processed=False, github_url=new_bounty.github_url):
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
        logging.error(f'got an unknown event from bounty {old_bounty.pk} => {new_bounty.pk}: {json_diff}')

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



def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """

    first_day = dt.replace(day=1)

    dom = dt.day
    adjusted_dom = dom + first_day.weekday()

    return int(ceil(adjusted_dom/7.0))


def get_payout_history(done_bounties):
    """ Returns payout history given a set of bounties

    Args:
        done_bounties: (BountyQuerySet) the bounties to aggregate the data for.
    """

    weekly = {
        "data": [],
        "labels": []
    }

    monthly = {
        "data": [],
        "labels": []
    }

    yearly = {
        "data": [],
        "labels": []
    }

    utc_now = datetime.datetime.now(timezone.utc)
    month_now = utc_now.month
    year_now = utc_now.year

    w = {}
    m = {}
    y = {}
    csv_all_time_paid_bounties = [[
        'Issue ID', 'Title', 'Bounty Type', 'Github Link', 'Value in USD', 'Value in ETH'
    ]]

    for bounty in done_bounties:
        bounty_date = bounty.fulfillment_accepted_on
        if bounty_date is None:
            continue

        bounty_val = bounty.get_value_in_usdt

        if bounty_val is None:
            bounty_val = 0.0

        # csv export - all done bounties, ever
        csv_row = []
        for key, value in to_funder_dashboard_bounty(bounty).items():
            if key == 'status' or key == 'statusPendingOrClaimed':
                continue
            csv_row.append(value)

        csv_all_time_paid_bounties.append(csv_row)

        week = week_of_month(bounty_date)
        month = bounty_date.month
        year = bounty_date.year

        # weekly payout history
        if year == year_now and month == month_now:
            if w.get(week):
                w[week] = w[week] + bounty_val
            else:
                w[week] = bounty_val

        # monthly payout history
        if year == year_now:
            if m.get(month):
                m[month] = m[month] + bounty_val
            else:
                m[month] = bounty_val

        # yearly payout history
        if y.get(year):
            y[year] = y[year] + bounty_val
        else:
            y[year] = bounty_val

    for key, value in sorted(w.items()):
        weekly['data'].append(key)
        weekly['labels'].append(value)

    for key, value in sorted(m.items()):
        monthly['data'].append(key)
        monthly['labels'].append(value)

    for key, value in sorted(y.items()):
        yearly['data'].append(key)
        yearly['labels'].append(value)

    return {
        # Used for payout history chart
        'weekly': weekly,
        'monthly': monthly,
        'yearly': yearly,
        # Used for csv export
        'csv_all_time_paid_bounties': csv_all_time_paid_bounties
    }


def to_funder_dashboard_bounty(bounty):
    pending_or_claimed = "None"

    if bounty.interested.exists():
        pending_or_claimed = 'Claimed'
    if bounty.status == 'open' or bounty.status == 'started' or bounty.status == 'submitted':
        pending_or_claimed = 'Pending'

    return {
        'id': bounty.github_issue_number,
        'title': escape(bounty.title),
        'type': bounty.bounty_type,
        'status': bounty.status,
        'statusPendingOrClaimed': pending_or_claimed,
        'githubLink': bounty.github_url,
        'worthDollars': usd_format(bounty.get_value_in_usdt),
        'worthEth': eth_format(bounty.get_value_in_eth)
    }


def usd_format(amount):
    if amount is None:
        return "0"
    return format(amount, '.2f')


def eth_format(amount):
    if amount is None:
        return "0"
    return format(amount, '.3f')
