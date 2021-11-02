# -*- coding: utf-8 -*-
"""Define the Grant views.

Copyright (C) 2021 Gitcoin Core

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
import hashlib
import html
import json
import logging
import math
import re
import time
import uuid
from datetime import datetime
from io import StringIO
from urllib.parse import urlencode

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intword
from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.paginator import EmptyPage, Paginator
from django.db import connection, transaction
from django.db.models import Q, Subquery
from django.http import Http404, HttpResponse, JsonResponse
from django.http.response import HttpResponseBadRequest, HttpResponseServerError
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

import boto3
import dateutil.parser
import pytz
import requests
import tweepy
from app.services import RedisService
from app.settings import (
    EMAIL_ACCOUNT_VALIDATION, TWITTER_ACCESS_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_CONSUMER_KEY,
    TWITTER_CONSUMER_SECRET,
)
from app.utils import allow_all_origins, get_profile
from boto3.s3.transfer import S3Transfer
from bs4 import BeautifulSoup
from cacheops import cached_view
from dashboard.brightid_utils import get_brightid_status
from dashboard.models import Activity, HackathonProject, Profile, SearchHistory
from dashboard.tasks import increment_view_count
from dashboard.utils import get_web3
from dashboard.views import invalid_file_response
from economy.models import Token as FTokens
from economy.utils import convert_token_to_usdt
from eth_account.messages import defunct_hash_message
from grants.clr_data_src import fetch_contributions
from grants.models import (
    CartActivity, Contribution, Flag, Grant, GrantAPIKey, GrantBrandingRoutingPolicy, GrantCLR, GrantCollection,
    GrantTag, GrantType, MatchPledge, Subscription,
)
from grants.tasks import (
    process_bsci_sybil_csv, process_grant_creation_admin_email, process_grant_creation_email, process_notion_db_write,
    update_grant_metadata,
)
from grants.utils import (
    emoji_codes, generate_collection_thumbnail, generate_img_thumbnail_helper, get_clr_rounds_metadata, get_user_code,
    is_grant_team_member, sync_payout, toggle_user_sybil,
)
from kudos.models import BulkTransferCoupon, Token
from marketing.mails import grant_cancellation, new_grant_flag_admin
from marketing.models import Keyword, Stat
from perftools.models import JSONStore, StaticJsonEnv
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from townsquare.models import Announcement, Favorite, PinnedPost
from townsquare.utils import can_pin
from web3 import HTTPProvider, Web3

logger = logging.getLogger(__name__)
w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

kudos_reward_pks = [12580, 12584, 12572, 125868, 12552, 12556, 12557, 125677, 12550, 12392, 12307, 12343, 12156, 12164]

grant_tenants = ['ETH', 'ZCASH', 'ZIL', 'CELO', 'POLKADOT', 'HARMONY', 'KUSAMA', 'BINANCE', 'RSK', 'ALGORAND']

clr_rounds_metadata = get_clr_rounds_metadata()


def get_keywords():
    """Get all Keywords."""
    return json.dumps([str(key) for key in Keyword.objects.all().cache().values_list('keyword', flat=True)])


def api_auth_profile(request):
    profile = request.user.profile if request.user.is_authenticated else None
    GAK = None
    api_key = request.GET.get('_key')
    api_secret = request.GET.get('_secret')

    should_look_at_api_key = (api_key and api_secret) or profile
    if should_look_at_api_key:
        if not api_key:
            api_key = str(uuid.uuid4())
        if not api_secret:
            api_secret = str(uuid.uuid4())
        GAK, _ = GrantAPIKey.objects.get_or_create(
            key=api_key,
            secret=api_secret,
            defaults={
                "profile" : profile,
                }
            )
        profile = GAK.profile

    GAK = {'_key': GAK.key, '_secret': GAK.secret} if GAK else None

    return profile, GAK

def lazy_round_number(n):
    if n>1000000:
        return f"{round(n/1000000, 1)}m"
    if n>1000:
        return f"{round(n/1000, 1)}k"
    return n

# helper functions - start
def helper_grants_round_start_end_date(request, round_id):
    start = timezone.now()
    end = timezone.now()
    try:
        gclr = GrantCLR.objects.filter(round_num=round_id, customer_name='ethereum').first()
        start = gclr.start_date
        end = gclr.end_date
    except Exception as e:
        print(e)
    return start, end


def helper_grants_output(request, meta_data, addresses, GAK=None):

    # gather_stats
    add_count = len(addresses)

    response = {
        'meta': {
            'generated_at': request.build_absolute_uri(),
            'generated_on': timezone.now().strftime("%Y-%m-%d"),
            'stat':{
                'unique_addresses_found': add_count,
            },
            'meta': meta_data,
            'api_key': GAK,
        },
        'addresses': addresses
    }
    return JsonResponse(response, safe=False)
# helper functions - end

grants_data_release_date = timezone.datetime(2020, 10, 22)

hide_wallet_address_anonymized_sql = "AND contributor_profile_id NOT IN (select id from dashboard_profile where hide_wallet_address_anonymized)"


@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def contribution_addr_from_grant_as_json(request, grant_id):

    # return all contirbutor addresses to the grant
    grant = Grant.objects.get(pk=grant_id)

    profile, GAK = api_auth_profile(request)
    if not profile:
        return redirect('/login/github/?next=' + request.get_full_path())
    if not grant.is_on_team(profile) and not request.user.is_staff:
        return JsonResponse({
            'msg': 'not_authorized, you must be a team member of this grant'
            }, safe=False)
    if timezone.now().timestamp() < grants_data_release_date.timestamp() and not request.user.is_staff:
        return JsonResponse({
            'msg': f'not_authorized, check back at {grants_data_release_date.strftime("%Y-%m-%d")}'
            }, safe=False)

    query = f"select distinct contributor_address from grants_subscription where grant_id = '{grant_id}' {hide_wallet_address_anonymized_sql}"
    earnings = query_to_results(query)
    meta_data = {
       'grant': grant_id,
    }
    return helper_grants_output(request, meta_data, earnings, GAK)


@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def contribution_addr_from_grant_during_round_as_json(request, grant_id, round_id):

    # return all contirbutor addresses to the grant
    grant = Grant.objects.get(pk=grant_id)

    profile, GAK = api_auth_profile(request)
    if not profile:
        return redirect('/login/github/?next=' + request.get_full_path())
    if not grant.is_on_team(profile) and not request.user.is_staff:
        return JsonResponse({
            'msg': 'not_authorized, you must be a team member of this grant'
            }, safe=False)
    if timezone.now().timestamp() < grants_data_release_date.timestamp() and not request.user.is_staff:
        return JsonResponse({
            'msg': f'not_authorized, check back at {grants_data_release_date.strftime("%Y-%m-%d")}'
            }, safe=False)

    start, end = helper_grants_round_start_end_date(request, round_id)
    query = f"select distinct contributor_address from grants_subscription where created_on BETWEEN '{start}' AND '{end}' and grant_id = '{grant_id}' {hide_wallet_address_anonymized_sql}"
    earnings = query_to_results(query)

    meta_data = {
        'start': start.strftime("%Y-%m-%d"),
        'end': end.strftime("%Y-%m-%d"),
        'round': round_id,
        'grant': grant_id,
    }
    return helper_grants_output(request, meta_data, earnings, GAK)

@ratelimit(key='ip', rate='1/m', method=ratelimit.UNSAFE, block=True)
def contribution_info_from_grant_during_round_as_json(request, grant_id, round_id):

    # return all contirbutor addresses to the grant
    grant = Grant.objects.get(pk=grant_id)

    profile, GAK = api_auth_profile(request)
    if not profile:
        return redirect('/login/github/?next=' + request.get_full_path())
    if not grant.is_on_team(profile) and not request.user.is_staff:
        return JsonResponse({
            'msg': 'not_authorized, you must be a team member of this grant'
            }, safe=False)
    if timezone.now().timestamp() < grants_data_release_date.timestamp() and not request.user.is_staff:
        return JsonResponse({
            'msg': f'not_authorized, check back at {grants_data_release_date.strftime("%Y-%m-%d")}'
            }, safe=False)

    start, end = helper_grants_round_start_end_date(request, round_id)
    query = f"""
select
    md5(grants_subscription.id::varchar(255)) as id,
    dashboard_profile.handle,
    CONCAT('https://gitcoin.co/dynamic/avatar/', dashboard_profile.handle) as url,
    comments

