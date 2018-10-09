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
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from grants.models import Grant, Subscription
from marketing.models import Keyword
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))


def get_keywords():
    """Get all Keywords."""
    return json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)])


def grants(request):
    """Handle grants explorer."""
    grants = Grant.objects.all()

    params = {
        'active': 'dashboard',
        'title': _('Grants Explorer'),
        'grants': grants,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/index.html', params)


def grant_details(request, grant_id):
    """Display the Grant details page."""
    try:
        grant = Grant.objects.get(pk=grant_id)
    except Grant.DoesNotExist:
        raise Http404

    params = {
        'active': 'dashboard',
        'title': _('Grant Details'),
        'grant': grant,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/show.html', params)


def grant_new(request):
    """Handle new grant."""
    profile = request.user.profile if request.user.is_authenticated else None

    if request.method == 'POST':
        logo = request.FILES.get('input_image', None)
        grant_kwargs = {
            'title': request.POST.get('input_name', ''),
            'description': request.POST.get('description', ''),
            'reference_url': request.POST.get('reference_url'),
            'admin_address': request.POST.get('admin_address', ''),
            'frequency': request.POST.get('frequency', 30),
            'token_address': request.POST.get('denomination', ''),
            'amount_goal': request.POST.get('amount_goal', 0),
            'transaction_hash': request.POST.get('transaction_hash', ''),
            'contract_address': request.POST.get('contract_address', ''),
            'network': request.POST.get('network', 'mainnet'),
            'admin_profile': profile,
            'logo': logo,
        }
        grant = Grant.objects.create(**grant_kwargs)
        return redirect(reverse('grants:details', args=(grant.pk, )))

    grant = {}
    params = {
        'active': 'grants',
        'title': _('New Grant'),
        'grant': grant,
        'keywords': get_keywords(),
    }

    return TemplateResponse(request, 'grants/new.html', params)


def grant_fund(request, grant_id):
    """Handle grant funding."""
    try:
        grant = Grant.objects.get(pk=grant_id)
    except Grant.DoesNotExist:
        raise Http404

    profile = request.user.profile if request.user.is_authenticated else None
    # make sure a user can only create one subscription per grant
    if request.method == 'POST':
        subscription = Subscription()
        # subscriptionHash and ContributorSignature will be given from smartcontracts and web3
        # subscription.subscriptionHash = request.POST.get('input_name')
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
        'title': _('Fund Grant'),
        'subscription': subscription,
        'grant': grant,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/fund.html', params)


def subscription_cancel(request, subscription_id):
    """Handle the cancellation of a grant subscription."""
    subscription = Subscription.objects.select_related('grant').get(pk=subscription_id)
    grant = getattr(subscription, 'grant', None)

    if request.method == 'POST':
        subscription.status = False
        subscription.save()

    params = {
        'title': _('Cancel Grant Subscription'),
        'subscription': subscription,
        'grant': grant,
        'keywords': get_keywords(),
    }

    return TemplateResponse(request, 'grants/cancel.html', params)
