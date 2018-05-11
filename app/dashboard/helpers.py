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

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import transaction
from django.http import Http404, JsonResponse
from django.utils import timezone

import requests
from bs4 import BeautifulSoup
from dashboard.models import Bounty, BountyFulfillment, BountySyncRequest, UserAction
from dashboard.notifications import (
    maybe_market_to_email, maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter,
    maybe_market_to_user_slack,
)
from dashboard.tokens import addr_to_token
from economy.utils import convert_amount
from github.utils import _AUTH
from jsondiff import diff
from pytz import UTC
from ratelimit.decorators import ratelimit

from .models import Profile

logger = logging.getLogger(__name__)


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
    response = {}

    url = request.GET.get('url')
    url_val = URLValidator()
    try:
        url_val(url)
    except ValidationError as e:
        response['message'] = 'invalid arguments'
        return JsonResponse(response)

    if url.lower()[:19] != 'https://github.com/':
        response['message'] = 'invalid arguments'
        return JsonResponse(response)

    # Web format:  https://github.com/jasonrhaas/slackcloud/issues/1
    # API format:  https://api.github.com/repos/jasonrhaas/slackcloud/issues/1
    gh_api = url.replace('github.com', 'api.github.com/repos')

    try:
        api_response = requests.get(gh_api, auth=_AUTH)
    except ValidationError:
        response['message'] = 'could not pull back remote response'
        return JsonResponse(response)

    if api_response.status_code != 200:
        response['message'] = f'there was a problem reaching the github api, status code {api_response.status_code}'
        response['github_resopnse'] = api_response.json()
        return JsonResponse(response)

    try:
        response = api_response.json()
        body = response['body']
    except (KeyError, ValueError) as e:
        response['message'] = str(e)
    else:
        response['description'] = body.replace('\n', '').strip()
        response['title'] = response['title']

    keywords = []

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
        repo_url = None
        if '/pull' in url:
            repo_url = url.split('/pull')[0]
        if '/issue' in url:
            repo_url = url.split('/issue')[0]
        split_repo_url = repo_url.split('/')
        keywords.append(split_repo_url[-1])
        keywords.append(split_repo_url[-2])

        html_response = requests.get(repo_url, auth=_AUTH)
    except (AttributeError, ValidationError):
        response['message'] = 'could not pull back remote response'
        return JsonResponse(response)

    try:
        soup = BeautifulSoup(html_response.text, 'html.parser')

        eles = soup.findAll("span", {"class": "lang"})
        for ele in eles:
            keywords.append(ele.text)

    except ValidationError:
        response['message'] = 'could not parse html'
        return JsonResponse(response)

    try:
        response['keywords'] = keywords
    except Exception as e:
        print(e)
        response['message'] = 'could not find a title'

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
                kwargs['profile_id'] = Profile.objects.get(handle=github_username).pk
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
                title=bounty_payload.get('title', ''),
                issue_description=bounty_payload.get('description', ' '),
                web3_created=timezone.make_aware(
                    timezone.datetime.fromtimestamp(bounty_payload.get('created')),
                    timezone=UTC),
                value_in_token=bounty_details.get('fulfillmentAmount'),
                token_name=token_name,
                token_address=token_address,
                bounty_type=metadata.get('bountyType', ''),
                project_length=metadata.get('projectLength', ''),
                experience_level=metadata.get('experienceLevel', ''),
                github_url=url,  # Could also use payload.get('webReferenceURL')
                bounty_owner_address=bounty_issuer.get('address', ''),
                bounty_owner_email=bounty_issuer.get('email', ''),
                bounty_owner_github_username=bounty_issuer.get('githubUsername', ''),
                bounty_owner_name=bounty_issuer.get('name', ''),
                is_open=True if (bounty_details.get('bountyStage') == 1 and not accepted) else False,
                raw_data=bounty_details,
                metadata=metadata,
                current_bounty=True,
                contract_address=bounty_details.get('token'),
                network=bounty_details.get('network'),
                accepted=accepted,
                interested_comment=interested_comment_id,
                submissions_comment=submissions_comment_id,
                privacy_preferences=bounty_payload.get('privacy_preferences', {}),
                # These fields are after initial bounty creation, in bounty_details.js
                expires_date=timezone.make_aware(
                    timezone.datetime.fromtimestamp(bounty_details.get('deadline')),
                    timezone=UTC),
                standard_bounties_id=bounty_id,
                balance=bounty_details.get('balance'),
                num_fulfillments=len(fulfillments),
                # info to xfr over from latest_old_bounty
                github_comments=latest_old_bounty.github_comments if latest_old_bounty else 0,
                override_status=latest_old_bounty.override_status if latest_old_bounty else '',
                last_comment_date=latest_old_bounty.last_comment_date if latest_old_bounty else None,
                snooze_warnings_for_days=latest_old_bounty.snooze_warnings_for_days if latest_old_bounty else 0,
            )
            new_bounty.fetch_issue_item()

            # Pull the interested parties off the last old_bounty
            if latest_old_bounty:
                for interest in latest_old_bounty.interested.all():
                    new_bounty.interested.add(interest)

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

    if not schema_name:
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


def record_user_action(event_name, old_bounty, new_bounty):
    """Records a user action 

    Args:
        event_name (string): the event
        old_bounty (Bounty): the old_bounty
        new_bounty (Bounty): the new_bounty

    Raises:
        None

    Returns:
        None
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
    elif old_bounty.value_in_token < new_bounty.value_in_token:
        event_name = 'increase_payout'
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

    # Build profile pairs list
    if new_bounty.fulfillments.exists():
        profile_pairs = build_profile_pairs(new_bounty)

    # marketing
    if event_name != 'unknown_event':
        print("============ posting ==============")
        did_post_to_twitter = maybe_market_to_twitter(new_bounty, event_name)
        did_post_to_slack = maybe_market_to_slack(new_bounty, event_name)
        did_post_to_user_slack = maybe_market_to_user_slack(new_bounty, event_name)
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
            'did_post_to_twitter': did_post_to_twitter,
        }

        print("changes processed: ")
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(what_happened)
    else:
        print('No notifications sent - Event Type Unknown = did_bsr: ', did_bsr)
