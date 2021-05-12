# -*- coding: utf-8 -*-
"""Define the tip related views.

Copyright (C) 2021 Gitcoin Core

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
from __future__ import print_function, unicode_literals

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from dashboard.utils import get_web3, is_valid_eth_address
from dashboard.views import record_user_action
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from git.utils import get_emails_by_category, get_github_primary_email
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import Web3

from .models import Activity, FundRequest, Profile, Tip, TipPayout
from .notifications import maybe_market_tip_to_email, maybe_market_tip_to_github, maybe_market_tip_to_slack

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


def request_money(request):
    """"""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip('@')
        token_name = request.POST.get('tokenName')
        amount = request.POST.get('amount')
        comments = request.POST.get('comments')
        network = request.POST.get('network')
        address = request.POST.get('address')
        profiles = Profile.objects.filter(handle=username.lower())

        if network != 'ETH':
            token_name = ''

        if profiles.exists():
            profile = profiles.first()
            kwargs = {
                'profile': profile,
                'token_name': token_name,
                'network': network,
                'address': address,
                'amount': amount,
                'comments': comments,
                'requester': request.user.profile,
            }
            fund_request = FundRequest.objects.create(**kwargs)
            if network == 'ETH':
                if not profile.preferred_payout_address:
                    profile.preferred_payout_address = address
                    profile.save() #save preferred payout addr
            messages.success(request, f'Stay tuned, {profile.handle} has been notified by email.')
        else:
            messages.error(request, f'The user {username} doesn\'t exists.')

    params = {
        'class': 'send2',
        'title': 'Request Money | Gitcoin',
        'card_desc': 'Request money from any user at the click of a button.',
        'preferred_payout_address': request.user.profile.preferred_payout_address if request.user.is_authenticated else '',
    }

    return TemplateResponse(request, 'request_payment.html', params)

def record_tip_activity(tip, github_handle, event_name, override_created=None, other_handle=None):
    kwargs = {
        'created_on': timezone.now() if not override_created else override_created,
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

    associated_profile = get_profile(github_handle)
    if associated_profile:
        kwargs['profile'] = associated_profile

    associated_profile = get_profile(other_handle) if other_handle else None
    if associated_profile:
        kwargs['other_profile'] = associated_profile

    try:
        if tip.bounty:
            kwargs['bounty'] = tip.bounty
    except Exception:
        pass

    try:
        Activity.objects.create(**kwargs)
    except Exception as e:
        logger.debug('error in record_tip_activity: %s - %s - %s - %s', e, event_name, tip, github_handle)


@csrf_exempt
@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def receive_tip_v3(request, key, txid, network):
    """Handle the receiving of a tip (the POST).

    Returns:
        TemplateResponse: the UI with the tip confirmed.

    """
    these_tips = Tip.objects.filter(web3_type='v3', txid=txid, network=network)
    tips = these_tips.filter(metadata__reference_hash_for_receipient=key) | these_tips.filter(metadata__reference_hash_for_funder=key)
    tip = tips.first()
    if not tip:
        messages.error(request, 'This tip was not found')
        return redirect('/')
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        login_redirect = redirect('/login/github/?next=' + request.get_full_path())
        return login_redirect

    is_authed = request.user.username.lower() == tip.username.lower() or request.user.username.lower() == tip.from_username.lower() or not tip.username
    not_mined_yet = get_web3(tip.network).eth.getBalance(Web3.toChecksumAddress(tip.metadata['address'])) == 0
    did_fail = False
    if not_mined_yet:
        tip.update_tx_status()
        did_fail = tip.tx_status in ['dropped', 'unknown', 'na', 'error']

    num_redemptions = tip.metadata.get("num_redemptions", 0)
    max_redemptions = tip.metadata.get("max_redemptions", 0)
    is_redeemable = not (tip.receive_txid and (num_redemptions >= max_redemptions)) and is_authed
    has_this_user_redeemed = request.user.profile.tip_payouts.filter(tip=tip).count()
    if has_this_user_redeemed:
        is_redeemable = False
    if not is_redeemable:
        messages.info(request, 'This tip has been received already')
    elif not is_authed:
        messages.error(request, f'This tip is for @{tip.username} but you are logged in as @{request.user.username}.  Please logout and log back in as {tip.username}.')
    elif did_fail:
        messages.info(request, f'This tx {tip.txid}, failed.  Please contact the sender and ask them to send the tx again.')
    elif not_mined_yet:
        messages.info(request, f'This tx {tip.txid}, is still mining.  Please wait a moment before submitting the receive form.')
    elif request.POST.get('receive_txid') and is_redeemable:
        params = request.POST

        # db mutations
        try:
            profile = get_profile(tip.username)
            eth_address = params['forwarding_address']
            if not is_valid_eth_address(eth_address):
                eth_address = profile.preferred_payout_address
            if params['save_addr']:
                if profile:
                    profile.preferred_payout_address = eth_address
                    profile.save()
            tip.receive_txid = params['receive_txid']
            tip.receive_tx_status = 'pending'
            tip.receive_address = eth_address
            tip.received_on = timezone.now()
            num_redemptions = tip.metadata.get("num_redemptions", 0)
            # note to future self: to create a tip like this in the future set
            # tip.username
            # tip.metadata.max_redemptions
            # tip.metadata.override_send_amount
            # tip.amount to the amount you want to send
            # ,"override_send_amount":1,"max_redemptions":29

            num_redemptions += 1
            tip.metadata["num_redemptions"] = num_redemptions
            tip.save()
            record_user_action(tip.from_username, 'receive_tip', tip)
            record_tip_activity(tip, tip.username, 'receive_tip')
            TipPayout.objects.create(
                txid=tip.receive_txid,
                profile=request.user.profile,
                tip=tip,
                )
            messages.success(request, 'This tip has been received')
            is_redeemable = False
            has_this_user_redeemed = True
        except Exception as e:
            messages.error(request, str(e))
            logger.exception(e)

    gas_price_sanity_multiplier = 1.3
    params = {
        'issueURL': request.GET.get('source'),
        'class': 'receive',
        'title': _('Receive Tip'),
        'gas_price': round(float(gas_price_sanity_multiplier) * float(recommend_min_gas_price_to_confirm_in_time(1)), 1),
        'tip': tip,
        'has_this_user_redeemed': has_this_user_redeemed,
        'key': key,
        'is_redeemable': is_redeemable,
        'is_authed': is_authed,
        'disable_inputs': not is_redeemable or not is_authed,
    }

    return TemplateResponse(request, 'onepager/receive.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='25/m', method=ratelimit.UNSAFE, block=True)
def send_tip_4(request):
    """Handle the fourth stage of sending a tip (the POST).

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
    tip.tx_status = 'pending'
    if is_direct_to_recipient:
        tip.receive_txid = txid
        tip.receive_tx_status = 'pending'
        tip.receive_address = destinationAccount
        TipPayout.objects.create(
            txid=txid,
            profile=get_profile(tip.username),
            tip=tip,
            )
    tip.save()
    tip.trigger_townsquare()

    from townsquare.tasks import calculate_clr_match
    calculate_clr_match.delay()

    # notifications
    maybe_market_tip_to_github(tip)
    maybe_market_tip_to_slack(tip, 'New tip')
    if tip.primary_email:
        maybe_market_tip_to_email(tip, [tip.primary_email])
    record_user_action(tip.from_username, 'send_tip', tip)
    record_tip_activity(tip, tip.from_username, 'new_tip' if tip.username else 'new_crowdfund', False, tip.username)

    return JsonResponse(response)


