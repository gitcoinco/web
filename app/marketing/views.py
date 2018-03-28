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
from __future__ import unicode_literals

import json

from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email
from django.db.models import Max
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils import timezone

from chartit import Chart, DataPool
from dashboard.models import Profile, UserAction
from marketing.models import (
    EmailEvent, EmailSubscriber, GithubEvent, Keyword, LeaderboardRank, SlackPresence, SlackUser, Stat,
)
from marketing.utils import get_or_save_email_subscriber
from retail.helpers import get_ip


def filter_types(types, _filters):
    return_me = []
    for t in types:
        add = False
        for f in _filters:
            if f in t:
                add = True
        if add:
            return_me.append(t)

    return return_me


@staff_member_required
def stats(request):
    # get param
    _filter = request.GET.get('filter')
    rollup = request.GET.get('rollup')
    _format = request.GET.get('format', 'chart')

    # types
    types = list(Stat.objects.distinct('key').values_list('key', flat=True))
    types.sort()

    # filters
    if _filter == 'Activity':
        _filters = [
            'tip',
            'bount'
        ]
        types = filter_types(types, _filters)
    if _filter == 'Marketing':
        _filters = [
            'slack',
            'email',
            'whitepaper',
            'twitter'
        ]
        types = filter_types(types, _filters)
    if _filter == 'KPI':
        _filters = [
            'browser_ext_chrome',
            'medium_subscribers',
            'github_stargazers_count',
            'slack_users',
            'email_subscribers_active',
            'bounties_open',
            'bounties_ful',
            'joe_dominance_index_30_count',
            'joe_dominance_index_30_value',
            'turnaround_time_hours_30_days_back',
            'tips',
            'twitter',
            'user_action_Login',
        ]
        types = filter_types(types, _filters)

    # params
    params = {
        'format': _format,
        'types': types,
        'chart_list': [],
        'filter_params': f"?filter={_filter}&format={_format}&rollup={rollup}",
        'tables': {},
    }

    for t in types:

        # get data
        source = Stat.objects.filter(key=t)
        if rollup == 'daily':
            source = source.filter(created_on__hour=1)
            source = source.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=30)))
        elif rollup == 'weekly':
            source = source.filter(created_on__hour=1, created_on__week_day=1)
            source = source.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=30*3)))
        else:
            source = source.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=2)))

        if source.count():
            # tables
            params['tables'][t] = source

            # charts
            # compute avg
            total = 0
            count = source.count() - 1
            avg = "NA"
            if count > 1:
                for i in range(0, count):
                    total += (source[i+1].val - source[i].val)
                avg = round(total / count, 1)
                avg = str("+{}".format(avg) if avg > 0 else avg)

            chartdata = DataPool(series=[{
                'options': {'source': source},
                'terms': [
                    'created_on',
                    'val'
                ]}])

            cht = Chart(
                datasource=chartdata,
                series_options=[{
                    'options': {
                        'type': 'line',
                        'stacking': False
                    },
                    'terms': {
                        'created_on': ['val']
                    }
                }],
                chart_options={
                    'title': {
                        'text': f'{t} trend ({avg} avg)'
                    },
                    'xAxis': {
                        'title': {
                            'text': 'Time'
                        }
                    }
                })
            params['chart_list'].append(cht)

    types = params['tables'].keys()
    params['chart_list_str'] = ",".join(types)
    params['types'] = types
    return TemplateResponse(request, 'stats.html', params)


def cohort_helper_users(start_time, end_time, data_source):
    if 'profile' in data_source:
        users = Profile.objects.filter(created_on__gte=start_time, created_on__lt=end_time).exclude(github_access_token='').distinct()
    elif data_source == 'slack-online':
        users = SlackUser.objects.filter(created_on__gte=start_time, created_on__lt=end_time).distinct()
    else:
        users = EmailSubscriber.objects.filter(created_on__gte=start_time, created_on__lt=end_time).distinct()
    return users


def cohort_helper_num(inner_start_time, inner_end_time, data_source, users):
    if 'profile' in data_source:
        if data_source == 'profile-githubinteraction':
            num = GithubEvent.objects.filter(
                profile__in=users,
                created_on__gte=inner_start_time,
                created_on__lt=inner_end_time,
                ).distinct('profile').count()
        else:
            event = 'start_work'
            if data_source == 'profile-login':
                event = 'Login'
            if data_source == 'profile-new_bounty':
                event = 'new_bounty'
            num = UserAction.objects.filter(
                profile__in=users,
                created_on__gte=inner_start_time,
                created_on__lt=inner_end_time,
                action=event,
                ).distinct('profile').count()
    elif data_source == 'slack-online':
        num = SlackPresence.objects.filter(
            slackuser__in=users,
            created_on__gte=inner_start_time,
            created_on__lt=inner_end_time,
            status='active',
            ).distinct('slackuser').count()
    else:
        event = data_source.split('-')[1]
        num = EmailEvent.objects.filter(
            email__in=users.values_list('email', flat=True),
            created_on__gte=inner_start_time,
            created_on__lt=inner_end_time,
            event=event,
            ).distinct('email').count()
    return num


def cohort_helper_timedelta(i, period_size):
    if period_size == 'months':
        return {'weeks': 4*i}
    elif period_size == 'quarters':
        return {'weeks': 4*3*i}
    else:
        return {period_size: i}


