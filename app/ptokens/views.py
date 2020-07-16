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
from datetime import date, datetime
from decimal import Decimal

import dateutil
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
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3

from app.settings import PTOKEN_ABI
from dashboard.models import Profile
from dashboard.utils import get_web3
from ptokens.helpers import record_ptoken_activity
from ptokens.models import PersonalToken, RedemptionToken, PurchasePToken

def quickstart(request):
    context = {}
    return TemplateResponse(request, 'personal_tokens.html', context)


def faq(request):
    context = {}
    return TemplateResponse(request, 'buy_a_token.html', context)

@csrf_exempt
def tokens(request, token_state=None):
    """List JSON data for the user tokens"""
    error = None
    user = request.user if request.user.is_authenticated else None
    minimal = request.GET.get('minimal')

    if request.method == 'POST':
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)

        network = request.POST.get('network')
        web3_created = request.POST.get('web3_created')
        token_name = request.POST.get('token_name')
        token_symbol = request.POST.get('token_symbol')
        token_address = request.POST.get('token_address')
        token_owner_address = request.POST.get('token_owner_address')
        tx_status = request.POST.get('tx_status')
        txid = request.POST.get('txid')
        total_minted = request.POST.get('total_minted', 0)
        value = request.POST.get('value', 0)

        if not token_name:
            error = 'Missing token name'
        if not token_address:
            error = 'Missing token address'
        if not token_owner_address:
            error = 'Missing token owner address'
        if not total_minted:
            error = 'Missing total minted'
        else:
            try:
                total_minted = float(total_minted)
            except ValueError:
                error = 'bad format on total minted token value'
        if not value:
            error = 'No initial price for token'
        else:
            try:
                value = float(value)
            except ValueError:
                error = 'bad format on price value'
        if not txid:
            error = 'Missing tx id'
        if web3_created:
            try:
                web3_created = dateutil.parser.isoparse(web3_created)
            except ValueError:
                error = 'bad date format in web3_created'
        else:
            web3_created = datetime.now()

        if error:
            return JsonResponse(
                {'error': _(error)},
                status=401)

        kwargs = {
            'token_owner_profile': request.user.profile,
            'txid': txid,
            'total_minted': total_minted,
            'token_owner_address': token_owner_address,
            'token_address': token_address,
            'token_symbol': token_symbol,
            'token_name': token_name,
            'web3_created': web3_created,
            'network': network,
            'value': value
        }

        token = PersonalToken.objects.create(**kwargs)
        record_ptoken_activity('create_ptoken', token, request.user.profile)

        if minimal:
            return JsonResponse({
                'id': token.id,
                'name': token.token_name,
                'symbol': token.token_symbol,
                'price': token.value,
                'supply': token.total_minted,
                'address': token.token_address,
                'available': token.available_supply,
                'purchases': token.total_purchases,
                'redemptions': token.total_redemptions,
            })

        return JsonResponse({
            'error': False,
            'data': token.to_standard_dict()
        })

    if token_state in ['open', 'in_progress', 'completed', 'denied']:
        query = PersonalToken.objects.filter(token_state=token_state)
        return JsonResponse(
            [token.to_standard_dict() for token in query], safe=False
        )


@csrf_exempt
def ptoken(request, tokenId):
    """Access and change the state for fiven ptoken"""
    ptoken = get_object_or_404(PersonalToken, pk=tokenId)
    minimal = request.GET.get('minimal', False)
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        kwargs = {}
        metadata = {}
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)
        event_name = request.POST.get('event_name')
        if user.profile != ptoken.token_owner_profile:
            return JsonResponse(
                {'error': _('You don\'t own the requested ptoken !')},
                status=401)

        if event_name == 'mint_ptoken':
            try:
                new_amount_minted = float(request.POST.get('amount'))
            except ValueError:
                return JsonResponse(
                    {'error': _('Invalid amount!')},
                    status=401)
            kwargs['total_minted'] = new_amount_minted
            metadata['amount_minted'] = new_amount_minted
        elif event_name == 'edit_price_ptoken':
            value = request.POST.get('value')

            try:
                new_price = float(value)
            except ValueError:
                return JsonResponse(
                    {'error': _('Invalid amount!')},
                    status=401)
            kwargs['value'] = new_price
            metadata['previous_price'] = float(ptoken.value)
        elif event_name == 'tx_update':
            kwargs['tx_status'] = request.POST.get('tx_status')
        elif event_name == 'update_address':
            kwargs['token_address'] = request.POST.get('token_address')

            # Experimental
            # if PTOKEN_ABI:
            #    web3 = get_web3(ptoken.network)
            #    ptoken_contract = web3.eth.contract(Web3.toChecksumAddress(kwargs['token_address']), abi=PTOKEN_ABI)

            #    try:
            #        token_name = ptoken_contract.functions.symbol().call()
            #        if token_name != ptoken.token_name:
            #            return JsonResponse(
            #                {'error': _('Token name should match to the previous token registered!')},
            #                status=401)
            #    except:
            #        return JsonResponse(
            #            {'error': _('Invalid ptoken contract address!')},
            #            status=401)

        if kwargs:
            PersonalToken.objects.filter(pk=ptoken.id).update(**kwargs)
            ptoken.refresh_from_db()

            if metadata:
                record_ptoken_activity(event_name, ptoken, user.profile, metadata)

    if minimal:
        return JsonResponse({
            'id': ptoken.id,
            'name': ptoken.token_name,
            'symbol': ptoken.token_symbol,
            'price': ptoken.value,
            'supply': ptoken.total_minted,
            'address': ptoken.token_address,
            'available': ptoken.available_supply,
            'purchases': ptoken.total_purchases,
            'redemptions': ptoken.total_redemptions,
        })


    return JsonResponse({'error': False, 'data': ptoken.to_standard_dict()})


