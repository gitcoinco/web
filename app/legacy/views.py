# -*- coding: utf-8 -*-
"""Handle legacy views.

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
import logging

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.helpers import normalize_url
from dashboard.models import BountySyncRequest
from gas.utils import conf_time_spread, eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from ratelimit.decorators import ratelimit

from .helpers import process_bounty_changes, process_bounty_details

logging.basicConfig(level=logging.DEBUG)

confirm_time_minutes_target = 60


@csrf_exempt
@ratelimit(key='ip', rate='2/s', method=ratelimit.UNSAFE, block=True)
def sync_web3(request):
    """Sync web3 for legacy."""
    # setup
    result = {}
    issue_url = request.POST.get('issueURL', False)
    bountydetails = request.POST.getlist('bountydetails[]', [])
    if issue_url:
        issue_url = normalize_url(issue_url)
        if not bountydetails:
            # create a bounty sync request
            result['status'] = 'OK'
            for existing_bsr in BountySyncRequest.objects.filter(github_url=issue_url, processed=False):
                existing_bsr.processed = True
                existing_bsr.save()
        else:
            # normalize data
            bountydetails[0] = int(bountydetails[0])
            bountydetails[1] = str(bountydetails[1])
            bountydetails[2] = str(bountydetails[2])
            bountydetails[3] = str(bountydetails[3])
            bountydetails[4] = bool(bountydetails[4] == 'true')
            bountydetails[5] = bool(bountydetails[5] == 'true')
            bountydetails[6] = str(bountydetails[6])
            bountydetails[7] = int(bountydetails[7])
            bountydetails[8] = str(bountydetails[8])
            bountydetails[9] = int(bountydetails[9])
            bountydetails[10] = str(bountydetails[10])
            print(bountydetails)
            contract_address = request.POST.get('contract_address')
            network = request.POST.get('network')
            did_change, old_bounty, new_bounty = process_bounty_details(
                bountydetails, issue_url, contract_address, network)
            print(f"LEGACY: {did_change} changed, {issue_url}")
            if did_change:
                print("- processing changes")
                process_bounty_changes(old_bounty, new_bounty)

        BountySyncRequest.objects.create(
            github_url=issue_url,
            processed=False)

    return JsonResponse(result)


def fulfill_bounty(request):
    """Claim a legacy bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Fulfill Issue',
        'active': 'fulfill_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'handle': request.session.get('handle', ''),
        'email': request.session.get('email', ''),
        'is_legacy': True,
    }

    return TemplateResponse(request, 'fulfill_bounty.html', params)


def clawback_bounty(request):
    """Clawback an expired legacy bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Kill Bounty',
        'active': 'kill_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'is_legacy': True,
    }

    return TemplateResponse(request, 'kill_bounty.html', params)


def process_bounty(request):
    """Process the legacy bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Process Issue',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'is_legacy': True,
    }

    return TemplateResponse(request, 'process_bounty.html', params)
