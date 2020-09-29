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
import hashlib
import html
import json
import logging
import random
import re
import time
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intword, naturaltime
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Avg, Count, Max, Q, Subquery
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
from django.views.decorators.http import require_GET, require_POST

import requests
import tweepy
from app.services import RedisService
from app.settings import (
    EMAIL_ACCOUNT_VALIDATION, TWITTER_ACCESS_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)
from app.utils import get_profile
from bs4 import BeautifulSoup
from cacheops import cached_view
from chartit import PivotChart, PivotDataPool
from dashboard.models import Activity, Profile, SearchHistory
from dashboard.tasks import increment_view_count
from dashboard.utils import get_web3, has_tx_mined
from economy.models import Token as FTokens
from economy.utils import convert_amount
from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time
from grants.models import (
    CartActivity, Contribution, Flag, Grant, GrantCategory, GrantCLR, GrantCollection, GrantType, MatchPledge,
    PhantomFunding, Subscription,
)
from grants.utils import emoji_codes, get_leaderboard, get_user_code, is_grant_team_member
from inbox.utils import send_notification_to_user_from_gitcoinbot
from kudos.models import BulkTransferCoupon, Token
from marketing.mails import (
    grant_cancellation, new_grant, new_grant_admin, new_grant_flag_admin, new_grant_match_pledge, new_supporter,
    subscription_terminated, support_cancellation, thank_you_for_supporting,
)
from marketing.models import Keyword, Stat
from perftools.models import JSONStore
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from townsquare.models import Comment, Favorite, PinnedPost
from townsquare.utils import can_pin
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

# Round Schedule
# from canonical source of truth https://gitcoin.co/blog/gitcoin-grants-round-4/
# Round 5 - March 23th — April 7th 2020
# Round 6 - June 15th — June 29th 2020
# Round 7 - September 15th 9am MST — Oct 2nd 2020 at 5pm MST
# Round 8: December 2nd — December 18th 2020

# TODO-SELF-SERVICE: REMOVE BELOW VARIABLES NEEDED FOR MGMT
clr_round=7
last_round_start = timezone.datetime(2020, 6, 15, 12, 0)
last_round_end = timezone.datetime(2020, 7, 3, 16, 0) #tz=utc, not mst
# TODO, also update grants.clr:CLR_START_DATE, PREV_CLR_START_DATE, PREV_CLR_END_DATE
next_round_start = timezone.datetime(2020, 9, 14, 15, 0) #tz=utc, not mst
after_that_next_round_begin = timezone.datetime(2020, 12, 2, 12, 0)
round_end = timezone.datetime(2020, 10, 2, 23, 0) #tz=utc, not mst

round_types = ['media', 'tech', 'change']
# TODO-SELF-SERVICE: END

kudos_reward_pks = [12580, 12584, 12572, 125868, 12552, 12556, 12557, 125677, 12550, 12392, 12307, 12343, 12156, 12164]


def get_stats(round_type):
    if not round_type:
        round_type = 'tech'
    created_on = next_round_start + timezone.timedelta(days=1)
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
            top_grants = Grant.objects.filter(active=True, grant_type__name=round_type).exclude(pk=86).order_by(order_by)[0:50]
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
        try:
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
        except Exception as e:
            logger.exception(e)
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
        make_paid_for_first_minutes=0,
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
    cht, chart_list = None, None
    try:
        cht, chart_list = get_stats(request.GET.get('category'))
    except Exception as e:
        logger.exception(e)
        raise Http404
    round_types = GrantType.objects.all()
    round_types = [ele.name for ele in round_types if ele.active_clrs.exists()]
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

    _type = request.GET.get('type', 'all')
    return grants_by_grant_type(request, _type)


def get_collections(user, keyword, sort='-modified_on', collection_id=None, following=None,
                    idle_grants=None, only_contributions=None, featured=False):
    three_months_ago = timezone.now() - datetime.timedelta(days=90)

    _collections = GrantCollection.objects.filter(hidden=False)

    if collection_id:
        _collections = _collections.filter(pk=int(collection_id))

    if idle_grants:
        _collections = _collections.filter(grants__last_update__gt=three_months_ago)

    if only_contributions:
        contributions = user.profile.grant_contributor.filter(subscription_contribution__success=True).values('grant_id')
        _collections = _collections.filter(grants__in=Subquery(contributions))

    if following and user.is_authenticated:
        favorite_grants = Favorite.grants().filter(user=user).values('grant_id')
        _collections = _collections.filter(grants__in=Subquery(favorite_grants))

    if user.is_authenticated and user.profile.handle == keyword:
        _collections = _collections.filter(Q(profile=user.profile) | Q(curators=user.profile))
    else:
        _collections = _collections.keyword(keyword)

    if featured:
        _collections = _collections.filter(featured=featured)

    _collections = _collections.order_by('-featured', sort, 'pk')
    _collections = _collections.prefetch_related('grants')

    return _collections


def bulk_grants_for_cart(request):
    grant_type = request.GET.get('type', 'all')
    sort = request.GET.get('sort_option', 'weighted_shuffle')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    state = request.GET.get('state', 'active')
    category = request.GET.get('category', '')
    idle_grants = request.GET.get('idle', '') == 'true'
    following = request.GET.get('following', '') != ''
    only_contributions = request.GET.get('only_contributions', '') == 'true'

    filters = {
        'request': request,
        'grant_type': grant_type,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'state': state,
        'category': category,
        'following': following,
        'idle_grants': idle_grants,
        'only_contributions': only_contributions,
        'omit_my_grants': True
    }
    _grants = build_grants_by_type(**filters)
    grants = []

    for grant in _grants:
        grants.append(grant.cart_payload())

    return JsonResponse({'grants': grants})


def clr_grants(request, round_num):
    """CLR grants explorer."""

    try:
        clr_round = GrantCLR.objects.get(round_num__icontains=round_num)

    except GrantCLR.DoesNotExist:
        return redirect('/grants')

    return grants_by_grant_clr(request, clr_round)


