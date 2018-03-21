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

import datetime

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from dashboard.views import w3
from ens import ENS
from web3 import HTTPProvider, Web3

from .models import ENSSubdomainRegistration

ns = ENS.fromWeb3(w3)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

@csrf_exempt
def ens_subdomain(request):
    """Register ENS Subdomain."""
    github_handle = request.session.get('handle', None)
    if request.method == "POST":
        signedMsg = request.POST.get('signedMsg', '')
        signer = request.POST.get('singer', '').lower()
        if signedMsg and signer:
            recovered_signer = w3.eth.account.recoverMessage(text="Github Username : {}".format(github_handle),
                                                             signature=signedMsg).lower()
            if recovered_signer == signer:
                txn_hash = '0xbc7e56b035978e4b7ca6dc6cffc205370683c8a91833dc85b89c60d12f877b1d'
                # txn_hash = ns.setup_address("{}.{}".format(github_handle, settings.ENS_TLD), recovered_signer)
                ENSSubdomainRegistration.objects.create(github_handle=github_handle,
                                                        subdomain_wallet_address=signer, txn_hash=txn_hash,
                                                        pending=True).save()
                return JsonResponse(
                    {'success': 'false', 'msg': 'Created Successfully! Please wait for the transaction to mine!'})
            else:
                return JsonResponse({'success': 'false', 'msg': 'Sign Mismatch Error'})
    try:
        last_request = ENSSubdomainRegistration.objects.filter(github_handle=github_handle).latest('created_on')
        request_reset_time = timezone.now() - datetime.timedelta(days=7)
        if last_request.pending:
            txn_receipt = w3.eth.getTransactionReceipt(last_request.txn_hash)
            if txn_receipt:
                if w3.toHex(txn_receipt.transactionHash) == last_request.txn_hash:
                    last_request.pending = False
                    last_request.save()
                    return redirect('/ens')
            params = {
                'title': 'ENS Subdomain',
                'txn_hash': last_request.txn_hash,
                'txn_hash_partial': '{}...'.format(last_request.txn_hash[:20]),
                'github_handle': github_handle,
                'owner' : last_request.subdomain_wallet_address,
            }
            return TemplateResponse(request, 'ens/ens_pending.html', params)
        elif request_reset_time > last_request.created_on:
            params = {
                'title': 'ENS Subdomain',
                'owner': last_request.subdomain_wallet_address,
                'github_handle': github_handle,
            }
            return TemplateResponse(request, 'ens/ens_edit.html', params)
        else:
            params = {
                'title': 'ENS Subdomain',
                'owner': last_request.subdomain_wallet_address,
                'github_handle': github_handle,
                'try_after' : last_request.created_on + datetime.timedelta(days=7)
            }
            return TemplateResponse(request, 'ens/ens_rate_limit.html', params)
    except ENSSubdomainRegistration.DoesNotExist:
        params = {
            'title': 'ENS Subdomain',
            'github_handle': github_handle,
        }
        return TemplateResponse(request, 'ens/ens_register.html', params)
