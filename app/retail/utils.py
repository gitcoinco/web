# -*- coding: utf-8 -*-
"""Define the Retail utility methods and general logic.

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
import cgi
import json
import re
import statistics
import time

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import pytz
from cacheops import CacheMiss, cache
from marketing.models import Alumni, EmailSubscriber, LeaderboardRank, Stat
from requests_oauthlib import OAuth2Session

programming_languages = ['css', 'solidity', 'python', 'javascript', 'ruby', 'rust', 'html', 'design']


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


def get_bounty_history_row(label, date, keyword):
    return [
        label,
        get_tip_history_at_date(date, keyword),
        get_bounty_history_at_date(['open'], date, keyword),
        get_bounty_history_at_date(['started', 'submitted'], date, keyword),
        get_bounty_history_at_date(['done'], date, keyword),
        get_bounty_history_at_date(['cancelled'], date, keyword),
    ]


def get_bounty_history_at_date(statuses, date, keyword):
    keyword_with_prefix = f"_{keyword}" if keyword else ""
    try:
        keys = [f'bounties_{status}{keyword_with_prefix}_value' for status in statuses]
        base_stats = Stat.objects.filter(
            key__in=keys,
            ).order_by('-pk')
        return base_stats.filter(created_on__lte=date).first().val
    except Exception as e:
        print(e)
        return 0


def get_tip_history_at_date(date, keyword):
    if keyword:
        # TODO - attribute tips to specific keywords
        return 0
    try:
        base_stats = Stat.objects.filter(
            key='tips_value',
            ).order_by('-pk')
        return base_stats.filter(created_on__lte=date).first().val
    except Exception as e:
        print(e)
        return 0


def get_history(base_stats, copy, num_months=6):
    today = base_stats.first().val if base_stats.exists() else 0

    # slack ticks
    increment = 1000
    ticks = json.dumps(list(x * increment for x in range(0, int(today/increment)+1)))
    history = [
        ['When', copy],
        ['Launch', 0],
    ]
    _range = list(range(1, num_months))
    _range.reverse()
    for i in _range:
        try:
            plural = 's' if i != 1 else ''
            before_then = (timezone.now() - timezone.timedelta(days=i*30))
            val = base_stats.filter(created_on__lt=before_then).order_by('-created_on').first().val
            history = history + [[f'{i} month{plural} ago', val], ]
        except Exception:
            pass

    history = history + [['Today', today], ]
    history = json.dumps(history)
    return history, ticks


def get_completion_rate(keyword):
    from dashboard.models import Bounty
    base_bounties = Bounty.objects.current().filter(network='mainnet', idx_status__in=['done', 'expired', 'cancelled'])
    if keyword:
        base_bounties = base_bounties.filter(raw_data__icontains=keyword)
    eligible_bounties = base_bounties.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=60)))
    eligible_bounties = eligible_bounties.exclude(interested__isnull=True)
    completed_bounties = eligible_bounties.filter(idx_status__in=['done']).count()
    not_completed_bounties = eligible_bounties.filter(idx_status__in=['expired', 'cancelled']).count()
    total_bounties = completed_bounties + not_completed_bounties

    try:
        return ((completed_bounties * 1.0 / total_bounties)) * 100
    except ZeroDivisionError:
        return 0


def get_funder_receiver_stats(keyword):
    from dashboard.models import Bounty, BountyFulfillment, Tip
    base_bounties = Bounty.objects.current().filter(network='mainnet')
    if keyword:
        base_bounties = base_bounties.filter(raw_data__icontains=keyword)

    eligible_bounties = base_bounties
    eligible_bounty_fulfillments = BountyFulfillment.objects.filter(bounty__in=base_bounties)
    eligible_tips = Tip.objects.filter(network='mainnet')

    bounty_funders = list(eligible_bounties.values_list('bounty_owner_address', flat=True))
    tip_funders = list(eligible_tips.values_list('from_address', flat=True))
    tip_recipients = list(eligible_tips.values_list('receive_address', flat=True))
    bounty_recipients = list(eligible_bounty_fulfillments.values_list('fulfiller_address', flat=True))

    num_funders = len(set(bounty_funders + tip_funders))
    num_recipients = len(set(bounty_recipients + tip_recipients))
    num_transactions = eligible_tips.count() + eligible_bounties.count()

    return {
        'funders': num_funders,
        'recipients': num_recipients,
        'transactions': num_transactions,
    }


def get_base_done_bounties(keyword):
    from dashboard.models import Bounty
    base_bounties = Bounty.objects.current().filter(network='mainnet', idx_status__in=['done', 'expired', 'cancelled'])
    if keyword:
        base_bounties = base_bounties.filter(raw_data__icontains=keyword)
    return base_bounties


def is_valid_bounty_for_headline_hourly_rate(bounty):
    hourly_rate = bounty.hourly_rate
    if None is hourly_rate:
        return False

    # smaller bounties were skewing the results
    min_hours = 3
    min_value_usdt = 300
    if bounty.value_in_usdt < min_value_usdt:
        return False
    for ful in bounty.fulfillments.filter(accepted=True):
        if ful.fulfiller_hours_worked and ful.fulfiller_hours_worked < min_hours:
            return False

    return True


def get_hourly_rate_distribution(keyword, bounty_value_range=None, methodology=None):
    if not methodology:
        methodology = 'quartile' if not keyword else 'minmax'
    base_bounties = get_base_done_bounties(keyword)
    if bounty_value_range:
        base_bounties = base_bounties.filter(_val_usd_db__lt=bounty_value_range[1], _val_usd_db__gt=bounty_value_range[0])
        hourly_rates = [ele.hourly_rate for ele in base_bounties if ele.hourly_rate is not None]
        print(bounty_value_range, len(hourly_rates))
    else:
        hourly_rates = [ele.hourly_rate for ele in base_bounties if is_valid_bounty_for_headline_hourly_rate(ele)]
    if len(hourly_rates) == 1:
        return f"${round(hourly_rates[0], 2)}"
    if len(hourly_rates) < 2:
        return ""
    if methodology == 'median_stdddev':
        stddev_divisor = 1
        median = int(statistics.median(hourly_rates))
        stddev = int(statistics.stdev(hourly_rates))
        min_hourly_rate = median - int(stddev/stddev_divisor)
        max_hourly_rate = median + int(stddev/stddev_divisor)
    elif methodology == 'quartile':
        hourly_rates.sort()
        num_quarters = 4
        first_quarter = int(len(hourly_rates)/num_quarters)
        third_quarter = first_quarter * (num_quarters-1)
        min_hourly_rate = int(hourly_rates[first_quarter])
        max_hourly_rate = int(hourly_rates[third_quarter])
    elif methodology == 'hardcode':
        min_hourly_rate = '15'
        max_hourly_rate = '120'
    else:
        min_hourly_rate = int(min(hourly_rates)) if len(hourly_rates) else 'n/a'
        max_hourly_rate = int(max(hourly_rates)) if len(hourly_rates) else 'n/a'
    return f'${min_hourly_rate} - ${max_hourly_rate}'


def get_bounty_median_turnaround_time(func='turnaround_time_started', keyword=None):
    base_bounties = get_base_done_bounties(keyword)
    eligible_bounties = base_bounties.exclude(idx_status='open') \
        .filter(created_on__gt=(timezone.now() - timezone.timedelta(days=60)))
    pickup_time_hours = []
    for bounty in eligible_bounties:
        tat = getattr(bounty, func)
        if tat:
            pickup_time_hours.append(tat / 60 / 60)

    pickup_time_hours.sort()
    try:
        return statistics.median(pickup_time_hours)
    except statistics.StatisticsError:
        return 0


def build_stat_results(keyword=None):
    timeout = 60 * 60 * 24
    key_salt = '3'
    key = f'build_stat_results_{keyword}_{key_salt}'
    try:
        results = cache.get(key)
    except CacheMiss:
        results = None
    if results and not settings.DEBUG:
        return results

    results = build_stat_results_helper(keyword)
    cache.set(key, results, timeout)

    return results


def get_bounty_history(keyword=None, cumulative=True):
    bh = [
        ['', 'Tips',  'Open / Available',  'Started / In Progress',  'Completed', 'Cancelled'],
    ]
    initial_stats = [
        ["December 2017", 2011, 903, 2329, 5534, 1203],
        ["January 2018", 5093, 1290, 1830, 15930, 1803],
        ["February 2018", 7391, 6903, 4302, 16302, 2390],
        ["March 2018", 8302, 5349, 5203, 26390, 3153],
        ["April 2018", 10109, 6702, 4290, 37342, 4281],
    ]
    if not keyword:
        bh = bh + initial_stats
    for year in range(2018, 2025):
        months = range(1, 12)
        if year == 2018:
            months = range(6, 12)
        for month in months:
            day_of_month = 3 if year == 2018 and month < 7 else 1
            then = timezone.datetime(year, month, day_of_month).replace(tzinfo=pytz.UTC)
            if then < timezone.now():
                label = (then - timezone.timedelta(days=2)).strftime("%B %Y")
                row = get_bounty_history_row(label, then, keyword)
                bh.append(row)

    if timezone.now().day > 10:
        # get current month date to month
        label = timezone.now().strftime("%B %Y") + " (MTD)"
        row = get_bounty_history_row(label, timezone.now(), keyword)
        bh.append(row)

    # adjust monthly totals
    if not cumulative:
        new_bh = bh.copy()
        for i in range(1, len(bh)):
            for k in range(1, len(bh[i])):
                try:
                    last_stat = int(bh[i-1][k])
                except:
                    last_stat = 0
                diff = bh[i][k] - last_stat
                new_bh[i][k] = diff
        return new_bh

    return bh


def build_stat_results_helper(keyword=None):
    """Buidl the results page context.

    Args:
        keyword (str): The keyword to build statistic results.
    """
    from dashboard.models import Bounty, Tip
    context = {
        'active': 'results',
        'title': _('Results'),
        'card_desc': _('Gitcoin is transparent by design.  Here are some stats about our core bounty product.'),
    }
    pp = PerformanceProfiler()
    pp.profile_time('start')
    base_alumni = Alumni.objects.all().cache()
    base_bounties = Bounty.objects.current().filter(network='mainnet').cache()
    base_leaderboard = LeaderboardRank.objects.all().cache()

    pp.profile_time('filters')
    if keyword:
        base_email_subscribers = EmailSubscriber.objects.filter(keywords__icontains=keyword).cache()
        base_profiles = base_email_subscribers.select_related('profile')
        base_bounties = base_bounties.filter(raw_data__icontains=keyword).cache()
        profile_pks = base_profiles.values_list('profile', flat=True)
        profile_usernames = base_profiles.values_list('profile__handle', flat=True)
        profile_usernames = list(profile_usernames) + list([bounty.github_repo_name for bounty in base_bounties])
        base_alumni = base_alumni.filter(profile__in=profile_pks)
        base_leaderboard = base_leaderboard.filter(github_username__in=profile_usernames)

    context['alumni_count'] = base_alumni.count()
    pp.profile_time('alumni')
    context['count_open'] = base_bounties.filter(network='mainnet', idx_status__in=['open']).count()
    context['count_started'] = base_bounties.filter(
        network='mainnet', idx_status__in=['started', 'submitted']
    ).count()
    context['count_done'] = base_bounties.filter(network='mainnet', idx_status__in=['done']).count()

    total_count = context['count_started'] + context['count_open'] + context['count_done']
    context['pct_done'] = round(100 * context['count_done'] / total_count)
    context['pct_started'] = round(100 * context['count_started'] / total_count)
    context['pct_open'] = round(100 * context['count_open'] / total_count)

    pp.profile_time('count_*')

    # Leaderboard
    num_to_show = 50
    context['top_orgs'] = base_leaderboard.filter(active=True, leaderboard='quarterly_orgs') \
        .order_by('rank').values_list('github_username', flat=True)[0:num_to_show]
    pp.profile_time('orgs')
    context['top_coders'] = base_leaderboard.filter(active=True, leaderboard='quarterly_earners') \
        .order_by('rank').values_list('github_username', flat=True)[0:num_to_show]
    pp.profile_time('orgs')

    # community size
    _key = 'email_subscriberse' if not keyword else f"subscribers_with_skill_{keyword}"
    base_stats = Stat.objects.filter(key=_key).order_by('-pk').cache()
    context['members_history'], context['slack_ticks'] = get_history(base_stats, "Members")

    pp.profile_time('Stats1')

    # jdi history
    key = f'joe_dominance_index_30_{keyword}_value' if keyword else 'joe_dominance_index_30_value'
    base_stats = Stat.objects.filter(
        key=key,
        ).order_by('-pk').cache()
    num_months = int((timezone.now() - timezone.datetime(2017, 10, 1).replace(tzinfo=pytz.UTC)).days/30)
    context['jdi_history'], __ = get_history(base_stats, 'Percentage', num_months)

    pp.profile_time('Stats2')

    # bounties history
    cumulative = False
    context['bounty_history'] = json.dumps(get_bounty_history(keyword, cumulative))
    pp.profile_time('bounty_history')

    # Bounties
    completion_rate = get_completion_rate(keyword)
    funder_receiver_stats = get_funder_receiver_stats(keyword)
    context['funders'] = funder_receiver_stats['funders']
    context['transactions'] = funder_receiver_stats['transactions']
    context['recipients'] = funder_receiver_stats['recipients']
    context['audience'] = json.loads(context['members_history'])[-1][1]
    pp.profile_time('completion_rate')
    bounty_abandonment_rate = round(100 - completion_rate, 1)
    total_bounties_usd = sum(base_bounties.exclude(idx_status__in=['expired', 'cancelled', 'canceled', 'unknown']).values_list('_val_usd_db', flat=True))
    total_tips_usd = sum([
        tip.value_in_usdt
        for tip in Tip.objects.filter(network='mainnet').exclude(txid='').cache() if tip.value_in_usdt
    ])
    context['universe_total_usd'] = float(total_bounties_usd) + float(total_tips_usd)
    pp.profile_time('universe_total_usd')
    context['max_bounty_history'] = float(context['universe_total_usd']) * .7
    context['bounty_abandonment_rate'] = bounty_abandonment_rate
    bounty_average_turnaround = round(get_bounty_median_turnaround_time('turnaround_time_submitted', keyword) / 24, 1)
    context['bounty_average_turnaround'] = f'{bounty_average_turnaround} days'
    pp.profile_time('bounty_average_turnaround')
    context['hourly_rate_distribution'] = get_hourly_rate_distribution(keyword)
    context['hourly_rate_distribution_by_range'] = {}
    usd_value_ranges = [[10, 50], [50, 150], [150, 500], [500, 1500], [1500, 5000], [5000, 50000]]
    for val_range in usd_value_ranges:
        low = val_range[0] if val_range[0] < 1000 else f"{round(val_range[0]/1000,1)}k"
        high = val_range[1] if val_range[1] < 1000 else f"{round(val_range[1]/1000,1)}k"
        key = f"${low} to ${high}"
        context['hourly_rate_distribution_by_range'][key] = get_hourly_rate_distribution(keyword, val_range, 'quartile')
    context['skill_rate_distribution_by_range'] = {}
    for programming_language in programming_languages:
        context['skill_rate_distribution_by_range'][programming_language] = get_hourly_rate_distribution(programming_language, None, 'quartile')

    context['bounty_claimed_completion_rate'] = completion_rate
    context['bounty_median_pickup_time'] = round(
        get_bounty_median_turnaround_time('turnaround_time_started', keyword), 1)
    pp.profile_time('bounty_median_pickup_time')
    pp.profile_time('final')
    context['keyword'] = keyword
    context['title'] = f"{keyword.capitalize() if keyword else ''} Results"
    context['programming_languages'] = ['All'] + programming_languages
    return context
