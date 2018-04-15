# -*- coding: utf-8 -*-
'''
    Copyright (C) 2017 Gitcoin Core

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

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from ratelimit.decorators import ratelimit
from django.template.response import TemplateResponse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from web3 import HTTPProvider, Web3

w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def redeem_coin(request, shortcode):
    params = {
        'class': 'redeem',
        'title': _('EthOS Coin'),
        'coin_status': _('PENDING')
    }
    return TemplateResponse(request, 'yge/redeem_coin.html', params)