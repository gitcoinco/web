# -*- coding: utf-8 -*-
'''
    Copyright (C) 2017 Gitcoin Core

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

'''
from __future__ import print_function, unicode_literals

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from dashboard.utils import generate_pub_priv_keypair, get_web3
from dashboard.views import record_user_action
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from git.utils import get_emails_master, get_github_primary_email
from marketing.mails import (
    admin_contact_funder, bounty_uninterested, start_work_approved, start_work_new_applicant, start_work_rejected,
)
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import Web3

from .models import (
    Activity, Bounty, CoinRedemption, CoinRedemptionRequest, Interest, Profile, ProfileSerializer, Subscription, Tip,
    Tool, ToolVote, UserAction,
)
from .notifications import (
    maybe_market_tip_to_email, maybe_market_tip_to_github, maybe_market_tip_to_slack, maybe_market_to_github,
    maybe_market_to_slack, maybe_market_to_twitter, maybe_market_to_user_discord, maybe_market_to_user_slack,
)
from .utils import (
    get_bounty, get_bounty_id, get_context, has_tx_mined, record_user_action_on_interest, web3_process_bounty,
)

logging.basicConfig(level=logging.DEBUG)

confirm_time_minutes_target = 4

logger = logging.getLogger(__name__)


def send_tip(request):
    """Handle the first stage of sending a tip."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': _('Send Tip'),
        'card_desc': _('Send a tip to any github user at the click of a button.'),
        'class': 'send',
    }

    return TemplateResponse(request, 'onepager/send1.html', params)


def record_tip_activity(tip, github_handle, event_name):
    kwargs = {
        'activity_type': event_name,
        'tip': tip,
        'metadata': {
            'amount': str(tip.amount),
            'token_name': tip.tokenName,
            'value_in_eth': str(tip.value_in_eth),
            'value_in_usdt_now': str(tip.value_in_usdt_now),
            'github_url': tip.github_url,
            'to_username': tip.username,
            'from_name': tip.from_name,
            'received_on': str(tip.received_on) if tip.received_on else None
        }
    }
    try:
        kwargs['profile'] = Profile.objects.get(handle=github_handle)
    except Profile.MultipleObjectsReturned:
        kwargs['profile'] = Profile.objects.filter(handle__iexact=github_handle).first()
    except Profile.DoesNotExist:
        logging.error(f"error in record_tip_activity: profile with github name {github_handle} not found")
        return
    try:
        kwargs['bounty'] = tip.bounty
    except:
        pass

    try:
        Activity.objects.create(**kwargs)
    except Exception as e:
        logging.error(f"error in record_tip_activity: {e} - {event_name} - {tip} - {github_handle}")


@csrf_exempt
@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def receive_tip_v3(request, key, txid, network):
    """Handle the receiving of a tip (the POST)

    Returns:
        TemplateResponse: the UI with the tip confirmed

    """

    these_tips = Tip.objects.filter(web3_type='v3', txid=txid, network=network)
    tips = these_tips.filter(metadata__reference_hash_for_receipient=key) | these_tips.filter(metadata__reference_hash_for_funder=key)
    tip = tips.first()
    is_authed = request.user.username.lower() == tip.username.lower() or request.user.username.lower() == tip.from_username.lower()
    not_mined_yet = get_web3(tip.network).eth.getBalance(Web3.toChecksumAddress(tip.metadata['address'])) == 0

    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect
    elif tip.receive_txid:
        messages.info(request, 'This tip has been received')
    elif not is_authed:
        messages.error(request, f'This tip is for @{tip.username} but you are logged in as @{request.user.username}.  Please logout and log back in as {tip.username}.')
    elif not_mined_yet:
        messages.info(request, f'This tx {tip.txid}, is still mining.  Please wait a moment before submitting the receive form.')
    elif request.GET.get('receive_txid') and not tip.receive_txid:
        params = request.GET

        # db mutations
        try:
            if params['save_addr']:
                profile = get_profile(tip.username)
                if profile:
                    profile.preferred_payout_address = params['forwarding_address']
                    profile.save()
            tip.receive_txid = params['receive_txid']
            tip.receive_address = params['forwarding_address']
            tip.received_on = timezone.now()
            tip.save()
            record_user_action(tip.from_username, 'receive_tip', tip)
            record_tip_activity(tip, tip.username, 'receive_tip')
            messages.success(request, 'This tip has been received')
        except Exception as e:
            messages.error(request, str(e))
            logger.exception(e)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'receive',
        'title': _('Receive Tip'),
        'gas_price': round(recommend_min_gas_price_to_confirm_in_time(120), 1),
        'tip': tip,
        'key': key,
        'is_authed': is_authed,
        'disable_inputs': tip.receive_txid or not_mined_yet or not is_authed,
    }

    return TemplateResponse(request, 'onepager/receive.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_tip_4(request):
    """Handle the fourth stage of sending a tip (the POST)

    Returns:
        JsonResponse: response with success state.

    """
    response = {
        'status': 'OK',
        'message': _('Tip Sent'),
    }

    is_user_authenticated = request.user.is_authenticated
    from_username = request.user.username if is_user_authenticated else ''

    params = json.loads(request.body)
    txid = params['txid']
    destinationAccount = params['destinationAccount']
    is_direct_to_recipient = params.get('is_direct_to_recipient', False)
    if is_direct_to_recipient:
        tip = Tip.objects.get(
            metadata__direct_address=destinationAccount,
            metadata__creation_time=params['creation_time'],
            metadata__salt=params['salt'],
            )
    else:
        tip = Tip.objects.get(
            metadata__address=destinationAccount,
            metadata__salt=params['salt'],
            )
    is_authenticated_for_this_via_login = (tip.from_username and tip.from_username == from_username)
    is_authenticated_for_this_via_ip = tip.ip == get_ip(request)
    is_authed = is_authenticated_for_this_via_ip or is_authenticated_for_this_via_login
    if not is_authed:
        response = {
            'status': 'error',
            'message': _('Permission Denied'),
        }
        return JsonResponse(response)

    # db mutations
    tip.txid = txid
    if is_direct_to_recipient:
        tip.receive_txid = txid
        tip.receive_address = destinationAccount
    tip.save()

    # notifications
    maybe_market_tip_to_github(tip)
    maybe_market_tip_to_slack(tip, 'New tip')
    maybe_market_tip_to_email(tip, tip.emails)
    record_user_action(tip.from_username, 'send_tip', tip)
    record_tip_activity(tip, tip.from_username, 'new_tip' if tip.username else 'new_crowdfund')

    return JsonResponse(response)


def get_profile(handle):
    try:
        to_profile = Profile.objects.get(handle__iexact=handle)
    except Profile.MultipleObjectsReturned:
        to_profile = Profile.objects.filter(handle__iexact=handle).order_by('-created_on').first()
    except Profile.DoesNotExist:
        to_profile = None
    return to_profile


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def tipee_address(request, handle):
    """returns the address, if any, that someone would like to be tipped directly at

    Returns:
        list of addresse

    """
    response = {
        'addresses': []
    }
    profile = get_profile(str(handle).replace('@', ''))
    if profile and profile.preferred_payout_address:
        response['addresses'].append(profile.preferred_payout_address)
    return JsonResponse(response)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_tip_3(request):
    """Handle the third stage of sending a tip (the POST)

    Returns:
        JsonResponse: response with success state.

    """
    response = {
        'status': 'OK',
        'message': _('Tip Created'),
    }

    is_user_authenticated = request.user.is_authenticated
    from_username = request.user.username if is_user_authenticated else ''
    primary_from_email = request.user.email if is_user_authenticated else ''
    access_token = request.user.profile.get_access_token() if is_user_authenticated else ''
    to_emails = []

    params = json.loads(request.body)

    to_username = params['username'].lstrip('@')
    to_emails = get_emails_master(to_username)

    if params.get('email'):
        to_emails.append(params['email'])

    # If no primary email in session, try the POST data. If none, fetch from GH.
    if params.get('fromEmail'):
        primary_from_email = params['fromEmail']
    elif access_token and not primary_from_email:
        primary_from_email = get_github_primary_email(access_token)

    to_emails = list(set(to_emails))
    expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])

    # metadata
    metadata = params['metadata']
    metadata['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

    # db mutations
    tip = Tip.objects.create(
        emails=to_emails,
        tokenName=params['tokenName'],
        amount=params['amount'],
        comments_priv=params['comments_priv'],
        comments_public=params['comments_public'],
        ip=get_ip(request),
        expires_date=expires_date,
        github_url=params['github_url'],
        from_name=params['from_name'] if params['from_name'] != 'False' else '',
        from_email=params['from_email'],
        from_username=from_username,
        username=params['username'],
        network=params['network'],
        tokenAddress=params['tokenAddress'],
        from_address=params['from_address'],
        is_for_bounty_fulfiller=params['is_for_bounty_fulfiller'],
        metadata=metadata,
        recipient_profile=get_profile(to_username),
        sender_profile=get_profile(from_username),
    )


    is_over_tip_tx_limit = False
    is_over_tip_weekly_limit = False
    max_per_tip = request.user.profile.max_tip_amount_usdt_per_tx if request.user.is_authenticated and request.user.profile else 500
    if tip.value_in_usdt_now:
        is_over_tip_tx_limit = tip.value_in_usdt_now > max_per_tip
        if request.user.is_authenticated and request.user.profile:
            tips_last_week_value = tip.value_in_usdt_now
            tips_last_week = Tip.objects.exclude(txid='').filter(sender_profile=get_profile(from_username), created_on__gt=timezone.now() - timezone.timedelta(days=7))
            for this_tip in tips_last_week:
                if this_tip.value_in_usdt_now:
                    tips_last_week_value += this_tip.value_in_usdt_now
            is_over_tip_weekly_limit = tips_last_week_value > request.user.profile.max_tip_amount_usdt_per_week

    increase_funding_form_title = _('Request a Funding Limit Increasement')
    increase_funding_form = f'<a target="_blank" href="{settings.BASE_URL}'\
                            f'requestincrease">{increase_funding_form_title}</a>'

    if is_over_tip_tx_limit:
        response['status'] = 'error'
        response['message'] = _('This tip is over the per-transaction limit of $') +\
            str(max_per_tip) + '. ' + increase_funding_form
    elif is_over_tip_weekly_limit:
        response['status'] = 'error'
        response['message'] = _('You are over the weekly tip send limit of $') +\
            str(request.user.profile.max_tip_amount_usdt_per_week) +\
            '. ' + increase_funding_form

    return JsonResponse(response)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_tip_2(request):
    """Handle the second stage of sending a tip.

    TODO:
        * Convert this view-based logic to a django form.

    Returns:
        JsonResponse: If submitting tip, return response with success state.
        TemplateResponse: Render the submission form.

    """

    is_user_authenticated = request.user.is_authenticated
    from_username = request.user.username if is_user_authenticated else ''
    primary_from_email = request.user.email if is_user_authenticated else ''

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': primary_from_email,
        'from_handle': from_username,
        'title': 'Send Tip | Gitcoin',
        'card_desc': 'Send a tip to any github user at the click of a button.',
    }

    return TemplateResponse(request, 'onepager/send2.html', params)
