'''
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

'''
from __future__ import unicode_literals

import csv
import json
import logging
from datetime import date, datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.db.models import Avg, Count, Max, Q, Sum
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

import dateutil
from app.settings import PTOKEN_ABI
from dashboard.models import Profile
from dashboard.utils import get_web3
from inbox.utils import send_notification_to_user
from ptokens.emails import render_ptoken_redemption_request
from ptokens.helpers import record_ptoken_activity
from ptokens.mails import (
    send_ptoken_redemption_accepted, send_ptoken_redemption_cancelled, send_ptoken_redemption_rejected,
    send_ptoken_redemption_request,
)
from ptokens.models import PersonalToken, PTokenEvent, PurchasePToken, RedemptionToken
from web3 import Web3


@staff_member_required
def quickstart(request):
    context = {}
    return TemplateResponse(request, 'personal_tokens.html', context)


@staff_member_required
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
            'tx_status': tx_status,
            'web3_created': web3_created,
            'network': network,
            'value': value
        }

        token = PersonalToken.objects.create(**kwargs)

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

    if token_state in ['open', 'in_progress', 'waiting_complete', 'completed', 'denied']:
        if token_state == 'waiting_complete':
            token_state = 'completed'

        query = PersonalToken.objects.filter(token_state=token_state)
        return JsonResponse(
            [token.to_standard_dict() for token in query], safe=False
        )


def verification(request):
    """Validate ptoken info"""

    name = request.GET.get('name', '')
    symbol = request.GET.get('symbol', '')
    ptokens = PersonalToken.objects.all()
    results = {}

    if name:
        results['name'] = ptokens.filter(token_name__iexact=name).exists()

    if symbol:
        results['symbol'] = ptokens.filter(token_symbol__iexact=symbol).exists()

    return JsonResponse(results)


@csrf_exempt
def ptoken(request, token_id='me'):
    """Access and change the state for fiven ptoken"""
    if token_id == 'me' and request.user.is_authenticated:
        ptoken = get_object_or_404(PersonalToken, token_owner_profile=request.user.profile)
    else:
        ptoken = get_object_or_404(PersonalToken, pk=token_id)

    minimal = request.GET.get('minimal', False)
    user = request.user if request.user.is_authenticated else None

    if request.method == 'POST':
        kwargs = {}
        metadata = {}
        if not user:
            return JsonResponse(
                {'error': _('You must be authenticated via github to use this feature!')},
                status=401)

        if not user.has_perm('auth.add_pToken_auth'):
            return JsonResponse(
                {'error': _('You are not allowed to use this feature!')},
                status=403)

        event_name = request.POST.get('event_name')
        if user.profile != ptoken.token_owner_profile:
            return JsonResponse(
                {'error': _('You don\'t own the requested ptoken !')},
                status=401)

        if event_name == 'mint_ptoken' or event_name == 'burn_ptoken':
            txid = request.POST.get('txid')
            network = request.POST.get('network')

            try:
                new_amount_minted = float(request.POST.get('amount'))
            except ValueError:
                return JsonResponse(
                    {'error': _('Invalid amount!')},
                    status=401)

            kwargs['total_minted'] = new_amount_minted
            metadata['amount_minted'] = new_amount_minted
            metadata = {
                'amount': new_amount_minted
            }

            PTokenEvent.objects.create(txid=txid, network=network, ptoken=ptoken, event=event_name,
                                       metadata=metadata, profile=user.profile)
        elif event_name == 'edit_price_ptoken':
            value = request.POST.get('value')
            txid = request.POST.get('txid')
            network = request.POST.get('network')
            metadata['previous_price'] = float(ptoken.value)

            try:
                metadata['new_price'] = float(value)
            except ValueError:
                return JsonResponse(
                    {'error': _('Invalid amount!')},
                    status=401)
            PTokenEvent.objects.create(txid=txid, network=network, ptoken=ptoken, event=event_name,
                                       metadata=metadata, profile=user.profile)
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

    if minimal:
        return JsonResponse({
            'id': ptoken.id,
            'name': ptoken.token_name,
            'symbol': ptoken.token_symbol,
            'price': ptoken.value,
            'supply': ptoken.total_minted,
            'address': ptoken.token_address,
            'available': ptoken.available_supply,
            'purchases': ptoken.purchases,
            'redemptions': ptoken.redemptions,
            'available_to_redeem': ptoken.get_available_amount(request.user.profile),
            'tx_status': ptoken.tx_status
        })


    return JsonResponse({'error': False, 'data': ptoken.to_standard_dict()})