def get_grants(request):
    grants = []
    paginator = None
    grant_type = request.GET.get('type', 'all')

    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    collections_page = request.GET.get('collections_page', 1)
    sort = request.GET.get('sort_option', 'weighted_shuffle')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    state = request.GET.get('state', 'active')
    category = request.GET.get('category', '')
    idle_grants = request.GET.get('idle', '') == 'true'
    following = request.GET.get('following', '') != ''
    only_contributions = request.GET.get('only_contributions', '') == 'true'
    featured = request.GET.get('featured', '') == 'true'
    collection_id = request.GET.get('collection_id', '')
    round_num = request.GET.get('round_num', None)

    clr_round = None
    try:
        if round_num:
            clr_round = GrantCLR.objects.get(round_num=round_num)
    except GrantCLR.DoesNotExist:
        pass

    filters = {
        'request': request,
        'grant_type': grant_type,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'state': state,
        'category': category,
        'following': following,
        'idle_grants': idle_grants,
        'only_contributions': only_contributions,
        'clr_round': clr_round
    }

    if grant_type == 'collections':
        _collections = get_collections(request.user, keyword, collection_id=collection_id,
                                       following=following, idle_grants=idle_grants,
                                       only_contributions=only_contributions, featured=featured)

        if collection_id:
            collection = _collections.first()
            if collection:
                paginator = Paginator(collection.grants.all(), 5)
                grants = paginator.get_page(page)
            collections = _collections
        else:
            paginator = Paginator(_collections, limit)
            collections = paginator.get_page(page)
    else:
        _grants = build_grants_by_type(**filters)

        collections = GrantCollection.objects.filter(grants__in=Subquery(_grants.values('id'))).distinct()[:12]

        paginator = Paginator(_grants, limit)
        grants = paginator.get_page(page)

    contributions = Contribution.objects.none()
    if request.user.is_authenticated:
        contributions = Contribution.objects.filter(
            id__in=request.user.profile.grant_contributor.filter(subscription_contribution__success=True).values(
                'subscription_contribution__id')).prefetch_related('subscription')

    contributions_by_grant = {}
    for contribution in contributions:
        grant_id = str(contribution.subscription.grant_id)
        group = contributions_by_grant.get(grant_id, [])

        group.append({
            **contribution.normalized_data,
            'id': contribution.id,
            'grant_id': contribution.subscription.grant_id,
            'created_on': contribution.created_on.strftime("%Y-%m-%d %H:%M")
        })

        contributions_by_grant[grant_id] = group

    grants_array = []
    for grant in grants:
        grant_json = grant.repr(request.user, request.build_absolute_uri)
        grants_array.append(grant_json)

    return JsonResponse({
        'grant_types': get_grant_clr_types(clr_round, _grants, network) if clr_round else get_grant_type_cache(network),
        'current_type': grant_type,
        'category': category,
        'grants': grants_array,
        'collections': [collection.to_json_dict() for collection in collections],
        'credentials': {
            'is_staff': request.user.is_staff,
            'is_authenticated': request.user.is_authenticated
        },
        'contributions': contributions_by_grant,
        'has_next': paginator.page(page).has_next() if paginator else False,
        'count': paginator.count if paginator else 0,
        'num_pages': paginator.num_pages if paginator else 0,
    })


def build_grants_by_type(request, grant_type='', sort='weighted_shuffle', network='mainnet', keyword='', state='active',
                         category='', following=False, idle_grants=False, only_contributions=False, omit_my_grants=False, clr_round=None):
    print(" " + str(round(time.time(), 2)))

    sort_by_clr_pledge_matching_amount = None
    profile = request.user.profile if request.user.is_authenticated else None
    three_months_ago = timezone.now() - datetime.timedelta(days=90)
    _grants = Grant.objects.filter(network=network, hidden=False)

    if clr_round:
        _grants = _grants.filter(**clr_round.grant_filters)

    if 'match_pledge_amount_' in sort:
        sort_by_clr_pledge_matching_amount = int(sort.split('amount_')[1])
    if sort in ['-amount_received_in_round', '-clr_prediction_curve__0__1']:
        _grants = _grants.filter(is_clr_active=True)

    if omit_my_grants and profile:
        grants_id = list(profile.grant_teams.all().values_list('pk', flat=True)) + \
                    list(profile.grant_admin.all().values_list('pk', flat=True))
        _grants = _grants.exclude(id__in=grants_id)
    elif grant_type == 'me' and profile:
        grants_id = list(profile.grant_teams.all().values_list('pk', flat=True)) + \
                    list(profile.grant_admin.all().values_list('pk', flat=True))
        _grants = _grants.filter(id__in=grants_id)
    elif only_contributions:
        contributions = profile.grant_contributor.filter(subscription_contribution__success=True).values('grant_id')
        _grants = _grants.filter(id__in=Subquery(contributions))

    print(" " + str(round(time.time(), 2)))
    _grants = _grants.keyword(keyword).order_by(sort, 'pk')
    _grants.first()

    if not idle_grants:
        _grants = _grants.filter(last_update__gt=three_months_ago)

    if state == 'active':
        _grants = _grants.active()

    if grant_type != 'all' and grant_type != 'me':
        _grants = _grants.filter(grant_type__name=grant_type)

    if following and request.user.is_authenticated:
        favorite_grants = Favorite.grants().filter(user=request.user).values('grant_id')
        _grants = _grants.filter(id__in=Subquery(favorite_grants))

    clr_prediction_curve_schema_map = {10**x: x+1 for x in range(0, 5)}
    if sort_by_clr_pledge_matching_amount in clr_prediction_curve_schema_map.keys():
        sort_by_index = clr_prediction_curve_schema_map.get(sort_by_clr_pledge_matching_amount, 0)
        field_name = f'clr_prediction_curve__{sort_by_index}__2'
        _grants = _grants.order_by(f"-{field_name}")

    print(" " + str(round(time.time(), 2)))
    if category:
        _grants = _grants.filter(Q(categories__category__icontains=category))

    _grants = _grants.prefetch_related('categories')

    return _grants


def get_grant_type_cache(network):
    try:
        return JSONStore.objects.get(view=f'get_grant_types_{network}').data
    except:
        return {}

def get_grant_types(network, filtered_grants=None):
    all_grants_count = 0
    grant_types = []
    if filtered_grants:
        active_grants = filtered_grants
    else:
        active_grants = Grant.objects.filter(network=network, hidden=False, active=True)

    for _grant_type in GrantType.objects.all():
        count = active_grants.filter(grant_type=_grant_type).count()

        if count > 0:
            all_grants_count += count

            grant_types.append({
                'label': _grant_type.label,
                'keyword': _grant_type.name,
                'count': count,
                'funding': int(_grant_type.active_clrs_sum),
                'funding_ui': f"${round(int(_grant_type.active_clrs_sum)/1000)}k",
            })

    grant_types = sorted(grant_types, key=lambda x: x['funding'], reverse=True)

    for grant_type in grant_types:
        _keyword = grant_type['keyword']
        grant_type['sub_categories'] = [{
            'label': tuple[0],
            'count': get_category_size(tuple[0]),
            # TODO: add in 'funding'
            } for tuple in basic_grant_categories(_keyword)]

    return grant_types


