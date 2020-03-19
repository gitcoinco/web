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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from app.utils import get_profile
from cacheops import cached_view
from dashboard.models import Activity, Profile, SearchHistory
from dashboard.utils import get_web3, has_tx_mined
from economy.utils import convert_amount
from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time
from grants.forms import MilestoneForm
from grants.models import (
    Contribution, Grant, GrantCategory, MatchPledge, Milestone, PhantomFunding, Subscription, Update,
)
from grants.utils import get_leaderboard, is_grant_team_member
from kudos.models import BulkTransferCoupon
from marketing.mails import (
    grant_cancellation, new_grant, new_grant_admin, new_supporter, subscription_terminated, support_cancellation,
    thank_you_for_supporting,
)
from marketing.models import Keyword, Stat
from retail.helpers import get_ip
from townsquare.models import Comment
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

clr_matching_banners_style = 'pledging'
matching_live = '($200K matching live now!) '
total_clr_pot = 200000
clr_round = 4
clr_active = False
show_clr_card = True
next_round_start = timezone.datetime(2020, 3, 23)

if True:
    clr_matching_banners_style = 'results'
    matching_live = ''

def get_keywords():
    """Get all Keywords."""
    return json.dumps([str(key) for key in Keyword.objects.all().cache().values_list('keyword', flat=True)])


def lazy_round_number(n):
    if n>1000000:
        return f"{round(n/1000000, 1)}m"
    if n>1000:
        return f"{round(n/1000, 1)}k"
    return n

def grants_addr_as_json(request):
    _grants = Grant.objects.filter(
        network='mainnet', hidden=False
    )
    response = list(set(_grants.values_list('title', 'admin_address')))
    return JsonResponse(response, safe=False)


def grants(request):
    """Handle grants explorer."""
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', 'weighted_shuffle')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    grant_type = request.GET.get('type', 'activity')
    state = request.GET.get('state', 'active')
    category = request.GET.get('category')
    _grants = None
    bg = int(request.GET.get('i', timezone.now().strftime("%j"))) % 5
    show_past_clr = False

    sort_by_index = None
    sort_by_clr_pledge_matching_amount = None
    if 'match_pledge_amount_' in sort:
        sort_by_clr_pledge_matching_amount = int(sort.split('amount_')[1])

    if state == 'active':
        _grants = Grant.objects.filter(
            network=network, hidden=False, grant_type=grant_type
        ).active().keyword(keyword).order_by(sort)
    else:
        _grants = Grant.objects.filter(
            network=network, hidden=False, grant_type=grant_type
        ).keyword(keyword).order_by(sort)

    clr_prediction_curve_schema_map = {10**x:x+1 for x in range(0, 5)}
    if sort_by_clr_pledge_matching_amount in clr_prediction_curve_schema_map.keys():
        sort_by_index = clr_prediction_curve_schema_map.get(sort_by_clr_pledge_matching_amount, 0)
        field_name = f'clr_prediction_curve__{sort_by_index}__2'
        _grants = _grants.order_by(f"-{field_name}")

    if category:
        _grants = _grants.filter(Q(categories__category__icontains = category))

    _grants = _grants.prefetch_related('categories')
    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)
    partners = MatchPledge.objects.filter(active=True, pledge_type=grant_type) if grant_type else MatchPledge.objects.filter(active=True)

    now = datetime.datetime.now()

    current_partners = partners.filter(end_date__gte=now).order_by('-amount')
    past_partners = partners.filter(end_date__lt=now).order_by('-amount')
    current_partners_fund = 0

    for partner in current_partners:
        current_partners_fund += partner.amount

    grant_amount = 0
    grant_stats = Stat.objects.filter(
        key='grants',
        ).order_by('-pk')
    if grant_stats.exists():
        grant_amount = lazy_round_number(grant_stats.first().val)

    tech_grants_count = Grant.objects.filter(
        network=network, hidden=False, grant_type='tech'
    ).count()
    media_grants_count = Grant.objects.filter(
        network=network, hidden=False, grant_type='media'
    ).count()
    health_grants_count = Grant.objects.filter(
        network=network, hidden=False, grant_type='health'
    ).count()

    categories = [category[0] for category in basic_grant_categories(grant_type)]

    grant_types = [
        {'label': 'Tech', 'keyword': 'tech', 'count': tech_grants_count},
        {'label': 'Media', 'keyword': 'media', 'count': media_grants_count},
        {'label': 'Public Health', 'keyword': 'health', 'count': health_grants_count}
    ]

    params = {
        'active': 'grants_landing',
        'title': matching_live + str(_('Gitcoin Grants Explorer')),
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'type': grant_type,
        'next_round_start': next_round_start,
        'now': timezone.now(),
        'clr_matching_banners_style': clr_matching_banners_style,
        'categories': categories,
        'grant_types': grant_types,
        'current_partners_fund': current_partners_fund,
        'current_partners': current_partners,
        'past_partners': past_partners,
        'card_desc': _('Get Substantial Sustainable Funding for Your Projects with Gitcoin Grants'),
        'card_player_override': 'https://www.youtube.com/embed/eVgEWSPFR2o',
        'card_player_stream_override': static('v2/card/grants.mp4'),
        'card_player_thumb_override': static('v2/card/grants.png'),
        'grants': grants,
        'target': f'/activity?what=all_grants',
        'bg': bg,
        'keywords': get_keywords(),
        'grant_amount': grant_amount,
        'total_clr_pot': total_clr_pot,
        'clr_active': clr_active,
        'show_clr_card': show_clr_card,
        'sort_by_index': sort_by_index,
        'clr_round': clr_round,
        'show_past_clr': show_past_clr,
        'is_staff': request.user.is_staff,
        'selected_category': category
    }

    # log this search, it might be useful for matching purposes down the line
    if keyword:
        try:
            SearchHistory.objects.update_or_create(
                search_type='grants',
                user=request.user,
                data=request.GET,
                ip_address=get_ip(request)
            )
        except Exception as e:
            logger.debug(e)
            pass

    return TemplateResponse(request, 'grants/index.html', params)