from grants_subscription
INNER JOIN dashboard_profile on dashboard_profile.id = contributor_profile_id
where
grants_subscription.created_on BETWEEN '{start}' AND '{end}' and grant_id = {grant_id}
AND hide_wallet_address_anonymized = false
order by grants_subscription.id desc
LIMIT 10
    """
    earnings = query_to_results(query)

    meta_data = {
        'start': start.strftime("%Y-%m-%d"),
        'end': end.strftime("%Y-%m-%d"),
        'round': round_id,
        'grant': grant_id,
    }
    return helper_grants_output(request, meta_data, earnings, GAK)


@login_required
@cached_view(timeout=3600)
def contribution_addr_from_round_as_json(request, round_id):

    if timezone.now().timestamp() < grants_data_release_date.timestamp() and not request.user.is_staff:
        return JsonResponse({
            'msg': f'not_authorized, check back at {grants_data_release_date.strftime("%Y-%m-%d")}'
            }, safe=False)

    start, end = helper_grants_round_start_end_date(request, round_id)
    query = f"select distinct contributor_address from grants_subscription where created_on BETWEEN '{start}' AND '{end}'  {hide_wallet_address_anonymized_sql}"
    earnings = query_to_results(query)
    meta_data = {
        'start': start.strftime("%Y-%m-%d"),
        'end': end.strftime("%Y-%m-%d"),
        'round': round_id,
    }
    return helper_grants_output(request, meta_data, earnings)


def query_to_results(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = []
        for _row in cursor.fetchall():
            rows.append(list(_row))
        return rows
    return []

@login_required
@cached_view(timeout=3600)
def contribution_addr_from_all_as_json(request):

    if timezone.now().timestamp() < grants_data_release_date.timestamp() and not request.user.is_staff:
        return JsonResponse({
            'msg': f'not_authorized, check back at {grants_data_release_date.strftime("%Y-%m-%d")}'
            }, safe=False)

    query = f'select distinct contributor_address from grants_subscription where true  {hide_wallet_address_anonymized_sql}'
    earnings = query_to_results(query)
    meta_data = {
    }
    return helper_grants_output(request, meta_data, earnings)


def grants_addr_as_json(request):
    _grants = Grant.objects.filter(
        network='mainnet', hidden=False
    )
    response = list(set(_grants.values_list('title', 'admin_address')))
    return JsonResponse(response, safe=False)


def grants(request):
    """Handle grants explorer."""

    grant_types = request.GET.get('type', 'all')
    return grants_by_grant_type(request, grant_types)


def get_collections(
    user, keyword, sort='-shuffle_rank', collection_id=None, following=None,
    idle_grants=None, featured=False, only_contributions=None, my_collections=None
):
    three_months_ago = timezone.now() - timezone.timedelta(days=90)

    _collections = GrantCollection.objects.filter(hidden=False)

    if collection_id and collection_id.isdigit():
        _collections = _collections.filter(pk=int(collection_id))

    if not idle_grants:
        _collections = _collections.filter(grants__last_update__gt=three_months_ago)

    if only_contributions:
        contributions = user.profile.grant_contributor.filter(subscription_contribution__success=True).values('grant_id')
        _collections = _collections.filter(grants__in=Subquery(contributions))

    if user.is_authenticated:
        if my_collections:
            _collections = _collections.filter(Q(profile=user.profile))
        if following:
            favorite_grants = Favorite.grants().filter(user=user).values('grant_id')
            _collections = _collections.filter(grants__in=Subquery(favorite_grants))

    if keyword:
        if user.profile.handle == keyword:
            _collections = _collections.filter(Q(profile=user.profile) | Q(curators=user.profile))
        else:
            _collections = _collections.keyword(keyword)

    if featured:
        _collections = _collections.filter(featured=featured)

    _collections = _collections.order_by('-featured', sort, 'pk')
    _collections = _collections.prefetch_related('grants')

    return _collections


def bulk_grants_for_cart(request):
    grant_types = request.GET.get('grant_types', None)
    sort = request.GET.get('sort_option', None)
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    state = request.GET.get('state', 'active')
    tenants = request.GET.get('tenants', '')
    grant_regions = request.GET.get('grant_regions', '')
    grant_tags = request.GET.get('grant_tags', '')
    idle_grants = request.GET.get('idle', '') == 'true'
    following = request.GET.get('following', '') != ''
    only_contributions = request.GET.get('only_contributions', '') == 'true'

    try:
        clr_round_pk = request.GET.get('clr_round')
        clr_round = GrantCLR.objects.get(pk=clr_round_pk)
    except GrantCLR.DoesNotExist:
        clr_round = None

    filters = {
        'request': request,
        'grant_types': grant_types,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'state': state,
        'tenants': tenants,
        'grant_regions': grant_regions,
        'grant_tags': grant_tags,
        'following': following,
        'idle_grants': idle_grants,
        'only_contributions': only_contributions,
        'clr_round': clr_round,
        'omit_my_grants': True
    }
    _grants = get_grants_by_filters(**filters)
    grants = []

    for grant in _grants:
        grants.append(grant.cart_payload(request.build_absolute_uri))

    return JsonResponse({'grants': grants})


def clr_grants(request, round_num, sub_round_slug='', customer_name=''):
    """CLR grants explorer."""

    try:
        params = {
            'round_num': round_num,
            'sub_round_slug': sub_round_slug,
            'customer_name': customer_name
        }
        clr_round = GrantCLR.objects.get(**params)

    except GrantCLR.DoesNotExist:
        return redirect('/grants')

    return grants_by_grant_clr(request, clr_round)

@login_required
def get_interrupted_contributions(request):
    all_contributions = Contribution.objects.filter(profile_for_clr=request.user.profile)
    user_contributions = []

    for contribution in all_contributions:
        validator_comment = contribution.validator_comment
        is_zksync = "zkSync" in validator_comment
        tx_not_found = "Transaction not found, unknown reason" in validator_comment
        deposit_no_transfer = "Found deposit but no transfer" in validator_comment
        if is_zksync and (tx_not_found or deposit_no_transfer):
            user_contributions.append(contribution.normalized_data)

    return JsonResponse({
        'success': True,
        'contributions': user_contributions
    })


def get_grants(request):
    grants = []
    collections = []
    paginator = None

    # 1. fetch all query params
    grant_types = request.GET.get('grant_types', None)
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '').strip()
    state = request.GET.get('state', 'active')
    grant_tags = request.GET.get('grant_tags', '')
    idle_grants = request.GET.get('idle', '') == 'true'
    following = request.GET.get('following', None) == 'true'
    only_contributions = request.GET.get('only_contributions', '') == 'true'
    featured = request.GET.get('featured', '') == 'true'
    collection_id = request.GET.get('collection_id', '')
    round_num = request.GET.get('round_num', None)
    sub_round_slug = request.GET.get('sub_round_slug', '')
    customer_name = request.GET.get('customer_name', '')
    sort = request.GET.get('sort_option', None)
    tenants = request.GET.get('tenants', '')
    grant_regions = request.GET.get('grant_regions', '')
    my_grants = request.GET.get('me', None) == 'true'
    my_collections = request.GET.get('my_collections', None) == 'true'

    # 2. Fetch GrantCLR if round_num is present
    clr_round = None
    try:
        if round_num:
            params = {
                'round_num': round_num,
                'sub_round_slug': sub_round_slug,
                'customer_name': customer_name
            }
            clr_round = GrantCLR.objects.get(**params)
    except GrantCLR.DoesNotExist:
        pass

    # 3. Populate filters to fetch grants
    filters = {
        'request': request,
        'grant_types': grant_types,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'state': state,
        'grant_tags': grant_tags,
        'following': following,
        'idle_grants': idle_grants,
        'only_contributions': only_contributions,
        'clr_round': clr_round,
        'tenants': tenants,
        'grant_regions': grant_regions,
        'my_grants': my_grants
    }
    _grants = get_grants_by_filters(**filters)

    if sort == '' and keyword:
        # return grants result starting with exact title matches
        exact_matches = [
            grant for grant in _grants if grant.title.lower() == keyword.lower()
        ]
        non_exact_matches = [
            grant for grant in _grants if grant.title.lower() != keyword.lower()
        ]
        _grants = exact_matches + non_exact_matches

    if collection_id and collection_id.isnumeric():
        # 4.1 Fetch grants by collection
        _collections = get_collections(
            request.user,
            keyword,
            collection_id=collection_id,
            following=following,
            idle_grants=idle_grants,
            only_contributions=only_contributions,
            featured=featured
        )

        # 4.2 Fetch grants within a collection
        collection = _collections.first()
        if collection:
            paginator = Paginator(collection.grants.all(), 5)
            grants = paginator.get_page(page)
        collections = _collections

    elif request.user.is_authenticated and my_collections:
        # 4.1 Fetch my collections
        collections = get_collections(
            user=request.user,
            keyword=None,
            idle_grants=idle_grants,
            my_collections=my_collections
        )

    else:
        # 4.1 Paginate results
        paginator = Paginator(_grants, limit)
        grants = paginator.get_page(page)

    contributions = Contribution.objects.none()
    contributions_by_grant = {}

    if only_contributions:

        if request.user.is_authenticated:
            contributions = Contribution.objects.filter(
                id__in=request.user.profile.grant_contributor.filter(subscription_contribution__success=True).values(
                    'subscription_contribution__id')).prefetch_related('subscription')

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

    # Clean up before sending response
    grants_array = []
    for grant in grants:
        grant_json = grant.repr(request.user, request.build_absolute_uri)
        if not request.user.is_staff:
            del grant_json['sybil_score']
            del grant_json['weighted_risk_score']
        grants_array.append(grant_json)

    pks = list([grant.pk for grant in grants])
    if len(pks):
        increment_view_count.delay(pks, grants[0].content_type, request.user.id, 'index')

    has_next = False
    next_page_number = False
    has_previous = False
    if paginator:
        try:
            has_next = paginator.page(page).has_next()
            next_page_number = paginator.page(page).next_page_number()
            has_previous = paginator.page(page).has_previous()
        except EmptyPage:
            pass

    return JsonResponse({
        'applied_filters': {
            'grant_types': grant_types,
            'grant_tags': grant_tags,
            'grant_regions': grant_regions,
            'round_num': round_num,
            'sub_round_slug': sub_round_slug,
            'customer_name': customer_name,
            'collection_id': collection_id
        },
        'grant_types': get_grant_clr_types(clr_round, _grants, network) if clr_round and _grants else get_grant_type_cache(network),
        'grants': grants_array,
        'collections': [collection.to_json_dict(request.build_absolute_uri) for collection in collections],
        'credentials': {
            'is_staff': request.user.is_staff,
            'is_authenticated': request.user.is_authenticated
        },
        'contributions': contributions_by_grant,
        'has_next': has_next,
        'next_page_number': next_page_number,
        'has_previous': has_previous,
        'count': paginator.count if paginator else 0,
        'num_pages': paginator.num_pages if paginator else 0,
        'metadata': {
            'claim_start_date': clr_round.claim_start_date if clr_round else None,
            'claim_end_date': clr_round.claim_end_date if clr_round else None,
            'start_date': clr_round.start_date if clr_round else None,
            'end_date': clr_round.end_date if clr_round else None,
        }
    })


def get_grants_by_filters(
    request,
    grant_types,
    sort=None,
    network='mainnet',
    keyword='',
    state='active',
    grant_tags='',
    following=False,
    idle_grants=False,
    only_contributions=False,
    omit_my_grants=False,
    clr_round=None,
    tenants='',
    grant_regions='',
    my_grants=False
):

    # sort_by_clr_pledge_matching_amount = None
    profile = request.user.profile if request.user.is_authenticated else None
    three_months_ago = timezone.now() - timezone.timedelta(days=90)

    # 1. Filter grants by network and hidden = false
    _grants = Grant.objects.filter(network=network, hidden=False)

    # 2. Filter grants belonging to a CLR round
    if clr_round:
        if clr_round.collection_filters:
            grant_ids = GrantCollection.objects.filter(**clr_round.collection_filters).values_list('grants', flat=True)
            _grants = _grants.filter(pk__in=grant_ids)

        _grants = _grants.filter(**clr_round.grant_filters)

    if profile:
        if my_grants:
            # 3. Filter grants created by user
            grants_id = list(profile.grant_teams.all().values_list('pk', flat=True)) + \
                        list(profile.grant_admin.all().values_list('pk', flat=True))
            _grants = _grants.filter(id__in=grants_id)
        if omit_my_grants:
            # 4. Exclude grants created by user
            grants_id = list(profile.grant_teams.all().values_list('pk', flat=True)) + \
                        list(profile.grant_admin.all().values_list('pk', flat=True))
            _grants = _grants.exclude(id__in=grants_id)
        elif only_contributions:
            # 5. Filter grants to which the user has contributed to
            contributions = profile.grant_contributor.filter(subscription_contribution__success=True).values('grant_id')
            _grants = _grants.filter(id__in=Subquery(contributions))

    if not idle_grants:
        # 6. Filter grants which are stale (last update was > 3 months )
        _grants = _grants.filter(last_update__gt=three_months_ago)

    if state == 'active':
        # 7. Filter grants which are active
        _grants = _grants.active()

    if grant_types and grant_types not in ['all', 'collections']:
        # 8. Fetch grants which have mentioned grant_types
        types= grant_types.split(',')
        type_query= Q()
        for grant_type in types:
            type_query |= Q(grant_type__name=grant_type)

        _grants = _grants.filter(type_query)

    if following and request.user.is_authenticated:
        # 9. Filter grants having matching title & description
        favorite_grants = Favorite.grants().filter(user=request.user).values('grant_id')
        _grants = _grants.filter(id__in=Subquery(favorite_grants))

    if grant_tags:
        tags = grant_tags.split(',')
        # 10. Fetch grants which have mentioned grant_tags
        tag_query= Q()
        for tag in tags:
            tag_query |= Q(tags__name=tag)

        _grants = _grants.filter(tag_query)

    if tenants:
        # 11. Fetch grants which have mentioned tenants
        tenant_query = Q()
        for tenant in tenants.split(','):
            if tenant in tenants:
                tenant = tenant.lower()
                tenant_filter = tenant + '_payout_address' if tenant != 'eth' else 'admin_address'
                tenant_query = ~Q(('%s' % tenant_filter, '0x0'))

            # _grants = _grants.exclude(Q(**{tenant_filter: '0x0'}))
        _grants = _grants.filter(tenant_query)

    if grant_regions:
        regions = grant_regions.split(',')
        # 12. Fetch grants which have mentioned regions
        region_query= Q()
        for region in regions:
            region_query |= Q(region=region)
        _grants = _grants.filter(region_query)

    if keyword:
        # 13. Grant search by title & description
        _grants = _grants.annotate(search=SearchVector('description'))
        keyword_query = Q(title__icontains=keyword)
        keyword_query |= Q(search=keyword)

        _grants = _grants.filter(keyword_query)

    if sort:
        # 14. Sort filtered grants
        if 'match_pledge_amount_' in sort:
            order = '-' if sort[0] is '-' else ''
            sort_by_clr_pledge_matching_amount = int(sort.split('amount_')[1])
            clr_prediction_curve_schema_map = {10**x: x+1 for x in range(0, 5)}
            if sort_by_clr_pledge_matching_amount in clr_prediction_curve_schema_map.keys():
                sort_by_index = clr_prediction_curve_schema_map.get(sort_by_clr_pledge_matching_amount, 0)
                field_name = f'clr_prediction_curve__{sort_by_index}__2'
                _grants = _grants.order_by(f"{order}{field_name}")

        # elif 'random_shuffle' in sort:
        #     _grants = _grants.order_by('?')

        elif sort.replace('-', '') in [
            'amount_received_in_round', 'clr_prediction_curve__0__1', 'positive_round_contributor_count'
        ]:
            _grants = _grants.filter(is_clr_active=True).order_by(f"{sort}")

        elif sort.replace('-', '') in [
            'weighted_shuffle', 'metadata__upcoming', 'metadata__gem', 'created_on', 'amount_received', 'contribution_count', 'contributor_count', 'last_update'
        ]:
            print(f"Sort is {sort}")
            _grants = _grants.order_by(f"{sort}")

        elif request.user.is_staff and sort.replace('-', '') in [
            'weighted_risk_score', 'sybil_score'
        ]:
            _grants = _grants.order_by(f"{sort}")

    _grants = _grants.prefetch_related('categories', 'team_members', 'admin_profile', 'grant_type')

    return _grants


def get_grant_type_cache(network):
    try:
        return JSONStore.objects.get(view=f'get_grant_types_{network}').data
    except:
        return []

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
                'is_active': _grant_type.is_active,
                'is_visible': _grant_type.is_visible,
                'count': count,
                'funding': int(_grant_type.active_clrs_sum),
                'funding_ui': f"${round(int(_grant_type.active_clrs_sum)/1000)}k",
            })

    grant_types = sorted(grant_types, key=lambda x: x['funding'], reverse=True)

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
    else:
        return grant_types

    for _grant_type in _grant_types:
        count = active_grants.filter(grant_type=_grant_type,network=network).count() if active_grants else 0

        grant_types.append({
            'label': _grant_type.label,
            'keyword': _grant_type.name,
            'is_active': _grant_type.is_active,
            'is_visible': _grant_type.is_visible,
            'count': count,
            'funding': int(_grant_type.active_clrs_sum),
            'funding_ui': f"${round(int(_grant_type.active_clrs_sum)/1000)}k",
        })

    return grant_types


# def get_bg(grant_type):
#     bg = 4
#     bg = f"{bg}.jpg"
#     mid_back = 'bg14.png'
#     bg_size = 'contain'
#     bg_color = '#030118'
#     bottom_back = 'bg13.gif'
#     if grant_type == 'tech':
#         bottom_back = 'bg20-2.png'
#         bg = '1.jpg'
#     if grant_type == 'media':
#         bottom_back = 'bg16.gif'
#         bg = '2.jpg'
#     if grant_type == 'health':
#         bottom_back = 'health.jpg'
#         bg = 'health2.jpg'
#     if grant_type in ['about', 'activity']:
#         bg = '3.jpg'
#     if grant_type != 'matic':
#         bg = '../grants/grants_header_donors_round_7-6.png'
#     if grant_type == 'ZCash':
#         bg = '../grants/grants_header_donors_zcash_round_1_2.png'
#         bg_color = '#FFFFFF'
#     if grant_type == 'matic':
#         # bg = '../grants/matic-banner.png'
#         bg = '../grants/matic-banner.png'
#         bg_size = 'cover'
#         bg_color = '#0c1844'

#     return bg, mid_back, bottom_back, bg_size, bg_color


def get_policy_state(policy, request):
    return {
        "url_pattern": policy.url_pattern,
        "banner_image": request.build_absolute_uri(policy.banner_image.url) if policy.banner_image else '',
        "background_image": request.build_absolute_uri(policy.background_image.url) if policy.background_image else '',
        "inline_css": policy.inline_css
    }


def get_branding_info(request):

    all_policies = GrantBrandingRoutingPolicy.objects.filter().order_by('-priority')
    for policy in all_policies:
        if re.search(policy.url_pattern, request.get_full_path()):
            return get_policy_state(policy, request)

def get_all_routing_policies(request):
    all_policies = GrantBrandingRoutingPolicy.objects.filter().order_by('-priority')
    return [get_policy_state(policy, request) for policy in all_policies]


def grants_landing(request):
    network = request.GET.get('network', 'mainnet')
    active_rounds = GrantCLR.objects.filter(start_date__lt=timezone.now(), end_date__gt=timezone.now())

    active_main_rounds= active_rounds.filter(type='main').order_by('-total_pot')
    active_cause_rounds= active_rounds.filter(type='cause').order_by('-total_pot')
    active_sponsor_rounds= active_rounds.filter(type='sponsor').order_by('-total_pot')


    now = datetime.now()
    sponsors = MatchPledge.objects.filter(active=True, end_date__gte=now).order_by('-amount')
    live_now = 'Gitcoin grants sustain web3 projects with quadratic funding'

    params = dict(
        {
            'active': 'grants_landing',
            'network': network,
            'grant_bg': get_branding_info(request),
            'title': 'Grants',
            'EMAIL_ACCOUNT_VALIDATION': EMAIL_ACCOUNT_VALIDATION,
            'card_desc': f'{live_now}',
            'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/grants11.png')),
            'card_type': 'summary_large_image',
            'avatar_height': 675,
            'avatar_width': 1200,
            'has_active_rounds': True if active_rounds else False,
            'active_main_rounds': active_main_rounds,
            'active_cause_rounds': active_cause_rounds,
            'active_sponsor_rounds': active_sponsor_rounds,
            'sponsors': sponsors,
            'featured': True,
            'now': now,
            'trust_bonus': round(request.user.profile.trust_bonus * 100) if request.user.is_authenticated and request.user.profile else 0
        },
        **clr_rounds_metadata
    )

    response = TemplateResponse(request, 'grants/landing/index.html', params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

def grants_by_grant_type(request, grant_type):
    """Handle grants explorer."""
    print(grant_type)

    # limit = request.GET.get('limit', 6)
    # page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', 'weighted_shuffle')
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    # category = request.GET.get('category', '')
    following = request.GET.get('following', '') == 'true'
    idle_grants = request.GET.get('idle', '') == 'true'
    only_contributions = request.GET.get('only_contributions', '') == 'true'
    featured = request.GET.get('featured', '') == 'true'
    collection_id = request.GET.get('collection_id', '')

    # if keyword:
    #     category = ''
    profile = get_profile(request)
    # bg, mid_back, bottom_back, bg_size, bg_color = get_bg(grant_type)
    show_past_clr = False
    # all_grant_types = GrantType.objects.all()

    all_styles = {}
    # for _gtype in all_grant_types:
    #     bg, mid_back, bottom_back, bg_size, bg_color = get_bg(_gtype)
    #     all_styles[_gtype.name] = dict(bg=bg, mid_back=mid_back, bottom_back=bottom_back, bg_size=bg_size, bg_color=bg_color)
    sort_by_index = None

    grant_amount = 0
    if grant_type == 'about':
        grant_stats = Stat.objects.filter(key='grants').order_by('-pk')
        if grant_stats.exists():
            grant_amount = lazy_round_number(grant_stats.first().val)

    # partners = MatchPledge.objects.filter(active=True, pledge_type=grant_type) if grant_type else MatchPledge.objects.filter(active=True)
    # now = datetime.now()
    # current_partners = partners.filter(end_date__gte=now).order_by('-amount')
    # current_partners_fund = 0

    # for partner in current_partners:
    #     current_partners_fund += partner.amount

    grant_types = get_grant_type_cache(network)

    try:
        what = 'all_grants'
        pinned = PinnedPost.objects.get(what=what)
    except PinnedPost.DoesNotExist:
        pinned = None

    grants_following = Favorite.objects.none()
    collections = []

    if request.user.is_authenticated:
        grants_following = Favorite.objects.filter(user=request.user, activity=None).count()
        allowed_collections = GrantCollection.objects.filter(Q(profile=request.user.profile) | Q(curators=request.user.profile))
        collections = [
            {
                'id': collection.id,
                'title': collection.title
            } for collection in allowed_collections.distinct()
        ]

    active_rounds = GrantCLR.objects.filter(is_active=True, start_date__lt=timezone.now(), end_date__gt=timezone.now()).order_by('-total_pot')

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

    round_start_date = clr_rounds_metadata['round_start_date']
    round_end_date = clr_rounds_metadata['round_end_date']

    params = {
        'active': 'grants_explorer',
        'title': title,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'type': grant_type,
        'grant_label': grant_label if grant_type else grant_type,
        'round_end': round_end_date,
        'next_round_start': round_start_date,
        'now': timezone.now(),
        'card_desc': f'{live_now}',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/default_grants.png')),
        'card_type': 'summary_large_image',
        'avatar_height': 675,
        'avatar_width': 1200,
        'what': what,
        'all_styles': all_styles,
        'all_routing_policies': get_all_routing_policies(request),
        'can_pin': can_pin(request, what),
        'pinned': pinned,
        'target': f'/activity?what=all_grants',
        'grant_bg': get_branding_info(request),
        'announcement': Announcement.objects.filter(key='grants', valid_from__lt=timezone.now(), valid_to__gt=timezone.now()).order_by('-rank').first(),
        'keywords': get_keywords(),
        'grant_amount': grant_amount,
        'total_clr_pot': total_clr_pot,
        'sort_by_index': sort_by_index,
        'show_past_clr': show_past_clr,
        'is_staff': request.user.is_staff,
        # 'selected_category': category,
        'profile': profile,
        'grants_following': grants_following,
        'following': following,
        'idle_grants': idle_grants,
        'only_contributions': only_contributions,
        'collection_id': collection_id,
        'collections': collections,
        'featured': featured,
        'active_rounds': active_rounds,
        'trust_bonus': round(request.user.profile.trust_bonus * 100) if request.user.is_authenticated and request.user.profile else 0
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

    if collection_id and collection_id.isdigit():
        collections = GrantCollection.objects.prefetch_related('profile').filter(pk=collection_id)
        if collections.exists():
            collection = collections.first()
            params['title'] = collection.title
            params['meta_title'] = collection.title
            params['meta_description'] = collection.description
            params['meta_owner'] = collection.profile.handle
            params['meta_owner_url'] = collection.profile.url
            params['meta_owner_avatar'] = collection.profile.avatar_url
            params['meta_grant_ids'] = json.dumps([ grant.id for grant in collection.grants.all() ])
            params['card_desc'] = collection.description
            params['avatar_url'] = request.build_absolute_uri(collection.cover.url) if collection.cover else ''


    response = TemplateResponse(request, 'grants/explorer.html', params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def get_grant_tags(request):
    """Fetch matching grants tags"""

    tag_phrase = request.GET.get('q', '')
    tags = GrantTag.objects.filter(name__icontains=tag_phrase).values_list('name', 'id')

    response = {
       'status': 200,
        'grant_tags': list(tags)
    }
    return JsonResponse(response)


def grants_type_redirect(request, grant_type):
    """Redirect old grant url with search params to /explorer keeping query params."""
    base_url = reverse('grants:grants_by_category', kwargs={"grant_type":grant_type})
    query_string =  urlencode(request.GET)
    url = '{}?{}'.format(base_url, query_string)
    return redirect(url, code=302)


def grants_by_grant_clr(request, clr_round):
    """Handle grants explorer."""
    grant_types = request.GET.get('type', None)
    limit = request.GET.get('limit', 6)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', None)
    network = request.GET.get('network', 'mainnet')
    keyword = request.GET.get('keyword', '')
    grant_tags = request.GET.get('grant_tags', '')
    only_contributions = request.GET.get('only_contributions', '') == 'true'

    profile = get_profile(request)

    _grants = None
    try:
        filters = {
            'request': request,
            'grant_types': grant_types,
            'sort': sort,
            'network': network,
            'keyword': keyword,
            'state': 'active',
            'grant_tags': grant_tags,
            'idle_grants': True,
            'only_contributions': only_contributions,
            'clr_round': clr_round
        }

        _grants = get_grants_by_filters(**filters)
    except Exception as e:
        print(e)
        return redirect('/grants')


    paginator = Paginator(_grants, limit)
    grants = paginator.get_page(page)

    # record view
    pks = list([grant.pk for grant in grants])
    if len(pks):
        increment_view_count.delay(pks, grants[0].content_type, request.user.id, 'index')

    # current_partners = MatchPledge.objects.filter(clr_round_num=clr_round)
    # current_partners_fund = 0

    # for partner in current_partners:
    #     current_partners_fund += partner.amount

    grant_types = get_grant_clr_types(clr_round, network=network)

    grants_following = Favorite.objects.none()
    collections = []
    if request.user.is_authenticated and request.user.profile:
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

    active_rounds = GrantCLR.objects.filter(is_active=True, start_date__lt=timezone.now(), end_date__gt=timezone.now()).order_by('-total_pot')

    params = {
        'active': 'grants_landing',
        'title': title,
        'sort': sort,
        'network': network,
        'keyword': keyword,
        'type': grant_types,
        'round_end': clr_rounds_metadata['round_end_date'],
        'next_round_start': clr_rounds_metadata['round_start_date'],
        'all_grants_count': _grants.count(),
        'now': timezone.now(),
        'grant_types': grant_types,
        'card_desc': f'{live_now}',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/default_grants.png')),
        'card_type': 'summary_large_image',
        'avatar_height': 675,
        'avatar_width': 1200,
        'grants': grants,
        'can_pin': False,# 'selected_category': category,
        'profile': profile,
        'grants_following': grants_following,
        'only_contributions': only_contributions,
        'clr_round': clr_round,
        'collections': collections,
        'grant_bg': get_branding_info(request),
        'active_rounds': active_rounds
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

    response = TemplateResponse(request, 'grants/explorer.html', params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


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
def grant_details_api(request, grant_id):
    """Json the Grant details."""
    grant = None
    try:
        grant = Grant.objects.get(pk=grant_id)
        grant_json = grant.repr(request.user, request.build_absolute_uri)
    except Exception as e:
        print(e)
        response = {
            'status': 500,
            'message': 'error: something went wrong while fetching grants clr'
        }
        return JsonResponse(response)

    response = {
        'status': 200,
        'grants': grant_json
    }
    return JsonResponse(response)


@csrf_exempt
def grant_details(request, grant_id, grant_slug):
    """Display the Grant details page."""
    tab = request.GET.get('tab')
    profile = get_profile(request)
    add_cancel_params = False

    try:
        grant = None
        try:
            grant = Grant.objects.prefetch_related('team_members').get(
                pk=grant_id, slug=grant_slug
            )
        except Grant.DoesNotExist:
            grant = Grant.objects.prefetch_related('team_members').get(
                pk=grant_id
            )

        if not grant.visible:
            raise Http404
        increment_view_count.delay([grant.pk], grant.content_type, request.user.id, 'individual')
        subscriptions = grant.subscriptions.none()
        cancelled_subscriptions = grant.subscriptions.none()

        activity_count = grant.contribution_count
        contributors = []
        contributions = []
        sybil_profiles = []

        # Sybil score
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
        # _contributions = Contribution.objects.filter(subscription__grant=grant, subscription__is_postive_vote=True).prefetch_related('subscription', 'subscription__contributor_profile')
        # contributions = list(_contributions.order_by('-created_on'))

        # # Contributors
        # if tab == 'contributors':
        #     phantom_funds = grant.phantom_funding.all().cache(timeout=60)
        #     contributors = list(_contributions.distinct('subscription__contributor_profile')) + list(phantom_funds.distinct('profile'))
        # activity_count = len(cancelled_subscriptions) + len(contributions)
        user_subscription = None
        user_non_errored_subscription = None
        add_cancel_params = user_subscription
    except Grant.DoesNotExist:
        raise Http404

    is_admin = (grant.admin_profile.id == profile.id) if profile and grant.admin_profile else False
    if is_admin:
        add_cancel_params = True

    is_team_member = is_grant_team_member(grant, profile)

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
    else:
        is_clr_active = False

    is_clr_active = True if clr_round else False
    title = grant.title + " | Grants"

    if is_clr_active:
        title = '💰 ' + title

    should_show_claim_match_button = False
    try:
        # If the user viewing the page is team member or admin, check if grant has match funds available
        # to withdraw

        is_match_available_to_claim = False
        is_within_payout_period_for_most_recent_round = timezone.now() < timezone.datetime(2022, 2, 1, 12, 0).replace(tzinfo=pytz.utc)
        is_staff = request.user.is_authenticated and request.user.is_staff

        # Check if this grant needs to complete KYC before claiming match funds
        clr_matches = grant.clr_matches.filter(round_number=settings.MATCH_PAYOUTS_ROUND_NUM)
        is_blocked_by_kyc = clr_matches.exists() and not clr_matches.first().ready_for_payout

        # calculate whether is available
        # TODO - do this asyncronously so as not to block the pageload
        amount_available = 0
        if is_within_payout_period_for_most_recent_round and not is_blocked_by_kyc and grant.admin_address != '0x0':
            if is_team_member or is_staff or is_admin:
                w3 = get_web3(grant.network)
                match_payouts_abi = settings.MATCH_PAYOUTS_ABI
                match_payouts_address = w3.toChecksumAddress(settings.MATCH_PAYOUTS_ADDRESS)
                match_payouts = w3.eth.contract(address=match_payouts_address, abi=match_payouts_abi)
                amount_available = match_payouts.functions.payouts(grant.admin_address).call()
                is_match_available_to_claim = True if amount_available > 0 else False

        # Determine if we should show the claim match button on the grant details page
        should_show_claim_match_button = grant.active and (is_team_member or is_staff or is_admin) and is_match_available_to_claim and not is_blocked_by_kyc

    except Exception as e:
        logger.exception(e)

    grant_tags = []
    for g_tag in GrantTag.objects.all():
        _grant_tag = {
            'id': g_tag.pk,
            'name': g_tag.name
        }
        grant_tags.append(_grant_tag)

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
        'user_subscription': user_subscription,
        'user_non_errored_subscription': user_non_errored_subscription,
        'is_admin': is_admin,
        'keywords': get_keywords(),
        'target': f'/activity?what={what}',
        'pinned': pinned,
        'what': what,
        'activity_count': activity_count,
        # 'contributors': contributors,
        'clr_active': is_clr_active,
        # 'round_num': grant.clr_round_num,
        'is_team_member': is_team_member,
        'is_owner': grant.admin_profile.pk == request.user.profile.pk if request.user.is_authenticated else False,
        'is_unsubscribed_from_updates_from_this_grant': is_unsubscribed_from_updates_from_this_grant,
        'options': [(f'Email Grant Funders ({grant.contributor_count})', 'bullhorn', 'Select this option to email your status update to all your funders.')] if is_team_member else [],
        'user_code': get_user_code(request.user.profile.id, grant, emoji_codes) if request.user.is_authenticated else '',
        'verification_tweet': get_grant_verification_text(grant),
        # 'tenants': grant.tenants,
        'should_show_claim_match_button': should_show_claim_match_button,
        'amount_to_claim': amount_available,
        'grant_tags': grant_tags
    }
    # Stats
    if tab == 'stats':
        import hashlib
        params['secret_id'] = hashlib.md5((settings.SECRET_KEY + str(grant.id)).encode('utf')).hexdigest()

    return TemplateResponse(request, 'grants/detail/_index.html', params)


@csrf_exempt
def grant_details_contributors(request, grant_id):
    page = int(request.GET.get('page', 1))
    network = request.GET.get('network', 'mainnet')
    limit = int(request.GET.get('limit', 30))

    try:
        grant = Grant.objects.prefetch_related('subscriptions').get(
            pk=grant_id
        )
    except Grant.DoesNotExist:
        response = {
            'message': 'error: grant cannot be found'
        }
        return JsonResponse(response)

    _contributors = set(Contribution.objects.filter(
        subscription__grant=grant,
        subscription__network=network,
        subscription__is_postive_vote=True,
        anonymous=False
    ).prefetch_related('subscription', 'profile_for_clr').values_list('profile_for_clr__handle', flat=True).order_by('-created_on'))

    contributors = list(_contributors)
    all_pages = Paginator(contributors, limit)
    this_page = all_pages.page(page)
    response = dict()
    all_contributors = []

    for contributor in this_page:
        contributor_json = {}
        contributor_json['user']=  contributor

        all_contributors.append(contributor_json)

    response['contributors'] = json.loads(json.dumps(all_contributors, default=str))
    response['has_next'] = all_pages.page(page).has_next()
    response['count'] = all_pages.count
    response['num_pages'] = all_pages.num_pages
    response['next_page_number'] = all_pages.page(page).next_page_number() if all_pages.page(page).has_next() else None

    return JsonResponse(response)


@csrf_exempt
def grant_details_contributions(request, grant_id):
    page = int(request.GET.get('page', 1))
    network = request.GET.get('network', 'mainnet')
    limit = int(request.GET.get('limit', 100))
    max_page_size = 300
    if limit > max_page_size:
        limit = max_page_size

    try:
        grant = Grant.objects.get(
            pk=grant_id
        )
    except Grant.DoesNotExist:
        response = {
            'message': 'error: grant cannot be found'
        }
        return JsonResponse(response)

    _contributions = Contribution.objects.filter(
        subscription__grant=grant,
    )

    contributions = _contributions.order_by('-created_on')
    # print(contributions)
    start_index = (page - 1) * limit
    end_index = (page) * limit
    this_page = contributions[start_index:end_index]
    response = dict()

    all_contributions = []
    for contribution in this_page:
        # print(contribution.subscription)
        # print(contribution.subscription.tx_id)
        subscription = contribution.subscription
        if not subscription.is_postive_vote:
            continue
        if subscription.network != network:
            continue

        contribution_json = {
            k: getattr(contribution, k) for k in
            ['id', 'success', 'tx_cleared', 'created_on', 'anonymous', 'tx_id']}

        contribution_json['subscription'] = {
            k: getattr(contribution.subscription, k) for k in
            ['id', 'contributor_profile', 'token_symbol', 'amount_per_period', 'amount_per_period_minus_gas_price', 'amount_per_period_usdt', 'amount_per_period_to_gitcoin', 'comments']}


        # contribution_json['subscription']
        contribution_json['subscription']['hide_wallet_address'] = contribution.subscription.contributor_profile.hide_wallet_address
        if (contribution.subscription.contributor_profile.hide_wallet_address):
            contribution_json['tx_id'] = None
        if (contribution.anonymous):
            contribution_json['subscription']['contributor_profile'] = None
        all_contributions.append(contribution_json)

    response['contributions'] = json.loads(json.dumps(all_contributions, default=str))
    response['next_page_number'] = page + 1 

    return JsonResponse(response)

@csrf_exempt
def grant_edit(request, grant_id):

    # profile = get_profile(request)
    profile = request.user.profile if hasattr(request.user, 'profile') else None
    grant = None

    try:
        grant = Grant.objects.prefetch_related('subscriptions','team_members').get(
            pk=grant_id
        )

    except Grant.DoesNotExist:
        raise Http404

    is_team_member = is_grant_team_member(grant, profile)
    if request.method == 'POST' and (is_team_member or request.user.is_staff):

        response = {
            'status': 400,
            'message': 'error: Bad Request. Unable to create grant'
        }

        # step 1: validate input

        user = request.user if request.user.is_authenticated else None
        if not user:
            response['message'] = 'error: user needs to be authenticated to create grant'
            return JsonResponse(response)

        if not profile:
            response['message'] = 'error: no matching profile found'
            return JsonResponse(response)

        title = request.POST.get('title', None)
        if not title:
            response['message'] = 'error: title is a mandatory parameter'
            return JsonResponse(response)

        description = request.POST.get('description', None)
        if not description:
            response['message'] = 'error: description is a mandatory parameter'
            return JsonResponse(response)

        has_external_funding = request.POST.get('has_external_funding', 'unknown')
        if has_external_funding == 'unknown':
            response['message'] = 'error: choose if grant has external funding or not'
            return JsonResponse(response)

        description_rich = request.POST.get('description_rich', None)
        if not description_rich:
            description_rich = description

        if grant.active:
            is_clr_eligible = json.loads(request.POST.get('is_clr_eligible', 'true'))
            grant.is_clr_eligible = is_clr_eligible

        eth_payout_address = request.POST.get('eth_payout_address', '0x0')
        zcash_payout_address = request.POST.get('zcash_payout_address', '0x0')
        celo_payout_address = request.POST.get('celo_payout_address', '0x0')
        zil_payout_address = request.POST.get('zil_payout_address', '0x0')
        polkadot_payout_address = request.POST.get('polkadot_payout_address', '0x0')
        harmony_payout_address = request.POST.get('harmony_payout_address', '0x0')
        kusama_payout_address = request.POST.get('kusama_payout_address', '0x0')
        binance_payout_address = request.POST.get('binance_payout_address', '0x0')
        rsk_payout_address = request.POST.get('rsk_payout_address', '0x0')
        algorand_payout_address = request.POST.get('algorand_payout_address', '0x0')

        if (
            eth_payout_address == '0x0' and
            zcash_payout_address == '0x0' and
            celo_payout_address == '0x0' and
            zil_payout_address == '0x0' and
            polkadot_payout_address == '0x0' and
            kusama_payout_address == '0x0' and
            harmony_payout_address == '0x0' and
            binance_payout_address == '0x0' and
            rsk_payout_address == '0x0' and
            algorand_payout_address == '0x0'
        ):
            response['message'] = 'error: payout_address is a mandatory parameter'
            return JsonResponse(response)

        if (
            zcash_payout_address != '0x0' and
            not zcash_payout_address.startswith('t')
        ):
            response['message'] = 'error: zcash_payout_address must be a transparent address'
            return JsonResponse(response)

        if eth_payout_address != '0x0':
            grant.admin_address = eth_payout_address

        if zcash_payout_address != '0x0':
            grant.zcash_payout_address = zcash_payout_address

        if celo_payout_address != '0x0':
            grant.celo_payout_address = celo_payout_address

        if zil_payout_address != '0x0':
            grant.zil_payout_address = zil_payout_address

        if polkadot_payout_address != '0x0':
            grant.polkadot_payout_address = polkadot_payout_address

        if kusama_payout_address != '0x0':
            grant.kusama_payout_address = kusama_payout_address

        if harmony_payout_address != '0x0':
            grant.harmony_payout_address = harmony_payout_address

        if binance_payout_address != '0x0':
            grant.binance_payout_address = binance_payout_address

        if rsk_payout_address != '0x0':
            grant.rsk_payout_address = rsk_payout_address

        if algorand_payout_address != '0x0':
            grant.algorand_payout_address = algorand_payout_address

        github_project_url = request.POST.get('github_project_url', None)
        if github_project_url:
            grant.github_project_url = github_project_url

        logo = request.FILES.get('logo', None)
        if logo:
            grant.logo = logo

        image_css = request.POST.get('image_css', None)
        if image_css:
            grant.image_css = image_css

        twitter_handle_1 = request.POST.get('handle1', '').strip('@')
        twitter_handle_2 = request.POST.get('handle2', '').strip('@')

        if twitter_handle_1 and not re.search(r'^@?[a-zA-Z0-9_]{1,15}$', twitter_handle_1):
            response['message'] = 'error: enter a valid project twitter handle e.g @humanfund'
            return JsonResponse(response)

        if twitter_handle_2 and not re.search(r'^@?[a-zA-Z0-9_]{1,15}$', twitter_handle_2):
            response['message'] = 'error: enter your twitter handle e.g @georgecostanza'
            return JsonResponse(response)

        if grant.twitter_handle_1 != twitter_handle_1:
            grant.twitter_verified = False
            grant.twitter_verified_by = None
            grant.twitter_verified_at = None
            grant.twitter_handle_1 = twitter_handle_1

        grant.twitter_handle_2 = twitter_handle_2

        reference_url = request.POST.get('reference_url', None)
        if reference_url:
            grant.reference_url = reference_url

        region = request.POST.get('region', None)
        if region:
            grant.region = region

        grant_tags = request.POST.get('grant_tags[]', None)
        if grant_tags:
            tags = [d['id'] for d in json.loads(grant_tags)]
            grant.tags.set(tags)


        team_members = request.POST.getlist('team_members[]', None)
        if team_members:
            save_team_members = []
            save_team_members = [d['id'] for d in json.loads(team_members[0])]
            save_team_members.append(grant.admin_profile.id)
            grant.team_members.set(save_team_members)

        grant.title = title
        grant.description = description
        grant.description_rich = description_rich
        grant.has_external_funding = has_external_funding
        grant.last_update = timezone.now()
        grant.hidden = False

        grant.save()

        record_grant_activity_helper('update_grant', grant, profile)

        response = {
            'status': 200,
            'success': True,
            'message': 'grant updated',
            'url': grant.url,
        }

        return JsonResponse(response)


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


@login_required
@transaction.atomic
def grant_new(request):
    """Handle new grant."""

    if request.method == 'POST':

        response = {
            'status': 400,
            'message': 'error: Bad Request. Unable to create grant'
        }

        # step 1: validate input

        user = request.user if request.user.is_authenticated else None
        if not user:
            response['message'] = 'error: user needs to be authenticated to create grant'
            return JsonResponse(response)

        profile = request.user.profile if hasattr(request.user, 'profile') else None
        if not profile:
            response['message'] = 'error: no matching profile found'
            return JsonResponse(response)

        grant_type = request.POST.get('grant_type', None)
        if not grant_type:
            response['message'] = 'error: grant_type is a mandatory parameter'
            return JsonResponse(response)

        title = request.POST.get('title', None)
        if not title:
            response['message'] = 'error: title is a mandatory parameter'
            return JsonResponse(response)

        description = request.POST.get('description', None)
        if not description:
            response['message'] = 'error: description is a mandatory parameter'
            return JsonResponse(response)

        description_rich = request.POST.get('description_rich', None)
        if not description_rich:
            description_rich = description

        has_external_funding = request.POST.get('has_external_funding', 'unknown')
        if has_external_funding == 'unknown':
            response['message'] = 'error: has_external_funding is a mandatory parameter'
            return JsonResponse(response)

        eth_payout_address = request.POST.get('eth_payout_address', request.POST.get('admin_address'))
        zcash_payout_address = request.POST.get('zcash_payout_address', None)
        celo_payout_address = request.POST.get('celo_payout_address', None)
        zil_payout_address = request.POST.get('zil_payout_address', None)
        polkadot_payout_address = request.POST.get('polkadot_payout_address', None)
        kusama_payout_address = request.POST.get('kusama_payout_address', None)
        harmony_payout_address = request.POST.get('harmony_payout_address', None)
        binance_payout_address = request.POST.get('binance_payout_address', None)
        rsk_payout_address = request.POST.get('rsk_payout_address', None)
        algorand_payout_address = request.POST.get('algorand_payout_address', None)

        if (
            not eth_payout_address and not zcash_payout_address and
            not celo_payout_address and not zil_payout_address and
            not polkadot_payout_address and not kusama_payout_address and
            not harmony_payout_address and not binance_payout_address and
            not rsk_payout_address and not algorand_payout_address
        ):
            response['message'] = 'error: payout_address is a mandatory parameter'
            return JsonResponse(response)

        if zcash_payout_address and not zcash_payout_address.startswith('t'):
            response['message'] = 'error: zcash_payout_address must be a transparent address'
            return JsonResponse(response)

        project_pk = request.POST.get('project_pk')
        if project_pk and project_pk != 'undefined':
            HackathonProject.objects.filter(pk=project_pk).update(grant_obj=grant)

        token_symbol = request.POST.get('token_symbol', 'Any Token')
        logo = request.FILES.get('logo', None)
        metdata = json.loads(request.POST.get('receipt', '{}'))
        team_members = request.POST.getlist('team_members[]')
        reference_url = request.POST.get('reference_url', '')
        github_project_url = request.POST.get('github_project_url', None)
        network = request.POST.get('network', 'mainnet')
        twitter_handle_1 = request.POST.get('handle1', '').strip('@')
        twitter_handle_2 = request.POST.get('handle2', '').strip('@')

        if twitter_handle_1 and not re.search(r'^[a-zA-Z0-9_]{1,15}$', twitter_handle_1):
            response['message'] = 'error: enter a valid project twitter handle e.g @humanfund'
            return JsonResponse(response)

        if twitter_handle_2 and not re.search(r'^[a-zA-Z0-9_]{1,15}$', twitter_handle_2):
            response['message'] = 'error: enter your twitter handle e.g @georgecostanza'
            return JsonResponse(response)

        # TODO: REMOVE
        contract_version = request.POST.get('contract_version', '2')

        grant_kwargs = {
            'title': title,
            'description': description,
            'description_rich': description_rich,
            'reference_url': reference_url,
            'github_project_url': github_project_url,
            'admin_address': eth_payout_address if eth_payout_address else '0x0',
            'zcash_payout_address': zcash_payout_address if zcash_payout_address else '0x0',
            'celo_payout_address': celo_payout_address if celo_payout_address else '0x0',
            'zil_payout_address': zil_payout_address if zil_payout_address else '0x0',
            'polkadot_payout_address': polkadot_payout_address if polkadot_payout_address else '0x0',
            'kusama_payout_address': kusama_payout_address if kusama_payout_address else '0x0',
            'harmony_payout_address': harmony_payout_address if harmony_payout_address else '0x0',
            'binance_payout_address': binance_payout_address if binance_payout_address else '0x0',
            'rsk_payout_address': rsk_payout_address if rsk_payout_address else '0x0',
            'algorand_payout_address': algorand_payout_address if algorand_payout_address else '0x0',
            'token_symbol': token_symbol,
            'contract_version': contract_version,
            'deploy_tx_id': request.POST.get('transaction_hash', '0x0'),
            'network': network,
            'twitter_handle_1': twitter_handle_1,
            'twitter_handle_2': twitter_handle_2,
            'metadata': metdata,
            'last_update': timezone.now(),
            'admin_profile': profile,
            'logo': logo,
            'hidden': True,
            'active': False,
            'is_clr_eligible': False,
            'region': request.POST.get('region', None),
            'clr_prediction_curve': [[0.0, 0.0, 0.0] for x in range(0, 6)],
            'grant_type': GrantType.objects.get(name=grant_type),
            'has_external_funding': has_external_funding
        }

        grant = Grant.objects.create(**grant_kwargs)

        hackathon_project_id = request.GET.get('related_hackathon_project_id')
        if hackathon_project_id:
            hackathon_project = HackathonProject.objects.filter(id=hackathon_project_id).first()
            if hackathon_project and hackathon_project.profiles.filter(pk=profile.id).exists():
                hackathon_project.grant_obj  = grant
                hackathon_project.save()

        team_members = (team_members[0].split(','))
        team_members.append(profile.id)
        team_members = list(set(team_members))

        team_members = [int(i) for i in team_members if i != '']

        grant.team_members.add(*team_members)

        tag_ids = request.POST.getlist('tags[]')
        tag_ids = (tag_ids[0].split(','))
        tag_ids = list(set(tag_ids))

        for tag_id in tag_ids:
            try:
                tag = GrantTag.objects.get(pk=tag_id)
                grant.tags.add(tag)
            except Exception as e:
                pass

        grant.save()
        grant.calc_clr_round()
        grant.save()

        messages.success(
            request,
            _('Thank you for posting this Grant. Our team reviews each grant before it goes live on the website. This process takes 1-2 business days.')
        )

        if grant.active:
            record_grant_activity_helper('new_grant', grant, profile)

        # send email to creator and admin
        process_grant_creation_email.delay(grant.pk, profile.pk)
        process_grant_creation_admin_email.delay(grant.pk)

         # record to notion for sybil-hunters
        process_notion_db_write.delay(grant.pk)

        response = {
            'status': 200,
            'success': True,
            'message': 'grant created',
            'url': grant.url,
        }

        return JsonResponse(response)


    profile = get_profile(request)

    grant_types = []
    for g_type in GrantType.objects.filter(is_active=True):
        grant_type_temp = {
            'id': g_type.pk,
            'name': g_type.name,
            'label': g_type.label,
        }
        if g_type.logo:
            grant_type_temp['image_url'] = request.build_absolute_uri(g_type.logo.url)

        grant_types.append(grant_type_temp)

    grant_tags = []
    for g_tag in GrantTag.objects.all():
        _grant_tag = {
            'id': g_tag.pk,
            'name': g_tag.name
        }
        grant_tags.append(_grant_tag)

    params = {
        'active': 'new_grant',
        'title': _('New Grant'),
        'card_desc': _('Provide sustainable funding for Open Source with Gitcoin Grants'),
        'profile': profile,
        'trusted_relayer': settings.GRANTS_OWNER_ACCOUNT,
        'grant_types': grant_types,
        'grant_tags': grant_tags
    }
    return TemplateResponse(request, 'grants/_new.html', params)


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


@csrf_exempt
@require_POST
def cancel_grant_v1(request, grant_id):

    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to contribute to grant'
    }


    user = request.user if request.user.is_authenticated else None
    if not user:
        response['message'] = 'error: user needs to be authenticated to cancel grant'
        return JsonResponse(response)

    profile = request.user.profile if hasattr(request.user, 'profile') else None

    if not profile:
        response['message'] = 'error: no matching profile found'
        return JsonResponse(response)

    if not request.method == 'POST':
        response['message'] = 'error: grant cancellation is a POST operation'
        return JsonResponse(response)

    try:
        grant = Grant.objects.get(pk=grant_id)
    except Grant.DoesNotExist:
        response['message'] = 'error: grant cannot be found'
        return JsonResponse(response)

    if not is_grant_team_member(grant, profile) and not request.user.is_staff:
        response['message'] = 'error: grant cancellation can be done only by grant owner'
        return JsonResponse(response)

    if not grant.active:
        response['message'] = 'error: grant is already cancelled'
        return JsonResponse(response)

    grant.active = False
    grant.save()

    grant_cancellation(grant)
    record_grant_activity_helper('killed_grant', grant, profile)

    response = {
        'status': 200,
        'pk': grant.pk,
        'message': 'grant cancelled successfully'
    }
    return JsonResponse(response)

@login_required
def bulk_fund(request):
    """Called when checking out with an Ethereum cart"""
    if request.method != 'POST':
        raise Http404

    # Get list of grant IDs
    grant_ids_list = [int(pk) for pk in request.POST.get('grant_id').split(',')]

    # For each grant, we validate the data. If it fails, save it off and throw error at the end
    successes = []
    failures = []

    profile = get_profile(request)
    grants_with_payload = []

    for (index, grant_id) in enumerate(grant_ids_list):
        try:
            grant = Grant.objects.get(pk=grant_id)
        except Grant.DoesNotExist:
            # Commonly occurs when testing on Rinkeby, as the Gitcoin development fund does not exist there by default
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Does Not Exist'),
                'grant':grant_id,
                'text': _('This grant does not exist'),
                'subtext': _('No grant with this ID was found'),
                'success': False
            })
            continue

        if not grant.active:
            # This means a grant has been cancelled, which happens occasionally
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Ended'),
                'grant':grant_id,
                'text': _('This Grant has ended.'),
                'subtext': _('Contributions can no longer be made this grant'),
                'success': False
            })
            continue

        if grant.link_to_new_grant:
            # Occurs if users have duplicate grants and one is merged into the other
            failures.append({
                'active': 'grant_error',
                'title': _('Fund - Grant Migrated'),
                'grant':grant_id,
                'text': _('This Grant has ended'),
                'subtext': _('Contributions can no longer be made to this grant. <br> Visit the new grant to contribute.'),
                'success': False
            })
            continue


        try:
            payload = {
                # Values that are constant for all donations
                'checkout_type': request.POST.get('checkout_type'),
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
                'visitorId': request.POST.get('visitorId'),
                'splitter_contract_address': request.POST.get('splitter_contract_address'),
                'subscription_hash': request.POST.get('subscription_hash'),
                'anonymize_gitcoin_grants_contributions': json.loads(request.POST.get('anonymize_gitcoin_grants_contributions', 'false')),
                # Values that vary by donation
                'admin_address': request.POST.get('admin_address').split(',')[index],
                'amount_per_period': request.POST.get('amount_per_period').split(',')[index],
                'confirmed': request.POST.get('confirmed').split(',')[index],
                'contract_address': request.POST.get('contract_address').split(',')[index],
                'contract_version': request.POST.get('contract_version').split(',')[index],
                'denomination': request.POST.get('denomination').split(',')[index],
                'gitcoin-grant-input-amount': request.POST.get('gitcoin-grant-input-amount').split(',')[index],
                'grant_id': request.POST.get('grant_id').split(',')[index],
                'split_tx_id': request.POST.get('split_tx_id').split(',')[index],
                'sub_new_approve_tx_id': request.POST.get('sub_new_approve_tx_id').split(',')[index],
                'token_address': request.POST.get('token_address').split(',')[index],
                'token_symbol': request.POST.get('token_symbol').split(',')[index],
                'include_for_clr': json.loads(request.POST.get('include_for_clr', 'true'))
            }
            grants_with_payload.append({
                'grant_id': grant_id,
                'grant_slug': grant.slug,
                'payload': payload
            })
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
            'grant': grant_id,
            'text': _('Funding for this grant was successfully processed and saved.'),
            'success': True
        })

    from grants.tasks import batch_process_grant_contributions
    batch_process_grant_contributions.delay(grants_with_payload, profile.pk)
    return JsonResponse({
        'success': True,
        'grant_ids': grant_ids_list,
        'successes': successes,
        'failures': failures
    })

@login_required
def manage_ethereum_cart_data(request):
    """
    For the specified user address:
      1. `action == save` will save the provided cart data as a JSON Store
      2. `action == delete` will removed saved cart data from the JSON Store
    """
    if request.method != 'POST':
        raise Http404

    user_address = request.POST.get('user_address')
    action = request.POST.get('action')

    if action == 'save':
        ethereum_cart_data = json.loads(request.POST.get('ethereum_cart_data'))
        try:
            # Look for existing entry, and if present we overwrite it. This can occur when a user starts
            # checkout, does not finish it, then comes back to checkout later
            entry = JSONStore.objects.get(key=user_address, view='ethereum_cart_data')
            entry.data = ethereum_cart_data
            entry.save()
            return JsonResponse({ 'success': True })
        except JSONStore.DoesNotExist:
            # No entry exists for this user, so create a new one
            JSONStore.objects.create(key=user_address, view='ethereum_cart_data', data=ethereum_cart_data)
            return JsonResponse({ 'success': True })

    elif action == 'delete':
        try:
            # Look for existing entry, and if present we delete it
            entry = JSONStore.objects.get(key=user_address, view='ethereum_cart_data')
            entry.delete()
            return JsonResponse({ 'success': True })
        except JSONStore.DoesNotExist:
            # No entry exists for this user, so we return false to indicate this
            return JsonResponse({ 'success': False })

    else:
        raise Exception('Invalid action specified')

@login_required
def get_ethereum_cart_data(request):
    """
    For the specified user address, returns the saved checkout data if found
    """
    if request.method != 'GET':
        raise Http404

    try:
        user_address = request.GET.get('user_address')
        result = JSONStore.objects.get(key=user_address, view='ethereum_cart_data')
        return JsonResponse({ 'success': True, 'ethereum_cart_data': result.data })
    except JSONStore.DoesNotExist:
        # If there's no entry for this user, return false to indicate this
        return JsonResponse({ 'success': False })

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


def grants_cart_view(request):
    context = {
        'title': 'Grants Cart',
        'EMAIL_ACCOUNT_VALIDATION': EMAIL_ACCOUNT_VALIDATION,
    }
    if request.user.is_authenticated:
        profile = request.user.profile
        context['username'] = profile.username
        context['trust_bonus'] = round(request.user.profile.trust_bonus * 100)

        is_brightid_verified = ( 'verified' == get_brightid_status(profile.brightid_uuid) )

        context['is_fully_verified'] = (is_brightid_verified and profile.sms_verification and \
                                            profile.is_poap_verified and profile.is_twitter_verified and \
                                            profile.is_google_verified and profile.is_poh_verified)
    else:
        return redirect('/login/github/?next=' + request.get_full_path())

    response = TemplateResponse(request, 'grants/cart-vue.html', context=context)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def get_category_size(grant_type, category):
    key = f"grant_category_{grant_type.get('keyword')}_{category}"
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
    grant_ids = []

    for ele in grants_data:
        # new format will support amount and token in the URL separated by ;
        grant_data = ele.split(';')
        if len(grant_data) > 0 and grant_data[0].isnumeric():
            grant_id = grant_data[0]
            grants[grant_id] = {
                'id': int(grant_id)
            }
            grant_ids.append(grant_id)

            if len(grant_data) == 3:  # backward compatibility
                grants[grant_id]['amount'] = grant_data[1]
                grants[grant_id]['token'] = FTokens.objects.filter(id=int(grant_data[2])).first()

    by_whom = ""
    prefix = ""
    handle = ''
    try:
        handle = f"{grant_str.split(':')[1]}"
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

    grant_ids = ",".join([str(ele) for ele in grant_ids])
    avatar_url = f'https://gitcoin.co/dynamic/grants_cart_thumb/{handle}/{grant_ids}'
    context = {
        'grants': grants,
        'avatar_url': avatar_url,
        'avatar_height': 875,
        'avatar_width': 1740,
        'title': title,
        'card_desc': "Click to Add All to Cart: " + grant_titles

    }
    response = TemplateResponse(request, 'grants/bulk_add_to_cart.html', context=context)
    return response


@login_required
def profile(request):
    """Show grants profile of logged in user."""
    if not request.user.is_authenticated or not request.user.profile:
        raise Http404
    handle = request.user.profile.handle
    return redirect(f'/profile/{handle}/grants')


def quickstart(request):
    """Display quickstart guide."""
    params = {
        'active': 'grants_quickstart',
        'title': _('Quickstart'),
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/default_grants.png')),
    }
    return TemplateResponse(request, 'grants/quickstart.html', params)


def leaderboard(request):
    """Display leaderboard."""

    return redirect ('https://gitcoin.co/leaderboard/payers?cadence=quarterly&keyword=all&product=grants')


def record_subscription_activity_helper(activity_type, subscription, profile, anonymize=False):
    """Registers a new activity concerning a grant subscription

    Args:
        activity_type (str): The type of activity, as defined in dashboard.models.Activity.
        subscription (grants.models.Subscription): The subscription in question.
        profile (dashboard.models.Profile): The current user's profile.

    """
    if anonymize:
        profile = Profile.objects.filter(handle='gitcoinbot').first()
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
        'anonymize': anonymize,
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


@login_required
def new_matching_partner(request):

    grant_collections = []
    for g_collection in GrantCollection.objects.filter(hidden=False):
        grant_collections.append({
            'id': g_collection.pk,
            'name': g_collection.title,
        })

    grant_types = []
    for g_type in GrantType.objects.filter(is_active=True):
        grant_types.append({
            'id': g_type.pk,
            'name': g_type.label,
        })

    grant_tags = []
    for tag in GrantTag.objects.all():
        grant_tags.append({
            'id': tag.pk,
            'name': tag.name
        })

    params = {
        'title': 'Pledge your support.',
        'card_desc': f'Thank you for your interest in supporting public goods.on Gitcoin. Complete the form below to get started.',
        'grant_types': grant_types,
        'grant_tags': grant_tags,
        'grant_collections': grant_collections
    }

    return TemplateResponse(request, 'grants/new_match.html', params)


def create_matching_pledge_v1(request):

    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to create pledge'
    }

    user = request.user if request.user.is_authenticated else None
    if not user:
        response['message'] = 'error: user needs to be authenticated to create a pledge'
        return JsonResponse(response)

    profile = request.user.profile if hasattr(request.user, 'profile') else None

    if not profile:
        response['message'] = 'error: no matching profile found'
        return JsonResponse(response)

    if not request.method == 'POST':
        response['message'] = 'error: pledge creation is a POST operation'
        return JsonResponse(response)

    grant_types = request.POST.get('grant_types[]', None)
    grant_tags = request.POST.get('grant_tags[]', None)
    grant_collections = request.POST.get('grant_collections[]', None)

    if grant_types:
        grant_types = grant_types.split(',')
    if grant_tags:
        grant_tags = grant_tags.split(',')
    if grant_collections:
        grant_collections = grant_collections.split(',')

    if not grant_types and not grant_collections:
        response['message'] = 'error:  grant_types / grant_collections is parameter'
        return JsonResponse(response)

    matching_pledge_stage = request.POST.get('matching_pledge_stage', None)
    tx_id = request.POST.get('tx_id', None)
    if matching_pledge_stage == 'ready' and not tx_id:
        response['message'] = 'error: tx_id is a mandatory parameter'
        return JsonResponse(response)

    amount = request.POST.get('amount', False)

    if tx_id:
        # TODO
        collection_filters = None
        grant_filters = None

        if grant_types:
            grant_filters = {
                'grant_type__in': grant_types
            }
            if grant_tags:
                grant_filters['tags__in'] = grant_tags

        if grant_collections:
            collection_filters = {
                'pk__in': grant_collections
            }

        clr_round = GrantCLR.objects.create(
            round_num=0,
            sub_round_slug='pledge',
            start_date=timezone.now(),
            end_date=timezone.now(),
            total_pot=amount,
            grant_filters=grant_filters if grant_filters else {},
            collection_filters=collection_filters if collection_filters else {}
        )
        clr_round.save()


    end_date = timezone.now() + timezone.timedelta(days=7*3)
    match_pledge = MatchPledge.objects.create(
        profile=profile,
        active=False,
        end_date=end_date,
        amount=amount,
        data=json.dumps(request.POST.dict()),
        clr_round_num= clr_round if tx_id else None
    )

    match_pledge.save()

    response = {
        'status': 200,
        'message': 'success: match pledge created'
    }
    return JsonResponse(response)


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
def grants_info(request):
    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to fetch grant clr'
    }

    pks = request.GET.get('pks', None)
    slim = request.GET.get('slim', False)

    if not pks:
        response['message'] = 'error: missing parameter pks'
        return JsonResponse(response)

    grants = []

    try:
        for grant in Grant.objects.filter(pk__in=pks.split(',')):
            if slim:
                grants.append(grant.cart_payload(request.build_absolute_uri, request.user))
            else:
                grants.append(grant.repr(request.user, request.build_absolute_uri))
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
    from django.utils.safestring import mark_safe

    msg = f'I am verifying my ownership of { grant.title } on Gitcoin Grants'
    if long:
        msg += f' at https://gitcoin.co{grant.get_absolute_url()}.'

    return mark_safe(msg)


@login_required
def verify_grant(request, grant_id):
    try:
        grant = Grant.objects.get(pk=grant_id)
    except Grant.DoesNotExist:
        return JsonResponse({
            'ok': False,
            'msg': 'Invalid Gant.'
        })

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
    grants_complete = request.POST.get('grantsComplete')
    profile = request.user.profile
    grant_ids = [int(grant_id) for grant_id in grant_ids]

    if collection_id:
        collection = GrantCollection.objects.filter(
            Q(profile=request.user.profile) | Q(curators=request.user.profile)
        ).get(pk=collection_id)

        if collection:
            collection.title = title
            collection.description = description

            if not grants_complete:
                grant_ids = grant_ids + list(collection.grants.all().values_list('id', flat=True))
    else:
        kwargs = {
            'title': title,
            'description': description,
            'profile': profile,
        }
        collection = GrantCollection.objects.create(**kwargs)

    if request.user.profile.id == collection.profile.id or request.user.profile.id in collection.curators.all().values_list('id', flat=True):
        collection.grants.set(grant_ids)
        collection.generate_cache()
        collection.save()

        return JsonResponse({
            'ok': True,
            'collection': {
                'id': collection.id,
                'title': title,
                'description': description,
                'grant_ids': json.dumps(grant_ids)
            }
        })


    return JsonResponse({
        'ok': False,
        'msg': 'Auth error'
    }, status=500)


@login_required
@require_POST
def delete_collection(request):
    collection_id = request.POST.get('collection')
    profile = request.user.profile

    if collection_id:
        collection = GrantCollection.objects.filter(
            Q(profile=request.user.profile) | Q(curators=request.user.profile)
        ).get(pk=int(collection_id))

        if collection:
            collection.delete()

            return JsonResponse({
                'ok': True
            })

    return JsonResponse({
        'ok': False,
        'msg': 'Auth error'
    }, status=500)


def get_collection(request, collection_id):
    collection = GrantCollection.objects.get(pk=collection_id)

    grants = [grant.cart_payload(request.build_absolute_uri) for grant in collection.grants.order_by('-clr_prediction_curve__0__1')]
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
        'description': collection.description,
        'cover': collection.cover.url if collection.cover else '',
        'grants': grants,
        'owner': owner,
        'curators': curators + [owner],
        'grant_ids': json.dumps([ grant.id for grant in collection.grants.all() ])
    })


def get_grant_payload(request, grant_id):
    grant = Grant.objects.get(pk=grant_id)

    return JsonResponse({
        'grant': grant.cart_payload(request.build_absolute_uri),
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

des_urls = '''
https://c.gitcoin.co/grants/585d392a242103745b40d0e763ef5c17/Screen_Shot_2020-01-08_at_16.58.17.png
https://c.gitcoin.co/grants/b6511284c11682532274e0a34342249f/bitcoinmalaysia.png
https://c.gitcoin.co/grants/e1cf1b8778f29c49dff65ed3be4928d0/CheeseLogo_250px.png
https://c.gitcoin.co/grants/3ecf3eb0214a58fc3b068fae9f45ffbe/BANKLESS_logo_text_noLV.jpg
https://c.gitcoin.co/grants/f1c27815bc10332bff4a6264ae971fca/2.jpg
https://c.gitcoin.co/grants/46305a72ce062b63a53b0ebe12becda7/Picture1.png
https://c.gitcoin.co/grants/5d05dcc46be53030475cdbdf646b8afd/Mol_LeArt_-_White.png
https://c.gitcoin.co/grants/6ae1a8d3a8752d352247615b877cd02d/contraktor.png
https://c.gitcoin.co/grants/ce84fcbf185bd593e54f5c810d060aac/triad_gw_2.jpg
https://c.gitcoin.co/grants/b8fcf1833fee32fc4be6fba254c1d912/cashu.png
'''

def get_urls(scale):
    import random
    global des_urls
    urls = des_urls.split("\n")

    return_me = []
    scale_by = scale
    # set default, for when no CLR match enabled
    for grant in Grant.objects.filter(is_clr_active=True).order_by('-clr_prediction_curve__0__1'):
        url = None
        if grant.logo:
            url = grant.logo.url
            if settings.DEBUG:
                url = urls[random.randint(0, len(urls) - 2)]
        else:
            url = f'https://gitcoin.co/static/v2/images/grants/logos/{grant.id % 3}.png'
        size = scale_by * math.sqrt(math.sqrt(grant.clr_match_estimate_this_round))
        return_me.append((url, size))
    return return_me


@staff_member_required
def collage(request):
    scale = float(request.GET.get('scale', 0.03))
    context = {
        'urls': get_urls(scale)
    }

    response = TemplateResponse(request, 'grants/collage.html', context=context)
    return response


@cache_page(60 * 60)
def cart_thumbnail(request, profile, grants):
    width = int(request.GET.get('w', 348 * 5))
    height = int(request.GET.get('h', 175 * 5))
    grant_ids = grants.split(",")
    grant_ids = [ele for ele in grant_ids if ele]
    grants = Grant.objects.filter(pk__in=grant_ids).order_by('-amount_received_in_round')[:4]
    profile = Profile.objects.get(handle=profile.lower())
    thumbnail = generate_img_thumbnail_helper(grants, profile, width, height)

    response = HttpResponse(content_type="image/png")
    thumbnail.save(response, "PNG")

    return response

@login_required
@staff_member_required
def collection_thumbnail(request, collection_id):
    width = int(request.GET.get('w', 600))
    height = int(request.GET.get('h', 400))
    collection = GrantCollection.objects.get(pk=collection_id)
    thumbnail = generate_collection_thumbnail(collection, width, height)

    response = HttpResponse(content_type="image/png")
    thumbnail.save(response, "PNG")

    return response


@csrf_exempt
@require_POST
def contribute_to_grants_v1(request):

    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to contribute to grant'
    }

    # step 1: validate input

    user = request.user if request.user.is_authenticated else None
    if not user:
        response['message'] = 'error: user needs to be authenticated to contribute to grant'
        return JsonResponse(response)

    profile = request.user.profile if hasattr(request.user, 'profile') else None

    # profile = Profile.objects.get(pk=64423)

    if not profile:
        response['message'] = 'error: no matching profile found'
        return JsonResponse(response)

    if not request.method == 'POST':
        response['message'] = 'error: contribution to a grant is a POST operation'
        return JsonResponse(response)

    request_body = json.loads(request.body.decode("utf-8"))

    contributions = request_body.get('contributions', None)
    if not contributions:
        response['message'] = 'error: contributions in a mandatory parameter'
        return JsonResponse(response)


    failed_contributions = []
    invalid_contributions = []
    success_contributions = []

    for contribution in contributions:

        grant_id = contribution.get('grant_id', None)
        if not grant_id:
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: grant_id is mandatory param',
            })
            continue

        try:
            grant = Grant.objects.get(pk=grant_id)
        except Grant.DoesNotExist:
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: invalid grant'
            })
            continue

        if grant.link_to_new_grant or not grant.active:
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: grant is no longer active'
            })
            continue

        # if is_grant_team_member(grant, profile):
        #     invalid_contributions.append({
        #         'grant_id': grant_id,
        #         'message': 'error: team members cannot contribute to own grant'
        #     })
        #     continue

        contributor_address = contribution.get('contributor_address', '0x0')
        tx_id = contribution.get('tx_id', '0x0')

        if contributor_address == '0x0' and tx_id == '0x0':
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: either contributor_address or tx_id must be supplied'
            })
            continue

        token_symbol = contribution.get('token_symbol', None)
        if not token_symbol:
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: token_symbol is mandatory param'
            })
            continue

        amount_per_period = contribution.get('amount_per_period', None)
        if not amount_per_period:
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: amount_per_period is mandatory param'
            })
            continue

        tenant = contribution.get('tenant', None)
        if not tenant:
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: tenant is mandatory param'
            })
            continue

        if not tenant in grant_tenants:
            invalid_contributions.append({
                'grant_id': grant_id,
                'message': 'error: tenant chain is not supported for grant'
            })
            continue

        comment = contribution.get('comment', '')
        network = grant.network
        hide_wallet_address = contribution.get('hide_wallet_address', None)

        try:

            # step 2 : create 1 time subscription
            subscription = Subscription()
            subscription.contributor_address = contributor_address
            subscription.amount_per_period = amount_per_period
            subscription.token_symbol = token_symbol
            subscription.contributor_profile = profile
            subscription.grant = grant
            subscription.comments = comment
            subscription.network = network
            subscription.tenant = tenant
            # recurring payments set to none
            subscription.active = False
            subscription.real_period_seconds = 0
            subscription.frequency = 1
            subscription.frequency_unit ='days'
            subscription.token_address = ''
            subscription.gas_price = 0
            subscription.new_approve_tx_id = ''
            subscription.split_tx_id = ''

            subscription.error = True # cancel subs so it doesnt try to bill again
            subscription.subminer_comments = "skipping subminer as subscriptions aren't supported for this flow"

            subscription.save()

            # step 3: create contribution + fire celery
            contribution = subscription.create_contribution(tx_id, is_successful_contribution=True)
            contribution.success = True
            contribution.save()
            sync_payout(contribution)
            update_grant_metadata.delay(grant.pk)


            # step 4 : other tasks
            if hide_wallet_address and not profile.hide_wallet_address:
                profile.hide_wallet_address = hide_wallet_address
                profile.save()

            success_contributions.append({
                'grant_id': grant_id,
                'message': 'grant contributions recorded'
            })

        except Exception as error:
            failed_contributions.append({
                'grant_id': grant_id,
                'message': f'grant contribution not recorded',
                'error': error
            })

    if len(failed_contributions):
        response = {
            'status': 500,
            'success_contributions': success_contributions,
            'invalid_contributions': invalid_contributions,
            'failed_contributions': failed_contributions
        }
    elif len(invalid_contributions):
        response = {
            'status': 400,
            'success_contributions': success_contributions,
            'invalid_contributions': invalid_contributions,
            'failed_contributions': failed_contributions
        }
    else:
        response = {
            'status': 204,
            'success_contributions': success_contributions,
            'message': 'grant contributions recorded'
        }
    return JsonResponse(response)

@login_required
def ingest_contributions_view(request):
    context = {
        'title': 'Add missing contributions',
        'EMAIL_ACCOUNT_VALIDATION': EMAIL_ACCOUNT_VALIDATION
    }

    response = TemplateResponse(request, 'grants/ingest-contributions.html', context=context)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response

@login_required
def ingest_contributions(request):
    """Ingest missing contributions"""
    if request.method != 'POST':
        raise Http404

    profile = request.user.profile
    txHash = request.POST.get('txHash')
    userAddress = request.POST.get('userAddress')
    signature = request.POST.get('signature')
    message = request.POST.get('message')
    network = request.POST.get('network')
    ingestion_types = [] # after each series of ingestion, we append the ingestion_method to this array
    handle = request.POST.get('handle')

    if (profile.is_staff and
        ( not handle or Profile.objects.filter(handle=handle).count() == 0)
    ):
            return JsonResponse({ 'success': False, 'message': 'Profile could not be found' })

    # Setup web3
    w3 = get_web3(network)

    def get_profile(profile):
        """
        If a staff called this endpoint, we use the username passed with the payload. Otherwise, we use the
        caller's profile
        """
        return Profile.objects.filter(handle=request.POST.get('handle')).first() if profile.is_staff else profile

    def verify_signature(signature, message, expected_address):
        """
        Used to verify that the user ingesting actually owns the address they are ingesting for. This
        may not work for contract wallets or wallets that use relayers, so those will need to be ingested by staff
        to bypass this check
        """
        if profile.is_staff:
            return # Skip signature verification for staff so staff can ingest contributions on behalf of a user
        message_hash = defunct_hash_message(text=message)
        recovered_address = w3.eth.account.recoverHash(message_hash, signature=signature)
        if recovered_address.lower() != expected_address.lower():
            raise Exception("Signature could not be verified")

    try:
        if txHash != '':
            receipt = w3.eth.getTransactionReceipt(txHash)
            from_address = receipt['from']
            verify_signature(signature, message, from_address)
        if userAddress != '':
            verify_signature(signature, message, userAddress)
    except:
        return JsonResponse({ 'success': False, 'message': 'Signature could not be verified' })

    def get_token(w3, network, address):
        if (address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'):
            # 0xEeee... is used to represent ETH in the BulkCheckout contract
            address = '0x0000000000000000000000000000000000000000'
        try:
            # First try checksum
            address_checksum = w3.toChecksumAddress(address)
            return FTokens.objects.filter(network=network, address=address_checksum, approved=True).first().to_dict
        except AttributeError as e:
            address_lowercase = address.lower()
            return FTokens.objects.filter(network=network, address=address_lowercase, approved=True).first().to_dict

    def save_data(profile, txid, network, created_on, symbol, value_adjusted, grant, checkout_type, from_address):
        """
        Creates contribution and subscription and saves it to database if no matching one exists
        """
        currency = symbol
        amount = value_adjusted
        usd_val = amount * convert_token_to_usdt(symbol)

        # Check that subscription with these parameters does not exist
        existing_subscriptions = Subscription.objects.filter(
            grant__pk=grant.pk, contributor_profile=profile, split_tx_id=txid, token_symbol=currency
        )
        for existing_subscription in existing_subscriptions:
            tolerance = 0.01  # 1% tolerance to account for floating point
            amount_max = amount * (1 + tolerance)
            amount_min = amount * (1 - tolerance)

            if (
                existing_subscription.amount_per_period_minus_gas_price > amount_min
                and existing_subscription.amount_per_period_minus_gas_price < amount_max
            ):
                # Subscription exists
                logger.info("Subscription exists, exiting function\n")
                return

        # No subscription found, so create subscription and contribution
        try:
            # create objects
            validator_comment = f"created by ingest grant txn script"
            subscription = Subscription()
            subscription.is_postive_vote = True
            subscription.active = False
            subscription.error = True
            subscription.contributor_address = Web3.toChecksumAddress(from_address)
            subscription.amount_per_period = amount
            subscription.real_period_seconds = 2592000
            subscription.frequency = 30
            subscription.frequency_unit = "N/A"
            subscription.token_address = "0x0"
            subscription.token_symbol = currency
            subscription.gas_price = 0
            subscription.new_approve_tx_id = "0x0"
            subscription.num_tx_approved = 1
            subscription.network = network
            subscription.contributor_profile = profile
            subscription.grant = grant
            subscription.comments = validator_comment
            subscription.amount_per_period_usdt = usd_val
            subscription.created_on = created_on
            subscription.last_contribution_date = created_on
            subscription.next_contribution_date = created_on
            subscription.split_tx_id = txid
            subscription.save()

            # Create contribution and set the contribution as successful
            contrib = subscription.successful_contribution(
                '0x0', # subscription.new_approve_tx_id,
                True, # include_for_clr
                checkout_type=checkout_type
            )
            contrib.success=True
            contrib.tx_cleared=True
            contrib.tx_override=True
            contrib.validator_comment = validator_comment
            contrib.created_on = created_on
            contrib.save()
            logger.info(f"ingested {subscription.pk} / {contrib.pk}")

            metadata = {
                "id": subscription.id,
                "value_in_token": str(subscription.amount_per_period),
                "value_in_usdt_now": str(round(subscription.amount_per_period_usdt, 2)),
                "token_name": subscription.token_symbol,
                "title": subscription.grant.title,
                "grant_url": subscription.grant.url,
                "num_tx_approved": subscription.num_tx_approved,
                "category": "grant",
            }
            kwargs = {
                "profile": profile,
                "subscription": subscription,
                "grant": subscription.grant,
                "activity_type": "new_grant_contribution",
                "metadata": metadata,
            }

            Activity.objects.create(**kwargs)
            logger.info("Saved!\n")

        except Exception as e:
            logger.exception(e)
            logger.info("\n")

    def process_bulk_checkout_tx(w3, txid, profile, network, do_write):
        # Make sure tx was successful
        receipt = w3.eth.getTransactionReceipt(txid)
        from_address = receipt['from'] # this means wallets like Argent that use relayers will have the wrong from address
        if receipt.status == 0:
            raise Exception("Transaction was not successful")

        # Parse tx logs
        bulk_checkout_contract = w3.eth.contract(address=settings.BULK_CHECKOUT_ADDRESS, abi=settings.BULK_CHECKOUT_ABI)
        parsed_logs = bulk_checkout_contract.events.DonationSent().processReceipt(receipt)

        # Return if no donation logs were found
        if len(parsed_logs) == 0:
            raise Exception("No DonationSent events weren found in this transaction")

        # Get transaction timestamp
        block_info = w3.eth.getBlock(receipt['blockNumber'])
        created_on = pytz.UTC.localize(datetime.fromtimestamp(block_info['timestamp']))

        # For each event in the parsed logs, create the DB objects
        for (index,event) in enumerate(parsed_logs):
            logger.info(f'\nProcessing {index + 1} of {len(parsed_logs)}...')
            # Extract contribution parameters from events
            token_address = event["args"]["token"]
            value = event["args"]["amount"]
            token = get_token(w3, network, token_address)
            decimals = token["decimals"]
            symbol = token["name"]
            value_adjusted = int(value) / 10 ** int(decimals)
            to = event["args"]["dest"]

            # Find the grant
            try:
                grant = (
                    Grant.objects.filter(admin_address__iexact=to)
                    .order_by("-positive_round_contributor_count")
                    .first()
                )
                logger.info(f"{value_adjusted}{symbol}  => {to}, {grant} ")
            except Exception as e:
                logger.exception(e)
                logger.warning(f"{value_adjusted}{symbol}  => {to}, Unknown Grant ")
                logger.warning("Skipping unknown grant\n")
                continue

            if do_write:
                save_data(profile, txid, network, created_on, symbol, value_adjusted, grant, 'eth_std', from_address)
        return

    def handle_ingestion(profile, network, identifier, do_write):
        # Determine how to process the contributions
        if len(identifier) == 42:
            # An address was provided, so we'll use the zkSync API to fetch their transactions
            ingestion_method = 'zksync_api'
        elif len(identifier) == 66:
            # A transaction hash was provided, so we look for BulkCheckout logs in the L1 transaction
            ingestion_method = 'bulk_checkout'
        else:
            raise Exception('Invalid identifier')

        # Setup web3 and get user profile
        PROVIDER = f"wss://{network}.infura.io/ws/v3/{settings.INFURA_V3_PROJECT_ID}"
        w3 = Web3(Web3.WebsocketProvider(PROVIDER))

        # Handle ingestion
        if ingestion_method == 'bulk_checkout':
            # We were provided an L1 transaction hash, so process it
            txid = identifier
            process_bulk_checkout_tx(w3, txid, profile, network, True)

        elif ingestion_method == 'zksync_api':
            # Get history of transfers from this user's zkSync address using the zkSync API: https://zksync.io/api/v0.1.html#account-history
            user_address = identifier
            base_url = 'https://rinkeby-api.zksync.io/api/v0.1' if network == 'rinkeby' else 'https://api.zksync.io/api/v0.1'
            r = requests.get(f"{base_url}/account/{user_address}/history/older_than") # gets last 100 zkSync transactions
            r.raise_for_status()
            transactions = r.json()  # array of zkSync transactions

            # Paginate if required. API returns last 100 transactions by default, so paginate if response length was 100
            if len(transactions) == 100:
                max_length = 500 # only paginate until a max of most recent 500 transactions or no transaction are left
                last_tx_id = transactions[-1]["tx_id"]
                while len(transactions) < max_length:
                    r = requests.get(f"{base_url}/account/{user_address}/history/older_than?tx_id={last_tx_id}") # gets next 100 zkSync transactions
                    r.raise_for_status()
                    new_transactions = r.json()
                    if (len(new_transactions) == 0):
                        break
                    transactions.extend(new_transactions) # append to array
                    last_tx_id = transactions[-1]["tx_id"]

            for transaction in transactions:
                # Skip if this is not a transfer (can be Deposit, ChangePubKey, etc.)
                if transaction["tx"]["type"] != "Transfer":
                    continue

                # Extract contribution parameters from the JSON
                symbol = transaction["tx"]["token"]
                value = transaction["tx"]["amount"]
                token = FTokens.objects.filter(network=network, symbol=transaction["tx"]["token"], approved=True).first().to_dict
                decimals = token["decimals"]
                symbol = token["name"]
                value_adjusted = int(value) / 10 ** int(decimals)
                to = transaction["tx"]["to"]

                # Find the grant
                try:
                    grant = Grant.objects.filter(admin_address__iexact=to).order_by("-positive_round_contributor_count").first()
                    if not grant:
                        logger.warning(f"{value_adjusted}{symbol}  => {to}, Unknown Grant ")
                        logger.warning("Skipping unknown grant\n")
                        continue
                    logger.info(f"{value_adjusted}{symbol}  => {to}, {grant} ")
                except Exception as e:
                    logger.exception(e)
                    logger.warning(f"{value_adjusted}{symbol}  => {to}, Unknown Grant ")
                    logger.warning("Skipping unknown grant\n")
                    continue

                if do_write:
                    txid = transaction['hash']
                    created_on = dateutil.parser.parse(transaction['created_at'])
                    save_data(profile, txid, network, created_on, symbol, value_adjusted, grant, 'eth_zksync', user_address)

    try:
        if txHash != '':
            handle_ingestion(get_profile(profile), network, txHash, True)
            ingestion_types.append('L1')
        if userAddress != '':
            handle_ingestion(get_profile(profile), network, userAddress, True)
            ingestion_types.append('L2')
    except Exception as err:
        return JsonResponse({ 'success': False, 'message': err })

    return JsonResponse({ 'success': True, 'ingestion_types': ingestion_types })



def get_clr_sybil_input(request, round_id):
    '''
        This returns a paginated JSON response to return contributions
        which are considered while calculating the QF match for a given CLR
    '''
    token = request.headers['token']
    page = request.GET.get('page', 1)

    data = StaticJsonEnv.objects.get(key='BSCI_SYBIL_TOKEN').data

    if not round_id or not token or not data['token']:
        return HttpResponseBadRequest("error: missing arguments")

    if token != data['token']:
        return HttpResponseBadRequest("error: invalid token")

    clr = GrantCLR.objects.filter(pk=round_id).first()
    if not clr:
        return HttpResponseBadRequest("error: round not found")

    try:
        limit = data['limit'] if data['limit'] else 100

        # fetch grant contributions needed for round
        all_clr_contributions = fetch_contributions(clr)
        total_count = all_clr_contributions.count()

        # extract only needed fields
        all_clr_contributions = list(all_clr_contributions.values(
            'created_on', 'profile_for_clr__handle', 'profile_for_clr_id',
            'match', 'normalized_data'
        ))

        # paginate contributions
        contributions = Paginator(all_clr_contributions, limit)
        try:
            contributions_queryset = contributions.page(page)
        except EmptyPage:
            response = {
                'metadata': {
                    'count': 0,
                    'current_page': 0,
                    'num_pages': 0,
                    'has_next': False
                },
                'contributions': []
            }
            return HttpResponse(response)

        response = {
            'metadata': {
                'count': total_count,
                'current_page': page,
                'total_pages': contributions.num_pages,
                'has_next': contributions_queryset.has_next()
            },
            'contributions': contributions_queryset.object_list
        }

    except Exception as e:
        print(e)
        return HttpResponseServerError()

    return JsonResponse(response)


@csrf_exempt
def get_trust_bonus(request):
    '''
        JSON POST/GET endpoint which returns the trust bonus score of given addresses
    '''

    addresses = request.GET.get('addresses')
    if addresses:
        addresses = addresses.split(',')
    else:
        try:
            json_body = json.loads(request.body)
            addresses = json_body.get('addresses')
            if not addresses:
                return allow_all_origins(HttpResponse(status=204))
        except:
            return allow_all_origins(HttpResponse(status=400))

    query = Q()
    for address in addresses:
        query |= Q(contributor_address=address)

    subscriptions = Subscription.objects.filter(query).prefetch_related('contributor_profile')
    response = []
    _addrs = []
    for subscription in subscriptions:
        if subscription.contributor_address not in _addrs:
            response.append({
                'address': subscription.contributor_address,
                'score': subscription.contributor_profile.trust_bonus
            })
            _addrs.append(subscription.contributor_address)

    return allow_all_origins(JsonResponse(response, safe=False))



def api_toggle_user_sybil(request):
    '''
        POST endpoint which allows to mark a list of users as sybil
        or remove them the sybil tag from them.
        This is intended to be used by BSCI to ensure they can toggle it
        every 12 hours based on their findings as opposed to having it done
        at the end.
    '''

    json_body = json.loads(request.body)

    token = request.headers['token']
    sybil_users = json_body.get('sybil_users')
    non_sybil_users = json_body.get('non_sybil_users')

    data = StaticJsonEnv.objects.get(key='BSCI_SYBIL_TOKEN').data

    if (not sybil_users and not non_sybil_users ) or not token or not data['token']:
        return HttpResponseBadRequest("error: missing arguments")

    if token != data['token']:
        return HttpResponseBadRequest("error: invalid token")

    toggle_user_sybil(sybil_users, non_sybil_users)

    return JsonResponse({'success': 'ok'}, status=200)


@csrf_exempt
@require_POST
def upload_sybil_csv(request):
    '''
        This endpoint would be used by bsci to upload the csv
        generated by the bsci team which will be uploaded to S3
        for further processing. The history of the file uploaded will
        be stored in S3 and JSONStore would be updated to get the latest
        csv to mark users as sybil/not
    '''
    uploaded_file = request.FILES.get('csv')

    # validation checks
    if not uploaded_file:
        return HttpResponseBadRequest("error: missing csv file")
    if not uploaded_file.name.endswith('.csv'):
        return HttpResponseBadRequest("error: wrong file type")

    bsciJSON = StaticJsonEnv.objects.get(key='BSCI_SYBIL_TOKEN')

    now = datetime.now()
    # year-month-day-hour-minute (sortable)
    file_name = f'{now.strftime("%Y-%m-%d-%H-%M")}.csv'

    try:
        # upload to S3
        client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        client.put_object(Bucket=settings.S3_BSCI_SYBIL_BUCKET, Key=file_name, Body=uploaded_file.read())

        # store latest in JSONStore
        bsciJSON.data['csv_url'] = file_name
        bsciJSON.save()

        # process squelch data
        process_bsci_sybil_csv.delay(file_name, None)

    except Exception as e:
        return JsonResponse({'success': 'failed'}, status=500)

    return JsonResponse({'success': 'ok'}, status=200)
