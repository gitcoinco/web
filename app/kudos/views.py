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
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.search import SearchVector

from .models import MarketPlaceListing
from .forms import KudosSearchForm
import re

import logging

logger = logging.getLogger(__name__)


def about(request):
    """Render the about kudos response."""
    context = {
        'is_outside': True,
        'active': 'about',
        'title': 'About',
        'card_title': _('Gitcoin is a mission-driven organization.'),
        'card_desc': _('Our mission is to grow open source.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
        "listings": MarketPlaceListing.objects.all(),
    }
    return TemplateResponse(request, 'kudos_about.html', context)


def marketplace(request):
    """Render the marketplace kudos response."""
    q = request.GET.get('q')
    logger.info(q)

    results = MarketPlaceListing.objects.annotate(
        search=SearchVector('name', 'description', 'tags')
        ).filter(num_clones_allowed__gt=0, search=q)
    logger.info(results)

    if results:
        listings = results
    else:
        listings = MarketPlaceListing.objects.filter(num_clones_allowed__gt=0)

    # for x in context['listings']:
    #     x.price = x.price / 1000

    # Adjust the price units.  Change from Finney to ETH
    # updated_listings = []
    # for l in listings:
    #     # l.price = l.price / 1000
    #     logger.info(f'Price in ETH {l.price_in_eth()}')
    #     updated_listings.append(l)

    context = {
        'is_outside': True,
        'active': 'marketplace',
        'title': 'Marketplace',
        'card_title': _('Gitcoin is a mission-driven organization.'),
        'card_desc': _('Our mission is to grow open source.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
        'listings': listings
    }

    return TemplateResponse(request, 'kudos_marketplace.html', context)


def search(request):
    context = {}
    logger.info(request.GET)

    if request.method == 'GET':
        form = KudosSearchForm(request.GET)
        context = {'form': form}

    return TemplateResponse(request, 'kudos_marketplace.html', context)


def details(request):
    """Render the detail kudos response."""
    kudos_id = request.path.split('/')[-1]
    logger.info(f'kudos id: {kudos_id}')

    if not re.match(r'\d+', kudos_id):
        raise ValueError(f'Invalid Kudos ID found.  ID is not a number:  {kudos_id}')

    context = {
        'is_outside': True,
        'active': 'details',
        'title': 'Details',
        'card_title': _('Gitcoin is a mission-driven organization.'),
        'card_desc': _('Our mission is to grow open source.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
        'kudos': MarketPlaceListing.objects.get(pk=kudos_id),
    }

    return TemplateResponse(request, 'kudos_details.html', context)


def mint(request):
    context = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'kudos_mint.html', context)


def send(request):
    context = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'kudos_mint.html', context)


def receive(request):
    context = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'kudos_mint.html', context)