def add_form_categories_to_grant(form_category_ids, grant, grant_type):
    form_category_ids = [int(i) for i in form_category_ids if i != '']

    model_categories = basic_grant_categories(grant_type)
    model_categories = [ category[0] for category in model_categories ]
    selected_categories = [model_categories[i] for i in form_category_ids]

    for category in selected_categories:
        grant_category = GrantCategory.objects.get_or_create(category=category)[0]
        grant.categories.add(grant_category)

@csrf_exempt
def grant_details(request, grant_id, grant_slug):
    """Display the Grant details page."""
    tab = request.GET.get('tab', 'activity')
    profile = get_profile(request)
    add_cancel_params = False
    try:
        grant = Grant.objects.prefetch_related('subscriptions', 'milestones', 'updates', 'team_members').get(
            pk=grant_id, slug=grant_slug
        )
        milestones = grant.milestones.order_by('due_date')
        updates = grant.updates.order_by('-created_on')
        subscriptions = grant.subscriptions.filter(active=True, error=False).order_by('-created_on')
        cancelled_subscriptions = grant.subscriptions.filter(active=False, error=False).order_by('-created_on')

        activity_count = grant.contribution_count
        contributors = []
        contributions = []
        voucher_fundings = []
        if tab in ['transactions', 'contributors']:
            _contributions = Contribution.objects.filter(subscription__in=grant.subscriptions.all().cache(timeout=60)).cache(timeout=60)
            phantom_funds = grant.phantom_funding.all().cache(timeout=60)
            contributions = list(_contributions.order_by('-created_on'))
            voucher_fundings = [ele.to_mock_contribution() for ele in phantom_funds.order_by('-created_on')]
            contributors = list(_contributions.distinct('subscription__contributor_profile')) + list(phantom_funds.distinct('profile'))
            activity_count = len(cancelled_subscriptions) + len(contributions)
        user_subscription = grant.subscriptions.filter(contributor_profile=profile, active=True).first()
        user_non_errored_subscription = grant.subscriptions.filter(contributor_profile=profile, active=True, error=False).first()
        add_cancel_params = user_subscription
    except Grant.DoesNotExist:
        raise Http404

    is_admin = (grant.admin_profile.id == profile.id) if profile and grant.admin_profile else False
    if is_admin:
        add_cancel_params = True

    is_team_member = is_grant_team_member(grant, profile)

    if request.method == 'POST' and (is_team_member or request.user.is_staff):
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
        elif 'edit-title' in request.POST:
            grant.title = request.POST.get('edit-title')
            grant.reference_url = request.POST.get('edit-reference_url')
            grant.amount_goal = Decimal(request.POST.get('edit-amount_goal'))
            team_members = request.POST.getlist('edit-grant_members[]')
            team_members.append(str(grant.admin_profile.id))
            grant.team_members.set(team_members)

            if 'edit-description' in request.POST:
                grant.description = request.POST.get('edit-description')
                grant.description_rich = request.POST.get('edit-description_rich')
            grant.save()

            form_category_ids = request.POST.getlist('edit-categories[]')

            '''Overwrite the existing categories and then add the new ones'''
            grant.categories.clear()
            add_form_categories_to_grant(form_category_ids, grant, grant.grant_type)

            record_grant_activity_helper('update_grant', grant, profile)
            return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

    # handle grant updates unsubscribe
    key = 'unsubscribed_profiles'
    is_unsubscribed_from_updates_from_this_grant = request.user.is_authenticated and request.user.profile.pk in grant.metadata.get(key, [])
    if request.GET.get('unsubscribe') and request.user.is_authenticated:
        ups = grant.metadata.get(key, [])
        ups.append(request.user.profile.pk)
        grant.metadata[key] = ups
        grant.save()
        messages.info(
                request,
                _('You have been unsubscribed from the updates from this grant.')
            )
        is_unsubscribed_from_updates_from_this_grant = True

    params = {
        'active': 'grant_details',
        'clr_matching_banners_style': clr_matching_banners_style,
        'grant': grant,
        'tab': tab,
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
        'target': f'/activity?what=grant:{grant.pk}',
        'activity_count': activity_count,
        'contributors': contributors,
        'clr_active': clr_active,
        'show_clr_card': show_clr_card,
        'is_team_member': is_team_member,
        'voucher_fundings': voucher_fundings,
        'is_unsubscribed_from_updates_from_this_grant': is_unsubscribed_from_updates_from_this_grant,
        'tags': [(f'Email Grant Funders ({len(contributors)})', 'bullhorn')] if is_team_member else [],
    }

    if tab == 'stats':
        params['max_graph'] = grant.history_by_month_max
        params['history'] = json.dumps(grant.history_by_month)

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

    return TemplateResponse(request, 'grants/detail/index.html', params)