@csrf_exempt
def ptoken_redemptions(request, token_id=None, redemption_state=None):
    """List and create token redemptions"""

    if token_id:
        ptoken = get_object_or_404(PersonalToken, id=token_id)
        network = request.POST.get('network')
        total = request.POST.get('total', 0)
        description = request.POST.get('description', '')

        if request.method == 'POST':
            if not request.user.is_authenticated:
                return JsonResponse(
                    {'message': _('You must be authenticated via github to use this feature!')},
                    status=401)

            tokens_available = ptoken.get_available_amount(request.user.profile)
            if float(total) < 0 or float(total) > tokens_available:
                return JsonResponse(
                    {'message': _(f'You don\'t have enough ${ptoken.token_symbol} tokens!')},
                    status=401)

            redemption = RedemptionToken.objects.create(
                ptoken=ptoken,
                network=network,
                total=total,
                reason=description,
                redemption_requester=request.user.profile
            )

            send_ptoken_redemption_request(ptoken.token_owner_profile, ptoken, redemption)
            send_notification_to_user(
                request.user.profile.user,
                ptoken.token_owner_profile.user,
                f'{reverse("dashboard")}?tab=ptoken',
                'accept_redemption_ptoken',
                f'@{request.user.profile} <b>asked</b> to redeem <b>{ redemption.total } { ptoken.token_symbol }: {redemption.reason}</b>'
            )

    redemptions = RedemptionToken.objects.filter(Q(redemption_requester=request.user.profile) | Q(ptoken__token_owner_profile=request.user.profile))

    if redemption_state in ['request', 'accepted', 'denied', 'cancelled']:
        redemptions = redemptions.filter(redemption_state=redemption_state).nocache()
    elif redemption_state == 'completed':
        redemptions = redemptions.filter(redemption_state__in=['waiting_complete', 'completed']).nocache()

    redemptions_json = []
    for redemption in redemptions.distinct():
        current_redemption = redemption.to_standard_dict()

        current_redemption['avatar_url'] = redemption.redemption_requester.avatar_url
        current_redemption['requester'] = redemption.redemption_requester.handle
        current_redemption['amount'] = redemption.total
        current_redemption['token_symbol'] = redemption.ptoken.token_symbol
        current_redemption['token_address'] = redemption.ptoken.token_address
        current_redemption['token_owner'] = redemption.ptoken.token_owner_profile.handle
        current_redemption['token_name'] = redemption.ptoken.token_name
        current_redemption['creator'] = redemption.ptoken.token_owner_profile.handle
        current_redemption['canceller'] = redemption.canceller.handle if redemption.canceller else None
        redemptions_json.append(current_redemption)

    return JsonResponse(redemptions_json, safe=False)


@csrf_exempt
def ptoken_redemption(request, redemption_id):
    """Change the state for given redemption"""
    redemption = get_object_or_404(RedemptionToken, id=redemption_id)
    user = request.user if request.user.is_authenticated else None
    send_notifications = None

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

            send_notifications = lambda: send_ptoken_redemption_accepted(redemption.redemption_requester, redemption.ptoken, redemption)
        if event_name == 'denies_redemption_ptoken':
            if user.profile != redemption.ptoken.token_owner_profile and user.profile != redemption.redemption_requester:
                return JsonResponse(
                    {'error': _('You don\'t have permissions on the current redemption!')},
                    status=401)

            if user.profile == redemption.ptoken.token_owner_profile and redemption.redemption_state != 'accepted':
                kwargs['redemption_state'] = 'denied'
                send_notifications = lambda: send_ptoken_redemption_rejected(redemption.redemption_requester, redemption.ptoken, redemption)
            else:
                kwargs['redemption_state'] = 'cancelled'
                profile = redemption.redemption_requester if redemption.redemption_requester != user.profile else redemption.ptoken.token_owner_profile
                send_notifications = lambda: send_ptoken_redemption_cancelled(profile, redemption.ptoken, redemption)

            kwargs['canceller'] = user.profile
            metadata['redemption'] = redemption.id
            metadata['redemption_requester_name'] = redemption.redemption_requester.handle
            metadata['redemption_state'] = kwargs['redemption_state']
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

            kwargs['redemption_state'] = 'waiting_complete'
            kwargs['tx_status'] = request.POST.get('tx_status')
            kwargs['txid'] = request.POST.get('txid')
            kwargs['redemption_requester_address'] = request.POST.get('address')

        if kwargs:
            RedemptionToken.objects.filter(pk=redemption.id).update(**kwargs)

            if metadata:
                record_ptoken_activity(event_name, redemption.ptoken, user.profile, metadata, redemption)

            if send_notifications:
                redemption.refresh_from_db()
                send_notifications()

    return JsonResponse({
        'error': False,
        'data': redemption.to_standard_dict()
    })


@csrf_exempt
def ptoken_purchases(request, token_id):
    ptoken = get_object_or_404(PersonalToken, id=token_id)
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

        PurchasePToken.objects.create(
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

    return JsonResponse({
            'error': False,
            'data': [token.to_standard_dict() for token in PurchasePToken.objects.filter(
                token_holder_profile=request.user.profile
            )]
        })


@csrf_exempt
def process_ptokens(self):
    non_terminal_states = ['pending', 'na', 'unknown']
    for ptoken in PersonalToken.objects.filter(tx_status__in=non_terminal_states):
        ptoken.update_tx_status()
        print(f"syncing ptoken / {ptoken.pk} / {ptoken.network}")
        ptoken.save()

    for purchase in PurchasePToken.objects.filter(tx_status__in=non_terminal_states):
        purchase.update_tx_status()
        print(f"syncing purchase / {purchase.pk} / {purchase.network}")
        purchase.save()

    for redemption in RedemptionToken.objects.filter(tx_status__in=non_terminal_states):
        redemption.update_tx_status()
        print(f"syncing redemptions / {redemption.pk} / {redemption.network}")
        redemption.save()

    for event in PTokenEvent.objects.filter(tx_status__in=non_terminal_states):
        event.update_tx_status()
        print(f"syncing event ptoken / {event.pk} / {event.network}")
        event.save()

    return JsonResponse({
        'status': 200
    })
