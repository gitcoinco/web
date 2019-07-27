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
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, JsonResponse
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
from economy.utils import convert_amount
from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time
from grants.forms import MilestoneForm
from grants.models import Contribution, Grant, MatchPledge, Milestone, Subscription, Update
from marketing.mails import (
    change_grant_owner_accept, change_grant_owner_reject, change_grant_owner_request, grant_cancellation, new_grant,
    new_supporter, subscription_terminated, support_cancellation, thank_you_for_supporting,
)
from marketing.models import Keyword, Stat
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

clr_matching_banners_style = 'pledging'
matching_live = '($50K matching live now!) '
if True:
    clr_matching_banners_style = 'results'
    matching_live = ''

def get_keywords():
    """Get all Keywords."""
    return json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)])


def grants(request):
    """Handle grants explorer."""
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', '-created_on')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    state = request.GET.get('state', 'active')
    _grants = None

    if state == 'active':
        _grants = Grant.objects.filter(network=network, hidden=False).active().keyword(keyword).order_by(sort)
    else:
        _grants = Grant.objects.filter(network=network, hidden=False).keyword(keyword).order_by(sort)

    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)
    partners = MatchPledge.objects.filter(active=True)

    grant_amount = 0
    grant_stats = Stat.objects.filter(
        key='grants',
        ).order_by('-pk')
    if grant_stats.exists():
        grant_amount = grant_stats.first().val / 1000


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

    now = datetime.datetime.now()
    params = {
        'active': 'grants_landing',
        'title': matching_live + str(_('Gitcoin Grants Explorer')),
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'clr_matching_banners_style': clr_matching_banners_style,
        'nav_options': nav_options,
        'current_partners': partners.filter(end_date__gte=now).order_by('-amount'),
        'past_partners': partners.filter(end_date__lt=now).order_by('-amount'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'card_player_override': 'https://www.youtube.com/embed/eVgEWSPFR2o',
        'card_player_stream_override': static('v2/card/grants.mp4'),
        'card_player_thumb_override': static('v2/card/grants.png'),
        'grants': grants,
        'grants_count': _grants.count(),
        'keywords': get_keywords(),
        'grant_amount': grant_amount,
    }
    return TemplateResponse(request, 'grants/index.html', params)


@csrf_exempt
def grant_details(request, grant_id, grant_slug):
    """Display the Grant details page."""
    profile = get_profile(request)
    add_cancel_params = False
    try:
        grant = Grant.objects.prefetch_related('subscriptions', 'milestones', 'updates').get(
            pk=grant_id, slug=grant_slug
        )
        milestones = grant.milestones.order_by('due_date')
        updates = grant.updates.order_by('-created_on')
        subscriptions = grant.subscriptions.filter(active=True, error=False).order_by('-created_on')
        cancelled_subscriptions = grant.subscriptions.filter(active=False, error=False).order_by('-created_on')
        contributions = Contribution.objects.filter(subscription__in=grant.subscriptions.all()).order_by('-created_on')
        user_subscription = grant.subscriptions.filter(contributor_profile=profile, active=True).first()
        user_non_errored_subscription = grant.subscriptions.filter(contributor_profile=profile, active=True, error=False).first()
        add_cancel_params = user_subscription
    except Grant.DoesNotExist:
        raise Http404

    if request.method == 'POST' and (profile == grant.admin_profile or request.user.is_staff):
        if request.FILES.get('input_image'):
            logo = request.FILES.get('input_image', None)
            grant.logo = logo
            grant.save()
            record_grant_activity_helper('update_grant', grant, profile)
            return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))
        if 'contract_address' in request.POST:
            grant.cancel_tx_id = request.POST.get('grant_cancel_tx_id', '')
            grant.active = False
            grant.save()
            grant_cancellation(grant, user_subscription)
            for sub in subscriptions:
                subscription_terminated(grant, sub)
            record_grant_activity_helper('killed_grant', grant, profile)
        elif 'input-title' in request.POST:
            update_kwargs = {
                'title': request.POST.get('input-title', ''),
                'description': request.POST.get('description', ''),
                'grant': grant
            }
            Update.objects.create(**update_kwargs)
            record_grant_activity_helper('update_grant', grant, profile)
        elif 'contract_owner_address' in request.POST:
            grant.contract_owner_address = request.POST.get('contract_owner_address')
            grant.save()
            record_grant_activity_helper('update_grant', grant, profile)
            return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))
        elif 'edit-title' in request.POST:
            grant.title = request.POST.get('edit-title')
            grant.reference_url = request.POST.get('edit-reference_url')
            form_profile = request.POST.get('edit-admin_profile')
            admin_profile = Profile.objects.get(handle=form_profile)
            grant.description = request.POST.get('edit-description')
            grant.description_rich = request.POST.get('edit-description_rich')
            grant.amount_goal = Decimal(request.POST.get('edit-amount_goal'))
            team_members = request.POST.getlist('edit-grant_members[]')
            team_members.append(str(admin_profile.id))
            grant.team_members.set(team_members)
            if grant.admin_profile != admin_profile:
                grant.request_ownership_change = admin_profile
                change_grant_owner_request(grant, grant.request_ownership_change)
            grant.save()
            record_grant_activity_helper('update_grant', grant, profile)
            return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))
    is_admin = (grant.admin_profile.id == profile.id) if profile and grant.admin_profile else False
    if is_admin:
        add_cancel_params = True

    params = {
        'active': 'grant_details',
        'clr_matching_banners_style': clr_matching_banners_style,
        'grant': grant,
        'tab': request.GET.get('tab', 'description'),
        'title': matching_live + grant.title,
        'card_desc': grant.description,
        'avatar_url': grant.logo.url if grant.logo else None,
        'subscriptions': subscriptions,
        'cancelled_subscriptions': cancelled_subscriptions,
        'contributions': contributions,
        'user_subscription': user_subscription,
        'user_non_errored_subscription': user_non_errored_subscription,
        'is_admin': is_admin,
        'grant_is_inactive': not grant.active,
        'updates': updates,
        'milestones': milestones,
        'keywords': get_keywords(),
    }

    if add_cancel_params:
        add_in_params = {
            'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(4),
            'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(120),
            'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(15),
            'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(1),
            'eth_usd_conv_rate': eth_usd_conv_rate(),
            'conf_time_spread': conf_time_spread(),
            'gas_advisories': gas_advisories(),
        }
        for key, value in add_in_params.items():
            params[key] = value


    if request.method == 'GET' and grant.request_ownership_change and profile == grant.request_ownership_change:
        if request.GET.get('ownership', None) == 'accept':
            previous_owner = grant.admin_profile
            grant.admin_profile = grant.request_ownership_change
            grant.request_ownership_change = None
            grant.save()
            record_grant_activity_helper('update_grant', grant, profile)
            change_grant_owner_accept(grant, grant.admin_profile, previous_owner)
            params['change_ownership'] = 'Y'
        elif request.GET.get('ownership', None) == 'reject':
            grant.request_ownership_change = None
            grant.save()
            record_grant_activity_helper('update_grant', grant, profile)
            change_grant_owner_reject(grant, grant.admin_profile)
            params['change_ownership'] = 'N'

    return TemplateResponse(request, 'grants/detail/index.html', params)


