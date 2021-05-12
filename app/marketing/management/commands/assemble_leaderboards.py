# -*- coding: utf-8 -*-
"""Define the management command to assemble leaderboard rankings.

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
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db import connection, transaction
from django.db.models import Q
from django.utils import timezone

from cacheops import CacheMiss, cache
from dashboard.models import Earning, Profile
from marketing.models import LeaderboardRank

# Constants
IGNORE_PAYERS = []
IGNORE_EARNERS = ['owocki', 'trufflesuite', 'thegivingblock', 'blockscout' ]

ALL = 'all'

DAILY = 'daily'
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

BREAKDOWNS = [FULFILLED, ALL, PAYERS, EARNERS, ORGS, KEYWORDS, KUDOS, TOKENS, COUNTRIES, CITIES, CONTINENTS]
BREAKDOWNS = [ORGS, PAYERS, EARNERS, TOKENS]

DAILY_CUTOFF = timezone.now() - timezone.timedelta(days=1)
WEEKLY_CUTOFF = timezone.now() - timezone.timedelta(days=(30 if settings.DEBUG else 7))
MONTHLY_CUTOFF = timezone.now() - timezone.timedelta(days=30)
QUARTERLY_CUTOFF = timezone.now() - timezone.timedelta(days=90)
YEARLY_CUTOFF = timezone.now() - timezone.timedelta(days=365)
ALL_CUTOFF = timezone.now() - timezone.timedelta(days=365*10)

only_save_below_rank = 9999


def should_suppress_leaderboard(handle):
    if not handle:
        return True
    profiles = Profile.objects.filter(handle=handle.lower())
    if profiles.exists():
        profile = profiles.first()
        if profile.suppress_leaderboard or profile.hide_profile:
            return True
    return False


def do_leaderboard_feed(cadence, cadence_ui):
    from dashboard.models import Activity
    max_rank = 25
    for _type in [PAYERS, EARNERS, ORGS]:
        key = f'{cadence}_{_type}'
        lrs = LeaderboardRank.objects.active().filter(leaderboard=key, rank__lte=max_rank, product='all')
        print(key, lrs.count())
        for lr in lrs:
            metadata = {
                'title': f"was ranked #{lr.rank} on the Gitcoin {cadence_ui} {_type.title()} Leaderboard",
                'link': f'/leaderboard/{_type}'
                }
            if lr.profile:
                Activity.objects.create(profile=lr.profile, activity_type='leaderboard_rank', metadata=metadata)

    profile = Profile.objects.filter(handle='gitcoinbot').first()
    for _type in [PAYERS, EARNERS, ORGS, TOKENS]:
        url = f'/leaderboard/{_type}'
        what = _type.title() if _type != PAYERS else "Funders"
        key = f'{cadence}_{_type}'
        lrs = LeaderboardRank.objects.active().filter(leaderboard=key, rank__lte=max_rank, product='all').order_by('rank')[0:10]
        copy = f"<a href={url}>{cadence_ui} {what} Leaderboard</a>:<BR>"
        counter = 0
        for lr in lrs:
            profile_link = f"<a href=/{lr.profile}>@{lr.profile}</a>" if _type not in [CITIES, TOKENS] else f"<strong>{lr.github_username}</strong>"
            copy += f" - {profile_link} was ranked <strong>#{lr.rank}</strong>. <BR>"
        metadata = {
            'copy': copy,
        }
        key = f'{cadence}_{_type}'
        Activity.objects.create(profile=profile, activity_type='consolidated_leaderboard_rank', metadata=metadata)


def query_to_results(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        rows = []
        for _row in cursor.fetchall():
            rows.append(list(_row))
        return rows
    return []


def build_query(from_date, to_date, content_type=None, index_on='dashboard_profile.handle', join_on='to_profile_id'):

    content_type_sql = ''
    if content_type:
        content_type_sql = f"and source_type_id = {content_type.id} "

    query = f"""
SELECT
    distinct {index_on} as idx,
    count(1) as num,
    sum(value_usd) as amount
FROM
    dashboard_earning
INNER JOIN
    dashboard_profile on dashboard_earning.{join_on} = dashboard_profile.id
WHERE
    dashboard_earning.created_on > '{from_date}'
    and dashboard_earning.created_on < '{to_date}'
    and dashboard_earning.network = 'mainnet'
    and success=true
    {content_type_sql}