def get_grant_clr_types(clr_round, active_grants=None, network='mainnet'):

    grant_types = []
    if not clr_round:
        return []

    grant_filters = clr_round.grant_filters

    if not grant_filters:
        return grant_types

    if grant_filters.get('grant_type'):
        _grant_types =  GrantType.objects.filter(pk=grant_filters['grant_type'])
    elif grant_filters.get('grant_type__in'):
        _grant_types = GrantType.objects.filter(pk__in=grant_filters['grant_type__in'])

    for _grant_type in _grant_types:
        count = active_grants.filter(grant_type=_grant_type,network=network).count() if active_grants else 0

        grant_types.append({
            'label': _grant_type.label, 'keyword': _grant_type.name, 'count': count
        })

    for grant_type in grant_types: # TODO : Tweak to get only needed categories
        _keyword = grant_type['keyword']
        grant_type['sub_categories'] = [{
            'label': tuple[0],
            'count': get_category_size(tuple[0]),
            } for tuple in basic_grant_categories(_keyword)]

    return grant_types


def get_bg(grant_type):
    bg = 4
    bg = f"{bg}.jpg"
    mid_back = 'bg14.png'
    bg_size = 'contain'
    bg_color = '#030118'
    bottom_back = 'bg13.gif'
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
    if grant_type != 'matic':
        bg = '../grants/grants_header_donors_round_7-5.png'
    if grant_type == 'matic':
        # bg = '../grants/matic-banner.png'
        bg = '../grants/matic-banner.png'
        bg_size = 'cover'
        bg_color = '#0c1844'

    return bg, mid_back, bottom_back, bg_size, bg_color


