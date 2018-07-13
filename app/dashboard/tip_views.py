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

from django.contrib import messages
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from dashboard.abi import erc20_abi
from dashboard.utils import generate_pub_priv_keypair, get_web3, has_tx_mined
from dashboard.views import record_user_action
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from github.utils import (
    get_auth_url, get_github_emails, get_github_primary_email, get_github_user_data, is_github_token_valid,
)
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
        kwargs['bounty'] = Bounty.objects.get(current_bounty=True, network=tip.network, github_url=tip.github_url)
    except:
        pass

    try:
        Activity.objects.create(**kwargs)
    except Exception as e:
        logging.error(f"error in record_tip_activity: {e} - {event_name} - {tip} - {github_handle}")


@csrf_exempt
@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def receive_tip_legacy(request):
    """Receive a tip."""
    if request.body:
        status = 'OK'
        message = _('Tip has been received')
        params = json.loads(request.body)

        # db mutations
        try:
            tip = Tip.objects.get(txid=params['txid'])
            tip.receive_address = params['receive_address']
            tip.receive_txid = params['receive_txid']
            tip.received_on = timezone.now()
            tip.save()
            record_user_action(tip.username, 'receive_tip', tip)
            record_tip_activity(tip, tip.username, 'receive_tip')
        except Exception as e:
            status = 'error'
            message = str(e)

        # http response
        response = {
            'status': status,
            'message': message,
        }

        return JsonResponse(response)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'receive',
        'title': _('Receive Tip'),
        'gas_price': round(recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target), 1),
    }

    return TemplateResponse(request, 'onepager/receive_legacy.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def receive_tip_v2(request, pk, txid, network):
    """Handle the receiving of a tip (the POST)

    Returns:
        TemplateResponse: the UI with the tip confirmed

    """

    tip = Tip.objects.get(web3_type='v2', metadata__priv_key=pk, txid=txid, network=network)

    if tip.receive_txid:
        messages.info(request, 'This tip has already been received')

    not_mined_yet = not has_tx_mined(tip.txid, tip.network)
    if not_mined_yet:
        messages.info(request, f'This tx {tip.txid}, is still mining.  Please wait a moment before submitting the receive form.')

    """Receive a tip."""
    if request.POST and not tip.receive_txid:
        params = request.POST

        # db mutations
        try:
            address = params['forwarding_address']
            if not address or address == '0x0':
                raise Exception('bad forwarding address')

            # send tokens

            address = Web3.toChecksumAddress(address)
            w3 = get_web3(tip.network)
            is_erc20 = tip.tokenName.lower() != 'eth'
            amount = int(tip.amount_in_wei)
            gasPrice = recommend_min_gas_price_to_confirm_in_time(25) * 10**9
            from_address = Web3.toChecksumAddress(tip.metadata['address'])
            nonce = w3.eth.getTransactionCount(from_address)
            if is_erc20:
                # ERC20 contract receive
                balance = w3.eth.getBalance(from_address)
                contract = w3.eth.contract(Web3.toChecksumAddress(tip.tokenAddress), abi=erc20_abi)
                gas = contract.functions.transfer(address, amount).estimateGas() + 1
                gasPrice = gasPrice if ((gas * gasPrice) < balance) else (balance * 1.0 / gas)
                tx = contract.functions.transfer(address, amount).buildTransaction({
                    'nonce': nonce,
                    'gas': w3.toHex(gas),
                    'gasPrice': w3.toHex(int(gasPrice)),
                })
            else:
                # ERC20 contract receive
                gas = 100000
                amount -= gas * gasPrice
                tx = dict(
                    nonce=nonce,
                    gasPrice=w3.toHex(gasPrice),
                    gas=w3.toHex(gas),
                    to=address,
                    value=w3.toHex(amount),
                    data=b'',
                  )
            signed = w3.eth.account.signTransaction(tx, tip.metadata['priv_key'])
            receive_txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

            tip.receive_address = params['forwarding_address']
            tip.receive_txid = receive_txid
            tip.received_on = timezone.now()
            tip.save()
            record_user_action(tip.username, 'receive_tip', tip)
            record_tip_activity(tip, tip.username, 'receive_tip')
            messages.success(request, 'This tip has been received')
        except Exception as e:
            messages.error(request, str(e))

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'receive',
        'title': _('Receive Tip'),
        'gas_price': round(recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target), 1),
        'tip': tip,
        'disable_inputs': tip.receive_txid or not_mined_yet,
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
    primary_from_email = request.user.email if is_user_authenticated else ''
    access_token = request.user.profile.get_access_token() if is_user_authenticated else ''
    to_emails = []

    params = json.loads(request.body)
    txid = params['txid']
    destinationAccount = params['destinationAccount']
    tip = Tip.objects.get(metadata__address=destinationAccount)
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
    tip.save()

    # notifications
    maybe_market_tip_to_github(tip)
    maybe_market_tip_to_slack(tip, 'new_tip')
    maybe_market_tip_to_email(tip, to_emails)
    record_user_action(tip.username, 'send_tip', tip)
    record_tip_activity(tip, tip.from_name, 'new_tip')

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
    try:
        to_profile = Profile.objects.get(handle__iexact=to_username)
    except Profile.MultipleObjectsReturned:
        to_profile = Profile.objects.filter(handle__iexact=to_username).first()
    except Profile.DoesNotExist:
        to_profile = None
    if to_profile:
        if to_profile.email:
            to_emails.append(to_profile.email)
        if to_profile.github_access_token:
            to_emails = get_github_emails(to_profile.github_access_token)

    if params.get('email'):
        to_emails.append(params['email'])

    # If no primary email in session, try the POST data. If none, fetch from GH.
    if params.get('fromEmail'):
        primary_from_email = params['fromEmail']
    elif access_token and not primary_from_email:
        primary_from_email = get_github_primary_email(access_token)

    to_emails = list(set(to_emails))
    expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])
    priv_key, pub_key, address = generate_pub_priv_keypair()

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
        from_name=params['from_name'],
        from_email=params['from_email'],
        from_username=from_username,
        username=params['username'],
        network=params['network'],
        tokenAddress=params['tokenAddress'],
        from_address=params['from_address'],
        metadata={
            'priv_key': priv_key,
            'pub_key': pub_key,
            'address': address,
        }
    )
    response['payload'] = {
        'address': address,
    }
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
        'title': _('Send Tip'),
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': primary_from_email,
        'from_handle': from_username,
        'title': 'Send Tip | Gitcoin',
        'card_desc': 'Send a tip to any github user at the click of a button.',
    }

    return TemplateResponse(request, 'onepager/send2.html', params)
