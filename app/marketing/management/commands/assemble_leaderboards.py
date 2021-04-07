# -*- coding: utf-8 -*-
"""Define the management command to assemble leaderboard rankings.

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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from cacheops import CacheMiss, cache
from dashboard.models import Earning, Profile
from marketing.models import LeaderboardRank
from django.contrib.contenttypes.models import ContentType

# Constants
IGNORE_PAYERS = []
IGNORE_EARNERS = ['owocki', 'trufflesuite', 'thegivingblock', 'blockscout' ]

ALL = 'all'

WEEKLY = 'weekly'
QUARTERLY = 'quarterly'
YEARLY = 'yearly'
MONTHLY = 'monthly'

FULFILLED = 'fulfilled'
PAYERS = 'payers'
EARNERS = 'earners'
ORGS = 'orgs'
KUDOS = 'kudos'
KEYWORDS = 'keywords'
TOKENS = 'tokens'
COUNTRIES = 'countries'
CITIES = 'cities'
CONTINENTS = 'continents'

TIMES = [WEEKLY, MONTHLY]
BREAKDOWNS = [FULFILLED, ALL, PAYERS, EARNERS, ORGS, KEYWORDS, KUDOS, TOKENS, COUNTRIES, CITIES, CONTINENTS]

WEEKLY_CUTOFF = timezone.now() - timezone.timedelta(days=(30 if settings.DEBUG else 7))
MONTHLY_CUTOFF = timezone.now() - timezone.timedelta(days=30)
QUARTERLY_CUTOFF = timezone.now() - timezone.timedelta(days=90)
YEARLY_CUTOFF = timezone.now() - timezone.timedelta(days=365)


def default_ranks():
    """Generate a dictionary of nested dictionaries defining default ranks.

    Returns:
        dict: A nested dictionary mapping of all default ranks with empty dicts.

    """
    return_dict = {}
    for time in TIMES:
        for breakdown in BREAKDOWNS:
            key = f'{time}_{breakdown}'
            return_dict[key] = {}
    return return_dict


ranks = default_ranks()
counts = default_ranks()


def profile_to_location(handle):
    timeout = 60 * 20
    key_salt = '1'
    key = f'profile_to_location{handle}_{key_salt}'
    try:
        results = cache.get(key)
    except CacheMiss:
        results = None

    if not results:
        results = profile_to_location_helper(handle)
    cache.set(key, results, timeout)

    return results


def profile_to_location_helper(handle):
    if not handle:
        return []
    
    profiles = Profile.objects.filter(handle=handle.lower())
    if handle and profiles.exists():
        profile = profiles.first()
        if len(profile.locations):
            return [profile.locations[0]]
    return []


def earning_to_location(earning):
    locations = []
    usernames = list(
        earning.to_profile,
        earning.from_profile
    )
    for username in usernames:
        locations = locations + profile_to_location(username)
    return locations


def earning_to_country(earning):
    return list(set(ele['country_name'] for ele in earning_to_location(earning) if ele and ele.get('country_name')))


def earning_to_continent(earning):
    return list(set(ele['continent_name'] for ele in earning_to_location(earning) if ele and ele.get('continent_name')))


def earning_to_city(earning):
    return list(set(ele['city'] for ele in earning_to_location(earning) if ele and ele.get('city')))


def earning_index_terms(earning):
    index_terms = []
    if not should_suppress_leaderboard(earning.from_profile.handle.lower()):
        index_terms.append(earning.from_profile.handle.lower())
    if earning.org_profile:
        index_terms.append(earning.org_profile.handle.lower())
    if not should_suppress_leaderboard(earning.to_profile.lower()):
        index_terms.append(earning.to_profile.lower())
    index_terms.append(earning.token_name)
    for keyword in earning_to_city(earning):
        index_terms.append(keyword)
    for keyword in earning_to_continent(earning):
        index_terms.append(keyword)
    for keyword in earning_to_country(earning):
        index_terms.append(keyword)
    return index_terms


def add_element(key, index_term, amount):
    try:
        index_term = index_term.replace('@', '')
        if not index_term or index_term == "None":
            return
        if index_term not in ranks[key].keys():
            ranks[key][index_term] = 0
        if index_term not in counts[key].keys():
            counts[key][index_term] = 0
        ranks[key][index_term] += round(float(amount), 2)
        counts[key][index_term] += 1
    except:
        pass


def sum_earning_helper(e, time, index_term, val_usd):
    handle_index_terms = [e.to_profile.handle]
    add_element(f'{time}_{ALL}', index_term, val_usd)
    add_element(f'{time}_{FULFILLED}', index_term, val_usd)
    if index_term == e.from_profile.handle and index_term not in IGNORE_PAYERS:
        add_element(f'{time}_{PAYERS}', index_term, val_usd)
    if index_term == e.org_profile.handle and index_term not in IGNORE_PAYERS:
        add_element(f'{time}_{ORGS}', index_term, val_usd)
    if index_term in handle_index_terms and index_term not in IGNORE_EARNERS:
        add_element(f'{time}_{EARNERS}', index_term, val_usd)
    if index_term == e.token_name:
        add_element(f'{time}_{TOKENS}', index_term, val_usd)
    if index_term in earning_to_country(e):
        add_element(f'{time}_{COUNTRIES}', index_term, val_usd)
    if index_term in earning_to_city(e):
        add_element(f'{time}_{CITIES}', index_term, val_usd)
    if index_term in earning_to_continent(e):
        add_element(f'{time}_{CONTINENTS}', index_term, val_usd)
    # TODO: keywords


def sum_earnings(e, index_terms):
    val_usd = e.value_usd
    for index_term in index_terms:
        sum_earning_helper(e, ALL, index_term, val_usd)
        if e.created_on > WEEKLY_CUTOFF:
            sum_earning_helper(e, WEEKLY, index_term, val_usd)
        if e.created_on > MONTHLY_CUTOFF:
            sum_earning_helper(e, MONTHLY, index_term, val_usd)
        if e.created_on > QUARTERLY_CUTOFF:
            sum_earning_helper(e, QUARTERLY, index_term, val_usd)
        if e.created_on > YEARLY_CUTOFF:
            sum_earning_helper(e, YEARLY, index_term, val_usd)


def should_suppress_leaderboard(handle):
    if not handle:
        return True
    profiles = Profile.objects.filter(handle=handle.lower())
    if profiles.exists():
        profile = profiles.first()
        if profile.suppress_leaderboard or profile.hide_profile:
            return True
    return False


def do_leaderboard_feed():
    from dashboard.models import Activity
    max_rank = 25
    for _type in [PAYERS, EARNERS, ORGS]:
        key = f'{WEEKLY}_{_type}'
        lrs = LeaderboardRank.objects.active().filter(leaderboard=key, rank__lte=max_rank, product='all')
        print(key, lrs.count())
        for lr in lrs:
            metadata = {
                'title': f"was ranked #{lr.rank} on the Gitcoin Weekly {_type.title()} Leaderboard",
                'link': f'/leaderboard/{_type}'
                }
            if lr.profile:
                Activity.objects.create(profile=lr.profile, activity_type='leaderboard_rank', metadata=metadata)

    profile = Profile.objects.filter(handle='gitcoinbot').first()
    for _type in [PAYERS, EARNERS, ORGS, CITIES, TOKENS]:
        url = f'/leaderboard/{_type}'
        what = _type.title() if _type != PAYERS else "Funders"
        key = f'{WEEKLY}_{_type}'
        lrs = LeaderboardRank.objects.active().filter(leaderboard=key, rank__lte=max_rank, product='all').order_by('rank')[0:10]
        copy = f"<a href={url}>Weekly {what} Leaderboard</a>:<BR>"
        counter = 0
        for lr in lrs:
            profile_link = f"<a href=/{lr.profile}>@{lr.profile}</a>" if _type not in [CITIES, TOKENS] else f"<strong>{lr.github_username}</strong>"
            copy += f" - {profile_link} was ranked <strong>#{lr.rank}</strong>. <BR>"
        metadata = {
            'copy': copy,
        }
        key = f'{WEEKLY}_{_type}'
        Activity.objects.create(profile=profile, activity_type='consolidated_leaderboard_rank', metadata=metadata)


def do_leaderboard():
    global ranks
    global counts
    CUTOFF = MONTHLY_CUTOFF

    products_to_content_type = {
        'kudos': ContentType.objects.get(app_label='kudos', model='kudostransfer'),
        'grants': ContentType.objects.get(app_label='grants', model='contribution'),
        'bounties': ContentType.objects.get(app_label='dashboard', model='bounties'),
        'tips': ContentType.objects.get(app_label='dashboard', model='tip'),
        'all': None
        }

    products = ['kudos', 'grants', 'bounties', 'tips', 'all']
    for product in products:

        ranks = default_ranks()
        counts = default_ranks()
        index_terms = []

        print('---')
        # get earnings
        earnings = Earning.objects.filter(network='mainnet').filter(created_on__gt=CUTOFF)
        ct = products_to_content_type.get(product)
        if ct:
            earnings = earnings.filter(source_type=ct)

        # iterate
        print(product, earnings.count())
        for earning in earnings:
            try:
                index_terms = earning_index_terms(earning)
                sum_earnings(earning, index_terms)
            except Exception as e:
                print(earning.id)
                print(e)

        # set old LR as inactive
        created_on = timezone.now()
        with transaction.atomic():
            print(" - saving -")
            lrs = LeaderboardRank.objects.active().filter(product=product)
            lrs = lrs.filter(Q(leaderboard__startswith=WEEKLY) | Q(leaderboard__startswith=MONTHLY))
            lrs.update(active=False)

            # save new LR in DB
            for key, rankings in ranks.items():
                rank = 1
                for index_term, amount in sorted(rankings.items(), key=lambda x: x[1], reverse=True):
                    count = counts[key][index_term]
                    lbr_kwargs = {
                        'count': count,
                        'active': True,
                        'amount': amount,
                        'rank': rank,
                        'leaderboard': key,
                        'github_username': index_term,
                        'product': product,
                        'created_on': created_on,
                    }

                    try:
                        profile = Profile.objects.get(handle=index_term.lower())
                        lbr_kwargs['profile'] = profile
                        lbr_kwargs['tech_keywords'] = profile.keywords
                    except Profile.MultipleObjectsReturned:
                        profile = Profile.objects.filter(handle=index_term.lower()).latest('id')
                        lbr_kwargs['profile'] = profile
                        lbr_kwargs['tech_keywords'] = profile.keywords
                        print(f'Multiple profiles found for username: {index_term}')
                    except Profile.DoesNotExist:
                        print(f'No profiles found for username: {index_term}')

                    # TODO: Bucket LeaderboardRank objects and .bulk_create
                    LeaderboardRank.objects.create(**lbr_kwargs)
                    rank += 1
                    print(key, index_term, amount, count, rank, product)


class Command(BaseCommand):

    help = 'creates leaderboard objects'

    def handle(self, *args, **options):
        do_leaderboard()
        do_leaderboard_feed()
