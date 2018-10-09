# -*- coding: utf-8 -*-
"""Define the Grant views.

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
import json
import logging

from django.conf import settings
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from grants.models import Grant, Subscription
from marketing.models import Keyword
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))


def grants(request):
    """Handle grants explorer."""
    grants = Grant.objects.all()

    params = {
        'active': 'dashboard',
        'title': 'Grants Explorer',
        'grants': grants,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'grants/index.html', params)


def grant_show(request, grant_id):
    """Display a grant."""
    grant = Grant.objects.get(pk=grant_id)

    params = {
        'active': 'dashboard',
        'title': 'Grant Show',
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'grants/show.html', params)


def new_grant(request):
    """Handle new grant."""
    profile = request.user.profile if request.user.is_authenticated else None

    if request.method == "POST":
        grant = Grant()
        grant.title = request.POST.get('input-name')
        grant.description = request.POST.get('description')
        grant.reference_url = request.POST.get('reference_url')
        grant.image_url = request.POST.get('input-image')
        grant.admin_address = request.POST.get('admin_address')
        grant.frequency = request.POST.get('frequency')
        grant.token_address = request.POST.get('denomination')
        grant.amount_goal = request.POST.get('amount_goal')
        grant.transaction_hash = request.POST.get('transaction_hash')
        grant.contract_address = request.POST.get('contract_address')
        grant.network = request.POST.get('network')
        grant.admin_profile = profile
        grant.save()
        return redirect(f'/grants/{grant.pk}')

    grant = {}
    params = {
        'active': 'grants',
        'title': 'New Grant',
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }

    return TemplateResponse(request, 'grants/new.html', params)


def fund_grant(request, grant_id):
    """Handle grant funding."""
    grant = Grant.objects.get(pk=grant_id)
    profile = request.user.profile if request.user.is_authenticated else None

    print("this is the username:", profile)
    print("this is the grant instance", grant)
    print("this is the web3 instance", w3.eth.account)

    # make sure a user can only create one subscription per grant
    if request.method == "POST":
        subscription = Subscription()
        # subscriptionHash and ContributorSignature will be given from smartcontracts and web3
        # subscription.subscriptionHash = request.POST.get('input-name')
        # subscription.contributorSignature = request.POST.get('description')
        # Address will come from web3 instance
        # subscription.contributorAddress = request.POST.get('reference_url')
        subscription.amount_per_period = request.POST.get('amount_per_period')
        # subscription.tokenAddress = request.POST.get('denomination')
        subscription.gas_price = request.POST.get('gas_price')
        # network will come from web3 instance
        # subscription.network = request.POST.get('amount_goal')
        subscription.contributor_profile = profile
        subscription.grant = grant
        subscription.save()
    else:
        subscription = {}

    params = {
        'active': 'dashboard',
        'title': 'Fund Grant',
        'subscription': subscription,
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'grants/fund.html', params)


def cancel_subscription(request, subscription_id):
    """Handle Cancelation of grant funding."""
    subscription = Subscription.objects.get(pk=subscription_id)
    grant = subscription.grant

    print("this is the subscription:", subscription.pk)
    print("this is the grant:", grant)

    if request.method == "POST":
        subscription.status = False
        subscription.save()

    params = {
        'title': 'Fund Grant',
        'subscription': subscription,
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }

    return TemplateResponse(request, 'grants/cancel.html', params)
