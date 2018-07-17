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
from django.template.response import TemplateResponse

from .models import MarketPlaceListing


def about(request):
    params = dict()
    return TemplateResponse(request, 'kudos_about.html', params)


def marketplace(request):
    params = {"listings": MarketPlaceListing.objects.all()}

    return TemplateResponse(request, 'kudos_marketplace.html', params)


def details(request):
    params = dict()

    return TemplateResponse(request, 'kudos_details.html', params)


def mint(request):
    params = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'kudos_mint.html', params)
