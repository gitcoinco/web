'''
    Copyright (C) 2019 Gitcoin Core

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
from __future__ import unicode_literals

import csv
import json
import logging
from datetime import date

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.db.models import Avg, Count, Max, Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import gettext_lazy as _

from dashboard.models import Profile
from ptokens.helpers import record_ptoken_activity
from ptokens.models import PersonalToken, RedemptionToken


def quickstart(request):
    context = {}
    return TemplateResponse(request, 'personal_tokens.html', context)


def faq(request):
    context = {}
    return TemplateResponse(request, 'buy_a_token.html', context)


def tokens(request, token_state):
    """List JSON data for the user tokens"""
    error = None
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)

        web3_type = request.POST.get('web3_type')
        title = request.POST.get('title')
        web3_created = date.fromisoformat(request.POST.get('token_state'))
        token_name = request.POST.get('token_name')
        token_address = request.POST.get('token_address')
        token_owner_name = request.POST.get('token_owner_name')
        token_owner_address = request.POST.get('token_owner_address')
        txid = request.POST.get('txid')

        try:
            total_minted = int(request.POST.get('total_minted', 0))
        except ValueError:
            error = 'bad format on total minted token value'

        if not token_name:
            error = 'Missing token name'
        if not token_address:
            error = 'Missing token address'
        if not token_owner_address:
            error = 'Missing token name'
        if not total_minted:
            error = 'Missing token name'
        if not txid:
            error = 'Missing token name'

        if error:
            return JsonResponse(
                {'error': _(error)},
                status=401)

        kwargs = {
            'token_owner_profile': request.user.profile,
            'txid': txid,
            'total_minted': total_minted,
            'token_owner_address': token_owner_address,
            'token_owner_name': token_owner_name,
            'token_address': token_address,
            'token_name': token_name,
            'web3_created': web3_created,
            'title': title,
            'web3_type': web3_type
        }

        ptoken = PersonalToken.objects.create(**kwargs)
        record_ptoken_activity('create_ptoken', ptoken, request.user.profile)

        return JsonResponse({
            'error': False,
            'data': ptoken.to_standard_dict()
        })

    if token_state in ['open', 'in_progress', 'completed', 'denied']:
        query = PersonalToken.objects.filter(token_state=token_state)
        return JsonResponse({
            'error': False,
            'data': [token.to_standard_dict() for token in query]
        })


def ptoken(request, tokenId):
    """List JSON data for the user tokens"""
    ptoken = get_object_or_404(PersonalToken, id=tokenId)
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        kwargs = {}
        metadata = {}
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)
        event_name = request.POST.get('event_name')

        if event_name not in ['mint_ptoken', 'edit_price_ptoken']:
            return JsonResponse(
                {'error': _('Event name invalid')},
                status=401)

        if event_name == 'mint_ptoken':
            try:
                new_amount_minted = int(request.POST.get('amount'))
            except ValueError:
                return JsonResponse(
                    {'error': _('Invalid amount!')},
                    status=401)
            kwargs['total_minted'] = new_amount_minted
            metadata['amount_minted'] = new_amount_minted
        elif event_name == 'edit_price_ptoken':
            event_name = request.POST.get('event_name')
            metadata = {}

            return JsonResponse(
                {'error': _('Needs implementation!')},
                status=401)

        ptoken.objects.update(**kwargs)
        record_ptoken_activity(event_name, ptoken, request.user.profile, metadata)
        return JsonResponse({
            'status': 'ok',
            'id': ptoken.id
        })

    return JsonResponse({'error': False, 'data': ptoken.to_standard_dict()})


def ptoken_redemptions(request, tokenId):
    """List JSON data for the user tokens"""
    ptoken = get_object_or_404(PersonalToken, id=tokenId)
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        kwargs = {}
        metadata = {}
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)
        event_name = request.POST.get('event_name')

    return JsonResponse(
        {'error': _('Needs implementation!')},
        status=401)


def ptoken_redemptions(request, redemptionId):
    """List JSON data for the user tokens"""
    redemption = get_object_or_404(RedemptionToken, id=redemptionId)
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        kwargs = {}
        metadata = {}
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)
        event_name = request.POST.get('event_name')

        if not event_name in ['accept_redemption_ptoken', 'denies_redemption_ptoken',
                              'complete_redemption_ptoken']:
            return JsonResponse(
                {'error': _('Event name invalid')},
                status=401)

    return JsonResponse(
        {'error': _('Needs implementation!')},
        status=401)
