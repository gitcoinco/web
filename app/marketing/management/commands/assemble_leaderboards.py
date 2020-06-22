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
from django.utils import timezone

from cacheops import CacheMiss, cache
from dashboard.models import Bounty, Profile, Tip
from grants.models import Contribution
from kudos.models import KudosTransfer
from marketing.models import LeaderboardRank

# Constants
IGNORE_PAYERS = []
IGNORE_EARNERS = ['owocki']  # sometimes owocki pays to himself. what a jerk!

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

TIMES = [ALL, WEEKLY, QUARTERLY, YEARLY, MONTHLY]
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


def bounty_to_location(bounty):
    locations = profile_to_location(bounty.bounty_owner_github_username)
    fulfiller_usernames = list(
        bounty.fulfillments.filter(accepted=True).values_list('profile__handle', flat=True)
    )
    for username in fulfiller_usernames:
        locations = locations + profile_to_location(username)
    return locations


def grant_to_location(grant):
    return profile_to_location(grant.subscription.contributor_profile.handle) + profile_to_location(grant.subscription.grant.admin_profile.handle)


def grant_to_country(grant):
    return list(set(ele['country_name'] for ele in grant_to_location(grant) if ele and ele.get('country_name')))


def grant_to_continent(grant):
    return list(set(ele['continent_name'] for ele in grant_to_location(grant) if ele and ele.get('continent_name')))


def grant_to_city(grant):
    return list(set(ele['city'] for ele in grant_to_location(grant) if ele and ele.get('city')))


def tip_to_location(tip):
    return profile_to_location(tip.username) + profile_to_location(tip.from_username)


def tip_to_country(tip):
    return list(set(ele['country_name'] for ele in tip_to_location(tip) if ele and ele.get('country_name')))


def tip_to_continent(tip):
    return list(set(ele['continent_name'] for ele in tip_to_location(tip) if ele and ele.get('continent_name')))


def tip_to_city(tip):
    return list(set(ele['city'] for ele in tip_to_location(tip) if ele and ele.get('city')))


def bounty_to_country(bounty):
    return list(set(ele['country_name'] for ele in bounty_to_location(bounty) if ele and ele.get('country_name')))


def bounty_to_continent(bounty):
    return list(set(ele['continent_name'] for ele in bounty_to_location(bounty) if ele and ele.get('continent_name')))


def bounty_to_city(bounty):
    return list(set(ele['city'] for ele in bounty_to_location(bounty) if ele and ele.get('city')))


def bounty_index_terms(bounty):
    index_terms = []
    if not should_suppress_leaderboard(bounty.bounty_owner_github_username):
        index_terms.append(bounty.bounty_owner_github_username.lower())
    if bounty.org_name:
        index_terms.append(bounty.org_name.lower())
    for fulfiller in bounty.fulfillments.filter(accepted=True):
        if not should_suppress_leaderboard(fulfiller.fulfiller_github_username):
            index_terms.append(fulfiller.fulfiller_github_username.lower())
    index_terms.append(bounty.token_name)
    for keyword in bounty_to_city(bounty):
        index_terms.append(keyword)
    for keyword in bounty_to_continent(bounty):
        index_terms.append(keyword)
    for keyword in bounty_to_country(bounty):
        index_terms.append(keyword)
    for keyword in bounty.keywords_list:
        index_terms.append(keyword.lower())
    return index_terms


def tip_index_terms(tip):
    index_terms = []
    if not should_suppress_leaderboard(tip.username):
        index_terms.append(tip.username.lower())
    if not should_suppress_leaderboard(tip.from_username):
        index_terms.append(tip.from_username.lower())
    if not should_suppress_leaderboard(tip.org_name):
        index_terms.append(tip.org_name.lower())
    if not should_suppress_leaderboard(tip.tokenName):
        index_terms.append(tip.tokenName)
    for keyword in tip_to_country(tip):
        index_terms.append(keyword)
    for keyword in tip_to_city(tip):
        index_terms.append(keyword)
    for keyword in tip_to_continent(tip):
        index_terms.append(keyword)
    return index_terms



def grant_index_terms(gc):
    index_terms = []
    if not gc.subscription:
        return index_terms
    if not should_suppress_leaderboard(gc.subscription.contributor_profile.handle):
        index_terms.append(gc.subscription.contributor_profile.handle.lower())
    if not should_suppress_leaderboard(gc.subscription.grant.admin_profile.handle):
        index_terms.append(gc.subscription.grant.admin_profile.handle.lower())
    if not should_suppress_leaderboard(gc.subscription.grant.org_name):
        index_terms.append(gc.subscription.grant.org_name.lower())
    if not should_suppress_leaderboard(gc.subscription.token_symbol):
        index_terms.append(gc.subscription.token_symbol)
    for keyword in grant_to_country(gc):
        index_terms.append(keyword)
    for keyword in grant_to_city(gc):
        index_terms.append(keyword)
    for keyword in grant_to_continent(gc):
        index_terms.append(keyword)
    return index_terms


