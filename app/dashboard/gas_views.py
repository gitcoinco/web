# -*- coding: utf-8 -*-
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
from __future__ import print_function, unicode_literals

import logging

from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cacheops import CacheMiss, cache, cached_view, cached_view_as
from economy.utils import convert_amount
from gas.models import GasGuzzler
from gas.utils import conf_time_spread, gas_advisories, gas_history, recommend_min_gas_price_to_confirm_in_time
from perftools.models import JSONStore

from .helpers import handle_bounty_views

logging.basicConfig(level=logging.DEBUG)

confirm_time_minutes_target = 4

lines = {
    1: 'red',
    5: 'orange',
    60: 'green',
    90: 'steelblue',
    105: 'purple',
    120: '#dddddd',
    180: 'black',
}


def gas(request):
    _cts = conf_time_spread()
    recommended_gas_price = recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target)
    if recommended_gas_price < 2:
        _cts = conf_time_spread(recommended_gas_price)

    context = {
        'title': _('Live Ethereum (ETH) Gas Usage & Confirmation Times'),
        'card_desc': _('Real-time graph of Ethereum (ETH) Live Predicted Confirmation Times (x axis) vs Gas Usage'),
        'eth_to_usd': round(convert_amount(1, 'ETH', 'USDT'), 0),
        'start_gas_cost': recommended_gas_price,
        'gas_advisories': gas_advisories(),
        'conf_time_spread': _cts,
        'hide_send_tip': True,
        'is_3d': request.GET.get("is_3d", False),
    }
    return TemplateResponse(request, 'gas.html', context)


def gas_intro(request):
    context = {
        'title': _('What is Ethereum (ETH) Gas & Web3 | Gitcoin'),
        'card_desc': _('About Ethereum (ETH) Gas and how it works. '
                       'Gas is the payment that is sent to the ethereum node operators (also called miners), '
                       'in exchange for execution of a smart contract.'),
        'hide_send_tip': True,
    }
    return TemplateResponse(request, 'gas_intro.html', context)


def gas_heatmap(request):
    gas_histories = {}
    mins = request.GET.get('mins', 60)
    min_options = [key for key, val in lines.items()]
    if mins not in min_options:
        mins = min_options[0]
    breakdown = 'hourly'
    key = f"{breakdown}:{mins}"
    gas_histories[mins] = JSONStore.objects.filter(view='gas_history', key=key).order_by('-created_on').first().data
    context = {
        'title': _('Live Ethereum (ETH) Gas Heatmap'),
        'card_desc': _(''),
        'hide_send_tip': True,
        'gas_histories': gas_histories,
        'mins': mins,
        'min_options': min_options,
    }
    return TemplateResponse(request, 'gas_heatmap.html', context)


def gas_faq(request):
    context = {
        'title': _('Live Ethereum (ETH) Gas FAQ'),
        'card_desc': _('Frequently asked questions and answers about Ethereum (ETH) Gas'),
        'hide_send_tip': True,
    }
    return TemplateResponse(request, 'gas_faq.html', context)


def gas_faucet_list(request):

    context = {
        'title': _('Live Ethereum (ETH) Gas Faucet List'),
        'card_desc': _('Ethereum (ETH) Gas Faucet List including the Mainnet, Rinkeby Testnet and Ropsten Testnet'),
        'hide_send_tip': True,
    }
    return TemplateResponse(request, 'gas_faucet_list.html', context)


