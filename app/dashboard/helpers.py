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
import csv
import datetime
import io
import logging
import math
import pprint
import time
from decimal import Decimal
from enum import Enum
from math import ceil

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.http import Http404, JsonResponse
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from app.utils import sync_profile
from dashboard.models import Activity, Bounty, BountyFulfillment, BountySyncRequest, UserAction
from dashboard.notifications import (
    maybe_market_to_email, maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter,
    maybe_market_to_user_discord, maybe_market_to_user_slack,
)
from dashboard.tokens import addr_to_token
from economy.utils import convert_amount, eth_from_wei, etherscan_link
from git.utils import get_gh_issue_details, get_url_dict
from jsondiff import diff
from pytz import UTC
from ratelimit.decorators import ratelimit

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
            'value_in_token': bounty_details.get('fulfillmentAmount', Decimal(1.0))
        }
        if not latest_old_bounty:
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
                'funding_organisation': metadata.get('fundingOrganisation', ''),
                'project_length': metadata.get('projectLength', ''),
                'experience_level': metadata.get('experienceLevel', ''),
                'project_type': bounty_payload.get('schemes', {}).get('project_type', 'traditional'),
                'permission_type': bounty_payload.get('schemes', {}).get('permission_type', 'permissionless'),
                'attached_job_description': bounty_payload.get('hiring', {}).get('jobDescription', None),
                'bounty_owner_github_username': bounty_issuer.get('githubUsername', ''),
                'bounty_owner_address': bounty_issuer.get('address', ''),
                'bounty_owner_email': bounty_issuer.get('email', ''),
                'bounty_owner_name': bounty_issuer.get('name', ''),
            })
        else:
            latest_old_bounty_dict = latest_old_bounty.to_standard_dict(
                fields=[
                    'web3_created', 'github_url', 'token_name', 'token_address', 'privacy_preferences', 'expires_date',
                    'title', 'issue_description', 'balance', 'contract_address', 'network', 'bounty_type',
                    'project_length', 'experience_level', 'project_type', 'permission_type', 'attached_job_description',
                    'bounty_owner_github_username', 'bounty_owner_address', 'bounty_owner_email', 'bounty_owner_name',
                    'github_comments', 'override_status', 'last_comment_date', 'snooze_warnings_for_days',
                    'admin_override_and_hide', 'admin_override_suspend_auto_approval', 'admin_mark_as_remarket_ready',
                    'funding_organisation'
                ],
            )
            bounty_kwargs.update(latest_old_bounty_dict)

        try:
            new_bounty = Bounty.objects.create(**bounty_kwargs)
            new_bounty.fetch_issue_item()
            try:
                issue_kwargs = get_url_dict(new_bounty.github_url)
                new_bounty.github_issue_details = get_gh_issue_details(**issue_kwargs)
            except Exception as e:
                logger.error(e)

            # migrate data objects from old bounty
            if latest_old_bounty:
                # Pull the interested parties off the last old_bounty
                for interest in latest_old_bounty.interested.all().nocache():
                    new_bounty.interested.add(interest)

                # pull the activities off the last old bounty
                for activity in latest_old_bounty.activities.all().nocache():
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
            logger.error(f'{e} encountered during new bounty creation for: {url}')
            new_bounty = None

        if fulfillments:
            handle_bounty_fulfillments(fulfillments, new_bounty, latest_old_bounty)
            for inactive in Bounty.objects.filter(
                current_bounty=False, github_url=url
            ).nocache().order_by('-created_on'):
                BountyFulfillment.objects.filter(bounty_id=inactive.id).nocache().delete()
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
    latest_old_bounty = old_bounties.nocache().order_by('-pk').first()

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


def week_of_month(in_datetime):
    """Get the current week of the month as a number.

    Args:
        in_datetime (datetime): the input datetime to get the week of month for.

    Returns:
        int: The week of the month (1,2,3,4,5).

    """
    day_of_month = in_datetime.day
    adjusted_day_of_month = day_of_month + in_datetime.replace(day=1).weekday()

    return int(ceil(adjusted_day_of_month/7.0))


