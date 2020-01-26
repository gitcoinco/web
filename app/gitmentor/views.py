# -*- coding: utf-8 -*-
"""Define the Grant views.

Copyright (C) 2020 Gitcoin Core

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
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from app.utils import get_profile
from cacheops import cached_view
from dashboard.models import Activity, Profile, SearchHistory
from dashboard.utils import get_web3, has_tx_mined
from economy.utils import convert_amount
from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time
from gitmentor.forms import SessionRequestForm
from marketing.models import Keyword, Stat
from retail.helpers import get_ip
from web3 import HTTPProvider, Web3


logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))


def index(request):
    return TemplateResponse(request, 'gitmentor/index.html')


@login_required
def request_session(request):
    profile = get_profile(request)

    if request.method == "POST":
        form = SessionRequestForm(request.POST)

        if form.is_valid():
            session_request = form.save(commit=False)
            session_request.sablier_tx_receipt = json.loads(
                request.POST.get('sablier_tx_receipt', '{}')
            )
            session_request.session_datetime = json.loads(
                request.POST.get('session_datetime', '{}')
            )
            session_request.gitmentor_session_id = json.loads(
                request.POST.get('gitmentor_session_id', '{}')
            )
            session_request.mentee_address = '0xd21aEff7Fc73AB5D608808c99427B1B9084D372e'
            session_request.session_cost = 5;
            session_request.session_duration = 15;
            session_request.save()

    form = SessionRequestForm()

    params = {
        'active': 'schedule_session',
        'profile': profile,
        'form': form,
    }
    return TemplateResponse(request, 'gitmentor/schedule.html', params)
