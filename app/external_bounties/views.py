# -*- coding: utf-8 -*-
"""Define external bounty related views.

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
from html.parser import HTMLParser

from django.core.paginator import Paginator
from django.http import Http404
from django.template.response import TemplateResponse

from app.utils import ellipses
from external_bounties.forms import ExternalBountyForm
from external_bounties.models import ExternalBounty
from marketing.mails import new_external_bounty


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


def strip_html(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def sort_index(request, bounties):
    direction = "" if request.GET.get('direction') == 'asc' else '-'
    column = 'created_on'
    sort = request.GET.get('sort')
    if sort == 'Created':
        column = 'created_on'
    if sort == 'Value':
        column = 'idx_fiat_price'

    bounties = bounties.order_by(f"{direction}{column}")

    return bounties, sort, direction


def external_bounties_index(request):
    """Handle External Bounties index page.

    Returns:
        django.TemplateResponse: The external bounty index view.

    """
    tags = []
    external_bounties_results = []
    bounties = ExternalBounty.objects.filter(active=True).order_by('-created_on')
    search_query = request.GET.get('q', False)
    if search_query == 'False':
        search_query = None
    if search_query:
        master_bounties = bounties
        bounties = master_bounties.filter(title__contains=search_query) 
        bounties = bounties | master_bounties.filter(description__contains=search_query) 
        bounties = bounties | master_bounties.filter(source_project__contains=search_query) 
        bounties = bounties | master_bounties.filter(tags__overlap=[search_query])
        bounties = bounties.distinct()
    bounties, sorted_by, sort_direction = sort_index(request, bounties)
    num_bounties = bounties.count()
    page = request.GET.get('page', 1)
    for bounty in bounties:
        tags = tags + bounty.tags
    bounties = Paginator(bounties, 25)
    bounties_paginator = bounties.get_page(page)
    for external_bounty_result in bounties_paginator:
        external_bounty = {
            "created_on": external_bounty_result.created_on,
            "avatar": external_bounty_result.avatar,
            "title": external_bounty_result.title,
            "source": external_bounty_result.source_project,
            "crypto_price": round(external_bounty_result.amount, 2) if external_bounty_result.amount else None,
            "fiat_price": external_bounty_result.fiat_price,
            "crypto_label": external_bounty_result.amount_denomination,
            "tags": external_bounty_result.tags,
            "url": external_bounty_result.url,
        }
        external_bounties_results.append(external_bounty)
    categories = list(set(tags))
    categories = [ele.lower() for ele in categories if ele]
    categories.sort()
    params = {
        'active': 'offchain',
        'title': 'Bounty Universe Explorer',
        'card_desc': 'Bounties for Software Work from across the internets.',
        'bounties': external_bounties_results,
        'categories': categories,
        'sort_direction': sort_direction,
        'sorted_by': sorted_by,
        'q': search_query,
        'page': page,
        'num_bounties': num_bounties,
        'bounties_paginator': bounties_paginator,
    }
    return TemplateResponse(request, 'external_bounties.html', params)


def external_bounties_new(request):
    """Create a new external bounty.

    Returns:
        django.TemplateResponse: The new external bounty form or submission status.

    """
    params = {
        'active': 'offchain',
        'title': 'New Universal Bounty',
        'card_desc': 'Create a new Bounty for Software Work from across the internets.',
        'formset': ExternalBountyForm,
    }

    if request.POST:
        new_eb = ExternalBountyForm(request.POST)
        new_eb.github_handle = request.session.get('handle')
        new_eb.save()
        new_external_bounty()
        params['msg'] = "An email has been sent to an administrator to approve your submission"

    return TemplateResponse(request, 'external_bounties_new.html', params)


def external_bounties_show(request, issuenum, slug):
    """Handle Dummy External Bounties show page.

    Args:
        issuenum (int): The Github issue number.
        slug (str): The external bounty slug represenation.

    Returns:
        django.TemplateResponse: The external bounty details view.

    """
    print('************')
    print(issuenum)
    if issuenum == '':
        return external_bounties_index(request)

    try:
        bounty = ExternalBounty.objects.get(pk=issuenum, active=True)
    except Exception:
        raise Http404

    external_bounty = {}
    external_bounty_result = bounty
    external_bounty['created_on'] = external_bounty_result.created_on
    external_bounty['title'] = external_bounty_result.title
    external_bounty['crypto_price'] = round(external_bounty_result.amount, 2) if external_bounty_result.amount else None
    external_bounty['crypto_label'] = external_bounty_result.amount_denomination
    external_bounty['fiat_price'] = round(external_bounty_result.amount, 2) if external_bounty_result.amount else None
    external_bounty['source'] = external_bounty_result.source_project
    external_bounty['content'] = strip_html(external_bounty_result.description)
    external_bounty['action_url'] = external_bounty_result.action_url
    external_bounty['avatar'] = external_bounty_result.avatar
    external_bounty['fiat_price'] = external_bounty_result.fiat_price

    params = {
        'active': 'offchain',
        'title': 'Bounty Universe Explorer',
        'card_desc': ellipses(external_bounty['content'], 300),
        "bounty": external_bounty,
    }

    # determine whether this should be a no_index_or_not
    # the below list may want to keep their SEO juice
    no_index_tag_list = ['HackerOne', 'OpenBounty', 'Bounty0x', 'BountySource']
    no_index = False
    for tag in no_index_tag_list:
        if tag in bounty.tags:
            no_index = True
    if no_index:
        params['no_index'] = True

    return TemplateResponse(request, 'external_bounties_show.html', params)