def get_payout_history(done_bounties):
    """Aggregate a funder's payout history given a set of bounties that belong to that funder.

    Args:
        done_bounties: (BountyQuerySet) the bounties to aggregate the data for, should be in "done" status.

    Returns:
        dict: A dictionary containing a funder's payout history, grouped as weekly, monthly and yearly, as well as
              a csv representation of the funder's all time payout history.

    """
    utc_now = datetime.datetime.now(timezone.utc)
    month_now = utc_now.month
    year_now = utc_now.year

    # 0: weekly
    # 1: monthly
    # 2: yearly
    working_payout_history = [{}, {}, {}]

    weekly_payout_history = working_payout_history[0]
    monthly_payout_history = working_payout_history[1]
    yearly_payout_history = working_payout_history[2]

    csv_all_time_paid_bounties = io.StringIO()
    wr = csv.writer(csv_all_time_paid_bounties, quoting=csv.QUOTE_ALL)
    wr.writerow([
        'Issue ID', 'Title', 'Bounty Type', 'Github Link', 'Value in USD', 'Value in ETH'
    ])

    for bounty in done_bounties:
        bounty_date = bounty.fulfillment_accepted_on
        if bounty_date is None:
            continue

        bounty_val = bounty.get_value_in_usdt

        if bounty_val is None:
            bounty_val = 0.0

        # csv export - all done bounties
        csv_row = []
        fd_bounty = to_funder_dashboard_bounty(bounty)

        csv_row.append(fd_bounty['id'])
        csv_row.append(fd_bounty['title'])
        csv_row.append(fd_bounty['type'])
        csv_row.append(fd_bounty['githubLink'])
        csv_row.append(fd_bounty['worthDollars'])
        csv_row.append(fd_bounty['worthEth'])

        wr.writerow(csv_row)

        week = week_of_month(bounty_date)
        month = bounty_date.month
        year = bounty_date.year

        # weekly payout history
        if year == year_now and month == month_now:
            if weekly_payout_history.get(week):
                weekly_payout_history[week] = weekly_payout_history[week] + bounty_val
            else:
                weekly_payout_history[week] = bounty_val

        # monthly payout history
        if year == year_now:
            if monthly_payout_history.get(month):
                monthly_payout_history[month] = monthly_payout_history[month] + bounty_val
            else:
                monthly_payout_history[month] = bounty_val

        # yearly payout history
        if yearly_payout_history.get(year):
            yearly_payout_history[year] = yearly_payout_history[year] + bounty_val
        else:
            yearly_payout_history[year] = bounty_val

    payout_history = []
    for i in range(0, 3):
        payout_history.append({
            "data": [],
            "labels": []
        })

    for index, payout_history_in_period in enumerate(working_payout_history):
        for key, value in sorted(payout_history_in_period.items()):
            payout_history[index]['data'].append(value)
            payout_history[index]['labels'].append(key)

    csv_data = csv_all_time_paid_bounties.getvalue()
    csv_all_time_paid_bounties.close()

    return {
        # Used for payout history chart
        'weekly': payout_history[0],
        'monthly': payout_history[1],
        'yearly': payout_history[2],
        # Used for csv export
        'csv_all_time_paid_bounties': csv_data
    }


def to_funder_expiring_bounty_notifications(expiring_bounties):
    """Maps expiring bounties into a list of dictionary objects to be displayed as notifications for these expiring
    bounties in the funder dashboard.

    Args:
        expiring_bounties: (BountyQuerySet) The expiring bounties to search in.

    Returns:
        list of dict: A list of dictionaries of the form {
            title: bounty id and title formatted for display,
            expiring_days: the number of days in which the bounty is expiring, can be 0,
            url: the Gitcoin url to the bounty
        }

    """

    utc_now = datetime.datetime.now(timezone.utc)
    expiring_bounty_notifications = []

    for bounty in expiring_bounties:
        expiring_bounty_notifications.append({
            "title": f"#{bounty.id}: {bounty.title}",
            "expiring_days": (bounty.expires_date - utc_now).days,
            "url": bounty.url
        })

    return expiring_bounty_notifications


def get_top_contributors(done_bounties, contributors_to_take):
    """Get the top contributors for a set of done bounties.

    Args:
        done_bounties: (BountyQuerySet) A set of bounties with status done, that will be searched in.
        contributors_to_take: (int) Take the first X contributors. If 12, will take 12 contributors.

    Returns:
        list of dict: A list of up to max_contributor_count objects of the form: {
            githubLink (a link to the contributor's github profile),
            profilePictureSrc (a link to the contributor's profile picture),
            handle (the contributor's github username)
        }

    """
    contributors_usernames = []

    for bounty in done_bounties:
        contributors = bounty.fulfillments.filter(accepted_on__isnull=False) \
            .values('fulfiller_github_username') \
            .distinct()

        for contributor in contributors:
            contributor_github_username = contributor['fulfiller_github_username']
            if (
                contributor_github_username
                and contributor_github_username not in contributors_usernames
                and len(contributors_usernames) <= contributors_to_take
            ):
                contributors_usernames.append(contributor_github_username)

    top_contributors = []
    for contributor_github_username in contributors_usernames:
        top_contributors.append({
            'githubLink': 'https://gitcoin.co/profile/' + contributor_github_username,
            'profilePictureSrc': '/dynamic/avatar/' + contributor_github_username,
            'handle': contributor_github_username,
        })

    return top_contributors


