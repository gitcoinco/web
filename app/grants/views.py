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
import random
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Max, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from app.utils import get_profile
from cacheops import cached_view
from chartit import PivotChart, PivotDataPool
from dashboard.models import Activity, Profile, SearchHistory
from dashboard.tasks import increment_view_count
from dashboard.utils import get_web3, has_tx_mined
from economy.utils import convert_amount
from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time
from grants.clr import predict_clr_live
from grants.models import Contribution, Flag, Grant, GrantCategory, MatchPledge, PhantomFunding, Subscription
from grants.utils import get_leaderboard, is_grant_team_member
from inbox.utils import send_notification_to_user_from_gitcoinbot
from kudos.models import BulkTransferCoupon, Token
from marketing.mails import (
    grant_cancellation, new_grant, new_grant_admin, new_grant_flag_admin, new_supporter, subscription_terminated,
    support_cancellation, thank_you_for_supporting,
)
from marketing.models import Keyword, Stat
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from townsquare.models import Comment, PinnedPost
from townsquare.utils import can_pin
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

clr_matching_banners_style = 'pledging'
matching_live = '(💰$50K Match LIVE!) '
live_now = '❇️ LIVE NOW! Up to $50k Matching Funding on Gitcoin Grants'
matching_live_tiny = '💰'
total_clr_pot = 250000
clr_round = 5
clr_active = True
show_clr_card = True
round_5_5_grants = [656, 493, 494, 502, 504, 662] # special grants for round 5.5
# Round Schedule
# from canonical source of truth https://gitcoin.co/blog/gitcoin-grants-round-4/
# Round 5 - March 23th — April 7th 2020
# Round 6 - June 15th — June 29th 2020
# Round 7 - September 14th — September 28th 2020

next_round_start = timezone.datetime(2020, 3, 23, 12, 0)
after_that_next_round_begin = timezone.datetime(2020, 6, 15, 12, 0)
round_end = timezone.datetime(2020, 4, 10, 10, 0)
round_types = ['media', 'tech', 'health']

kudos_reward_pks = [12580, 12584, 12572, 125868, 12552, 12556, 12557, 125677, 12550, 12392, 12307, 12343, 12156, 12164]

if not clr_active:
    clr_matching_banners_style = 'results'
    matching_live = ''
    matching_live_tiny = ''
    live_now = 'Gitcoin Grants helps you find funding for your projects'


def get_stats(round_type):
    if not round_type:
        round_type = 'tech'
    created_on = next_round_start
    charts = []
    minute = 15 if not settings.DEBUG else 60
    key_titles = [
        ('_match', 'Estimated Matching Amount ($)', '-positive_round_contributor_count', 'grants' ),
        ('_pctrbs', 'Positive Contributors', '-positive_round_contributor_count', 'grants' ),
        ('_nctrbs', 'Negative Contributors', '-negative_round_contributor_count', 'grants' ),
        ('_amt', 'CrowdFund Amount', '-amount_received_in_round', 'grants' ),
        ('_admt1', 'Estimated Matching Amount (in cents) / Twitter Followers', '-positive_round_contributor_count', 'grants' ),
        ('count_', 'Top Contributors by Num Contributations', '-val', 'profile' ),
        ('sum_', 'Top Contributors by Value Contributed', '-val', 'profile' ),
    ]
    for ele in key_titles:
        key = ele[0]
        title = ele[1]
        order_by = ele[2]
        if key == '_nctrbs' and round_type != 'media':
            continue
        keys = []
        if ele[3] == 'grants':
            top_grants = Grant.objects.filter(active=True, grant_type=round_type).order_by(order_by)[0:50]
            keys = [grant.title[0:43] + key for grant in top_grants]
        if ele[3] == 'profile':
            startswith = f"{ele[0]}{round_type}_"
            keys = list(Stat.objects.filter(created_on__gt=created_on, key__startswith=startswith).values_list('key', flat=True))
        charts.append({
            'title': f"{title} Over Time ({round_type.title()} Round)",
            'db': Stat.objects.filter(key__in=keys, created_on__gt=created_on, created_on__minute__lt=minute),
            })
    results = []
    counter = 0
    for chart in charts:
        source = chart['db']
        rankdata = \
            PivotDataPool(
               series=
                [{'options': {
                   'source': source,
                    'legend_by': 'key',
                    'categories': ['created_on'],
                    'top_n_per_cat': 10,
                    },
                  'terms': {
                    'val': Avg('val'),
                    }}
                 ])

        #Step 2: Create the Chart object
        cht = PivotChart(
                datasource = rankdata,
                series_options =
                  [{'options':{
                      'type': 'line',
                      'stacking': False
                      },
                    'terms':
                        ['val']

                }],
                chart_options =
                  {'title': {
                       'text': chart['title']},
                   'xAxis': {
                        'title': {
                           'text': 'Time'}
                        },
                    'renderTo':f'container{counter}',
                    'height': '800px',
                    'legend': {
                        'enabled': False,
                    },
                    },
                )
        results.append(cht)
        counter += 1
    chart_list_str = ",".join([f'container{i}' for i in range(0, counter)])
    return results, chart_list_str