def get_profile(handle):
    try:
        to_profile = Profile.objects.get(handle=handle.lower())
    except Profile.MultipleObjectsReturned:
        to_profile = Profile.objects.filter(handle=handle.lower()).order_by('-created_on').first()
    except Profile.DoesNotExist:
        to_profile = None
    return to_profile


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def tipee_address(request, handle):
    """Return the address, if any, that someone would like to be tipped directly at.

    Returns:
        list: The list of tipee address strings.

    """
    response = {
        'addresses': []
    }
    profile = get_profile(str(handle).replace('@', ''))
    if profile and profile.preferred_payout_address:
        response['addresses'].append(profile.preferred_payout_address)
    return JsonResponse(response)


@csrf_exempt
@ratelimit(key='ip', rate='15/m', method=ratelimit.UNSAFE, block=True)
def send_tip_3(request):
    """Handle the third stage of sending a tip (the POST).

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
    access_token = request.user.profile.get_access_token() if is_user_authenticated and request.user.profile else ''

    params = json.loads(request.body)

    to_username = params['username'].lstrip('@')
    to_emails = get_emails_by_category(to_username)
    primary_email = ''

    if params.get('email'):
        primary_email = params['email']
    elif to_emails.get('primary', None):
        primary_email = to_emails['primary']
    elif to_emails.get('github_profile', None):
        primary_email = to_emails['github_profile']
    else:
        if len(to_emails.get('events', None)):
            primary_email = to_emails['events'][0]
        else:
            print("TODO: no email found.  in the future, we should handle this case better because it's GOING to end up as a support request")
    if primary_email and isinstance(primary_email, list):
        primary_email = primary_email[0]

    # If no primary email in session, try the POST data. If none, fetch from GH.
    if params.get('fromEmail'):
        primary_from_email = params['fromEmail']
    elif access_token and not primary_from_email:
        primary_from_email = get_github_primary_email(access_token)

    expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])

    # metadata
    metadata = params['metadata']
    metadata['user_agent'] = request.META.get('HTTP_USER_AGENT', '')

    # db mutations
    tip = Tip.objects.create(
        primary_email=primary_email,
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
        network=params.get('network', 'unknown'),
        tokenAddress=params['tokenAddress'],
        from_address=params['from_address'],
        is_for_bounty_fulfiller=params['is_for_bounty_fulfiller'],
        metadata=metadata,
        recipient_profile=get_profile(to_username),
        sender_profile=get_profile(from_username),
    )

    return JsonResponse(response)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
@login_required
def send_tip_2(request):
    """Handle the second stage of sending a tip.

    TODO:
        * Convert this view-based logic to a django form.

    Returns:
        JsonResponse: If submitting tip, return response with success state.
        TemplateResponse: Render the submission form.

    """
    profile = None
    fund_request = None
    username = request.GET.get('username', None)
    pk_fund_request = request.GET.get('request', None)
    is_user_authenticated = request.user.is_authenticated
    from_username = request.user.username if is_user_authenticated else ''
    primary_from_email = request.user.email if is_user_authenticated else ''

    user = {}
    if username:
        profiles = Profile.objects.filter(handle=username.lower())
        if profiles.exists():
            profile = profiles.first()

    if pk_fund_request:
        requests = FundRequest.objects.filter(pk=int(pk_fund_request))
        if requests.exists():
            fund_request = requests.first()
            profile = fund_request.requester
        else:
            messages.error(f'Failed to retrieve the fund request {fund_request}')

    if profile:
        user['id'] = profile.id
        user['text'] = profile.handle
        user['avatar_url'] = profile.avatar_url

        if profile.avatar_baseavatar_related.exists():
            user['avatar_id'] = profile.avatar_baseavatar_related.filter(active=True).first().pk
            user['avatar_url'] = profile.avatar_baseavatar_related.filter(active=True).first().avatar_url
            user['preferred_payout_address'] = profile.preferred_payout_address

    recent_tips = Tip.objects.filter(sender_profile=request.user.profile).order_by('-created_on')
    recent_tips_profiles = []

    for tip in recent_tips:
        if len(recent_tips_profiles) == 7:
            break
        if tip.recipient_profile not in recent_tips_profiles:
            recent_tips_profiles.append(tip.recipient_profile)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': primary_from_email,
        'from_handle': from_username,
        'title': 'Send Tip | Gitcoin',
        'card_desc': 'Send a tip to any github user at the click of a button.',
        'fund_request': fund_request,
        'recent_tips_profiles': recent_tips_profiles
    }

    if user:
        params['user_json'] = user

    return TemplateResponse(request, 'onepager/send2.html', params)
