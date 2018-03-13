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

from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from dashboard.views import w3
from ens import ENS

ns = ENS.fromWeb3(w3)

@csrf_exempt
def ens_subdomain_registration(request):
    """Register ENS Subdomain."""
    github_handle = request.session.get('handle', None)
    owner = ns.address("{}.{}".format(github_handle, settings.ENS_TLD))
    if request.method == "POST":
        signedMsg = request.POST.get('signedMsg', '')
        signer = request.POST.get('singer', '').lower()
        if signedMsg and signer:
            recovered_signer = w3.eth.account.recoverMessage(text="Github Username : {}".format(github_handle), signature=signedMsg).lower()
            print(recovered_signer,signer)
            if recovered_signer == signer:
                ns.setup_address("{}.{}".format(github_handle, settings.ENS_TLD), recovered_signer)
                return JsonResponse({'success': 'false', 'msg': 'Created Successfully! Please wait for the transaction to mine!'})
            else:
                return JsonResponse({'success': 'false', 'msg': 'Sign Mismatch Error'})
    params = {
        'title': 'ENS Subdomain',
        'github_handle' : 'scottydelta',
    }
    return TemplateResponse(request, 'ens/ens_register.html', params)


@csrf_exempt
def ens_subdomain_delete(request):
    """Delete ENS Subdomain."""
    github_handle = request.session.get('handle', None)
    owner = ns.address("{}.{}".format(github_handle, settings.ENS_TLD))
    if request.method == "POST":
        signedMsg = request.POST.get('signedMsg', '')
        signer = request.POST.get('singer', '').lower()
        if signedMsg and signer:
            recovered_signer = w3.eth.account.recoverMessage(text="Github Username : {}".format(github_handle), signature=signedMsg).lower()
            print(recovered_signer,signer,owner)
            if (recovered_signer == signer) and (signer == owner.lower()):
                ns.setup_address("{}.{}".format(github_handle, settings.ENS_TLD), '')
                return JsonResponse({'success': 'false', 'msg': 'Deleted Successfully! Please wait for the transaction to mine!'})
            else:
                return JsonResponse({'success': 'false', 'msg': 'Sign Mismatch Error'})
    params = {
        'title': 'ENS Subdomain',
        'owner': owner,
    }
    return TemplateResponse(request, 'ens/ens_delete.html', params)