def get_fund_reward(request, grant):
    token = Token.objects.filter(
        id__in=kudos_reward_pks,
        num_clones_available_counting_indirect_send__gt=0,
        owner_address__iexact='0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F').order_by('?').first()
    if not token:
        return None
    key_len = 25
    _key = get_random_string(key_len)
    btc = BulkTransferCoupon.objects.create(
        token=token,
        num_uses_total=1,
        num_uses_remaining=1,
        current_uses=0,
        secret=_key,
        comments_to_put_in_kudos_transfer=f"Thank you for funding '{grant.title}' on Gitcoin Grants!",
        sender_profile=Profile.objects.get(handle='gitcoinbot'),
        make_paid_for_first_minutes=300,
        )

    #store btc on session
    request.session['send_notification'] = 1
    request.session['cta_text'] = "Redeem Kudos"
    request.session['msg_html'] = f"You have received a new {token.ui_name} for your contribution to {grant.title}"
    request.session['cta_url'] = btc.url

    return btc

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

@cache_page(60 * 60)
def grants_stats_view(request):
    cht, chart_list = get_stats(request.GET.get('category'))
    params = {
        'cht': cht,
        'chart_list': chart_list,
        'round_types': round_types,
    }
    response =  TemplateResponse(request, 'grants/shared/landing_stats.html', params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def grants(request):
    """Handle grants explorer."""
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', 'weighted_shuffle')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    grant_type = request.GET.get('type', 'all')
    state = request.GET.get('state', 'active')
    category = request.GET.get('category', '')
    _grants = None
    bg = 4
    bg = f"{bg}.jpg"
    mid_back = 'bg14.png'
    bottom_back = 'bg13.gif'
    if grant_type == 'tech':
        bottom_back = '0.png'
        bg = '0.jpg'
    if grant_type == 'tech':
        bottom_back = 'bg20-2.png'
        bg = '1.jpg'
    if grant_type == 'media':
        bottom_back = 'bg16.gif'
        bg = '2.jpg'
    if grant_type == 'health':
        bottom_back = 'health.jpg'
        bg = 'health2.jpg'
    if grant_type in ['about', 'activity']:
        bg = '3.jpg'
    show_past_clr = False

    sort_by_index = None
    sort_by_clr_pledge_matching_amount = None
    if 'match_pledge_amount_' in sort:
        sort_by_clr_pledge_matching_amount = int(sort.split('amount_')[1])

    _grants = Grant.objects.filter(
        network=network, hidden=False
    ).keyword(keyword)
    try:
        _grants = _grants.order_by(sort, 'pk')
        ____ = _grants.first()
    except Exception as e:
        print(e)
        return redirect('/grants')
    if state == 'active':
        _grants = _grants.active()
    if keyword:
        grant_type = ''
    else:
        # dotn do search by cateogry
        if grant_type != 'all':
            _grants = _grants.filter(grant_type=grant_type)


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

    # record view 
    pks = list([grant.pk for grant in grants])
    if len(pks):
        increment_view_count.delay(pks, grants[0].content_type, request.user.id, 'index')


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
    matic_grants_count = Grant.objects.filter(
        network=network, hidden=False, grant_type='matic'
    ).count()
    all_grants_count = Grant.objects.filter(
        network=network, hidden=False
    ).count()


    categories = [_category[0] for _category in basic_grant_categories(grant_type)]

    grant_types = [
        {'label': 'Tech', 'keyword': 'tech', 'count': tech_grants_count},
        {'label': 'Media', 'keyword': 'media', 'count': media_grants_count},
        {'label': 'Health', 'keyword': 'health', 'count': health_grants_count},
        {'label': 'Matic', 'keyword': 'matic', 'count': matic_grants_count},

    ]
    title = matching_live + str(_('Grants'))
    has_real_grant_type = grant_type and grant_type != 'activity'
    grant_type_title_if_any = grant_type.title() if has_real_grant_type else ''
    grant_type_gfx_if_any = grant_type if has_real_grant_type else 'total'
    if has_real_grant_type:
        title = f"{matching_live} {grant_type_title_if_any.title()} {category.title()} Grants"
    if grant_type == 'stats':
        title = f"Round {clr_round} Stats"
    cht = []
    chart_list = ''
    try:
        what = 'all_grants'
        pinned = PinnedPost.objects.get(what=what)
    except PinnedPost.DoesNotExist:
        pinned = None
    params = {
        'active': 'grants_landing',
        'title': title,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'type': grant_type,
        'round_end': round_end,
        'next_round_start': next_round_start,
        'after_that_next_round_begin': after_that_next_round_begin,
        'all_grants_count': all_grants_count,
        'now': timezone.now(),
        'mid_back': mid_back,
        'cht': cht,
        'chart_list': chart_list,
        'bottom_back': bottom_back,
        'clr_matching_banners_style': clr_matching_banners_style,
        'categories': categories,
        'grant_types': grant_types,
        'current_partners_fund': current_partners_fund,
        'current_partners': current_partners,
        'past_partners': past_partners,
        'card_desc': f'{live_now}',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/tw_cards-03.png')),
        'card_type': 'summary_large_image',
        'avatar_height': 1097,
        'avatar_width': 1953,
        'grants': grants,
        'what': what,
        'can_pin': can_pin(request, what),
        'pinned': pinned,
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
        'selected_category': category,
        'round_5_5_grants': round_5_5_grants
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

    response = TemplateResponse(request, 'grants/index.html', params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

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
    tab = request.GET.get('tab', 'description')
    profile = get_profile(request)
    add_cancel_params = False
    try:
        grant = Grant.objects.prefetch_related('subscriptions','team_members').get(
            pk=grant_id, slug=grant_slug
        )
        increment_view_count.delay([grant.pk], grant.content_type, request.user.id, 'individual')
        subscriptions = grant.subscriptions.filter(active=True, error=False, is_postive_vote=True).order_by('-created_on')
        cancelled_subscriptions = grant.subscriptions.filter(active=False, error=False, is_postive_vote=True).order_by('-created_on')

        activity_count = grant.contribution_count
        contributors = []
        contributions = []
        negative_contributions = []
        voucher_fundings = []
        if tab in ['transactions', 'contributors']:
            _contributions = Contribution.objects.filter(subscription__in=grant.subscriptions.all().cache(timeout=60)).cache(timeout=60)
            negative_contributions = _contributions.filter(subscription__is_postive_vote=False)
            _contributions = _contributions.filter(subscription__is_postive_vote=True)
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
        elif 'edit-title' in request.POST:
            grant.title = request.POST.get('edit-title')
            grant.reference_url = request.POST.get('edit-reference_url')
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

    try:
        what = f'grant:{grant.pk}'
        pinned = PinnedPost.objects.get(what=what)
    except PinnedPost.DoesNotExist:
        pinned = None
    params = {
        'active': 'grant_details',
        'clr_matching_banners_style': clr_matching_banners_style,
        'grant': grant,
        'tab': tab,
        'title': matching_live_tiny + grant.title + " | Grants",
        'card_desc': grant.description,
        'avatar_url': grant.logo.url if grant.logo else None,
        'subscriptions': subscriptions,
        'cancelled_subscriptions': cancelled_subscriptions,
        'contributions': contributions,
        'negative_contributions': negative_contributions,
        'user_subscription': user_subscription,
        'user_non_errored_subscription': user_non_errored_subscription,
        'is_admin': is_admin,
        'grant_is_inactive': not grant.active,
        'keywords': get_keywords(),
        'target': f'/activity?what={what}',
        'pinned': pinned,
        'what': what,
        'activity_count': activity_count,
        'contributors': contributors,
        'clr_active': clr_active,
        'show_clr_card': show_clr_card,
        'is_team_member': is_team_member,
        'voucher_fundings': voucher_fundings,
        'is_unsubscribed_from_updates_from_this_grant': is_unsubscribed_from_updates_from_this_grant,
        'is_round_5_5': grant.id in round_5_5_grants,
        'options': [(f'Email Grant Funders ({grant.contributor_count})', 'bullhorn', 'Select this option to email your status update to all your funders.')] if is_team_member else [],
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
@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def flag(request, grant_id):
    comment = request.POST.get("comment", '')
    grant = Grant.objects.get(pk=grant_id)
    if comment and request.user.is_authenticated and grant:
        flag = Flag.objects.create(
            comments=comment,
            profile=request.user.profile,
            grant=grant,
            )
        new_grant_flag_admin(flag)
        profile = Profile.objects.filter(handle='gitcoinbot').first()
        activity = Activity.objects.create(profile=profile, activity_type='flagged_grant', grant=grant)
        comment = Comment.objects.create(
            profile=profile,
            activity=activity,
            comment=f"Comment from anonymous user: {comment}")


    return JsonResponse({
        'success': True,
    })


@login_required
def grant_new_whitelabel(request):
    """Create a new grant, with a branded creation form for specific tribe"""

    params = {
        'active': 'new_grant',
        'title': _('Matic Build-n-Earn x Gitcoin'),
        'card_desc': _('Earn Rewards by Making Your DApps Superior'),
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
    return TemplateResponse(request, 'grants/new-whitelabel.html', params)



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
                'contract_version': request.POST.get('contract_version', ''),
                'deploy_tx_id': request.POST.get('transaction_hash', ''),
                'network': request.POST.get('network', 'mainnet'),
                'twitter_handle_1': request.POST.get('handle1', ''),
                'twitter_handle_2': request.POST.get('handle2', ''),
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
        grant=grant_id, active=True, error=False, contributor_profile=request.user.profile, is_postive_vote=True
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

            if grant.negative_voting_enabled:
                #is_postive_vote = True if request.POST.get('is_postive_vote', 1) else False
                is_postive_vote = request.POST.get('match_direction', '+') == '+'
            else:
                is_postive_vote = True
            subscription.is_postive_vote = is_postive_vote

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
                    profile = request.user.profile
                    if subscription and subscription.negative:
                        profile = Profile.objects.filter(handle='gitcoinbot').first()
                        comment = f"Comment from contributor: {comment}"
                    comment = Comment.objects.create(
                        profile=profile,
                        activity=activity,
                        comment=comment)

            message = 'Your contribution has succeeded. Thank you for supporting Public Goods on Gitcoin !'
            if request.session.get('send_notification'):
                msg_html = request.session.get('msg_html')
                cta_text = request.session.get('cta_text')
                cta_url = request.session.get('cta_url')
                to_user = request.user
                send_notification_to_user_from_gitcoinbot(to_user, cta_url, cta_text, msg_html)
            if int(subscription.num_tx_approved) > 1:
                message = 'Your subscription has been created. It will bill within the next 5 minutes or so. Thank you for supporting Public Goods on Gitcoin !'

            messages.info(
                request,
                message
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
            if not subscription.negative:
                new_supporter(grant, subscription)
                thank_you_for_supporting(grant, subscription)
            return JsonResponse({
                'success': True,
                'url': reverse('grants:details', args=(grant.pk, grant.slug))
            })

    # handle phantom funding
    active_tab = 'normal'
    fund_reward = None
    round_number = clr_round
    can_phantom_fund = request.user.is_authenticated and request.user.groups.filter(name='phantom_funders_round_5').exists() and clr_active
    phantom_funds = PhantomFunding.objects.filter(profile=request.user.profile, round_number=round_number).order_by('created_on').nocache() if request.user.is_authenticated else PhantomFunding.objects.none()
    is_phantom_funding_this_grant = can_phantom_fund and phantom_funds.filter(grant=grant).exists()
    show_tweet_modal = False
    fund_reward = get_fund_reward(request, grant)
    if can_phantom_fund and request.POST.get('toggle_phantom_fund'):
        if is_phantom_funding_this_grant:
            msg = "You are no longer signaling for this grant."
            phantom_funds.filter(grant=grant).delete()
        else:
            msg = "You are now signaling for this grant."
            show_tweet_modal = True
            pt = PhantomFunding.objects.create(grant=grant, profile=request.user.profile, round_number=round_number)
            record_grant_activity_helper('new_grant_contribution', grant, request.user.profile, amount=pt.value, token='DAI')

        messages.info(
            request,
            msg
        )
        is_phantom_funding_this_grant = not is_phantom_funding_this_grant
    images = [
        'new.svg',
        'torchbearer.svg',
        'robots.png',
        'profile/fund.svg',
    ]
    img = random.choice(images)
    params = {
        'profile': profile,
        'active': 'fund_grant',
        'title': matching_live + grant.title + " | Fund Now",
        'card_desc': grant.description,
        'avatar_url': grant.logo.url if grant.logo else None,
        'subscription': {},
        'show_tweet_modal': show_tweet_modal,
        'direction': request.GET.get('direction', '+'),
        'grant_has_no_token': True if grant.token_address == '0x0000000000000000000000000000000000000000' else False,
        'grant': grant,
        'img': img,
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
    params = {
    'active': 'grants_quickstart',
    'title': _('Quickstart'),
    'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/tw_cards-03.png')),
    }
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
    if subscription and subscription.negative:
        profile = Profile.objects.filter(handle='gitcoinbot').first()
        activity_type = 'negative_contribution'
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
        'num_tx_approved': subscription.num_tx_approved,
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

def record_grant_activity_helper(activity_type, grant, profile, amount=None, token=None):
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
        'value_in_token': '{0:.2f}'.format(grant.amount_received) if not amount else amount,
        'token_name': grant.token_symbol if not token else token,
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


@csrf_exempt
@require_GET
def predict_clr_v1(request, grant_id):
    '''
        {
            amount: <float>,
            is_postive_vote: <char> +, -
        }
    '''
    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to predict clr match'
    }

    user = request.user if request.user.is_authenticated else None

    if not user:
        response['message'] = 'error: user needs to be authenticated to predict clr'
        return JsonResponse(response)

    profile = request.user.profile if hasattr(request.user, 'profile') else None

    if not profile:
        response['message'] = 'error: no matching profile found'
        return JsonResponse(response)

    try:
       grant = Grant.objects.get(pk=grant_id)
    except Grant.DoesNotExist:
        response['message'] = 'error: grant not found'
        return JsonResponse(response)

    amount = request.GET.get('amount')
    if not amount:
        response['message'] = 'error: missing parameter amount'
        return JsonResponse(response)

    is_postive_vote = True if request.GET.get('is_postive_vote', 1) else False

    predicted_clr_match = predict_clr_live(
        grant,
        profile,
        float(amount),
        is_postive_vote
    )

    response = {
        'status': 200,
        'grant_id': grant_id,
        'clr_match': predicted_clr_match
    }

    return JsonResponse(response)
