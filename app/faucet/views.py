# -*- coding: utf-8 -*-
"""Define faucet views.

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
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email, validate_slug
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import escape, strip_tags

from faucet.models import FaucetRequest
from github.utils import search_github
from marketing.mails import new_faucet_request, processed_faucet_request


def faucet(request):
    faucet_amount = getattr(settings, "FAUCET_AMOUNT", .003)
    params = {
        'title': 'Faucet',
        'faucet_amount': faucet_amount
    }

    return TemplateResponse(request, 'faucet_form.html', params)


def check_github(profile):
    user = search_github(profile + ' in:login type:user')
    response = {'status': 200, 'user': False}
    if not len(user['items']) == 0 or not user['items'][0]['login'].lower() != profile.lower():
        response['user'] = user['items'][0]
    return response


def save_faucet(request):
    github_profile = request.POST.get('githubProfile')
    email_address = request.POST.get('emailAddress')
    eth_address = request.POST.get('ethAddress')

    try:
        validate_slug(github_profile)
        validate_email(email_address)
        validate_slug(eth_address)
    except Exception as e:
        return JsonResponse({'message': e.messages[0]}, status=400)

    comment = escape(strip_tags(request.POST.get('comment')))
    checkeduser = check_github(github_profile)
    if FaucetRequest.objects.user(github_profile):
        return JsonResponse({
            'message': 'The submitted github profile shows a previous faucet distribution.'
        }, status=403)
    elif not checkeduser:
        return JsonResponse({'message': 'The submitted github profile could not be found on github.'}, status=400)

    fr = FaucetRequest.objects.create(
        fulfilled=False,
        github_username=github_profile,
        github_meta=checkeduser,
        address=eth_address,
        email=email_address,
        comment=comment,
    )
    new_faucet_request(fr)

    return JsonResponse({'message': 'Created.'}, status=201)


@staff_member_required
def process_faucet_request(request, pk):
    faucet_request = FaucetRequest.objects.get(pk=pk)

    if faucet_request.fulfilled:
        return redirect(reverse('process_faucet_request'))

    if request.POST.get('destinationAccount', False):
        faucet_request.fulfilled = True
        faucet_request.save()
        processed_faucet_request(faucet_request)

        return redirect(reverse('process_faucet_request'))

    faucet_amount = settings.FAUCET_AMOUNT
    context = {'obj': faucet_request, 'faucet_amount': faucet_amount}

    return TemplateResponse(request, 'process_faucet_request.html', context)