def grants_by_grant_type(request, grant_type):
    """Handle grants explorer."""
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', 'weighted_shuffle')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    state = request.GET.get('state', 'active')
    category = request.GET.get('category', '')
    following = request.GET.get('following', '') == 'true'
    idle_grants = request.GET.get('idle', '') == 'true'
    only_contributions = request.GET.get('only_contributions', '') == 'true'
    featured = request.GET.get('featured', '') == 'true'
    collection_id = request.GET.get('collection_id', '')

    if keyword:
        category = ''
    profile = get_profile(request)
    _grants = None
    bg, mid_back, bottom_back, bg_size, bg_color = get_bg(grant_type)
    show_past_clr = False

    sort_by_index = None

    grant_amount = 0
    if grant_type == 'about':
        grant_stats = Stat.objects.filter(key='grants').order_by('-pk')
        if grant_stats.exists():
            grant_amount = lazy_round_number(grant_stats.first().val)

    _grants = None
    try:
        _grants = build_grants_by_type(request, grant_type, sort, network, keyword, state, category)
    except Exception as e:
        print(e)
        return redirect('/grants')

    all_grants_count = Grant.objects.filter(
        network=network, hidden=False
    ).count()

    partners = MatchPledge.objects.filter(active=True, pledge_type=grant_type) if grant_type else MatchPledge.objects.filter(active=True)

    now = datetime.datetime.now()

    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    # record view
    pks = list([grant.pk for grant in grants])
    if len(pks):
        increment_view_count.delay(pks, grants[0].content_type, request.user.id, 'index')


    current_partners = partners.filter(end_date__gte=now).order_by('-amount')
    past_partners = partners.filter(end_date__lt=now).order_by('-amount')
    current_partners_fund = 0

    for partner in current_partners:
        current_partners_fund += partner.amount

    categories = [_category[0] for _category in basic_grant_categories(grant_type)]
    grant_types = get_grant_type_cache(network)

    cht = []
    chart_list = ''

    try:
        what = 'all_grants'
        pinned = PinnedPost.objects.get(what=what)
    except PinnedPost.DoesNotExist:
        pinned = None

    prev_grants = Grant.objects.none()
    grants_following = Favorite.objects.none()
    collections = []
    if request.user.is_authenticated:
        grants_following = Favorite.objects.filter(user=request.user, activity=None).count()
        # KO 9/10/2020
        # prev_grants = request.user.profile.grant_contributor.filter(created_on__gt=last_round_start, created_on__lt=last_round_end).values_list('grant', flat=True)
        # rev_grants = Grant.objects.filter(pk__in=prev_grants)
        allowed_collections = GrantCollection.objects.filter(Q(profile=request.user.profile) | Q(curators=request.user.profile))
        collections = [
            {
                'id': collection.id,
                'title': collection.title
            } for collection in allowed_collections.distinct()
        ]


    active_rounds = GrantCLR.objects.filter(is_active=True)

    # populate active round info
    total_clr_pot = None
    if active_rounds:
        for active_round in active_rounds:
            clr_round_amount = active_round.total_pot
            total_clr_pot = total_clr_pot + clr_round_amount if total_clr_pot else clr_round_amount

    if total_clr_pot:
        if total_clr_pot > 1000 * 1000:
            int_total_clr_pot = f"{round(total_clr_pot/1000/1000, 1)}m"
        elif total_clr_pot > 1000:
            int_total_clr_pot = f"{round(total_clr_pot/1000, 0)}k"
        else:
            int_total_clr_pot = intword(total_clr_pot)
        live_now = f'❇️ LIVE NOW! Up to ${int_total_clr_pot} Matching Funding on Gitcoin Grants' if total_clr_pot > 0 else ""
        title = f'(💰${int_total_clr_pot} Match LIVE!) Grants'
    else:
        live_now = 'Gitcoin Grants helps you find funding for your projects'
        title = 'Grants'

    grant_label = None
    for _type in grant_types:
        if _type.get("keyword") == grant_type:
            grant_label = _type.get("label")

    params = {
        'active': 'grants_landing',
        'title': title,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'type': grant_type,
        'grant_label': grant_label if grant_type else grant_type,
        'round_end': round_end,
        'next_round_start': next_round_start,
        'after_that_next_round_begin': after_that_next_round_begin,
        'all_grants_count': all_grants_count,
        'now': timezone.now(),
        'mid_back': mid_back,
        'cht': cht,
        'chart_list': chart_list,
        'bottom_back': bottom_back,
        'categories': categories,
        'prev_grants': prev_grants,
        'grant_types': grant_types,
        'current_partners_fund': current_partners_fund,
        'current_partners': current_partners,
        'past_partners': past_partners,
        'card_desc': f'{live_now}',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/grants7.png')),
        'card_type': 'summary_large_image',
        'avatar_height': 1097,
        'avatar_width': 1953,
        'grants': grants,
        'what': what,
        'can_pin': can_pin(request, what),
        'pinned': pinned,
        'target': f'/activity?what=all_grants',
        'styles': {
            'bg': bg,
            'bg_size': bg_size,
            'bg_color': bg_color
        },
        'bg': bg,
        'keywords': get_keywords(),
        'grant_amount': grant_amount,
        'total_clr_pot': total_clr_pot,
        'sort_by_index': sort_by_index,
        'show_past_clr': show_past_clr,
        'is_staff': request.user.is_staff,
        'selected_category': category,
        'profile': profile,
        'grants_following': grants_following,
        'following': following,
        'idle_grants': idle_grants,
        'only_contributions': only_contributions,
        'collection_id': collection_id,
        'collections': collections,
        'featured': featured
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

    if collection_id:
        collections = GrantCollection.objects.filter(pk=collection_id)
        if collections.exists():
            collection = collections.first()
            params['title'] = collection.title
            params['meta_title'] = collection.title
            params['meta_description'] = collection.description
            params['card_desc'] = collection.description

    response = TemplateResponse(request, 'grants/index.html', params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def grants_by_grant_clr(request, clr_round):
    """Handle grants explorer."""
    grant_type = request.GET.get('type', 'all')
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', 'weighted_shuffle')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    category = request.GET.get('category', '')
    only_contributions = request.GET.get('only_contributions', '') == 'true'

    if keyword:
        category = ''
    profile = get_profile(request)

    _grants = None
    try:
        filters = {
            'request': request,
            'grant_type': grant_type,
            'sort': sort,
            'network': network,
            'keyword': keyword,
            'state': 'active',
            'category': category,
            'idle_grants': True,
            'only_contributions': only_contributions,
            'clr_round': clr_round
        }

        _grants = build_grants_by_type(**filters)
    except Exception as e:
        print(e)
        return redirect('/grants')


    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    # record view
    pks = list([grant.pk for grant in grants])
    if len(pks):
        increment_view_count.delay(pks, grants[0].content_type, request.user.id, 'index')

    current_partners = MatchPledge.objects.filter(clr_round_num=clr_round)
    current_partners_fund = 0

    for partner in current_partners:
        current_partners_fund += partner.amount

    grant_types = get_grant_clr_types(clr_round, network=network)

    grants_following = Favorite.objects.none()
    collections = []
    if request.user.is_authenticated:
        grants_following = Favorite.objects.filter(user=request.user, activity=None).count()
        allowed_collections = GrantCollection.objects.filter(
            Q(profile=request.user.profile) | Q(curators=request.user.profile))
        collections = [
            {
                'id': collection.id,
                'title': collection.title
            } for collection in allowed_collections.distinct()
        ]


    # populate active round info
    total_clr_pot = clr_round.total_pot

    if  clr_round.is_active:
        if total_clr_pot > 1000 * 100:
            int_total_clr_pot = f"{round(total_clr_pot/1000/1000, 1)}m"
        elif total_clr_pot > 100:
            int_total_clr_pot = f"{round(total_clr_pot/1000, 1)}k"
        else:
            int_total_clr_pot = intword(total_clr_pot)
        live_now = f'❇️ LIVE NOW! Up to ${int_total_clr_pot} Matching Funding on Gitcoin Grants' if total_clr_pot > 0 else ""
        title = f'(💰${int_total_clr_pot} Match LIVE!) Grants'
    else:
        live_now = 'Gitcoin Grants helps you find funding for your projects'
        title = 'Grants'


    grant_label = None
    for _type in grant_types:
        if _type.get("keyword") == grant_type:
            grant_label = _type.get("label")

    params = {
        'active': 'grants_landing',
        'title': title,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'type': grant_type,
        'grant_label': grant_label if grant_type else grant_type,
        'round_end': round_end,
        'next_round_start': next_round_start,
        'after_that_next_round_begin': after_that_next_round_begin,
        'all_grants_count': _grants.count(),
        'now': timezone.now(),
        'grant_types': grant_types,
        'current_partners_fund': current_partners_fund,
        'current_partners': current_partners,
        'card_desc': f'{live_now}',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/grants7.png')),
        'card_type': 'summary_large_image',
        'avatar_height': 1097,
        'avatar_width': 1953,
        'grants': grants,
        'can_pin': False,
        'target': f'/activity?what=all_grants',
        'keywords': get_keywords(),
        'total_clr_pot': total_clr_pot,
        'is_staff': request.user.is_staff,
        'selected_category': category,
        'profile': profile,
        'grants_following': grants_following,
        'only_contributions': only_contributions,
        'clr_round': clr_round,
        'collections': collections
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


def get_grant_sybil_profile(grant_id=None, days_back=None, grant_type=None, index_on=None):
    grant_id_sql = f"= {grant_id}" if grant_id else "IS NOT NULL"
    days_back_sql = f"grants_subscription.created_on > now() - interval '{days_back} hours'" if days_back else "true"
    grant_type_sql = f"grant_type_id = '{grant_type.id}'" if grant_type else "true"
    order_sql = f"ORDER BY {index_on} ASC" if index_on != 'grants_contribution.originated_address' else "ORDER BY number_contriibutors DESC"
    having_sql = f"" if index_on != 'grants_contribution.originated_address' else "HAVING count(distinct grants_subscription.contributor_profile_id) >= 2"
    query = f"""
        SELECT
            DISTINCT {index_on},
            count(distinct grants_subscription.contributor_profile_id) as number_contriibutors,
            count(distinct grants_subscription.id) as number_contriibutions,
            (count(distinct grants_subscription.contributor_profile_id)::float / count(distinct grants_subscription.id)) as contributions_per_contributor,
            array_agg(distinct dashboard_profile.handle) as contributors
        from dashboard_profile
        INNER JOIN grants_subscription ON contributor_profile_id = dashboard_profile.id
        INNER JOIN grants_grant on grants_grant.id = grants_subscription.grant_id
        INNER JOIN grants_contribution on grants_contribution.subscription_id = grants_subscription.id
        where grants_subscription.grant_id {grant_id_sql} AND {days_back_sql} AND {grant_type_sql}
            GROUP BY {index_on}
            {having_sql}
            {order_sql}
        """
    # pull from DB
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = []
        for _row in cursor.fetchall():
            rows.append(list(_row))

    # mutate arrow
    sybil_avg = 0
    try:
        total_contributors = sum([ele[1] for ele in rows])
        svbil_total = sum([ele[0]*ele[1] for ele in rows if ele[0] >= 0])
        sybil_avg = svbil_total / total_contributors if total_contributors else 'N/A'
        for i in range(0, len(rows)):
            pct = rows[i][1] / total_contributors
            rows[i].append(round(pct * 100))
    except:
        pass

    return [rows, sybil_avg]

@csrf_exempt
def grant_details(request, grant_id, grant_slug):
    """Display the Grant details page."""
    tab = request.GET.get('tab', 'description')
    profile = get_profile(request)
    add_cancel_params = False
    try:
        grant = None
        try:
            grant = Grant.objects.prefetch_related('subscriptions','team_members').get(
                pk=grant_id, slug=grant_slug
            )
        except Grant.DoesNotExist:
            grant = Grant.objects.prefetch_related('subscriptions','team_members').get(
                pk=grant_id
            )

        increment_view_count.delay([grant.pk], grant.content_type, request.user.id, 'individual')
        subscriptions = grant.subscriptions.none()
        cancelled_subscriptions = grant.subscriptions.none()

        activity_count = grant.contribution_count
        contributors = []
        contributions = []
        negative_contributions = []
        voucher_fundings = []
        sybil_profiles = []

        if tab == 'sybil_profile' and request.user.is_staff:
            items = ['dashboard_profile.sybil_score', 'dashboard_profile.sms_verification', 'grants_contribution.originated_address']
            for item in items:
                title = 'Sybil' if item == 'dashboard_profile.sybil_score' else "SMS"
                if item == 'grants_contribution.originated_address':
                    title = 'Funds origination address'
                sybil_profiles += [
                    [f'THIS {title} Summary Last 60 days', get_grant_sybil_profile(grant.pk, 60 * 24, index_on=item)],
                    [f'{grant.grant_type.name} {title} Summary Last 60 Days', get_grant_sybil_profile(None, 60 * 24, grant.grant_type, index_on=item)],
                    [f'All {title} Summary Last 60 Days', get_grant_sybil_profile(None, 60 * 24, None, index_on=item)],
                ]
        _contributions = Contribution.objects.filter(subscription__grant=grant, subscription__is_postive_vote=True).prefetch_related('subscription', 'subscription__contributor_profile')
        contributions = list(_contributions.order_by('-created_on'))
        #voucher_fundings = [ele.to_mock_contribution() for ele in phantom_funds.order_by('-created_on')]
        if tab == 'contributors':
            phantom_funds = grant.phantom_funding.all().cache(timeout=60)
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
        grant.last_update = timezone.now()
        if request.FILES.get('input_image'):
            logo = request.FILES.get('input_image', None)
            grant.logo = logo
            grant.save()
            record_grant_activity_helper('update_grant', grant, profile)
            return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))
        if 'grant_cancel_tx_id' in request.POST:
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

            if 'edit-twitter_account' in request.POST and request.POST.get('edit-twitter_account') != grant.twitter_handle_1:
                grant.twitter_verified = False
                grant.twitter_verified_at = None
                grant.twitter_verified_by = None
                grant.twitter_handle_1 = request.POST.get('edit-twitter_account')

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

    clr_round = None
    if grant.in_active_clrs.count() > 0:
        clr_round = grant.in_active_clrs.first()

    if clr_round:
        is_clr_active = True
        clr_round_num = clr_round.round_num
    else:
        is_clr_active = False
        clr_round_num = 'LAST'

    is_clr_active = True if clr_round else False
    title = grant.title + " | Grants"

    if is_clr_active:
        title = '💰 ' + title

    params = {
        'active': 'grant_details',
        'grant': grant,
        'sybil_profiles': sybil_profiles,
        'tab': tab,
        'title': title,
        'card_desc': grant.description,
        'avatar_url': grant.logo.url if grant.logo else None,
        'subscriptions': subscriptions,
        'cancelled_subscriptions': cancelled_subscriptions,
        'contributions': contributions,
        'negative_contributions': negative_contributions,
        'user_subscription': user_subscription,
        'user_non_errored_subscription': user_non_errored_subscription,
        'is_admin': is_admin,
        'keywords': get_keywords(),
        'target': f'/activity?what={what}',
        'pinned': pinned,
        'what': what,
        'activity_count': activity_count,
        'contributors': contributors,
        'clr_active': is_clr_active,
        'round_num': clr_round_num,
        'is_team_member': is_team_member,
        'voucher_fundings': voucher_fundings,
        'is_unsubscribed_from_updates_from_this_grant': is_unsubscribed_from_updates_from_this_grant,
        'is_round_5_5': False,
        'options': [(f'Email Grant Funders ({grant.contributor_count})', 'bullhorn', 'Select this option to email your status update to all your funders.')] if is_team_member else [],
        'user_code': get_user_code(request.user.profile.id, grant, emoji_codes) if request.user.is_authenticated else '',
        'verification_tweet': get_grant_verification_text(grant),
    }

    if tab == 'stats':
        params['max_graph'] = grant.history_by_month_max
        params['history'] = json.dumps(grant.history_by_month)
        params['stats_history'] = grant.stats.filter(snapshot_type='increment').order_by('-created_on')

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


    return JsonResponse({
        'success': True,
    })


def grant_new_whitelabel(request):
    """Create a new grant, with a branded creation form for specific tribe"""

    profile = get_profile(request)

    params = {
        'active': 'new_grant',
        'title': _('Matic Build-n-Earn x Gitcoin'),
        'card_desc': _('Earn Rewards by Making Your DApps Superior'),
        'card_player_thumb_override': request.build_absolute_uri(static('v2/images/grants/maticxgitcoin.png')),
        'profile': profile,
        'is_logged_in': 1 if profile else 0,
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

    from grants.utils import add_grant_to_active_clrs

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
                'github_project_url': request.POST.get('github_project_url', ''),
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
                'last_update': timezone.now(),
                'admin_profile': profile,
                'logo': logo,
                'hidden': False,
                'clr_prediction_curve': [[0.0, 0.0, 0.0] for x in range(0, 6)],
                'grant_type': GrantType.objects.get(name=grant_type)
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

            messages.info(
                request,
                _('Thank you for posting this Grant.  Share the Grant URL with your friends/followers to raise your first tokens.')
            )
            grant.save()
            record_grant_activity_helper('new_grant', grant, profile)
            new_grant(grant, profile)
            add_grant_to_active_clrs(grant)

            return JsonResponse({
                'success': True,
                'url': grant.url,
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
        'trusted_relayer': settings.GRANTS_OWNER_ACCOUNT,
        'grant_types': GrantType.objects.all()
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

    if not grant.configured_to_receieve_funding:
        messages.info(
            request,
            _('This grant is not configured to accept funding at this time.  Please contact founders@gitcoin.co if you believe this message is in error!')
        )
        logger.error(f"Grant {grant.pk} is not properly configured for funding.  Please set grant.contract_address on this grant")
        return redirect(reverse('grants:details', args=(grant.pk, grant.slug)))

    if request.method == 'POST':
        from grants.tasks import process_grant_contribution
        process_grant_contribution.delay(grant_id, grant_slug, profile.pk, request.POST)

        return JsonResponse({
            'success': True,
        })

    raise Http404

@login_required
def bulk_fund(request):
    if request.method != 'POST':
        raise Http404

    # Save off payload data
    JSONStore.objects.create(
        key=request.POST.get('split_tx_id'), # use bulk data tx hash as key
        view='bulk_fund_post_payload',
        data=request.POST
    )

    # Get list of grant IDs
    grant_ids_list = [int(pk) for pk in request.POST.get('grant_id').split(',')]

    # For each grant, we validate the data. If it fails, save it off and throw error at the end
    successes = []
    failures = []
    for (index, grant_id) in enumerate(grant_ids_list):
        try:
            grant = Grant.objects.get(pk=grant_id)
        except Grant.DoesNotExist:
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Does Not Exist'),
                'grant':grant_id,
                'text': _('This grant does not exist'),
                'subtext': _('No grant with this ID was found'),
                'success': False
            })
            continue

        profile = get_profile(request)

        if not grant.active:
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Ended'),
                'grant':grant_id,
                'text': _('This Grant has ended.'),
                'subtext': _('Contributions can no longer be made this grant'),
                'success': False
            })
            continue

        if is_grant_team_member(grant, profile):
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant funding blocked'),
                'grant':grant_id,
                'text': _('This Grant cannot be funded'),
                'subtext': _('Grant team members cannot contribute to their own grant.'),
                'success': False
            })
            continue

        if grant.link_to_new_grant:
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Migrated'),
                'grant':grant_id,
                'text': _('This Grant has ended'),
                'subtext': _('Contributions can no longer be made to this grant. <br> Visit the new grant to contribute.'),
                'success': False
            })
            continue

        active_subscription = Subscription.objects.select_related('grant').filter(
            grant=grant_id, active=True, error=False, contributor_profile=request.user.profile, is_postive_vote=True
        )

        if active_subscription:
            failures.append({
                'active': 'grant_error',
                'title': _('Subscription Exists'),
                'grant':grant_id,
                'text': _('You already have an active subscription for this grant.'),
                'success': False
            })
            continue

        if not grant.configured_to_receieve_funding:
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Not Configured'),
                'grant':grant_id,
                'text': _('This Grant is not configured to accept funding at this time.'),
                'subtext': _('Grant is not properly configured for funding.  Please set grant.contract_address on this grant, or contact founders@gitcoin.co if you believe this message is in error!'),
                'success': False
            })
            continue

        try:
            from grants.tasks import process_grant_contribution
            payload = {
                # Values that are constant for all donations
                'contributor_address': request.POST.get('contributor_address'),
                'csrfmiddlewaretoken': request.POST.get('csrfmiddlewaretoken'),
                'frequency_count': request.POST.get('frequency_count'),
                'frequency_unit': request.POST.get('frequency_unit'),
                'gas_price': request.POST.get('gas_price'),
                'gitcoin_donation_address': request.POST.get('gitcoin_donation_address'),
                'hide_wallet_address': request.POST.get('hide_wallet_address'),
                'match_direction': request.POST.get('match_direction'),
                'network': request.POST.get('network'),
                'num_periods': request.POST.get('num_periods'),
                'real_period_seconds': request.POST.get('real_period_seconds'),
                'recurring_or_not': request.POST.get('recurring_or_not'),
                'signature': request.POST.get('signature'),
                'split_tx_id': request.POST.get('split_tx_id'),
                'splitter_contract_address': request.POST.get('splitter_contract_address'),
                'subscription_hash': request.POST.get('subscription_hash'),
                # Values that vary by donation
                'admin_address': request.POST.get('admin_address').split(',')[index],
                'amount_per_period': request.POST.get('amount_per_period').split(',')[index],
                'comment': request.POST.get('comment').split(',')[index],
                'confirmed': request.POST.get('confirmed').split(',')[index],
                'contract_address': request.POST.get('contract_address').split(',')[index],
                'contract_version': request.POST.get('contract_version').split(',')[index],
                'denomination': request.POST.get('denomination').split(',')[index],
                'gitcoin-grant-input-amount': request.POST.get('gitcoin-grant-input-amount').split(',')[index],
                'grant_id': request.POST.get('grant_id').split(',')[index],
                'sub_new_approve_tx_id': request.POST.get('sub_new_approve_tx_id').split(',')[index],
                'token_address': request.POST.get('token_address').split(',')[index],
                'token_symbol': request.POST.get('token_symbol').split(',')[index],
            }
            process_grant_contribution.delay(grant_id, grant.slug, profile.pk, payload)
        except Exception as e:
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Processing Failed'),
                'grant':grant_id,
                'text': _('This Grant was not processed successfully.'),
                'subtext': _(f'{str(e)}'),
                'success': False
            })
            continue

        successes.append({
            'title': _('Fund - Grant Funding Processed Successfully'),
            'grant':grant_id,
            'text': _('Funding for this grant was successfully processed and saved.'),
            'success': True
        })

    return JsonResponse({
        'success': True,
        'grant_ids': grant_ids_list,
        'successes': successes,
        'failures': failures
    })