@login_required
def grant_new(request):
    """Handle new grant."""
    profile = get_profile(request)

    if request.method == 'POST':
        if 'title' in request.POST:
            logo = request.FILES.get('input_image', None)
            receipt = json.loads(request.POST.get('receipt', '{}'))
            team_members = request.POST.getlist('team_members[]')
            grant_type = request.POST.get('grant_type', 'tech')

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
                'hidden': False,
                'clr_prediction_curve': [[0.0, 0.0, 0.0] for x in range(0, 6)],
                'grant_type': grant_type
            }
            grant = Grant.objects.create(**grant_kwargs)
            new_grant_admin(grant)

            team_members = (team_members[0].split(','))
            team_members.append(profile.id)
            team_members = list(set(team_members))

            team_members = [int(i) for i in team_members if i != '']

            grant.team_members.add(*team_members)
            grant.save()

            form_category_ids = request.POST.getlist('categories[]')
            form_category_ids = (form_category_ids[0].split(','))
            form_category_ids = list(set(form_category_ids))

            add_form_categories_to_grant(form_category_ids, grant, grant_type)

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
            messages.info(
                request,
                _('Thank you for posting this Grant.  Share the Grant URL with your friends/followers to raise your first tokens.')
            )
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

            team_members = (team_members[0].split(','))
            team_members.append(profile.id)
            team_members = list(set(team_members))

            for i in range(0, len(team_members)):
                team_members[i] = int(team_members[i])

            grant.team_members.add(*team_members)
            grant.save()

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

    if not is_grant_team_member(grant, profile):
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
            'title': _('Fund - Grant Ended'),
            'grant': grant,
            'text': _('This Grant has ended.'),
            'subtext': _('Contributions can no longer be made this grant')
        }
        return TemplateResponse(request, 'grants/shared/error.html', params)

    if is_grant_team_member(grant, profile):
        params = {
            'active': 'grant_error',
            'title': _('Fund - Grant funding blocked'),
            'grant': grant,
            'text': _('This Grant cannot be funded'),
            'subtext': _('Grant team members cannot contribute to their own grant.')
        }
        return TemplateResponse(request, 'grants/shared/error.html', params)

    if grant.link_to_new_grant:
        params = {
            'active': 'grant_error',
            'title': _('Fund - Grant Migrated'),
            'grant': grant.link_to_new_grant,
            'text': f'This Grant has ended',
            'subtext': 'Contributions can no longer be made to this grant. <br> Visit the new grant to contribute.',
            'button_txt': 'View New Grant'
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
            subscription.comments = request.POST.get('comment', '')
            subscription.save()

            # one time payments
            activity = None
            if int(subscription.num_tx_approved) == 1:
                subscription.successful_contribution(subscription.new_approve_tx_id);
                subscription.error = True #cancel subs so it doesnt try to bill again
                subscription.subminer_comments = "skipping subminer bc this is a 1 and done subscription, and tokens were alredy sent"
                subscription.save()
                activity = record_subscription_activity_helper('new_grant_contribution', subscription, profile)
            else:
                activity = record_subscription_activity_helper('new_grant_subscription', subscription, profile)

            if 'comment' in request.POST:
                comment = request.POST.get('comment')
                if comment and activity:
                    comment = Comment.objects.create(
                        profile=request.user.profile,
                        activity=activity,
                        comment=comment)

            # TODO - how do we attach the tweet modal WITH BULK TRANSFER COUPON next pageload??
            messages.info(
                request,
                _('Your subscription has been created. It will bill within the next 5 minutes or so. Thank you for supporting Open Source !')
            )

            return JsonResponse({
                'success': True,
            })

        if 'hide_wallet_address' in request.POST:
            profile.hide_wallet_address = bool(request.POST.get('hide_wallet_address', False))
            profile.save()

        if 'signature' in request.POST:
            sub_new_approve_tx_id = request.POST.get('sub_new_approve_tx_id', '')
            subscription = Subscription.objects.filter(new_approve_tx_id=sub_new_approve_tx_id).first()
            subscription.active = True
            subscription.subscription_hash = request.POST.get('subscription_hash', '')
            subscription.contributor_signature = request.POST.get('signature', '')
            if 'split_tx_id' in request.POST:
                subscription.split_tx_id = request.POST.get('split_tx_id', '')
                subscription.save_split_tx_to_contribution()
            if 'split_tx_confirmed' in request.POST:
                subscription.split_tx_confirmed = bool(request.POST.get('split_tx_confirmed', False))
                subscription.save_split_tx_to_contribution()
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

    # handle phantom funding
    active_tab = 'normal'
    fund_reward = None
    round_number = 4
    can_phantom_fund = request.user.is_authenticated and request.user.groups.filter(name='phantom_funders').exists() and clr_active
    phantom_funds = PhantomFunding.objects.filter(profile=request.user.profile, round_number=round_number).order_by('created_on').nocache() if request.user.is_authenticated else PhantomFunding.objects.none()
    is_phantom_funding_this_grant = can_phantom_fund and phantom_funds.filter(grant=grant).exists()
    show_tweet_modal = False
    if can_phantom_fund:
        active_tab = 'phantom'
    if can_phantom_fund and request.POST.get('toggle_phantom_fund'):
        if is_phantom_funding_this_grant:
            msg = "You are no longer signaling for this grant."
            phantom_funds.filter(grant=grant).delete()
        else:
            msg = "You are now signaling for this grant."
            show_tweet_modal = True
            name_search = 'grants_round_4_contributor' if not settings.DEBUG else 'pogs_eth'
            fund_reward = BulkTransferCoupon.objects.filter(token__name__contains=name_search).order_by('?').first()
            PhantomFunding.objects.create(grant=grant, profile=request.user.profile, round_number=round_number)
            record_grant_activity_helper('new_grant_contribution', grant, request.user.profile)

        messages.info(
            request,
            msg
        )
        is_phantom_funding_this_grant = not is_phantom_funding_this_grant

    params = {
        'profile': profile,
        'active': 'fund_grant',
        'title': _('Fund Grant'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'subscription': {},
        'show_tweet_modal': show_tweet_modal,
        'grant_has_no_token': True if grant.token_address == '0x0000000000000000000000000000000000000000' else False,
        'grant': grant,
        'clr_prediction_curve': [c[1] for c in grant.clr_prediction_curve] if grant.clr_prediction_curve and len(grant.clr_prediction_curve[0]) > 1 else [0, 0, 0, 0, 0, 0],
        'keywords': get_keywords(),
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(4),
        'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(120),
        'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(15),
        'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(1),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'gas_advisories': gas_advisories(),
        'splitter_contract_address': settings.SPLITTER_CONTRACT_ADDRESS,
        'gitcoin_donation_address': settings.GITCOIN_DONATION_ADDRESS,
        'can_phantom_fund': can_phantom_fund,
        'is_phantom_funding_this_grant': is_phantom_funding_this_grant,
        'active_tab': active_tab,
        'fund_reward': fund_reward,
        'phantom_funds': phantom_funds,
        'clr_round': clr_round,
        'clr_active': clr_active,
        'total_clr_pot': total_clr_pot,
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
    if not request.user.is_authenticated:
        raise Http404
    handle = request.user.profile.handle
    return redirect(f'/profile/{handle}/grants')

def quickstart(request):
    """Display quickstart guide."""
    params = {'active': 'grants_quickstart', 'title': _('Quickstart')}
    return TemplateResponse(request, 'grants/quickstart.html', params)


def leaderboard(request):
    """Display leaderboard."""

    return redirect ('https://gitcoin.co/leaderboard/payers?cadence=quarterly&keyword=all&product=grants')


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
        'value_in_usdt_now': str(round(subscription.amount_per_period_usdt,2)),
        'token_name': subscription.token_symbol,
        'title': subscription.grant.title,
        'grant_logo': grant_logo,
        'grant_url': subscription.grant.url,
        'category': 'grant',
    }
    kwargs = {
        'profile': profile,
        'subscription': subscription,
        'grant': subscription.grant,
        'activity_type': activity_type,
        'metadata': metadata,
    }
    return Activity.objects.create(**kwargs)

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


def invoice(request, contribution_pk):
    p_contribution = Contribution.objects.prefetch_related('subscription', 'subscription__grant')
    contribution = get_object_or_404(p_contribution, pk=contribution_pk)

    # only allow invoice viewing if admin or if grant contributor
    has_view_privs = request.user.is_staff or request.user.profile == contribution.subscription.contributor_profile

    if not has_view_privs:
        raise Http404

    params = {
        'contribution': contribution,
        'subscription': contribution.subscription,
        'amount_per_period': contribution.subscription.get_converted_monthly_amount()
    }

    return TemplateResponse(request, 'grants/invoice.html', params)

def basic_grant_categories(grant_type):
    categories = GrantCategory.all_categories()

    if grant_type == 'tech':
        categories = GrantCategory.tech_categories()
    elif grant_type == 'media':
        categories = GrantCategory.media_categories()
    elif grant_type == 'health':
        categories = GrantCategory.health_categories()
    else:
        categories = GrantCategory.all_categories()

    return [ (category,idx) for idx, category in enumerate(categories) ]

@csrf_exempt
def grant_categories(request):
    grant_type = request.GET.get('type', None)
    categories = basic_grant_categories(grant_type)

    return JsonResponse({
        'categories': categories
    })
