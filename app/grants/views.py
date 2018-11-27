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
from grants.models import Grant, Milestone, Subscription, Update
from marketing.mails import (
    grant_cancellation, new_grant, new_supporter, subscription_terminated, support_cancellation,
    thank_you_for_supporting,
)
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
    sort = request.GET.get('sort_option', '-created_on')

    _grants = Grant.objects.filter(active=True).order_by(sort)

    if request.method == 'POST':
        sort = request.POST.get('sort_option', '-created_on')
        keyword = request.POST.get('search_grants', '')
        _grants = Grant.objects.active().keyword(keyword).order_by(sort)

    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    params = {
        'active': 'grants_landing',
        'title': _('Grants Explorer'),
        'grants': grants,
        'grants_count': _grants.count(),
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/index.html', params)


def grant_details(request, grant_id, grant_slug):
    """Display the Grant details page."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None

    try:
        grant = Grant.objects.prefetch_related(
            'subscriptions',
            'milestones',
            'updates'
        ).get(pk=grant_id, slug=grant_slug)
        milestones = grant.milestones.order_by('due_date')
        updates = grant.updates.order_by('-created_on')
        subscriptions = grant.subscriptions.filter(active=True)
        user_subscription = grant.subscriptions.filter(contributor_profile=profile, active=True).first()
    except Grant.DoesNotExist:
        raise Http404

    if request.method == 'POST':
        if 'contract_address' in request.POST:
            grant.active = False
            grant.save()
            grant_cancellation(grant, user_subscription)
            for sub in subscriptions:
                subscription_terminated(grant, sub)
        elif 'input-title' in request.POST:
            update_kwargs = {
                'title': request.POST.get('input-title', ''),
                'description': request.POST.get('description', ''),
                'grant': grant
            }
            Update.objects.create(**update_kwargs)
        elif 'edit-title' in request.POST:
            pass


    params = {
        'active': 'grant_details',
        'title': _('Grant Details'),
        'grant': grant,
        'subscriptions': subscriptions,
        'user_subscription': user_subscription,
        'is_admin': (grant.admin_profile.id == profile.id) if profile and grant.admin_profile else False,
        'grant_is_inactive': not grant.active,
        'updates': updates,
        'milestones': milestones,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/detail.html', params)


@login_required
def grant_new(request):
    """Handle new grant."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None

    if request.method == 'POST':
        logo = request.FILES.get('input_image', None)
        receipt = json.loads(request.POST.get('receipt', '{}'))
        team_members = request.POST.getlist('team_members[]')
        print('team_members: ', team_members, dir(team_members))

        grant_kwargs = {
            'title': request.POST.get('input_title', ''),
            'description': request.POST.get('description', ''),
            'reference_url': request.POST.get('reference_url', ''),
            'admin_address': request.POST.get('admin_address', ''),
            'token_address': request.POST.get('denomination', ''),
            'token_symbol': request.POST.get('token_symbol', ''),
            'amount_goal': request.POST.get('amount_goal', 1),
            'contract_version': request.POST.get('contract_version', ''),
            'transaction_hash': request.POST.get('transaction_hash', ''),
            'contract_address': request.POST.get('contract_address', ''),
            'network': request.POST.get('network', 'mainnet'),
            'metadata': receipt,
            'admin_profile': profile,
            'logo': logo,
        }
        grant = Grant.objects.create(**grant_kwargs)
        new_grant(grant, profile)

        team_members.append(profile.id)
        grant.team_members.add(*list(filter(lambda member_id: member_id > 0, map(int, team_members))))


        return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

    params = {
        'active': 'new_grant',
        'title': _('New Grant'),
        'profile': profile,
        'grant': {},
        'keywords': get_keywords()
    }

    return TemplateResponse(request, 'grants/new.html', params)


@login_required
def milestones(request, grant_id, grant_slug):
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    grant = Grant.objects.prefetch_related('milestones').get(pk=grant_id, slug=grant_slug)

    if profile != grant.admin_profile:
        return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

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
            milestone = grant.milestones.get(pk=milestone_id)
            milestone.delete()

        return redirect(reverse('grants:milestones', args=(grant.pk, grant.slug)))

    form = MilestoneForm()
    milestones = grant.milestones.order_by('due_date')

    params = {
        'active': 'grant_milestones',
        'title': _('Grant Milestones'),
        'grant': grant,
        'milestones': milestones,
        'form': form,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/milestones.html', params)


@login_required
def grant_fund(request, grant_id,  grant_slug):
    """Handle grant funding."""
    try:
        grant = Grant.objects.get(pk=grant_id, slug=grant_slug)
    except Grant.DoesNotExist:
        raise Http404

    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    # make sure a user can only create one subscription per grant
    if request.method == 'POST':
        subscription = Subscription()

        subscription.subscription_hash = request.POST.get('subscription_hash', '')
        subscription.contributor_signature = request.POST.get('signature', '')
        subscription.contributor_address = request.POST.get('contributor_address', '')
        subscription.amount_per_period = request.POST.get('amount_per_period', 0)
        subscription.real_period_seconds = request.POST.get('real_period_seconds', 2592000)
        subscription.frequency = request.POST.get('frequency', 30)
        subscription.frequency_unit = request.POST.get('frequency_unit', 'days')
        subscription.token_address = request.POST.get('denomination', '')
        subscription.token_symbol = request.POST.get('token_symbol', '')
        subscription.gas_price = request.POST.get('gas_price', 0)
        subscription.network = request.POST.get('network', '')
        subscription.contributor_profile = profile
        subscription.grant = grant
        subscription.save()
        new_supporter(grant, subscription)
        thank_you_for_supporting(grant, subscription)
        return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

    params = {
        'active': 'fund_grant',
        'title': _('Fund Grant'),
        'subscription': {},
        'grant_has_no_token': True if grant.token_address == '0x0000000000000000000000000000000000000000' else False,
        'grant': grant,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/fund.html', params)


@login_required
def subscription_cancel(request, grant_id, grant_slug, subscription_id):
    """Handle the cancellation of a grant subscription."""
    subscription = Subscription.objects.select_related('grant').get(pk=subscription_id)
    grant = getattr(subscription, 'grant', None)
    now = datetime.datetime.now()
    profile = request.user.profile if request.user.is_authenticated else None

    if request.method == 'POST' and profile == subscription.contributor_profile:
        subscription.active = False
        subscription.save()
        support_cancellation(grant, subscription)
        return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

    params = {
        'active': 'cancel_grant',
        'title': _('Cancel Grant Subscription'),
        'subscription': subscription,
        'grant': grant,
        'now': now,
        'keywords': get_keywords(),
    }

    return TemplateResponse(request, 'grants/cancel.html', params)


@login_required
def profile(request):
    """Show grants profile of logged in user."""
    limit = request.GET.get('limit', 25)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '-created_on')

    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    _grants = Grant.objects.prefetch_related('team_members') \
        .filter(Q(admin_profile=profile) | Q(team_members__in=[profile])).order_by(sort)
    sub_grants = Grant.objects.filter(subscriptions__contributor_profile=profile).order_by(sort)

    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    history = [{
        'date': '16 Mar',
        'value_true': 1.0,
        'token_name': 'ETH',
        'frequency': 'days',
        'value_in_usdt_now': 80,
        'title': 'Lorem ipsum dolor sit amet',
        'link': 'https://etherscan.io/txs?a=0xcf267ea3f1ebae3c29fea0a3253f94f3122c2199&f=3',
        'avatar_url': 'https://c.gitcoin.co/avatars/57e79c0ae763bb27095f6b265a1a8bf3/thelostone-mc.svg'
    }, {
        'date': '24 April',
        'value_true': 90,
        'token_name': 'DAI',
        'frequency': 'months',
        'value_in_usdt_now': 90,
        'title': 'Lorem ipsum dolor sit amet',
        'link': 'https://etherscan.io/txs?a=0xcf267ea3f1ebae3c29fea0a3253f94f3122c2199&f=3',
        'avatar_url': 'https://c.gitcoin.co/avatars/57e79c0ae763bb27095f6b265a1a8bf3/thelostone-mc.svg'
    }]

    params = {
        'active': 'profile',
        'title': _('My Grants'),
        'grants': grants,
        'sub_grants': sub_grants,
        'history': history
    }

    return TemplateResponse(request, 'grants/profile/index.html', params)


def quickstart(request):
    """Display quickstart guide."""

    params = {'active': 'grants_quickstart', 'title': _('Quickstart')}
    return TemplateResponse(request, 'grants/quickstart.html', params)