@login_required
def zksync_set_interrupt_status(request):
    """
    For the specified address, save off the deposit hash of the value the tx that was interrupted.
    If a deposit hash is present, then the user was interrupted and must complete the existing
    checkout before doing another one
    """

    user_address = request.POST.get('user_address')
    deposit_tx_hash = request.POST.get('deposit_tx_hash')

    try:
        # Look for existing entry, and if present we overwrite it
        entry = JSONStore.objects.get(key=user_address, view='zksync_checkout')
        entry.data = deposit_tx_hash
        entry.save()
    except JSONStore.DoesNotExist:
        # No entry exists for this user, so create a new one
        JSONStore.objects.create(
            key=user_address,
            view='zksync_checkout',
            data=deposit_tx_hash
        )

    return JsonResponse({
        'success': True,
        'deposit_tx_hash': deposit_tx_hash
    })

@login_required
def zksync_get_interrupt_status(request):
    """
    Returns the transaction hash of a deposit into zkSync if user was interrupted before zkSync
    chekout was complete
    """
    user_address = request.GET.get('user_address')
    try:
        result = JSONStore.objects.get(key=user_address, view='zksync_checkout')
        deposit_tx_hash = result.data
    except JSONStore.DoesNotExist:
        # If there's no entry for this user, assume they haven't been interrupted
        deposit_tx_hash = False

    return JsonResponse({
        'success': True,
        'deposit_tx_hash': deposit_tx_hash
    })