def gas_calculator(request):
    recommended_gas_price = recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target)
    _cts = conf_time_spread()

    actions = [{
        'name': _('New Bounty'),
        'target': '/new',
        'persona': 'funder',
        'product': 'bounties',
    }, {
        'name': _('Fulfill Bounty'),
        'target': 'issue/fulfill',
        'persona': 'developer',
        'product': 'bounties',
    }, {
        'name': _('Increase Funding'),
        'target': 'issue/increase',
        'persona': 'funder',
        'product': 'bounties',
    }, {
        'name': _('Accept Submission'),
        'target': 'issue/accept',
        'persona': 'funder',
        'product': 'bounties',
    }, {
        'name': _('Cancel Funding'),
        'target': 'issue/cancel',
        'persona': 'funder',
        'product': 'bounties',
    }, {
        'name': _('Send tip'),
        'target': 'tip/send/2/',
        'persona': 'funder',
        'product': 'tips',
    }, {
        'name': _('Receive tip'),
        'target': 'tip/receive',
        'persona': 'developer',
        'product': 'tips',
    }, {
        'name': _('Create Grant'),
        'target': 'grants/new',
        'persona': 'developer',
        'product': 'grants',
    }, {
        'name': _('Fund Grant'),
        'target': 'grants/fund',
        'persona': 'funder',
        'product': 'grants',
    }, {
        'name': _('Cancel Grant Funding'),
        'target': 'grants/cancel',
        'persona': 'funder',
        'product': 'grants',
    }]
    context = {
        'title': _('Live Ethereum (ETH) Gas Calculator'),
        'card_desc': _('See what popular Gitcoin methods cost at different Gas Prices'),
        'actions': actions,
        'conf_time_spread': _cts,
        'eth_to_usd': round(convert_amount(1, 'ETH', 'USDT'), 0),
        'start_gas_cost': recommended_gas_price,
        'hide_send_tip': True,
    }
    return TemplateResponse(request, 'gas_calculator.html', context)


def gas_guzzler_view(request):
    breakdown = request.GET.get('breakdown', 'hourly')
    breakdown_ui = breakdown.replace('ly', '') if breakdown != 'daily' else 'day'
    num_guzzlers = 7
    gas_histories = {}
    _lines = {}
    top_guzzlers = GasGuzzler.objects.filter(
        created_on__gt=timezone.now() - timezone.timedelta(minutes=60)
    ).order_by('-pct_total')[0:num_guzzlers]
    counter = 0
    colors = [val for key, val in lines.items()]
    max_y = 0
    for guzzler in top_guzzlers:
        address = guzzler.address
        try:
            _lines[address] = colors[counter]
        except Exception:
            _lines[address] = 'purple'
        gas_histories[address] = []
        for og in GasGuzzler.objects.filter(address=address).order_by('-created_on'):
            if not og.created_on.hour < 1 and breakdown in ['daily', 'weekly']:
                continue
            if not og.created_on.weekday() < 1 and breakdown in ['weekly']:
                continue
            if breakdown == 'hourly':
                divisor = 3600
            elif breakdown == 'daily':
                divisor = 3600 * 7
            elif breakdown == 'weekly':
                divisor = 3600 * 24 * 7
            unit = int((timezone.now() - og.created_on).total_seconds() / divisor)
            point = [float(og.pct_total), unit]
            gas_histories[address].append(point)
            max_y = max(max_y, og.pct_total + 1)
        counter += 1
    context = {
        'title': _('Gas Guzzlers'),
        'card_desc': _('View the gas guzzlers on the Ethereum Network'),
        'max': max_y,
        'lines': _lines,
        'gas_histories': gas_histories,
        'breakdown': breakdown,
        'breakdown_ui': breakdown_ui,
        'granularity_options': ['hourly', 'daily', 'weekly'],
    }

    return TemplateResponse(request, 'gas_guzzler.html', context)


def gas_history_view(request):
    breakdown = request.GET.get('breakdown', 'hourly')
    granularity_options = ['hourly', 'daily', 'weekly']
    if breakdown not in granularity_options:
        breakdown = 'hourly'
    gas_histories = {}
    max_y = 0
    for i, __ in lines.items():
        key = f"{breakdown}:{i}"
        gas_histories[i] = JSONStore.objects.filter(view='gas_history', key=key).order_by('-created_on').first().data
        for gh in gas_histories[i]:
            max_y = max(gh[0], max_y)
    breakdown_ui = breakdown.replace('ly', '') if breakdown != 'daily' else 'day'
    context = {
        'title': _('Live Ethereum (ETH) Gas History'),
        'card_desc': _('See and comment on the Ethereum (ETH) Gas - Hourly History Graph'),
        'max': max_y,
        'lines': lines,
        'gas_histories': gas_histories,
        'breakdown': breakdown,
        'breakdown_ui': breakdown_ui,
        'granularity_options': granularity_options,
    }
    return TemplateResponse(request, 'gas_history.html', context)