GROUP BY {index_on}
ORDER BY amount DESC"""
    return query


def do_leaderboard():
    CUTOFF = MONTHLY_CUTOFF

    products_to_content_type = {
        'kudos': ContentType.objects.get(app_label='kudos', model='kudostransfer'),
        'grants': ContentType.objects.get(app_label='grants', model='contribution'),
        'bounties': ContentType.objects.get(app_label='dashboard', model='bountyfulfillment'),
        'tips': ContentType.objects.get(app_label='dashboard', model='tip'),
        'all': None
        }

    tag_to_datetime_full = {
        DAILY: DAILY_CUTOFF,
        WEEKLY: WEEKLY_CUTOFF,
        MONTHLY: MONTHLY_CUTOFF,
        QUARTERLY: QUARTERLY_CUTOFF,
        YEARLY: YEARLY_CUTOFF,
        ALL: ALL_CUTOFF,
    }
    tag_to_datetime = {
        DAILY: DAILY_CUTOFF,
    }

    if run_weekly():
        tag_to_datetime[WEEKLY] = WEEKLY_CUTOFF
    if run_monthly():
        tag_to_datetime[MONTHLY] = MONTHLY_CUTOFF
    if run_quarterly():
        tag_to_datetime[QUARTERLY] = QUARTERLY_CUTOFF
        tag_to_datetime[ALL] = ALL_CUTOFF
    if run_yearly():
        tag_to_datetime[YEARLY_CUTOFF] = YEARLY_CUTOFF

    products = ['kudos', 'grants', 'bounties', 'tips', 'all']
    for breakdown in BREAKDOWNS:
        for tag, from_date in tag_to_datetime.items():
            for product in products:

                print(breakdown, tag, product)

                ct = products_to_content_type.get(product)
                join_on = 'to_profile_id'
                index_on = 'dashboard_profile.handle'
                if breakdown == ORGS:
                    join_on = 'org_profile_id'
                if breakdown == PAYERS:
                    join_on = 'from_profile_id'
                if breakdown == TOKENS:
                    index_on = 'token_name'

                to_date = timezone.now()
                print(' - querying db -')
                query = build_query(from_date, to_date, content_type=ct, index_on=index_on, join_on=join_on)
                results = query_to_results(query)
                index_terms = []

                print('---')

                # set old LR as inactive
                created_on = timezone.now()
                with transaction.atomic():
                    print(" - saving -")
                    key = f"{tag}_{breakdown}"
                    lrs = LeaderboardRank.objects.active()
                    lrs = lrs.filter(leaderboard=key, product=product)
                    lrs.update(active=False)

                    # save new LR in DB
                    #for each time frame
                    if True:
                        rank = 1
                        for item in results:

                            if rank > only_save_below_rank:
                                continue

                            idx = item[0]
                            count = item[1]
                            amount = item[2]
                            if not amount:
                                continue
                            print(idx, count, amount, rank, product)

                            lbr_kwargs = {
                                'count': count,
                                'active': True,
                                'amount': amount,
                                'rank': rank,
                                'leaderboard': key,
                                'github_username': idx,
                                'product': product,
                                'created_on': created_on,
                            }

                            profile = None
                            if (index_on is not 'token_name'):
                                try:
                                    profile = Profile.objects.get(handle=idx.lower())
                                    if profile.suppress_leaderboard:
                                        continue
                                except Exception as e:
                                    print(e)
                            lbr_kwargs['profile'] = profile

                            LeaderboardRank.objects.create(**lbr_kwargs)
                            rank += 1


def run_weekly():
    return (timezone.now().strftime('%A')) == "Friday"


def run_monthly():
    return int(timezone.now().strftime('%d')) == 1


def run_quarterly():
    return run_monthly() and (int(timezone.now().strftime('%m'))-1) % 3 == 0


def run_yearly():
    return int(timezone.now().strftime('%j')) == 1


class Command(BaseCommand):

    help = 'creates leaderboard objects'

    def handle(self, *args, **options):
        do_leaderboard()

        cadences = [
        ]

        if not run_quarterly():
            cadences.append((DAILY, 'Daily'))
        if run_weekly():
            cadences.append((WEEKLY, 'Weekly'))
        if run_monthly():
            cadences.append((MONTHLY, 'Monthly'))
        if run_quarterly():
            cadences.append((QUARTERLY, 'Quarterly'))
        if run_yearly():
            cadences.append((YEARLY, 'Yearly'))
        for ele in cadences:
            do_leaderboard_feed(ele[0], ele[1])