@login_required
def get_replaced_tx(request):
    """
    scrapes etherscan to get the replaced tx
    """
    tx_hash = request.GET.get('tx_hash')
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    response = requests.get(f"https://etherscan.io/tx/{tx_hash}/", headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    # look for span that contains the dropped&replaced msg
    p = soup.find("span", "u-label u-label--sm u-label--warning rounded")
    if not p:
        return JsonResponse({
            'success': True,
            'tx_hash': tx_hash
        })
    if "Replaced" in p.text:  # check if it's a replaced tx
        # get the id for the replaced tx
        q = soup.find(href=re.compile("/tx/0x"))
        return JsonResponse({
            'success': True,
            'tx_hash': q.text
        })
    else:
        return JsonResponse({
            'success': True,
            'tx_hash': tx_hash
        })


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


def grants_cart_view(request):
    context = {
        'title': 'Grants Cart',
        'EMAIL_ACCOUNT_VALIDATION': EMAIL_ACCOUNT_VALIDATION
    }
    if request.user.is_authenticated:
        # GET THE SMS STATUS FROM PROFILE
        context['verified'] = request.user.profile.sms_verification
        context['brightid_uuid'] = request.user.profile.brightid_uuid
        context['username'] = request.user.profile.username
    else:
        return redirect('/login/github?next=' + request.get_full_path())

    response = TemplateResponse(request, 'grants/cart-vue.html', context=context)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def get_category_size(category):
    key = f"grant_category_{category}"
    redis = RedisService().redis
    try:
        return int(redis.get(key))
    except:
        return 0




def grants_bulk_add(request, grant_str):
    grants = {}
    redis = RedisService().redis
    key = hashlib.md5(grant_str.encode('utf')).hexdigest()
    views = redis.incr(key)

    grants_data = grant_str.split(':')[0].split(',')

    for ele in grants_data:
        # new format will support amount and token in the URL separated by ;
        grant_data = ele.split(';')
        if len(grant_data) > 0 and grant_data[0].isnumeric():
            grant_id = grant_data[0]
            grants[grant_id] = {
                'id': int(grant_id)
            }

            if len(grant_data) == 3:  # backward compatibility
                grants[grant_id]['amount'] = grant_data[1]
                grants[grant_id]['token'] = FTokens.objects.filter(id=int(grant_data[2])).first()

    by_whom = ""
    prefix = ""
    try:
        by_whom = f"by {grant_str.split(':')[1]}"
        prefix = f"{grant_str.split(':')[2]} : "
    except:
        pass

    # search valid grants and associate with its amount and token
    grants_info = grants.values()
    grant_ids = [grant['id'] for grant in grants_info]
    for grant in Grant.objects.filter(pk__in=grant_ids):
        grants[str(grant.id)]['obj'] = grant

    grants = [grant for grant in grants_info if grant.get('obj')]

    grant_titles = ", ".join([grant['obj'].title for grant in grants])
    title = f"{prefix}{len(grants)} Grants in Shared Cart {by_whom} : Viewed {views} times"

    context = {
        'grants': grants,
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/grants7.png')),
        'title': title,
        'card_desc': "Click to Add All to Cart: " + grant_titles

    }
    response = TemplateResponse(request, 'grants/bulk_add_to_cart.html', context=context)
    return response


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
    'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/grants7.png')),
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