@csrf_exempt
def ptoken_redemptions(request, tokenId=None, redemption_state=None):
    """List and create token redemptions"""

    if tokenId:
        ptoken = get_object_or_404(PersonalToken, id=tokenId)
        network = request.POST.get('network')
        total = request.POST.get('total', 0)
        description = request.POST.get('description', '')

        if request.method == 'POST':
            if not request.user:
                return JsonResponse(
                    {'error': _('You must be authenticated via github to use this feature!')},
                    status=401)
            RedemptionToken.objects.create(
                ptoken=ptoken,
                network=network,
                total=total,
                reason=description,
                redemption_requester=request.user.profile
            )

    redemptions = RedemptionToken.objects.filter(redemption_requester=request.user.profile)

    if redemption_state in ['request', 'accepted', 'denied', 'completed']:
        redemptions = redemptions.filter(redemption_state=redemption_state)

    redemptions_json = []
    for redemption in redemptions:
        current_redemption = redemption.to_standard_dict()

        current_redemption['avatar_url'] = redemption.redemption_requester.avatar_url
        current_redemption['requester'] = redemption.redemption_requester.handle
        current_redemption['amount'] = redemption.total
        current_redemption['token_symbol'] = redemption.ptoken.token_symbol
        current_redemption['token_name'] = redemption.ptoken.token_name
        current_redemption['creator'] = redemption.ptoken.token_owner_profile.handle
        redemptions_json.append(current_redemption)

    return JsonResponse(redemptions_json, safe=False)


@csrf_exempt
def ptoken_redemption(request, redemptionId):
    """Change the state for given redemption"""
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

        if event_name == 'accept_redemption_ptoken':
            if user.profile != redemption.ptoken.token_owner_profile:
                return JsonResponse(
                    {'error': _('You don\'t have permissions on the current redemption!')},
                    status=401)
            kwargs['redemption_accepted'] = datetime.now()
            kwargs['redemption_state'] = 'accepted'
            metadata['redemption'] = redemption.id
        if event_name == 'denies_redemption_ptoken':
            if user.profile != redemption.ptoken.token_owner_profile:
                return JsonResponse(
                    {'error': _('You don\'t have permissions on the current redemption!')},
                    status=401)

            kwargs['redemption_state'] = 'denied'
            metadata['redemption'] = redemption.id
        if event_name == 'complete_redemption_ptoken':
            if user.profile != redemption.redemption_requester:
                return JsonResponse(
                    {'error': _('You don\'t have permissions on the current redemption!')},
                    status=401)
            web3_created = request.POST.get('web3_created')
            if web3_created:
                try:
                    kwargs['web3_created'] = dateutil.parser.isoparse(web3_created)
                except ValueError:
                    return JsonResponse(
                        {'error': _('Bad date format in web3_created')},
                        status=401)
            else:
                kwargs['web3_created'] = datetime.now()

            kwargs['redemption_state'] = 'completed'
            kwargs['tx_status'] = request.POST.get('tx_status')
            kwargs['txid'] = request.POST.get('txid')
            metadata['redemption'] = redemption.id
        elif event_name == 'tx_update':
            kwargs['tx_status'] = request.POST.get('tx_status')

        if kwargs:
            RedemptionToken.objects.filter(pk=redemption.id).update(**kwargs)

            if metadata:
                record_ptoken_activity(event_name, redemption.ptoken, user.profile, metadata)

    return JsonResponse({
        'error': False,
        'data': redemption.to_standard_dict()
    })


@csrf_exempt
def ptoken_purchases(request, tokenId):
    ptoken = get_object_or_404(PersonalToken, id=tokenId)
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        error = ''
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)

        network = request.POST.get('network')
        web3_created = request.POST.get('token_state')
        token_holder_address = request.POST.get('token_holder_address')
        txid = request.POST.get('txid')
        tx_status = request.POST.get('tx_status')
        amount = request.POST.get('amount')
        token_id = request.POST.get('token')
        token_value_address = request.POST.get('token_address')
        token_value_name = request.POST.get('token_name')

        if not amount:
            error = 'Missing total minted'
        else:
            try:
                amount = float(amount)
            except ValueError:
                error = 'bad format on total minted token value'

        if not txid:
            error = 'Missing tx id'

        if web3_created:
            try:
                web3_created = dateutil.parser.isoparse(web3_created)
            except ValueError:
                error = 'bad date format in web3_created'
        else:
            web3_created = datetime.now()

        if error:
            return JsonResponse(
                {'error': _(error)},
                status=401)

        purchase = PurchasePToken.objects.create(
            ptoken=ptoken,
            amount=amount,
            token_name=token_value_name,
            token_address=token_value_address,
            network=network,
            txid=txid,
            tx_status=tx_status,
            web3_created=web3_created,
            token_holder_address=token_holder_address,
            token_holder_profile=request.user.profile,
        )
        metadata = {
            'purchase': purchase.id,
            'value_in_token': amount,
            'token_name': ptoken.token_symbol,
            'from_user': ptoken.token_owner_profile.handle,
            'holder_user': user.profile.handle
        }

        record_ptoken_activity('buy_ptoken', ptoken, user.profile, metadata)

    return JsonResponse({
            'error': False,
            'data': [token.to_standard_dict() for token in PurchasePToken.objects.filter(
                token_holder_profile=request.user.profile
            )]
        })