@login_required
def grant_new(request):
    """Handle new grant."""
    if not request.user.has_perm('grants.add_grant'):
        return redirect('https://gitcoin.typeform.com/to/C2IocD')

    profile = get_profile(request)

    if request.method == 'POST':
        if 'title' in request.POST:
            logo = request.FILES.get('input_image', None)
            receipt = json.loads(request.POST.get('receipt', '{}'))
            team_members = request.POST.getlist('team_members[]')

            grant_kwargs = {
                'title': request.POST.get('title', ''),
                'description': request.POST.get('description', ''),
                'description_rich': request.POST.get('description_rich', ''),
                'reference_url': request.POST.get('reference_url', ''),
                'admin_address': request.POST.get('admin_address', ''),
                'contract_owner_address': request.POST.get('contract_owner_address', ''),
                'token_address': request.POST.get('token_address', ''),
                'token_symbol': request.POST.get('token_symbol', ''),
                'amount_goal': request.POST.get('amount_goal', 1),
                'contract_version': request.POST.get('contract_version', ''),
                'deploy_tx_id': request.POST.get('transaction_hash', ''),
                'network': request.POST.get('network', 'mainnet'),
                'metadata': receipt,
                'admin_profile': profile,
                'logo': logo,
            }
            grant = Grant.objects.create(**grant_kwargs)
            team_members.append(profile.id)
            grant.team_members.add(*list(filter(lambda member_id: member_id > 0, map(int, team_members))))
            return JsonResponse({
                'success': True,
            })

        if 'contract_address' in request.POST:
            tx_hash = request.POST.get('transaction_hash', '')
            if not tx_hash:
                return JsonResponse({
                    'success': False,
                    'info': 'no tx hash',
                    'url': None,
                })

            grant = Grant.objects.filter(deploy_tx_id=tx_hash).first()
            grant.contract_address = request.POST.get('contract_address', '')
            print(tx_hash, grant.contract_address)
            grant.save()
            record_grant_activity_helper('new_grant', grant, profile)
            new_grant(grant, profile)
            return JsonResponse({
                'success': True,
                'url': reverse('grants:details', args=(grant.pk, grant.slug))
            })


    params = {
        'active': 'new_grant',
        'title': _('New Grant'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'profile': profile,
        'grant': {},
        'keywords': get_keywords(),
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(4),
        'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(120),
        'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(15),
        'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(1),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'gas_advisories': gas_advisories(),
        'trusted_relayer': settings.GRANTS_OWNER_ACCOUNT
    }
    return TemplateResponse(request, 'grants/new.html', params)

@login_required
def grant_new_v0(request):
    """Create a v0 version of a grant contract."""
    if not request.user.has_perm('grants.add_grant'):
        return redirect('https://gitcoin.typeform.com/to/C2IocD')
    profile = get_profile(request)

    if request.method == 'POST':
        if 'title' in request.POST:
            logo = request.FILES.get('input_image', None)
            receipt = json.loads(request.POST.get('receipt', '{}'))
            team_members = request.POST.getlist('team_members[]')

            grant_kwargs = {
                'title': request.POST.get('title', ''),
                'description': request.POST.get('description', ''),
                'reference_url': request.POST.get('reference_url', ''),
                'admin_address': request.POST.get('admin_address', ''),
                'contract_owner_address': request.POST.get('contract_owner_address', ''),
                'token_address': request.POST.get('token_address', ''),
                'token_symbol': request.POST.get('token_symbol', ''),
                'amount_goal': request.POST.get('amount_goal', 1),
                'contract_version': request.POST.get('contract_version', ''),
                'deploy_tx_id': request.POST.get('transaction_hash', ''),
                'network': request.POST.get('network', 'mainnet'),
                'metadata': receipt,
                'admin_profile': profile,
                'logo': logo,
            }
            grant = Grant.objects.create(**grant_kwargs)
            team_members.append(profile.id)
            grant.team_members.add(*list(filter(lambda member_id: member_id > 0, map(int, team_members))))
            return JsonResponse({
                'success': True,
            })

        if 'contract_address' in request.POST:
            tx_hash = request.POST.get('transaction_hash', '')
            if not tx_hash:
                return JsonResponse({
                    'success': False,
                    'info': 'no tx hash',
                    'url': None,
                })

            grant = Grant.objects.filter(deploy_tx_id=tx_hash).first()
            grant.contract_address = request.POST.get('contract_address', '')
            print(tx_hash, grant.contract_address)
            grant.save()
            record_grant_activity_helper('new_grant', grant, profile)
            new_grant(grant, profile)
            return JsonResponse({
                'success': True,
                'url': reverse('grants:details', args=(grant.pk, grant.slug))
            })


    params = {
        'active': 'new_grant',
        'title': _('New Grant'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'profile': profile,
        'grant': {},
        'keywords': get_keywords(),
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(4),
        'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(120),
        'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(15),
        'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(1),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'gas_advisories': gas_advisories(),
        'trusted_relayer': settings.GRANTS_OWNER_ACCOUNT
    }

    return TemplateResponse(request, 'grants/newv0.html', params)



@login_required
def milestones(request, grant_id, grant_slug):
    profile = get_profile(request)
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
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'grant': grant,
        'milestones': milestones,
        'form': form,
        'keywords': get_keywords(),
    }
    return TemplateResponse(request, 'grants/milestones.html', params)


@login_required
def grant_fund(request, grant_id, grant_slug):
    """Handle grant funding."""
    try:
        grant = Grant.objects.get(pk=grant_id, slug=grant_slug)
    except Grant.DoesNotExist:
        raise Http404

    profile = get_profile(request)

    if not grant.active:
        params = {
            'active': 'grant_error',
            'title': _('Grant Ended'),
            'grant': grant,
            'text': _('This Grant is not longer active.')
        }
        return TemplateResponse(request, 'grants/shared/error.html', params)

    if grant.admin_profile == profile:
        params = {
            'active': 'grant_error',
            'title': _('Invalid Grant Subscription'),
            'grant': grant,
            'text': _('You cannot fund your own Grant.')
        }
        return TemplateResponse(request, 'grants/shared/error.html', params)

    active_subscription = Subscription.objects.select_related('grant').filter(
        grant=grant_id, active=True, error=False, contributor_profile=request.user.profile
    )

    if active_subscription:
        params = {
            'active': 'grant_error',
            'title': _('Subscription Exists'),
            'grant': grant,
            'text': _('You already have an active subscription for this grant.')
        }
        return TemplateResponse(request, 'grants/shared/error.html', params)

    if grant.contract_address == '0x0':
        messages.info(
            request,
            _('This grant is not configured to accept funding at this time.  Please contact founders@gitcoin.co if you believe this message is in error!')
        )
        logger.error(f"Grant {grant.pk} is not properly configured for funding.  Please set grant.contract_address on this grant")
        return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

    if request.method == 'POST':
        if 'contributor_address' in request.POST:
            subscription = Subscription()

            subscription.active = False
            subscription.contributor_address = request.POST.get('contributor_address', '')
            subscription.amount_per_period = request.POST.get('amount_per_period', 0)
            subscription.real_period_seconds = request.POST.get('real_period_seconds', 2592000)
            subscription.frequency = request.POST.get('frequency', 30)
            subscription.frequency_unit = request.POST.get('frequency_unit', 'days')
            subscription.token_address = request.POST.get('token_address', '')
            subscription.token_symbol = request.POST.get('token_symbol', '')
            subscription.gas_price = request.POST.get('gas_price', 0)
            subscription.new_approve_tx_id = request.POST.get('sub_new_approve_tx_id', '0x0')
            subscription.num_tx_approved = request.POST.get('num_tx_approved', 1)
            subscription.network = request.POST.get('network', '')
            subscription.contributor_profile = profile
            subscription.grant = grant
            subscription.save()

            # one time payments
            if int(subscription.num_tx_approved) == 1:
                subscription.successful_contribution(subscription.new_approve_tx_id);
                subscription.error = True #cancel subs so it doesnt try to bill again
                subscription.subminer_comments = "skipping subminer bc this is a 1 and done subscription, and tokens were alredy sent"
                subscription.save()
                record_subscription_activity_helper('new_grant_contribution', subscription, profile)
            else:
                record_subscription_activity_helper('new_grant_subscription', subscription, profile)

            messages.info(
                request,
                _('Your subscription has been created. It will bill within the next 5 minutes or so. Thank you for supporting Open Source !')
            )

            return JsonResponse({
                'success': True,
            })

        if 'signature' in request.POST:
            sub_new_approve_tx_id = request.POST.get('sub_new_approve_tx_id', '')
            subscription = Subscription.objects.filter(new_approve_tx_id=sub_new_approve_tx_id).first()
            subscription.active = True
            subscription.subscription_hash = request.POST.get('subscription_hash', '')
            subscription.contributor_signature = request.POST.get('signature', '')
            subscription.save()

            value_usdt = subscription.get_converted_amount()
            if value_usdt:
                grant.monthly_amount_subscribed += subscription.get_converted_monthly_amount()

            grant.save()
            new_supporter(grant, subscription)
            thank_you_for_supporting(grant, subscription)
            return JsonResponse({
                'success': True,
                'url': reverse('grants:details', args=(grant.pk, grant.slug))
            })

    splitter_contract_address = settings.SPLITTER_CONTRACT_ADDRESS

    params = {
        'active': 'fund_grant',
        'title': _('Fund Grant'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'subscription': {},
        'grant_has_no_token': True if grant.token_address == '0x0000000000000000000000000000000000000000' else False,
        'grant': grant,
        'keywords': get_keywords(),
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(4),
        'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(120),
        'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(15),
        'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(1),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'gas_advisories': gas_advisories(),
        'splitter_contract_address': settings.SPLITTER_CONTRACT_ADDRESS,
        'gitcoin_donation_address': settings.GITCOIN_DONATION_ADDRESS
    }
    return TemplateResponse(request, 'grants/fund.html', params)


@login_required
def subscription_cancel(request, grant_id, grant_slug, subscription_id):
    """Handle the cancellation of a grant subscription."""
    subscription = Subscription.objects.select_related('grant').get(pk=subscription_id)
    grant = getattr(subscription, 'grant', None)
    now = datetime.datetime.now()
    profile = get_profile(request)

    if not subscription.active:
        params = {
            'active': 'grant_error',
            'title': _('Grant Subscription Cancelled'),
            'grant': grant
        }

        if grant.active:
            params['text'] = _('This Grant subscription has already been cancelled.')
        else:
            params['text'] = _('This Subscription is already cancelled as the grant is not longer active.')

        return TemplateResponse(request, 'grants/shared/error.html', params)

    if request.method == 'POST' and (
        profile == subscription.contributor_profile or request.user.has_perm('grants.change_subscription')
    ):
        subscription.end_approve_tx_id = request.POST.get('sub_end_approve_tx_id', '')
        subscription.cancel_tx_id = request.POST.get('sub_cancel_tx_id', '')
        subscription.active = False
        subscription.save()
        record_subscription_activity_helper('killed_grant_contribution', subscription, profile)

        value_usdt = subscription.get_converted_amount()
        if value_usdt:
            grant.monthly_amount_subscribed -= subscription.get_converted_monthly_amount()

        grant.save()
        support_cancellation(grant, subscription)
        messages.info(
            request,
            _('Your subscription has been canceled. We hope you continue to support other open source projects!')
        )
        return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

    params = {
        'active': 'cancel_grant',
        'title': _('Cancel Grant Subscription'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'subscription': subscription,
        'grant': grant,
        'now': now,
        'keywords': get_keywords(),
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(4),
        'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(120),
        'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(15),
        'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(1),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'gas_advisories': gas_advisories(),
    }

    return TemplateResponse(request, 'grants/cancel.html', params)


@login_required
def profile(request):
    """Show grants profile of logged in user."""
    limit = request.GET.get('limit', 25)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort', '-created_on')

    profile = get_profile(request)
    _grants_pks = Grant.objects.filter(Q(admin_profile=profile) | Q(team_members__in=[profile])).values_list(
        'pk', flat=True
    )
    _grants = Grant.objects.prefetch_related('team_members') \
        .filter(pk__in=_grants_pks).order_by(sort)
    sub_grants = Grant.objects.filter(subscriptions__contributor_profile=profile).order_by(sort)

    sub_contributions = []
    contributions = []

    for contribution in Contribution.objects.filter(subscription__contributor_profile=profile).order_by('-pk'):
        instance = {
            "cont": contribution,
            "sub": contribution.subscription,
            "grant":  contribution.subscription.grant,
            "profile": contribution.subscription.contributor_profile
        }
        sub_contributions.append(instance)

    for _grant in _grants:
        subs = Subscription.objects.filter(grant=_grant)
        for _sub in subs:
            conts = Contribution.objects.filter(subscription=_sub)
            for _cont in conts:
                instance = {
                    "cont": _cont,
                    "sub": _sub,
                    "grant":  _grant,
                    "profile": _sub.contributor_profile
                }
                contributions.append(instance)

    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    params = {
        'active': 'profile',
        'title': _('My Grants'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'grants': grants,
        'history': contributions,
        'sub_grants': sub_grants,
        'sub_history': sub_contributions
    }

    return TemplateResponse(request, 'grants/profile/index.html', params)


def quickstart(request):
    """Display quickstart guide."""
    params = {'active': 'grants_quickstart', 'title': _('Quickstart')}
    return TemplateResponse(request, 'grants/quickstart.html', params)


def leaderboard(request):
    """Display leaderboard."""
    params = {
        'active': 'grants_leaderboard',
        'title': _('Grants Leaderboard'),
        'card_desc': _('View the top contributors to Gitcoin Grants'),
        }

    # setup dict
    # TODO: in the future, store all of this in perftools.models.JSONStore
    handles = Subscription.objects.all().values_list('contributor_profile__handle', flat=True)
    default_dict = {
        'rank': None,
        'no': 0,
        'sum': 0,
        'handle': None,
    }
    users_to_results = { ele : default_dict.copy() for ele in handles }

    # get all contribution attributes
    for contribution in Contribution.objects.all().select_related('subscription'):
        key = contribution.subscription.contributor_profile.handle
        users_to_results[key]['handle'] = key
        amount = contribution.subscription.get_converted_amount()
        if amount:
            users_to_results[key]['no'] += 1
            users_to_results[key]['sum'] += round(amount)
    # prepare response for view
    params['items'] = []
    counter = 1
    for item in sorted(users_to_results.items(), key=lambda kv: kv[1]['sum'], reverse=True):
        item = item[1]
        if item['no']:
            item['rank'] = counter
            params['items'].append(item)
            counter += 1
    return TemplateResponse(request, 'grants/leaderboard.html', params)


def record_subscription_activity_helper(activity_type, subscription, profile):
    """Registers a new activity concerning a grant subscription

    Args:
        activity_type (str): The type of activity, as defined in dashboard.models.Activity.
        subscription (grants.models.Subscription): The subscription in question.
        profile (dashboard.models.Profile): The current user's profile.

    """
    try:
        grant_logo = subscription.grant.logo.url
    except:
        grant_logo = None
    metadata = {
        'id': subscription.id,
        'value_in_token': str(subscription.amount_per_period),
        'value_in_usdt_now': str(subscription.amount_per_period_usdt),
        'token_name': subscription.token_symbol,
        'title': subscription.grant.title,
        'grant_logo': grant_logo,
        'grant_url': subscription.grant.url,
        'category': 'grant',
    }
    kwargs = {
        'profile': profile,
        'subscription': subscription,
        'activity_type': activity_type,
        'metadata': metadata,
    }
    Activity.objects.create(**kwargs)

def record_grant_activity_helper(activity_type, grant, profile):
    """Registers a new activity concerning a grant

    Args:
        activity_type (str): The type of activity, as defined in dashboard.models.Activity.
        grant (grants.models.Grant): The grant in question.
        profile (dashboard.models.Profile): The current user's profile.

    """
    try:
        grant_logo = grant.logo.url
    except:
        grant_logo = None
    metadata = {
        'id': grant.id,
        'value_in_token': '{0:.2f}'.format(grant.amount_received),
        'amount_goal': '{0:.2f}'.format(grant.amount_goal),
        'token_name': grant.token_symbol,
        'title': grant.title,
        'grant_logo': grant_logo,
        'grant_url': grant.url,
        'category': 'grant',
    }
    kwargs = {
        'profile': profile,
        'grant': grant,
        'activity_type': activity_type,
        'metadata': metadata,
    }
    Activity.objects.create(**kwargs)


@csrf_exempt
def new_matching_partner(request):

    tx_hash = request.POST.get('hash')
    tx_amount = request.POST.get('amount')
    profile = get_profile(request)

    def get_json_response(message, status):
        return JsonResponse(
            {'status': status, 'message': message},
            status=status
        )

    def is_verified(tx_details, tx_hash, tx_amount, network):
        gitcoin_account = '0x00De4B13153673BCAE2616b67bf822500d325Fc3'
        return has_tx_mined(tx_hash, network) and\
            tx_details.to.lower() == gitcoin_account.lower()

    if not request.user.is_authenticated:
        return get_json_response("Not Authorized", 403)

    if not profile:
        return get_json_response("Profile not found.", 404)

    if request.POST and tx_hash:
        network = 'mainnet'
        web3 = get_web3(network)
        tx = web3.eth.getTransaction(tx_hash)
        if not tx:
            raise Http404
        match_pledge = MatchPledge.objects.create(
            profile=profile,
            amount=convert_amount(tx.value / 10**18, 'ETH', 'USDT'),
            data=json.dumps({
                'tx_hash': tx_hash,
                'network': network,
                'from': tx['from'],
                'to': tx.to,
                'tx_amount': tx.value}
            )
        )
        match_pledge.active = is_verified(tx, tx_hash, tx_amount, network)
        match_pledge.save()

        return get_json_response(
            """Thank you for volunteering to match on Gitcoin Grants.
            You are supporting open source, and we thank you.""", 201
        )

    return get_json_response("Wrong request.", 400)