def new_matching_partner(request):

    profile = get_profile(request)
    params = {
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/grants7.png')),
        'title': 'Pledge your support.',
        'card_desc': f'Thank you for your interest in supporting public goods.on Gitcoin. Complete the form below to get started.',
        'data': request.POST.dict(),
        'grant_types': basic_grant_types() + basic_grant_categories(None),
    }

    if not request.user.is_authenticated:
        messages.info(
                request,
                _('Please login to submit this form.')
            )
    elif request.POST:
        end_date = timezone.now() + timezone.timedelta(days=7*3)
        network = 'mainnet'
        match_pledge = MatchPledge.objects.create(
            profile=profile,
            active=False,
            end_date=end_date,
            amount=0,
            data=json.dumps(request.POST.dict())
        )
        match_pledge.save()
        new_grant_match_pledge(match_pledge)
        messages.info(
                request,
                _("""Thank you for your inquiry. We will respond within 1-2 business days.  """)
            )

    return TemplateResponse(request, 'grants/newmatch.html', params)


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

def basic_grant_types():
    result = GrantType.objects.all()
    return [ (ele.name, ele.label) for ele in result ]


def basic_grant_categories(name):
    result = []
    grant_type = GrantType.objects.filter(name=name).first()

    if name and grant_type:
        grant_categories = grant_type.categories.all()
        for category in grant_categories:
            result.append(category.category)

    else:
        grant_types = GrantType.objects.all()
        grant_categories = []
        for grant_type in grant_types:
            grant_categories = grant_type.categories.all()
            for category in grant_categories:
                result.append(category.category)

    result = list(set(result))

    return [ (category,idx) for idx, category in enumerate(result) ]


@csrf_exempt
def grant_categories(request):
    grant_type = request.GET.get('type', None)
    categories = basic_grant_categories(grant_type)

    return JsonResponse({
        'categories': categories
    })


@login_required
def grant_activity(request, grant_id=None):
    action = request.POST.get('action')
    metadata = request.POST.get('metadata')
    bulk = request.POST.get('bulk') == 'true'

    if not metadata:
        return redirect('/grants/activity/')

    if not grant_id:
        grant = None
    else:
        grant = get_object_or_404(Grant, pk=grant_id)

    _ca = CartActivity.objects.create(grant=grant, profile=request.user.profile, action=action,
                                metadata=json.loads(metadata), bulk=bulk, latest=True)

    for ca in CartActivity.objects.filter(profile=request.user.profile, latest=True, pk__lt=_ca.pk):
        ca.latest = False
        ca.save()

    return JsonResponse({
        'error': False
    })

