# -*- coding: utf-8 -*-
'''
    Copyright (C) 2017 Gitcoin Core

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

'''
import cgi
import json
import re
import statistics
import time

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import pytz
from marketing.models import Alumni, LeaderboardRank, Stat
from requests_oauthlib import OAuth2Session


class PerformanceProfiler:

    last_time = None
    start_time = None

    def profile_time(self, name):
        if not self.last_time:
            self.last_time = time.time()
            self.start_time = time.time()
            return

        self.end_time = time.time()
        this_time = self.end_time - self.last_time
        total_time = self.end_time - self.start_time
        print(f"pulled {name} in {round(this_time,2)} seconds (total: {round(total_time,2)} sec)")
        self.last_time = time.time()


def get_github_user_profile(token):
    github = OAuth2Session(
        settings.GITHUB_CLIENT_ID,
        token=token,
    )

    creds = github.get('https://api.github.com/user').json()
    print(creds)
    return creds


def strip_html(html):
    tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
    no_tags = tag_re.sub('', html)
    txt = cgi.escape(no_tags)

    return txt


def strip_double_chars(txt, char=' '):
    new_txt = txt.replace(char+char, char)
    if new_txt == txt:
        return new_txt
    return strip_double_chars(new_txt, char)


def get_bounty_history_row(label, date):
    return [
        label,
        get_tip_history_at_date(date),
        get_bounty_history_at_date(['open'], date),
        get_bounty_history_at_date(['started', 'submitted'], date),
        get_bounty_history_at_date(['done'], date),
        get_bounty_history_at_date(['cancelled'], date),
    ]


def get_bounty_history_at_date(statuses, date):
    try:
        keys = [f'bounties_{status}_value' for status in statuses]
        base_stats = Stat.objects.filter(
            key__in=keys,
            ).order_by('-pk')
        return base_stats.filter(created_on__lte=date).first().val
    except Exception as e:
        print(e)
        return 0


def get_tip_history_at_date(date):
    try:
        base_stats = Stat.objects.filter(
            key='tips_value',
            ).order_by('-pk')
        return base_stats.filter(created_on__lte=date).first().val
    except Exception as e:
        print(e)
        return 0


def get_history(base_stats, copy):
    today = base_stats.first().val

    # slack ticks
    increment = 1000
    ticks = json.dumps(list(x * increment for x in range(0, int(today/increment)+1)))
    history = json.dumps([
        ['When', copy],
        ['Launch', 0],
        ['6 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=6*30))).first().val],
        ['5 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=5*30))).first().val],
        ['4 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=4*30))).first().val],
        ['3 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=3*30))).first().val],
        ['2 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=2*30))).first().val],
        ['1 month ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=1*30))).first().val],
        ['Today', today],
        ])
    return history, ticks


def get_completion_rate():
    from dashboard.models import Bounty
    base_bounties = Bounty.objects.current().filter(network='mainnet').filter(idx_status__in=['done', 'expired', 'cancelled'])
    eligible_bounties = base_bounties.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=60)))
    eligible_bounties = eligible_bounties.exclude(interested__isnull=True)
    completed_bounties = eligible_bounties.filter(idx_status__in=['done']).count()
    not_completed_bounties = eligible_bounties.filter(idx_status__in=['expired', 'cancelled']).count()
    total_bounties = completed_bounties + not_completed_bounties

    return round((completed_bounties * 1.0 / total_bounties), 3) * 100


def get_bounty_median_turnaround_time(func='turnaround_time_started'):
    from dashboard.models import Bounty
    base_bounties = Bounty.objects.current().filter(network='mainnet')
    eligible_bounties = base_bounties.exclude(idx_status='open').filter(created_on__gt=(timezone.now() - timezone.timedelta(days=60)))
    pickup_time_hours = []
    for bounty in eligible_bounties:
        tat = getattr(bounty, func)
        if tat:
            pickup_time_hours.append(tat / 60 / 60)

    pickup_time_hours.sort()
    return statistics.median(pickup_time_hours)


def build_stat_results():
    from dashboard.models import Bounty

    """Buidl the results page context."""
    context = {
        'active': 'results',
        'title': _('Results'),
        'card_desc': _('Gitcoin is transparent by design.  Here are some stats about our core bounty product.'),
    }
    pp = PerformanceProfiler()
    pp.profile_time('start')
    base_bounties = Bounty.objects.current().filter(network='mainnet')
    context['alumni_count'] = Alumni.objects.count()
    pp.profile_time('alumni')
    context['count_open'] = base_bounties.filter(network='mainnet', idx_status__in=['open']).count()
    context['count_started'] = base_bounties.filter(network='mainnet', idx_status__in=['started', 'submitted']).count()
    context['count_done'] = base_bounties.filter(network='mainnet', idx_status__in=['done']).count()
    pp.profile_time('count_*')

    # Leaderboard 
    context['top_orgs'] = LeaderboardRank.objects.filter(active=True, leaderboard='quarterly_orgs').order_by('rank').values_list('github_username', flat=True)
    pp.profile_time('orgs')

    #community size
    base_stats = Stat.objects.filter(
        key='email_subscriberse',
        ).order_by('-pk')
    context['members_history'], context['slack_ticks'] = get_history(base_stats, "Members")

    pp.profile_time('Stats1')
    
    #jdi history
    base_stats = Stat.objects.filter(
        key='joe_dominance_index_30_value',
        ).order_by('-pk')
    context['jdi_history'], jdi_ticks = get_history(base_stats, 'Percentage')

    pp.profile_time('Stats2')

    # bounties hisotry
    context['bounty_history'] = [
        ['', 'Tips',  'Open / Available',  'Started / In Progress',  'Completed', 'Cancelled' ],
        ["January 2018", 2011, 903, 2329, 5534, 1203],
        ["February 2018", 5093, 1290, 1830, 15930, 1803],
        ["March 2018", 7391, 6903, 4302, 16302, 2390],
        ["April 2018", 8302, 5349, 5203, 26390, 3153],
        ["May 2018", 10109, 6702, 4290, 37342, 4281],
      ]
    for year in range(2018, 2025):
        months = range(1, 12)
        if year == 2018:
            months = range(6, 12)
        for month in months:
            then = timezone.datetime(year, month, 3).replace(tzinfo=pytz.UTC)
            if then < timezone.now():
                row = get_bounty_history_row(then.strftime("%B %Y"), then)
                context['bounty_history'].append(row)
    context['bounty_history'] = json.dumps(context['bounty_history'])
    pp.profile_time('bounty_history')

    # Bounties
    completion_rate = get_completion_rate()
    pp.profile_time('completion_rate')
    bounty_abandonment_rate = round(100 - completion_rate, 1)
    context['universe_total_usd'] = sum(base_bounties.filter(network='mainnet').values_list('_val_usd_db', flat=True))
    pp.profile_time('universe_total_usd')
    context['max_bounty_history'] = float(context['universe_total_usd']) * .7
    context['bounty_abandonment_rate'] = f'{bounty_abandonment_rate}%'
    context['bounty_average_turnaround'] = str(round(get_bounty_median_turnaround_time('turnaround_time_submitted')/24, 1)) + " days"
    pp.profile_time('bounty_average_turnaround')
    context['hourly_rate_distribution'] = '$15 - $120'
    context['bounty_claimed_completion_rate'] = f'{completion_rate}%'
    context['bounty_median_pickup_time'] = round(get_bounty_median_turnaround_time('turnaround_time_started'), 1)
    pp.profile_time('bounty_median_pickup_time')
    pp.profile_time('final')

    return context
