# -*- coding: utf-8 -*-
"""Define the ENS subdomain views.

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

import datetime
import logging

from django.conf import settings
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

import idna
from dashboard.models import Profile
from dashboard.views import w3
from ens import ENS
from ens.abis import ENS as ens_abi
from ens.abis import RESOLVER as resolver_abi
from ens.main import ENS_MAINNET_ADDR
from ens.utils import dot_eth_namehash, label_to_hash
from eth_account.messages import defunct_hash_message
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from web3 import Web3

from .models import ENSSubdomainRegistration
from .utils import convert_txn

logger = logging.getLogger(__name__)
mock_request = settings.DEBUG

RESOLVER_GAS_COST = 100000
OWNER_GAS_COST = 100000
SET_ADDRESS_GAS_COST = 100000


def get_gas_price(gas_multiplier=1.101):
    """Get the recommended minimum gas price."""
    return recommend_min_gas_price_to_confirm_in_time(1) * 10**9 if not settings.DEBUG else 15 * 10**9 * gas_multiplier


def handle_default_response(request, github_handle):
    params = {'github_handle': github_handle, 'ens_domain': settings.ENS_TLD, }
    return TemplateResponse(request, 'ens/ens_register.html', params)


def handle_subdomain_exists(request, github_handle):
    profile = Profile.objects.filter(handle=github_handle).first()
    last_request = ENSSubdomainRegistration.objects.filter(profile=profile).latest('created_on')
    request_reset_time = timezone.now() - datetime.timedelta(days=settings.ENS_LIMIT_RESET_DAYS)
    if last_request.pending:
        txn_receipt = w3.eth.getTransactionReceipt(last_request.txn_hash_3)
        if txn_receipt:
            if w3.toHex(txn_receipt.transactionHash) == last_request.txn_hash_3:
                last_request.pending = False
                last_request.save()
        params = {
            'txn_hash': last_request.txn_hash_3,
            'txn_hash_partial': f"{last_request.txn_hash_3[:20]}...",
            'github_handle': github_handle,
            'owner': last_request.subdomain_wallet_address,
            'ens_domain': settings.ENS_TLD,
        }
        return TemplateResponse(request, 'ens/ens_pending.html', params)
    if request_reset_time > last_request.created_on:
        params = {
            'owner': last_request.subdomain_wallet_address,
            'github_handle': github_handle,
            'ens_domain': settings.ENS_TLD,
        }
        return TemplateResponse(request, 'ens/ens_edit.html', params)

    params = {
        'owner': last_request.subdomain_wallet_address,
        'github_handle': github_handle,
        'limit_reset_days': settings.ENS_LIMIT_RESET_DAYS,
        'try_after': last_request.created_on + datetime.timedelta(days=settings.ENS_LIMIT_RESET_DAYS),
        'ens_domain': settings.ENS_TLD,
    }
    return TemplateResponse(request, 'ens/ens_rate_limit.html', params)


def set_resolver(signer, github_handle, nonce, gas_multiplier=1.101):
    if mock_request:
        return '0x7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39'

    ns = ENS.fromWeb3(w3)
    resolver_addr = ns.address('resolver.eth')
    signer = Web3.toChecksumAddress(signer)
    txn_hash = None
    gas_price = get_gas_price(gas_multiplier)
    subdomain = f"{github_handle}.{settings.ENS_TLD}"

    transaction = {
        'from': Web3.toChecksumAddress(settings.ENS_OWNER_ACCOUNT),
        'value': 0,
        'nonce': nonce,
        'gas': Web3.toHex(RESOLVER_GAS_COST),
        'gasPrice': Web3.toHex(int(float(gas_price))),
    }

    ens_contract = w3.eth.contract(address=ENS_MAINNET_ADDR, abi=ens_abi, )
    txn = ens_contract.functions.setResolver(dot_eth_namehash(subdomain), resolver_addr, ).buildTransaction(transaction)
    signed_txn = w3.eth.account.signTransaction(txn, private_key=settings.ENS_PRIVATE_KEY)
    try:
        txn_hash = convert_txn(w3.eth.sendRawTransaction(signed_txn.rawTransaction))
    except ValueError as e:
        logger.warning(f'{e} - set_resolver')

    return txn_hash


def set_owner(signer, github_handle, nonce, gas_multiplier=1.101):
    if mock_request:
        return '0x7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39'
    owned = settings.ENS_TLD
    label = github_handle
    txn_hash = None
    gas_price = get_gas_price(gas_multiplier)

    transaction = {
        'from': Web3.toChecksumAddress(settings.ENS_OWNER_ACCOUNT),
        'value': 0,
        'nonce': nonce,
        'gas': Web3.toHex(OWNER_GAS_COST),
        'gasPrice': Web3.toHex(int(float(gas_price))),
    }

    ens_contract = w3.eth.contract(address=ENS_MAINNET_ADDR, abi=ens_abi, )

    txn = ens_contract.functions.setSubnodeOwner(
        dot_eth_namehash(owned), label_to_hash(label), Web3.toChecksumAddress(settings.ENS_OWNER_ACCOUNT),
    ).buildTransaction(transaction)
    signed_txn = w3.eth.account.signTransaction(txn, private_key=settings.ENS_PRIVATE_KEY)
    try:
        txn_hash = convert_txn(w3.eth.sendRawTransaction(signed_txn.rawTransaction))
    except ValueError as e:
        logger.warning(f'{e} - set_owner')
    return txn_hash


def set_address_at_resolver(signer, github_handle, nonce, gas_multiplier=1.101):
    if mock_request:
        return '0x7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39'
    ns = ENS.fromWeb3(w3)
    resolver_addr = ns.address('resolver.eth')
    signer = Web3.toChecksumAddress(signer)
    txn_hash = ''
    gas_price = get_gas_price(gas_multiplier)
    subdomain = f"{github_handle}.{settings.ENS_TLD}"

    transaction = {
        'from': Web3.toChecksumAddress(settings.ENS_OWNER_ACCOUNT),
        'value': 0,
        'nonce': nonce,
        'gas': Web3.toHex(SET_ADDRESS_GAS_COST),
        'gasPrice': Web3.toHex(int(float(gas_price))),
    }

    resolver_contract = w3.eth.contract(address=resolver_addr, abi=resolver_abi, )
    txn = resolver_contract.functions.setAddr(dot_eth_namehash(subdomain), signer, ).buildTransaction(transaction)
    signed_txn = w3.eth.account.signTransaction(txn, private_key=settings.ENS_PRIVATE_KEY)
    try:
        txn_hash = convert_txn(w3.eth.sendRawTransaction(signed_txn.rawTransaction))
    except ValueError as e:
        logger.error(e)

    return txn_hash


def get_nonce():
    web3_nonce = w3.eth.getTransactionCount(settings.ENS_OWNER_ACCOUNT)
    next_db_nonce = 0
    try:
        last_ens = ENSSubdomainRegistration.objects.order_by('-end_nonce').first()
        next_db_nonce = last_ens.end_nonce + 1
    except Exception:
        pass

    return max([web3_nonce, next_db_nonce])


def helper_process_registration(signer, github_handle, signedMsg, gas_multiplier=1.101, override_nonce=None):
    # actually setup subdomain
    start_nonce = get_nonce() if not override_nonce else override_nonce
    nonce = start_nonce
    txn_hash_1 = set_owner(signer, github_handle, nonce, gas_multiplier=gas_multiplier)
    nonce += 1
    txn_hash_2 = set_resolver(signer, github_handle, nonce, gas_multiplier=gas_multiplier)
    nonce += 1
    txn_hash_3 = set_address_at_resolver(signer, github_handle, nonce, gas_multiplier=gas_multiplier)

    profile = Profile.objects.filter(handle__iexact=github_handle).first()
    return ENSSubdomainRegistration.objects.create(
        profile=profile,
        subdomain_wallet_address=signer,
        txn_hash_1=txn_hash_1,
        txn_hash_2=txn_hash_2,
        txn_hash_3=txn_hash_3,
        pending=True,
        signed_msg=signedMsg,
        start_nonce=start_nonce,
        end_nonce=nonce,
        comments=f"github_handle: {github_handle}\n\n",
    )


def handle_subdomain_post_request(request, github_handle):
    # setup
    signed_msg = request.POST.get('signedMsg', '')
    signer = request.POST.get('signer', '').lower()
    if signed_msg and signer:
        # validation
        message_hash = defunct_hash_message(text=f'Github Username : {github_handle}')
        recovered_signer = w3.eth.account.recoverHash(message_hash, signature=signed_msg).lower()
        if recovered_signer != signer:
            return JsonResponse({'success': False, 'msg': _('Sign Mismatch Error')})
        if not request.user.profile.trust_profile and request.user.profile.github_created_on > (
            timezone.now() - timezone.timedelta(days=7)
        ):
            return JsonResponse({
                'success': False,
                'msg':
                    _(
                        'For SPAM prevention reasons, you may not perform this action right now.  '
                        'Please contact support if you believe this message is in error.'
                    )
            })

        # actually setup subdomain
        start_nonce = get_nonce()
        nonce = start_nonce
        txn_hash_1 = set_owner(signer, github_handle, nonce)
        nonce += 1
        txn_hash_2 = set_resolver(signer, github_handle, nonce)
        nonce += 1
        txn_hash_3 = set_address_at_resolver(signer, github_handle, nonce)

        gas_price = get_gas_price()
        gas_cost_eth = (RESOLVER_GAS_COST + OWNER_GAS_COST + SET_ADDRESS_GAS_COST) * gas_price / 10**18
        profile = Profile.objects.filter(handle=github_handle).first()
        if not txn_hash_1 or not txn_hash_2 or not txn_hash_3:
            return JsonResponse({'success': False, 'msg': _('Your ENS request has failed. Please try again.')})
        ENSSubdomainRegistration.objects.create(
            profile=profile,
            subdomain_wallet_address=signer,
            txn_hash_1=txn_hash_1,
            txn_hash_2=txn_hash_2,
            txn_hash_3=txn_hash_3,
            pending=True,
            signed_msg=signed_msg,
            start_nonce=start_nonce,
            end_nonce=nonce,
            gas_cost_eth=gas_cost_eth,
        )
        return JsonResponse({
            'success': True,
            'msg': _('Your request has been submitted. Please wait for the transaction to mine!')
        })
    return handle_default_response(request, github_handle)


@csrf_exempt
def ens_subdomain(request):
    """Register ENS Subdomain."""
    github_handle = request.user.profile.handle if request.user.is_authenticated and hasattr(
        request.user, 'profile'
    ) else None
    if github_handle:
        github_handle = github_handle.lower().replace('.', '')
        github_handle = idna.encode(github_handle, uts46=True).decode("utf-8")

    if github_handle:
        if request.method == "POST":
            return handle_subdomain_post_request(request, github_handle)
        try:
            return handle_subdomain_exists(request, github_handle)
        except ENSSubdomainRegistration.DoesNotExist:
            return handle_default_response(request, github_handle)
    return handle_default_response(request, github_handle)