@require_GET
def grants_clr(request):
    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to fetch grant clr'
    }

    pks = request.GET.get('pks', None)

    if not pks:
        response['message'] = 'error: missing parameter pks'
        return JsonResponse(response)

    grants = []

    try:
        for grant in Grant.objects.filter(pk__in=pks.split(',')):
           grants.append({
               'pk': grant.pk,
               'title': grant.title,
               'clr_prediction_curve': grant.clr_prediction_curve
           })
    except Exception as e:
        print(e)
        response = {
            'status': 500,
            'message': 'error: something went wrong while fetching grants clr'
        }
        return JsonResponse(response)

    response = {
        'status': 200,
        'grants': grants
    }
    return JsonResponse(response)


@login_required
@csrf_exempt
def toggle_grant_favorite(request, grant_id):
    grant = get_object_or_404(Grant, pk=grant_id)
    favorite = Favorite.objects.filter(user=request.user, grant_id=grant_id)
    if favorite.exists():
        favorite.delete()

        return JsonResponse({
            'action': 'unfollow'
        })

    Favorite.objects.create(user=request.user, grant=grant)

    return JsonResponse({
        'action': 'follow'
    })


def get_grant_verification_text(grant, long=True):
    msg = f'I am verifying my ownership of { grant.title } on Gitcoin Grants'
    if long:
        msg += f' at https://gitcoin.co{grant.get_absolute_url()}.'
    return msg


@login_required
def verify_grant(request, grant_id):
    grant = Grant.objects.get(pk=grant_id)

    if not is_grant_team_member(grant, request.user.profile):
        return JsonResponse({
            'ok': False,
            'msg': f'You need to be a member of this grants to verify it.'
        })

    if grant.twitter_verified:
        return JsonResponse({
            'ok': True,
            'msg': 'Grant was verified previously'
        })

    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
    try:
        api = tweepy.API(auth)
        last_tweet = api.user_timeline(screen_name=grant.twitter_handle_1, count=1, tweet_mode="extended",
                                       include_rts=False, exclude_replies=False)[0]
    except tweepy.TweepError:
        return JsonResponse({
            'ok': False,
            'msg': f'Sorry, we couldn\'t get the last tweet from @{grant.twitter_handle_1}'
        })
    except IndexError:
        return JsonResponse({
            'ok': False,
            'msg': 'Sorry, we couldn\'t retrieve the last tweet from your timeline'
        })

    if last_tweet.retweeted or 'RT @' in last_tweet.full_text:
        return JsonResponse({
            'ok': False,
            'msg': 'We get a retweet from your last status, at this moment we don\'t supported retweets.'
        })

    user_code = get_user_code(request.user.profile.id, grant, emoji_codes)
    text = get_grant_verification_text(grant, False)

    full_text = html.unescape(last_tweet.full_text)
    for url in last_tweet.entities['urls']:
        full_text = full_text.replace(url['url'], url['display_url'])

    has_code = user_code in full_text
    has_text = text in full_text

    if has_code and has_text:
        grant.twitter_verified = True
        grant.twitter_verified_by = request.user.profile
        grant.twitter_verified_at = timezone.now()

        grant.save()

    return JsonResponse({
        'ok': True,
        'verified': grant.twitter_verified,
        'text': last_tweet.full_text,
        'expanded_text': full_text,
        'has_code': has_code,
        'has_text': has_text,
        'account': grant.twitter_handle_1
    })


def get_collections_list(request):
    if request.user.is_authenticated:
        collections = GrantCollection.objects.filter(Q(profile=request.user.profile) | Q(curators=request.user.profile))
        return JsonResponse({
            'collections': [{
                'id': collection['id'],
                'title': collection['title'],
                'description': collection['description']
            } for collection in collections.values('id', 'title', 'description')]
        })

    return JsonResponse({
        'collections': []
    })


@login_required
@require_POST
def save_collection(request):
    title = request.POST.get('collectionTitle')
    description = request.POST.get('collectionDescription')
    grant_ids = request.POST.getlist('grants[]')
    collection_id = request.POST.get('collection')
    profile = request.user.profile
    grant_ids = [int(grant_id) for grant_id in grant_ids]

    if len(grant_ids) == 0:
        return JsonResponse({
            'ok': False,
            'msg': 'We can\'t create empty collections'

        }, status=422)

    if collection_id:
        collection = GrantCollection.objects.filter(
            Q(profile=request.user.profile) | Q(curators=request.user.profile)
        ).get(pk=collection_id)

        grant_ids = grant_ids + list(collection.grants.all().values_list('id', flat=True))
    else:
        kwargs = {
            'title': title,
            'description': description,
            'profile': profile,
        }
        collection = GrantCollection.objects.create(**kwargs)

    collection.grants.set(grant_ids)
    collection.generate_cache()

    return JsonResponse({
        'ok': True,
        'collection': {
            'id': collection.id,
            'title': title,
        }
    })


def get_collection(request, collection_id):
    collection = GrantCollection.objects.get(pk=collection_id)

    grants = [grant.cart_payload() for grant in collection.grants.order_by('-clr_prediction_curve__0__1')]
    curators = [{
        'url': curator.url,
        'handle': curator.handle,
        'avatar_url': curator.avatar_url
    } for curator in collection.curators.all()]

    owner = {
        'url': collection.profile.url,
        'handle': collection.profile.handle,
        'avatar_url': collection.profile.avatar_url
    }

    return JsonResponse({
        'id': collection.id,
        'title': collection.title,
        'grants': grants,
        'owner': owner,
        'curators': curators + [owner]
    })


def get_grant_payload(request, grant_id):
    grant = Grant.objects.get(pk=grant_id)

    return JsonResponse({
        'grant': grant.cart_payload(),
    })


@csrf_exempt
@login_required
@require_POST
def remove_grant_from_collection(request, collection_id):
    grant_id = request.POST.get('grant')
    grant = Grant.objects.get(pk=grant_id)
    collection = GrantCollection.objects.filter(Q(profile=request.user.profile) | Q(curators=request.user.profile)).get(pk=collection_id)

    collection.grants.remove(grant)
    collection.generate_cache()

    grants = [grant.repr(request.user, request.build_absolute_uri) for grant in collection.grants.all()]

    return JsonResponse({
        'grants': grants,
    })


@csrf_exempt
@login_required
@require_POST
def add_grant_from_collection(request, collection_id):
    grant_id = request.POST.get('grant')
    grant = Grant.objects.get(pk=grant_id)
    collection = GrantCollection.objects.filter(Q(profile=request.user.profile) | Q(curators=request.user.profile)).get(pk=collection_id)

    collection.grants.add(grant)
    collection.generate_cache()

    grants = [grant.repr(request.user, request.build_absolute_uri) for grant in collection.grants.all()]

    return JsonResponse({
        'grants': grants,
    })
