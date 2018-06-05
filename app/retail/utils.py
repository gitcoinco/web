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

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import pytz
from marketing.models import Alumni, LeaderboardRank, Stat
from requests_oauthlib import OAuth2Session


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


def build_stat_results():
    from dashboard.models import Bounty

    """Buidl the results page context."""
    context = {
        'active': 'results',
        'title': _('Results'),
        'card_desc': _('Gitcoin is transparent by design.  Here are some stats about our core bounty product.'),
    }

    base_bounties = Bounty.objects.current().filter(network='mainnet')
    context['alumni_count'] = Alumni.objects.count()
    context['count_open'] = base_bounties.filter(network='mainnet', idx_status__in=['open']).count()
    context['count_started'] = base_bounties.filter(network='mainnet', idx_status__in=['started', 'submitted']).count()
    context['count_done'] = base_bounties.filter(network='mainnet', idx_status__in=['done']).count()

    # Leaderboard 
    context['top_orgs'] = LeaderboardRank.objects.filter(active=True, leaderboard='quarterly_orgs').order_by('rank').values_list('github_username', flat=True)

    #community size
    base_stats = Stat.objects.filter(
        key='email_subscriberse',
        ).order_by('-pk')
    today = base_stats.first().val
    context['members_history'] = ([
        ['Year', 'Members'],
        ['Launch', 0],
        ['6 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=6*30))).first().val],
        ['5 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=5*30))).first().val],
        ['4 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=4*30))).first().val],
        ['3 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=3*30))).first().val],
        ['2 months ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=2*30))).first().val],
        ['1 month ago', base_stats.filter(created_on__lt=(timezone.now() - timezone.timedelta(days=1*30))).first().val],
        ['Today', today]
        ])
    context['members_history'] = json.dumps(context['members_history'])

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

    # slack ticks
    increment = 1000
    context['slack_ticks'] = list(x * increment for x in range(0, int(today/increment)+1))
    context['slack_ticks'] = json.dumps(context['slack_ticks'])

    # Bounties
    # TODO: make this info dynamic
    context['universe_total_usd'] = sum(base_bounties.filter(network='mainnet').values_list('_val_usd_db', flat=True))
    context['max_bounty_history'] = float(context['universe_total_usd']) * .7
    context['bounty_abandonment_rate'] = '9.5%'
    context['bounty_average_turnaround'] = '2.1 Weeks'
    context['hourly_rate_distribution'] = '$15 - $120'
    context['bounty_claimed_completion_rate'] = '82%'
    context['bounty_median_pickup_time'] = '2.25'

    return context