def is_funder_allowed_to_input_total_budget(total_budget_last_update_date, funder_total_budget_type):
    """Describe whether a funder should be able to set a total_budget,
       based on the date that they updated their total budget last time, and the total budget type they set.

        A funder is only allowed to input a total budget if the updated total budget date is null,
            or if there is an updated on date but the type saved is monthly and the months are different,
            or if there is an updated on date but the type saved is quarterly and the quarters are different.

    Args:
        total_budget_last_update_date: (datetime) Last time the total budget was updated for a user, utc time.
        funder_total_budget_type: (string) either 'monthly' or 'quarterly'. Describes what kind of budget a user set.

    Returns:
        bool: True if the funder can input a total budget, False otherwise.

    """
    allow_total_budget_input = False

    if total_budget_last_update_date is None:
        allow_total_budget_input = True
    else:
        month_saved = total_budget_last_update_date.month
        month_now = datetime.datetime.now(timezone.utc).month

        if funder_total_budget_type == 'monthly' and month_now != month_saved:
            allow_total_budget_input = True
        elif funder_total_budget_type == 'quarterly':
            quarter_now = int(math.ceil(month_now / 3.))
            quarter_saved = int(math.ceil(month_saved / 3.))

            if quarter_now != quarter_saved:
                allow_total_budget_input = True

    return allow_total_budget_input


def get_funder_total_budget(use_input_layout, funder_total_budget_dollars, budget_type):
    """Get the data needed for the total budget module of the funder dashboard, wrapped in a dictionary.

    Args:
        use_input_layout: (boolean) is funder allowed to edit their total budget or should the existing one be shown?
        funder_total_budget_dollars: (decimal) the total budget of the funder in dollars.
        budget_type: (str) "monthly" or "quarterly".

    Returns:
        dict: Contains the total budget of the funder in dollars and eth, and the time period in display format for
              which this budget is for.

    """
    utc_now = datetime.datetime.now(timezone.utc)

    if use_input_layout:
        total_budget_dollars = 0
        total_budget_eth = 0
        total_budget_used_time_period = None
    else:
        # we should display their total budget
        total_budget_dollars = funder_total_budget_dollars
        total_budget_eth = convert_amount(total_budget_dollars, "USDT", "ETH")

        if budget_type == 'monthly':
                total_budget_used_time_period = utc_now.strftime('%B')
        else:
            # it's a quarterly budget
            quarter_now = int(ceil(utc_now.month / 3.))

            if quarter_now == 0:
                total_budget_used_time_period = _("January 1 - March 31")
            elif quarter_now == 1:
                total_budget_used_time_period = _("April 1 - June 31")
            elif quarter_now == 2:
                total_budget_used_time_period = _("July 1 - September 31")
            else:
                # quarter_now == 3
                total_budget_used_time_period = _("October 1 - December 31")

    return {
        'total_budget_dollars': total_budget_dollars,
        'total_budget_eth': total_budget_eth,
        'total_budget_used_time_period': total_budget_used_time_period
    }


def get_funder_outgoing_funds(done_bounties, funder_tips):
    """Create the model for the outgoing funds table of the funder dashboard.

    Args:
        done_bounties: (BountyQuerySet) Done bounties that a funder has funded.
        funder_tips: (TipQuerySet) Tips sent from the funder to gitcoiners.

    Returns:
        list of dict: The outgoing funds of a user, to be JSON stringified for use in the front-end of the funder
        dashboard.
        Each dictionary object in the list is of the form: {
            id,
            createdOn (timestamp),
            etherscanLink,
            title,
            type ("Tip" / "Payment"),
            status ("Pending" / "Claimed"),
            worthEth,
            worthDollars
        }

    """
    def to_outgoing_fund(id, created_on, title, type, status, link_to_etherscan, worth_eth, worth_dollars):
        return {
            'id': id,
            'createdOn': time.mktime(created_on.timetuple()),
            'etherscanLink': link_to_etherscan,
            'title': escape(title),
            'type': type,
            'status': status,
            'worthEth': eth_format(eth_from_wei(worth_eth)),
            'worthDollars': usd_format(worth_dollars)
        }

    outgoing_funds = []
    for bounty in done_bounties:
        # TODO: Use the txid to generate the etherscan link.
        # link_to_etherscan = etherscan_link('#')

        if bounty.fulfillments.filter(accepted=True).exists():
            fund_status = 'Claimed'
        else:
            fund_status = 'Pending'

        outgoing_funds.append(to_outgoing_fund(bounty.github_issue_number,
                                               bounty.created_on,
                                               bounty.title,
                                               'Payment',
                                               fund_status,
                                               bounty.url,
                                               bounty.get_value_in_eth,
                                               bounty.get_value_in_usdt))

    for tip in funder_tips:
        if tip.status == "RECEIVED":
            tip_status = "Claimed"
        else:
            tip_status = "Pending"

        if tip.bounty:
            outgoing_funds.append(
                to_outgoing_fund(tip.bounty.github_issue_number,
                                 tip.bounty.created_on,
                                 tip.bounty.title,
                                 'Tip',
                                 tip_status,
                                 etherscan_link(tip.txid),
                                 tip.value_in_eth,
                                 tip.value_in_usdt))

    return outgoing_funds


