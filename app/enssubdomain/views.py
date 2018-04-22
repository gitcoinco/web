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
from eth_account.messages import defunct_hash_message
from web3 import HTTPProvider, Web3

from .models import ENSSubdomainRegistration

ns = ENS.fromWeb3(w3)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))


@csrf_exempt
@login_required
def ens_subdomain(request):
    """Register ENS Subdomain."""
    github_handle = request.user.username.lower()
    if request.method == "POST" and github_handle:
        signedMsg = request.POST.get('signedMsg', '')
        signer = request.POST.get('signer', '').lower()
        if signedMsg and signer:
            message_hash = defunct_hash_message(text=f'Github Username : {github_handle}')
            recovered_signer = w3.eth.account.recoverHash(message_hash, signature=signedMsg).lower()
            if recovered_signer == signer:
                txn_hash = '0x6477f3640d9d910c589937b25d5892f525cfde2dd634d9490abc7542c946e8e3'
                # txn_hash = ns.setup_owner(f'{github_handle}.{settings.ENS_TLD}', signer)
                profile = Profile.objects.filter(handle=github_handle).first()
                ENSSubdomainRegistration.objects.create(profile=profile,
                                                        subdomain_wallet_address=signer,
                                                        txn_hash=txn_hash,
                                                        pending=True)
                return JsonResponse(
                    {'success': _('false'), 'msg': _('Created Successfully! Please wait for the transaction to mine!')})
            else:
                return JsonResponse({'success': _('false'), 'msg': _('Sign Mismatch Error')})
    try:
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
            }
            return TemplateResponse(request, 'ens/ens_pending.html', params)
        elif request_reset_time > last_request.created_on:
            params = {
                'owner': last_request.subdomain_wallet_address,
                'github_handle': github_handle,
            }
            return TemplateResponse(request, 'ens/ens_edit.html', params)
        else:
            params = {
                'owner': last_request.subdomain_wallet_address,
                'github_handle': github_handle,
                'limit_reset_days': settings.ENS_LIMIT_RESET_DAYS,
                'try_after': last_request.created_on + datetime.timedelta(days=settings.ENS_LIMIT_RESET_DAYS)
            }
            return TemplateResponse(request, 'ens/ens_rate_limit.html', params)
    except ENSSubdomainRegistration.DoesNotExist:
        params = {
            'github_handle': github_handle,
        }
        return TemplateResponse(request, 'ens/ens_register.html', params)