def add_element(key, index_term, amount):
    index_term = index_term.replace('@', '')
    if not index_term or index_term == "None":
        return
    if index_term not in ranks[key].keys():
        ranks[key][index_term] = 0
    if index_term not in counts[key].keys():
        counts[key][index_term] = 0
    ranks[key][index_term] += round(float(amount), 2)
    counts[key][index_term] += 1


def sum_bounty_helper(b, time, index_term, val_usd):
    fulfiller_index_terms = list(b.fulfillments.filter(accepted=True).values_list('profile__handle', flat=True))
    add_element(f'{time}_{ALL}', index_term, val_usd)
    add_element(f'{time}_{FULFILLED}', index_term, val_usd)
    if index_term == b.bounty_owner_github_username and index_term not in IGNORE_PAYERS:
        add_element(f'{time}_{PAYERS}', index_term, val_usd)
    if index_term == b.org_name and index_term not in IGNORE_PAYERS:
        add_element(f'{time}_{ORGS}', index_term, val_usd)
    if index_term in fulfiller_index_terms and index_term not in IGNORE_EARNERS:
        add_element(f'{time}_{EARNERS}', index_term, val_usd)
    if index_term == b.token_name:
        add_element(f'{time}_{TOKENS}', index_term, val_usd)
    if index_term in bounty_to_country(b):
        add_element(f'{time}_{COUNTRIES}', index_term, val_usd)
    if index_term in bounty_to_city(b):
        add_element(f'{time}_{CITIES}', index_term, val_usd)
    if index_term in bounty_to_continent(b):
        add_element(f'{time}_{CONTINENTS}', index_term, val_usd)
    if index_term.lower() in (k.lower() for k in b.keywords_list):
        is_github_org_name = Bounty.objects.filter(github_url__icontains=f'https://github.com/{index_term}').exists()
        is_github_repo_name = Bounty.objects.filter(github_url__icontains=f'/{index_term}/').exists()
        if not is_github_repo_name and not is_github_org_name:
            add_element(f'{time}_{KEYWORDS}', index_term.lower(), val_usd)


def sum_bounties(b, index_terms):
    val_usd = b._val_usd_db
    for index_term in index_terms:
        if b.idx_status == 'done':
            sum_bounty_helper(b, ALL, index_term, val_usd)
            if b.created_on > WEEKLY_CUTOFF:
                sum_bounty_helper(b, WEEKLY, index_term, val_usd)
            if b.created_on > MONTHLY_CUTOFF:
                sum_bounty_helper(b, MONTHLY, index_term, val_usd)
            if b.created_on > QUARTERLY_CUTOFF:
                sum_bounty_helper(b, QUARTERLY, index_term, val_usd)
            if b.created_on > YEARLY_CUTOFF:
                sum_bounty_helper(b, YEARLY, index_term, val_usd)


def sum_tip_helper(t, time, index_term, val_usd):
    add_element(f'{time}_{ALL}', index_term, val_usd)
    add_element(f'{time}_{FULFILLED}', index_term, val_usd)
    if t.username == index_term:
        add_element(f'{time}_{EARNERS}', index_term, val_usd)
    if t.from_username == index_term:
        add_element(f'{time}_{PAYERS}', index_term, val_usd)
    if t.org_name == index_term:
        add_element(f'{time}_{ORGS}', index_term, val_usd)
    if t.tokenName == index_term:
        add_element(f'{time}_{TOKENS}', index_term, val_usd)
    if index_term in tip_to_country(t):
        add_element(f'{time}_{COUNTRIES}', index_term, val_usd)
    if index_term in tip_to_city(t):
        add_element(f'{time}_{CITIES}', index_term, val_usd)
    if index_term in tip_to_continent(t):
        add_element(f'{time}_{CONTINENTS}', index_term, val_usd)


def sum_kudos(kt):
    val_usd = kt.value_in_usdt_now
    if not kt.kudos_token_cloned_from:
        return
    index_terms = [kt.kudos_token_cloned_from.url]
    for index_term in index_terms:
        sum_kudos_helper(kt, ALL, index_term, val_usd)
        if kt.created_on > WEEKLY_CUTOFF:
            sum_kudos_helper(kt, WEEKLY, index_term, val_usd)
        if kt.created_on > MONTHLY_CUTOFF:
            sum_kudos_helper(kt, MONTHLY, index_term, val_usd)
        if kt.created_on > QUARTERLY_CUTOFF:
            sum_kudos_helper(kt, QUARTERLY, index_term, val_usd)
        if kt.created_on > YEARLY_CUTOFF:
            sum_kudos_helper(kt, YEARLY, index_term, val_usd)


