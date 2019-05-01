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
import datetime
import json
import logging
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from app.utils import get_profile
from cacheops import cached_view
from dashboard.models import Activity, Profile
from dashboard.utils import get_web3, has_tx_mined
from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time
from grants.forms import MilestoneForm
from grants.models import Contribution, Grant, MatchPledge, Milestone, Subscription, Update
from marketing.mails import (
    change_grant_owner_accept, change_grant_owner_reject, change_grant_owner_request, grant_cancellation, new_grant,
    new_supporter, subscription_terminated, support_cancellation, thank_you_for_supporting,
)
from marketing.models import Keyword
from web3 import HTTPProvider, Web3

from dashboard.utils import get_context

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

clr_matching_banners_style = 'pledging'
matching_live = '($50K matching live now!) '


# def index(request):
#     print('yo')
#     return TemplateResponse(request, 'experts/index.html', {})


def quickstart(request):
    """Display quickstart guide."""
    params = {'active': 'experts_quickstart', 'title': _('Quickstart')}
    return TemplateResponse(request, 'experts/quickstart.html', params)


def get_keywords():
    """Get all Keywords."""
    return json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)])


def frontend(request, session_id=None):
    # Make sure user has a profile
    profile = get_profile(request)
    return TemplateResponse(request, 'experts/frontend.html', {})


def index(request):
    """Handle experts explorer."""
    # NOTE this is only for reference - open sessions do not show in this list
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', 'last_visit')
    keyword = request.GET.get('keyword', '')
    _experts = None

    _experts = Profile.objects.all().order_by(sort)
    paginator = Paginator(_experts, limit)
    experts = paginator.get_page(page)

    nav_options = [
        {'label': 'All', 'keyword': ''},
        {'label': 'Security', 'keyword': 'security'},
        {'label': 'Scalability', 'keyword': 'scalability'},
        {'label': 'UI/UX', 'keyword': 'UI'},
        {'label': 'DeFI', 'keyword': 'defi'},
        {'label': 'Education', 'keyword': 'education'},
        {'label': 'Wallets', 'keyword': 'wallet'},
        {'label': 'Community', 'keyword': 'community'},
        {'label': 'ETH 2.0', 'keyword': 'ETH 2.0'},
        {'label': 'ETH 1.x', 'keyword': 'ETH 1.x'},
    ]

    params = {
        'active': 'experts_landing',
        'title': matching_live + str(_('Gitcoin Experts Explorer')),
        'sort': sort,
        'keyword': keyword,
        'nav_options': nav_options,
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Experts'),
        'card_player_override': 'https://www.youtube.com/embed/eVgEWSPFR2o',
        'card_player_stream_override': static('v2/card/experts.mp4'),
        'card_player_thumb_override': static('v2/card/experts.png'),
        'experts': experts,
        'experts_count': _experts.count(),
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'experts/index.html', params)