@staff_member_required
def cohort(request):
    cohorts = {}

    data_source = request.GET.get('data_source', 'Slack')
    num_periods = request.GET.get('num_periods', 10)
    period_size = request.GET.get('period_size', 'weeks')
    kwargs = {}

    for i in range(1, num_periods):
        start_time = timezone.now() - timezone.timedelta(**cohort_helper_timedelta(i, period_size))
        end_time = timezone.now() - timezone.timedelta(**cohort_helper_timedelta(i-1, period_size))
        users = cohort_helper_users(start_time, end_time, data_source)
        num_entries = users.count()
        usage_by_time_period = {}
        for k in range(1, i):
            inner_start_time = timezone.now() - timezone.timedelta(**cohort_helper_timedelta(k, period_size))
            inner_end_time = timezone.now() - timezone.timedelta(**cohort_helper_timedelta(k-1, period_size))
            num = cohort_helper_num(inner_start_time, inner_end_time, data_source, users)
            pct = round(num/num_entries, 2) if num_entries else 0
            usage_by_time_period[k] = {
                'num': num,
                'pct_float': pct,
                'pct_int': int(pct * 100),
            }
        cohorts[i] = {
            'num': num_entries,
            'start_time': start_time,
            'end_time': end_time,
            'cohort_progression': usage_by_time_period,
        }

    params = {
        'title': "Cohort Analysis",
        'cohorts': cohorts,
        'title_rows': range(1, num_periods-1),
        'args': {
            'data_source': data_source,
            'num_periods': num_periods,
            'period_size': period_size,
        }
    }
    return TemplateResponse(request, 'cohort.html', params)


def email_settings(request, key):
    # handle 'noinput' case
    es = EmailSubscriber.objects.none()
    email = ''
    level = ''
    msg = ''
    if not key:
        email = request.session.get('email', '')
        if not email:
            github_handle = request.session.get('handle', '')
            profiles = Profile.objects.filter(handle__iexact=github_handle).exclude(email='')
            if profiles.exists():
                email = profiles.first()
        es = EmailSubscriber.objects.filter(email__iexact=email)
        if not es.exists():
            raise Http404
    else:
        es = EmailSubscriber.objects.filter(priv=key)
        if es.exists():
            email = es.first().email
            level = es.first().preferences.get('level', False)
        else:
            raise Http404
    es = es.first()
    if request.POST.get('email', False):
        level = request.POST.get('level')
        comments = request.POST.get('comments')[:255]
        email = request.POST.get('email')
        github = request.POST.get('github')
        print(es.github)
        keywords = request.POST.get('keywords').split(',')
        validation_passed = True
        try:
            validate_email(email)
        except Exception as e:
            print(e)
            validation_passed = False
            msg = 'Invalid Email'

        if level not in ['lite', 'lite1', 'regular', 'nothing']:
            validation_passed = False
            msg = 'Invalid Level'
        if validation_passed:
            key = get_or_save_email_subscriber(email, 'settings')
            es = EmailSubscriber.objects.get(priv=key)
            es.preferences['level'] = level
            es.metadata['comments'] = comments
            es.github = github
            es.keywords = keywords
            ip = get_ip(request)
            es.active = level != 'nothing'
            es.newsletter = level in ['regular', 'lite1']
            if not es.metadata.get('ip', False):
                es.metadata['ip'] = [ip]
            else:
                es.metadata['ip'].append(ip)

            es.save()
            msg = "Updated your preferences.  "
    context = {
        'nav': 'internal',
        'active': 'email_settings',
        'title': 'Email Settings',
        'es': es,
        'keywords': ",".join(es.keywords),
        'msg': msg,
        'autocomplete_keywords': json.dumps(
            [str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'email_settings.html', context)


def _leaderboard(request):
    return leaderboard(request, '')


def leaderboard(request, key=''):
    """Display the leaderboard for top earning or paying profiles.

    Args:
        key (str): The leaderboard display type. Defaults to: quarterly_earners.

    Returns:
        TemplateResponse: The leaderboard template response.

    """
    if not key:
        key = 'quarterly_earners'

    titles = {
        'quarterly_payers': 'Top Payers',
        'quarterly_earners': 'Top Earners',
        #        'weekly_fulfilled': 'Weekly Leaderboard: Fulfilled Funded Issues',
        #        'weekly_all': 'Weekly Leaderboard: All Funded Issues',
        #        'monthly_fulfilled': 'Monthly Leaderboard',
        #        'monthly_all': 'Monthly Leaderboard: All Funded Issues',
        #        'yearly_fulfilled': 'Yearly Leaderboard: Fulfilled Funded Issues',
        #        'yearly_all': 'Yearly Leaderboard: All Funded Issues',
        #        'all_fulfilled': 'All-Time Leaderboard: Fulfilled Funded Issues',
        #        'all_all': 'All-Time Leaderboard: All Funded Issues',
        # TODO - also include options for weekly, yearly, and all cadences of earning
    }
    if key not in titles.keys():
        raise Http404

    title = titles[key]
    leadeboardranks = LeaderboardRank.objects.filter(active=True, leaderboard=key)
    amount = leadeboardranks.values_list('amount').annotate(Max('amount')).order_by('-amount')
    items = leadeboardranks.order_by('-amount')
    top_earners = ''

    if amount:
        amount_max = amount[0][0]
        top_earners = leadeboardranks.order_by('-amount')[0:3].values_list('github_username', flat=True)
        top_earners = ['@' + username for username in top_earners]
        top_earners = f'The top earners of this period are {", ".join(top_earners)}'
    else:
        amount_max = 0

    context = {
        'items': items,
        'titles': titles,
        'selected': title,
        'title': f'Leaderboard: {title}',
        'card_title': f'Leaderboard: {title}',
        'card_desc': f'See the most valued members in the Gitcoin community this month. {top_earners}',
        'action_past_tense': 'Transacted' if 'submitted' in key else 'bountied',
        'amount_max': amount_max,
        'podium_items': items[:3] if items else []
    }
    return TemplateResponse(request, 'leaderboard.html', context)