def sum_kudos_helper(t, time, index_term, val_usd):
    add_element(f'{time}_{KUDOS}', index_term, val_usd)
    add_element(f'{time}_{ALL}', index_term, val_usd)
    add_element(f'{time}_{FULFILLED}', index_term, val_usd)
    if t.username == index_term:
        add_element(f'{time}_{EARNERS}', index_term, val_usd)
    if t.from_username == index_term:
        add_element(f'{time}_{PAYERS}', index_term, val_usd)
    if t.org_name == index_term:
        add_element(f'{time}_{ORGS}', index_term, val_usd)
    if index_term in tip_to_country(t):
        add_element(f'{time}_{COUNTRIES}', index_term, val_usd)
    if index_term in tip_to_city(t):
        add_element(f'{time}_{CITIES}', index_term, val_usd)
    if index_term in tip_to_continent(t):
        add_element(f'{time}_{CONTINENTS}', index_term, val_usd)


def sum_tips(t, index_terms):
    val_usd = t.value_in_usdt_now
    for index_term in index_terms:
        sum_tip_helper(t, ALL, index_term, val_usd)
        if t.created_on > WEEKLY_CUTOFF:
            sum_tip_helper(t, WEEKLY, index_term, val_usd)
        if t.created_on > MONTHLY_CUTOFF:
            sum_tip_helper(t, MONTHLY, index_term, val_usd)
        if t.created_on > QUARTERLY_CUTOFF:
            sum_tip_helper(t, QUARTERLY, index_term, val_usd)
        if t.created_on > YEARLY_CUTOFF:
            sum_tip_helper(t, YEARLY, index_term, val_usd)


def sum_grants(t, index_terms):
    val_usd = t.subscription.amount_per_period_usdt
    for index_term in index_terms:
        sum_grant_helper(t, ALL, index_term, val_usd)
        if t.created_on > WEEKLY_CUTOFF:
            sum_grant_helper(t, WEEKLY, index_term, val_usd)
        if t.created_on > MONTHLY_CUTOFF:
            sum_grant_helper(t, MONTHLY, index_term, val_usd)
        if t.created_on > QUARTERLY_CUTOFF:
            sum_grant_helper(t, QUARTERLY, index_term, val_usd)
        if t.created_on > YEARLY_CUTOFF:
            sum_grant_helper(t, YEARLY, index_term, val_usd)



def sum_grant_helper(gc, time, index_term, val_usd):
    add_element(f'{time}_{ALL}', index_term, val_usd)
    add_element(f'{time}_{FULFILLED}', index_term, val_usd)
    if gc.subscription.grant.admin_profile.handle.lower() == index_term:
        add_element(f'{time}_{EARNERS}', index_term, val_usd)
    if gc.subscription.contributor_profile.handle.lower() == index_term:
        add_element(f'{time}_{PAYERS}', index_term, val_usd)
    if gc.subscription.grant.org_name.lower() == index_term:
        add_element(f'{time}_{ORGS}', index_term, val_usd)
    if gc.subscription.token_symbol == index_term:
        add_element(f'{time}_{TOKENS}', index_term, val_usd)
    if index_term in grant_to_country(gc):
        add_element(f'{time}_{COUNTRIES}', index_term, val_usd)
    if index_term in grant_to_city(gc):
        add_element(f'{time}_{CITIES}', index_term, val_usd)
    if index_term in grant_to_continent(gc):
        add_element(f'{time}_{CONTINENTS}', index_term, val_usd)


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

    products = ['kudos', 'grants', 'bounties', 'tips', 'all']
    for product in products:

        ranks = default_ranks()
        counts = default_ranks()
        index_terms = []

        if product in ['all', 'grants']:
            # get grants
            grants = Contribution.objects.filter(subscription__network='mainnet')
            # iterate
            for gc in grants:
                try:
                    index_terms = grant_index_terms(gc)
                    sum_grants(gc, index_terms)
                except Exception as e:
                    print(gc.id)
                    print(e)

        if product in ['all', 'bounties']:
            # get bounties
            bounties = Bounty.objects.current().filter(network='mainnet')

            # iterate
            for b in bounties:
                if not b._val_usd_db:
                    continue

                index_terms = bounty_index_terms(b)
                sum_bounties(b, index_terms)

        if product in ['all', 'tips']:
            # get tips
            tips = Tip.objects.send_success().filter(network='mainnet')

            # iterate
            for t in tips:
                if not t.value_in_usdt_now:
                    continue
                index_terms = tip_index_terms(t)
                sum_tips(t, index_terms)

        if product in ['all', 'kudos']:
            # kudos'
            for kt in KudosTransfer.objects.send_success().filter(network='mainnet'):
                sum_kudos(kt)

        # set old LR as inactive
        created_on = timezone.now()
        with transaction.atomic():
            lrs = LeaderboardRank.objects.active().filter(product=product)
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
