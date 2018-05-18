# -*- coding: utf-8 -*-
"""
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

import binascii
import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Profile
from dashboard.views import w3
from ens import ENS
from ens.abis import ENS as ens_abi
from ens.utils import dot_eth_namehash, label_to_hash
from eth_account.messages import defunct_hash_message
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from web3 import HTTPProvider, Web3

from .models import ENSSubdomainRegistration

ns = ENS.fromWeb3(w3)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))
ENS_MAINNET_ADDR = '0x314159265dD8dbb310642f98f50C066173C1259b'

ens_contract = w3.eth.contract(
    address=ENS_MAINNET_ADDR,
    abi=ens_abi,
)


def handle_subdomain_exists(request, github_handle):
    profile = Profile.objects.filter(handle=github_handle).first()
    last_request = ENSSubdomainRegistration.objects.filter(profile=profile).latest('created_on')
    request_reset_time = timezone.now() - datetime.timedelta(days=settings.ENS_LIMIT_RESET_DAYS)
    if last_request.pending:
        txn_receipt = w3.eth.getTransactionReceipt(last_request.txn_hash)
        if txn_receipt:
            if w3.toHex(txn_receipt.transactionHash) == last_request.txn_hash:
                last_request.pending = False
                last_request.save()
        params = {
            'txn_hash': last_request.txn_hash,
            'txn_hash_partial': f"{last_request.txn_hash[:20]}...",
            'github_handle': github_handle,
            'owner': last_request.subdomain_wallet_address,
            'ens_domain': settings.ENS_TLD,
        }
        return TemplateResponse(request, 'ens/ens_pending.html', params)
    elif request_reset_time > last_request.created_on:
        params = {
            'owner': last_request.subdomain_wallet_address,
            'github_handle': github_handle,
            'ens_domain': settings.ENS_TLD,
        }
        return TemplateResponse(request, 'ens/ens_edit.html', params)
    else:
        params = {
            'owner': last_request.subdomain_wallet_address,
            'github_handle': github_handle,
            'limit_reset_days': settings.ENS_LIMIT_RESET_DAYS,
            'try_after': last_request.created_on + datetime.timedelta(days=settings.ENS_LIMIT_RESET_DAYS),
            'ens_domain': settings.ENS_TLD,
        }
        return TemplateResponse(request, 'ens/ens_rate_limit.html', params)


def handle_subdomain_post_request(request, github_handle):
    signedMsg = request.POST.get('signedMsg', '')
    signer = request.POST.get('signer', '').lower()
    if signedMsg and signer:
        message_hash = defunct_hash_message(text=f'Github Username : {github_handle}')
        recovered_signer = w3.eth.account.recoverHash(message_hash, signature=signedMsg).lower()
        if recovered_signer == signer:
            signer = Web3.toChecksumAddress(signer)
            txn_hash = None
            gasPrice = recommend_min_gas_price_to_confirm_in_time(1) * 10**9 if not settings.DEBUG else 15 * 10**9
            transaction = {
                'from': Web3.toChecksumAddress(settings.ENS_OWNER_ACCOUNT),
                'value': 0,
                'nonce': w3.eth.getTransactionCount(settings.ENS_OWNER_ACCOUNT),
                'gas': 100000,
                'gasPrice': gasPrice
            }
            # TODO -- refactor to use_high_level_code once construct_sign_and_send_raw_middleware is merged 
            # into web3py
            use_high_level_code = False
            if use_high_level_code:
                # from enssubdomain.web3.middleware.signing import construct_sign_and_send_raw_middleware
                # w3.middleware_stack.add(construct_sign_and_send_raw_middleware(settings.ENS_PRIVATE_KEY))
                ns._assert_control = lambda *_: True # monkey patch https://github.com/ethereum/web3.py/issues/852#issuecomment-390054210
                txn_hash = ns.setup_owner(f'{github_handle}.{settings.ENS_TLD}', signer)
            else:
                owned = settings.ENS_TLD
                label = github_handle
                txn = ens_contract.functions.setSubnodeOwner(
                    dot_eth_namehash(owned),
                    label_to_hash(label),
                    signer,
                    ).buildTransaction(transaction)
                signed_txn = w3.eth.account.signTransaction(txn, private_key=settings.ENS_PRIVATE_KEY)
                txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction) 
                # hack to convert 
                # "b'7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39'"
                # to "0x7bce7e4bcd2fea4d26f3d254bb8cf52b9ee8dd7353b19bfbc86803c27d9bbf39"
                txn_hash = str(binascii.b2a_hex(txn_hash)).replace("b'","0x").replace("'","") 

            profile = Profile.objects.filter(handle=github_handle).first()
            ENSSubdomainRegistration.objects.create(profile=profile,
                                                    subdomain_wallet_address=signer,
                                                    txn_hash=txn_hash,
                                                    pending=True)
            return JsonResponse(
                {'success': _('false'), 'msg': _('Created Successfully! Please wait for the transaction to mine!')})
        else:
            return JsonResponse({'success': _('false'), 'msg': _('Sign Mismatch Error')})


@csrf_exempt
@login_required
def ens_subdomain(request):
    """Register ENS Subdomain."""
    github_handle = request.user.profile.handle if request.user.is_authenticated and hasattr(request.user, 'profile') else None
    if request.method == "POST" and github_handle:
        return handle_subdomain_post_request(request, github_handle)
    try:
        return handle_subdomain_exists(request, github_handle)
    except ENSSubdomainRegistration.DoesNotExist:
        params = {
            'github_handle': github_handle,
            'ens_domain': settings.ENS_TLD,
        }
        return TemplateResponse(request, 'ens/ens_register.html', params)
