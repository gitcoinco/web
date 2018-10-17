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
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from grants.forms import MilestoneForm
from grants.models import Grant, Milestone, Subscription
from marketing.models import Keyword
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))


def get_keywords():
    """Get all Keywords."""
    return json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)])


def grants(request):
    """Handle grants explorer."""
    limit = request.GET.get('limit', 25)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '-created_on')

    _grants = Grant.objects.all().order_by(sort)

    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    params = {
        'active': 'dashboard',
        'title': _('Grants Explorer'),
        'grants': grants,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/index.html', params)


def grant_details(request, grant_id):
    """Display the Grant details page."""
    profile = request.user.profile if request.user.is_authenticated else None

    try:
        grant = Grant.objects.prefetch_related('subscriptions', 'milestones').get(pk=grant_id)
        milestones = grant.milestones.order_by('due_date')
    except Grant.DoesNotExist:
        raise Http404

    # TODO: Determine how we want to chunk out articles and where we want to store this data.
    activity_data = [{
        'title': 'allow funder to turn off auto approvals during bounty creation',
        'date': '08.02.2018',
        'description':
            'Vestibulum ante ipsum primis in faucibus orci luctus ultrices '
            'posuere cubilia Curae; Proin vel ante.',
    }, {
        'title': 'Beyond The Naked Eye',
        'date': '2012 - Present',
        'description':
            'What is the loop of Creation? How is there something from nothing? '
            'In spite of the fact that it is impossible to prove that anything exists beyond '
            'one’s perception since any such proof would involve one’s perception (I observed it, '
            'I heard it, I thought about it, I calculated it, and etc.), science deals with a '
            'so-called objective reality “out there,” beyond one’s perception professing to '
            'describe Nature objectively (as if there was a Nature or reality external '
            'to one’s perception). The shocking impact of Matrix was precisely the valid '
            'possibility that what we believed to be reality was but our perception; however, '
            'this was presented through showing a real reality wherein the perceived reality was a '
            'computer simulation. Many who toy with the idea that perhaps, indeed, we are computer '
            'simulations, deviate towards questions, such as, who could create such software and what '
            'kind of hardware would be needed for such a feat. Although such questions assume that reality '
            'is our perception, they also axiomatically presuppose the existence of an objective '
            'deterministic world “out there” that nevertheless must be responsible for how we perceive '
            'our reality. This is a major mistake emphasizing technology and algorithms instead of trying '
            'to discover the nature of reality and the structure of creation. As will be shown in the following, '
            'the required paradigm shift from “perception is our reality fixed within an objective world,” '
            'to “perception is reality without the need of an objective world ‘out there,” '
            'is provided by a dynamic logical structure. The Holophanic loop logic is responsible '
            'for a consistent and complete worldview that not only describes, but also creates whatever '
            'can be perceived or experienced.'
    }, {
        'title': 'Awesome Update',
        'date': '08.02.2018',
        'description': 'Some awesome update about this project.',
    }, {
        'title': 'Stellar Update',
        'date': '08.02.2018',
        'description': 'Another stellar update about this project.',
    }]

    gh_data = [{
        'title': 'Initial commit by flapjacks',
        'date': '08.02.2018',
        'description': 'Initial commit with some blah blah blah...',
    }, {
        'title': 'Fix the build by derp-nation',
        'date': '08.02.2018',
        'description': 'Initial commit with some blah blah blah...',
    }, {
        'title': 'A subpar commit by derp-diggity',
        'date': '08.02.2018',
        'description': 'Initial commit with some blah blah blah...',
    }]

    params = {
        'active': 'dashboard',
        'title': _('Grant Details'),
        'grant': grant,
        'is_admin': (grant.admin_profile.id == profile.id) if profile and grant.admin_profile else False,
        'activity': activity_data,
        'gh_activity': gh_data,
        'milestones': milestones,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/detail.html', params)


@login_required
def grant_new(request):
    """Handle new grant."""
    profile = request.user.profile if request.user.is_authenticated else None

    if request.method == 'POST':
        logo = request.FILES.get('input_image', None)
        receipt = json.loads(request.POST.get('receipt', '{}'))
        team_members = request.POST.getlist('team_members[]')

        grant_kwargs = {
            'title': request.POST.get('input_name', ''),
            'description': request.POST.get('description', ''),
            'reference_url': request.POST.get('reference_url', ''),
            'admin_address': request.POST.get('admin_address', ''),
            'frequency': request.POST.get('frequency', 30),
            'token_address': request.POST.get('denomination', ''),
            'amount_goal': request.POST.get('amount_goal', 0),
            'transaction_hash': request.POST.get('transaction_hash', ''),
            'contract_address': request.POST.get('contract_address', ''),
            'network': request.POST.get('network', 'mainnet'),
            'metadata': receipt,
            'admin_profile': profile,
            'logo': logo,
        }
        grant = Grant.objects.create(**grant_kwargs)

        if team_members:
            grant.team_members.add(*list(map(int, team_members)))

        return redirect(reverse('grants:details', args=(grant.pk, )))

    params = {
        'active': 'grants',
        'title': _('New Grant'),
        'grant': {},
        'keywords': get_keywords(),
    }

    return TemplateResponse(request, 'grants/new.html', params)


@login_required
def milestones(request, grant_id):
    profile = request.user.profile if request.user.is_authenticated else None
    grant = Grant.objects.get(pk=grant_id)

    if profile != grant.admin_profile:
        return redirect(reverse('grants:details', args=(grant.pk, )))

    if request.method == "POST":
        method = request.POST.get('method')

        if method == "POST":
            form = MilestoneForm(request.POST)
            milestone = form.save(commit=False)
            milestone.grant = grant
            milestone.save()

        if method == "PUT":
            milestone_id = request.POST.get('milestone_id')
            milestone = Milestone.objects.get(pk=milestone_id)
            milestone.completion_date = request.POST.get('completion_date')
            milestone.save()

        if method == "DELETE":
            milestone_id = request.POST.get('milestone_id')
            milestone = Milestone.objects.get(pk=milestone_id)
            milestone.delete()

        return redirect(reverse('grants:milestones', args=(grant.pk, )))

    form = MilestoneForm()
    milestones = Milestone.objects.filter(grant_id=grant_id).order_by('due_date')

    params = {
        'active': 'grants',
        'title': _('Grant Milestones'),
        'grant': grant,
        'milestones': milestones,
        'form': form,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/milestones.html', params)


@login_required
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

        subscription.subscription_hash = request.POST.get('subscription_hash', '')
        subscription.contributor_signature = request.POST.get('signature', '')
        subscription.contributor_address = request.POST.get('contributor_address', '')
        subscription.amount_per_period = request.POST.get('amount_per_period', 0)
        subscription.token_address = request.POST.get('token_address', '')
        subscription.gas_price = request.POST.get('gas_price', 0)
        subscription.network = request.POST.get('network', '')
        subscription.contributor_profile = profile
        subscription.grant = grant
        subscription.save()
        return redirect(reverse('grants:details', args=(grant.pk, )))

    params = {
        'active': 'dashboard',
        'title': _('Fund Grant'),
        'subscription': {},
        'grant': grant,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/fund.html', params)


@login_required
def subscription_cancel(request, subscription_id):
    """Handle the cancellation of a grant subscription."""
    subscription = Subscription.objects.select_related('grant').get(pk=subscription_id)
    grant = getattr(subscription, 'grant', None)

    if request.method == 'POST':
        subscription.active = False
        subscription.save()
        return redirect(reverse('grants:details', args=(grant.pk, )))

    params = {
        'title': _('Cancel Grant Subscription'),
        'subscription': subscription,
        'grant': grant,
        'keywords': get_keywords(),
    }

    return TemplateResponse(request, 'grants/cancel.html', params)


@login_required
def profile(request):
    """Show grants profile of logged in user."""
    limit = request.GET.get('limit', 25)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '-created_on')

    profile = request.user.profile if request.user.is_authenticated else None
    _grants = Grant.objects.prefetch_related('team_members', 'subscriptions').filter(
        Q(admin_profile=profile) | Q(team_members__in=[profile])).order_by(sort)

    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    history = [
        {
            'date': '16 Mar',
            'value_true': 1.0,
            'token_name': 'ETH',
            'frequency': 'days',
            'value_in_usdt_now': 80,
            'title': 'Lorem ipsum dolor sit amet',
            'link': 'https://etherscan.io/txs?a=0xcf267ea3f1ebae3c29fea0a3253f94f3122c2199&f=3',
            'avatar_url': 'https://c.gitcoin.co/avatars/57e79c0ae763bb27095f6b265a1a8bf3/thelostone-mc.svg'
        },
        {
            'date': '24 April',
            'value_true': 90,
            'token_name': 'DAI',
            'frequency': 'months',
            'value_in_usdt_now': 90,
            'title': 'Lorem ipsum dolor sit amet',
            'link': 'https://etherscan.io/txs?a=0xcf267ea3f1ebae3c29fea0a3253f94f3122c2199&f=3',
            'avatar_url': 'https://c.gitcoin.co/avatars/57e79c0ae763bb27095f6b265a1a8bf3/thelostone-mc.svg'
        }
    ]

    params = {
        'active': 'profile',
        'title': _('My Grants'),
        'grants': grants,
        'history': history
    }

    return TemplateResponse(request, 'grants/profile.html', params)