def get_outgoing_funds_filters():
    """Get the filters that a funder can use to filter the "outgoing funds" table in the funder dashboard.

    Returns:
        dict: The filters, to be used in the template of the funder dashboard.

    """
    def outgoing_funds_filter(value, value_display, is_all_filter, is_type_filter, is_status_filter):
        return {
            'value': value,
            'value_display': value_display,
            'is_all_filter': is_all_filter,
            'is_type_filter': is_type_filter,
            'is_status_filter': is_status_filter
        }

    return [
        outgoing_funds_filter('All', _('All'), True, False, False),
        outgoing_funds_filter('Tip', _('Tip'), False, True, False),
        outgoing_funds_filter('Payment', _('Payment'), False, True, False),
        outgoing_funds_filter('Pending', _('Pending'), False, False, True),
        outgoing_funds_filter('Claimed', _('Claimed'), False, False, True),
    ]


def get_all_bounties_filters():
    """Get the filters that a funder can use to filter the "all bounties" table in the funder dashboard.

    Returns:
        dict: The filters, to be used in the template of the funder dashboard.

    """
    def all_bounties_filter(value, value_display, is_all_filter, is_status_pending_or_claimed_filter):
        return {
            'value': value,
            'value_display': value_display,
            'is_all_filter': is_all_filter,
            'is_status_pending_or_claimed_filter': is_status_pending_or_claimed_filter
        }

    return [
        all_bounties_filter('All', _('All'), True, False),
        all_bounties_filter('Pending', _('Pending'), False, True),
        all_bounties_filter('Claimed', _('Claimed'), False, True),
    ]


def usd_format(amount):
    """Convert an amount in USD to a display string format.

    Args:
        amount: (decimal) The amount in USD to display.

    Returns:
        str: The display format for the given USD amount, using 2 decimal places.

    """
    if amount is None:
        return "0"
    return format(amount, '.2f')


def eth_format(amount):
    """Convert an amount in ETH to a display string format.

    Args:
        amount: (decimal) The amount in ETH to display.

    Returns:
        str: The display format for the given ETH amount, using 3 decimal places.

    """
    if amount is None:
        return "0"
    return format(amount, '.3f')


def to_funder_dashboard_bounty(bounty):
    """Map a bounty object to a dict that is suitable for display in the funder dashboard.

    Args:
        bounty: (Bounty) the bounty to map.

    Returns:
        dict: The mapped bounty, to be JSON stringified for use in the front-end of the funder dashboard.
              The mapped bounty is of the form: {
                  id,
                  createdOn (timestamp),
                  githubLink,
                  title,
                  type,
                  status ("active", "done", "expired" etc. - uses bounty.status),
                  statusPendingOrClaimed ("Pending" / "Claimed"),
                  worthDollars,
                  worthEth
              }

    """
    bounty_dict = bounty.to_standard_dict(fields=['title', 'bounty_type'])
    bounty_dict.update({
        'id': bounty.github_issue_number,
        'createdOn': time.mktime(bounty.created_on.timetuple()),
        'githubLink': bounty.url,
        'title': escape(bounty_dict['title']),
        'type': bounty_dict.pop('bounty_type'),
        'status': bounty.status,
        'statusPendingOrClaimed': 'None',
        'worthEth': eth_format(eth_from_wei(bounty.get_value_in_eth)),
        'worthDollars': usd_format(bounty.get_value_in_usdt)
    })

    if bounty.interested.exists() and bounty.status in Bounty.FUNDED_STATUSES:
        bounty_dict['statusPendingOrClaimed'] = 'Claimed'
    elif bounty.status in Bounty.OPEN_STATUSES:
        bounty_dict['statusPendingOrClaimed'] = 'Pending'

    return bounty_dict
