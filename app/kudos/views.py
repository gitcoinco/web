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
from django.contrib.postgres.search import SearchVector

from .models import MarketPlaceListing
from .forms import KudosSearchForm
import re

import logging

logging.basicConfig(level=logging.INFO)


def about(request):
    context = dict()
    return TemplateResponse(request, 'kudos_about.html', context)


def marketplace(request):
    q = request.GET.get('q')
    logging.info(q)

    results = MarketPlaceListing.objects.annotate(
        search=SearchVector('name', 'description', 'tags')
        ).filter(search=q)
    logging.info(results)

    if results:
        context = {"listings": results}
    else:
        context = {"listings": MarketPlaceListing.objects.all()}

    return TemplateResponse(request, 'kudos_marketplace.html', context)


def search(request):
    context = {}
    logging.info(request.GET)

    if request.method == 'GET':
        form = KudosSearchForm(request.GET)
        context = {'form': form}

    return TemplateResponse(request, 'kudos_marketplace.html', context)


def details(request):
    context = dict()
    kudos_id = request.path.split('/')[-1]
    logging.info(f'kudos id: {kudos_id}')

    if not re.match(r'\d+', kudos_id):
        raise ValueError(f'Invalid Kudos ID found.  ID is not a number:  {kudos_id}')

    context = {"kudos": MarketPlaceListing.objects.get(pk=kudos_id)}

    return TemplateResponse(request, 'kudos_details.html', context)


def mint(request):
    context = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'kudos_mint.html', context)
