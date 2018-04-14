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
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db.models import Max
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.utils import sync_profile
from chartit import Chart, DataPool
from dashboard.models import Bounty, Profile, UserAction
from marketing.mails import new_feedback
from marketing.models import (
    EmailEvent, EmailSubscriber, GithubEvent, Keyword, LeaderboardRank, SlackPresence, SlackUser, Stat,
)
import math
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


def data_viz_helper_get_data_responses(request, _type):
    data_dict = {}
    network = 'mainnet'
    for bounty in Bounty.objects.filter(network=network, web3_type='bounties_network', current_bounty=True):

        if _type == 'status_progression':
            max_size = 12
            value = 1
            if not value:
                continue;
            response = []
            prev_bounties = Bounty.objects.filter(standard_bounties_id=bounty.standard_bounties_id, network=network).exclude(pk=bounty.pk).order_by('created_on')
            if prev_bounties.exists() and prev_bounties.first().status == 'started':
                response.append('open') #mock for status changes not mutating status
            last_bounty_status = None
            for ibounty in prev_bounties:
                if last_bounty_status != ibounty.status:
                    response.append(ibounty.status)
                last_bounty_status = ibounty.status
            if bounty.status != last_bounty_status:
                response.append(bounty.status)
            response = response[0:max_size]
            while len(response) < max_size:
                response.append('_')

        if _type == 'repos':
            value = bounty.value_in_usdt_then

            response = [
                bounty.org_name.replace('-',''),
                bounty.github_repo_name.replace('-',''),
                str(bounty.github_issue_number),
            ]

        if _type == 'fulfillers':
            response = []
            if bounty.status == 'done':
                for fulfillment in bounty.fulfillments.filter(accepted=1):
                    value = bounty.value_in_usdt_then

                    response = [
                        fulfillment.fulfiller_github_username.replace('-','')
                    ]

        if _type == 'funders':
            value = bounty.value_in_usdt_then
            response = []
            if bounty.bounty_owner_github_username and value:
                response = [
                    bounty.bounty_owner_github_username.replace('-','')
                ]

        if response:
            response = "-".join(response)
            if response in data_dict.keys():
                data_dict[response] += value
            else:
                data_dict[response] = value

    return data_dict


@staff_member_required
def viz_spiral(request, key='email_open'):
    stats = Stat.objects.filter(created_on__hour=1)
    type_options = stats.distinct('key').values_list('key', flat=True)
    stats = stats.filter(key=key).order_by('created_on')
    params = {
        'stats': stats,
        'key': key,
        'page_route': 'spiral',
        'type_options': type_options,
        'viz_type': key,
    }
    return TemplateResponse(request, 'dataviz/spiral.html', params)


@staff_member_required
def viz_heatmap(request, key='email_open'):
    stats = Stat.objects.filter(created_on__lt=timezone.now(), created_on__gt=(timezone.now() - timezone.timedelta(weeks=2)))
    type_options = stats.distinct('key').values_list('key', flat=True)
    stats = stats.filter(key=key).order_by('-created_on')

    if request.GET.get('data'):
        _max = max([stat.val_since_hour for stat in stats])
        output = {
            # {"timestamp": "2014-10-16T22:00:00", "value": {"PM2.5": 61.92}}
            "data": [{
                'timestamp': stat.created_on.strftime("%Y-%m-%dT%H:00:00"),
                'value': {"PM2.5": stat.val_since_hour * 800.0 / _max},
            } for stat in stats]
        }
        ## output = {"data":[{"timestamp": "2014-09-25T00:00:00", "value": {"PM2.5": 30.22}}, {"timestamp": "2014-09-25T01:00:00", "value": {"PM2.5": 41.61}}, {"timestamp": "2014-09-25T02:00:00", "value": {"PM2.5": 50.71}}, {"timestamp": "2014-09-25T03:00:00", "value": {"PM2.5": 57.34}}, {"timestamp": "2014-09-25T04:00:00", "value": {"PM2.5": 79.64}}, {"timestamp": "2014-09-25T05:00:00", "value": {"PM2.5": 76.93}}, {"timestamp": "2014-09-25T06:00:00", "value": {"PM2.5": 106.45}}, {"timestamp": "2014-09-25T07:00:00", "value": {"PM2.5": 79.72}}, {"timestamp": "2014-09-25T08:00:00", "value": {"PM2.5": 74.23}}, {"timestamp": "2014-09-25T09:00:00", "value": {"PM2.5": 90.48}}, {"timestamp": "2014-09-25T10:00:00", "value": {"PM2.5": 94.74}}, {"timestamp": "2014-09-25T11:00:00", "value": {"PM2.5": 85.97}}, {"timestamp": "2014-09-25T12:00:00", "value": {"PM2.5": 69.23}}, {"timestamp": "2014-09-25T13:00:00", "value": {"PM2.5": 82.63}}, {"timestamp": "2014-09-25T14:00:00", "value": {"PM2.5": 244.89}}, {"timestamp": "2014-09-25T15:00:00", "value": {"PM2.5": 363.18}}, {"timestamp": "2014-09-25T16:00:00", "value": {"PM2.5": 397.89}}, {"timestamp": "2014-09-25T17:00:00", "value": {"PM2.5": 344.67}}, {"timestamp": "2014-09-25T18:00:00", "value": {"PM2.5": 328.47}}, {"timestamp": "2014-09-25T19:00:00", "value": {"PM2.5": 305.47}}, {"timestamp": "2014-09-25T20:00:00", "value": {"PM2.5": 344.87}}, {"timestamp": "2014-09-25T21:00:00", "value": {"PM2.5": 336.82}}, {"timestamp": "2014-09-25T22:00:00", "value": {"PM2.5": 291.29}}, {"timestamp": "2014-09-25T23:00:00", "value": {"PM2.5": 260.16}}, {"timestamp": "2014-09-26T00:00:00", "value": {"PM2.5": 251.12}}, {"timestamp": "2014-09-26T01:00:00", "value": {"PM2.5": 213.73}}, {"timestamp": "2014-09-26T02:00:00", "value": {"PM2.5": 188.96}}, {"timestamp": "2014-09-26T03:00:00", "value": {"PM2.5": 170.37}}, {"timestamp": "2014-09-26T04:00:00", "value": {"PM2.5": 152.53}}, {"timestamp": "2014-09-26T05:00:00", "value": {"PM2.5": 145.44}}, {"timestamp": "2014-09-26T06:00:00", "value": {"PM2.5": 144.09}}, {"timestamp": "2014-09-26T07:00:00", "value": {"PM2.5": 169.71}}, {"timestamp": "2014-09-26T08:00:00", "value": {"PM2.5": 207.33}}, {"timestamp": "2014-09-26T09:00:00", "value": {"PM2.5": 208.24}}, {"timestamp": "2014-09-26T10:00:00", "value": {"PM2.5": 215.42}}, {"timestamp": "2014-09-26T11:00:00", "value": {"PM2.5": 208.86}}, {"timestamp": "2014-09-26T12:00:00", "value": {"PM2.5": 239.67}}, {"timestamp": "2014-09-26T13:00:00", "value": {"PM2.5": 242.51}}, {"timestamp": "2014-09-26T14:00:00", "value": {"PM2.5": 252.05}}, {"timestamp": "2014-09-26T15:00:00", "value": {"PM2.5": 239.24}}, {"timestamp": "2014-09-26T16:00:00", "value": {"PM2.5": 254.14}}, {"timestamp": "2014-09-26T17:00:00", "value": {"PM2.5": 287.29}}, {"timestamp": "2014-09-26T18:00:00", "value": {"PM2.5": 280.43}}, {"timestamp": "2014-09-26T19:00:00", "value": {"PM2.5": 294.95}}, {"timestamp": "2014-09-26T20:00:00", "value": {"PM2.5": 269.68}}, {"timestamp": "2014-09-26T21:00:00", "value": {"PM2.5": 105.62}}, {"timestamp": "2014-09-26T22:00:00", "value": {"PM2.5": 94.32}}, {"timestamp": "2014-09-26T23:00:00", "value": {"PM2.5": 66.55}}, {"timestamp": "2014-09-27T00:00:00", "value": {"PM2.5": 76.33}}, {"timestamp": "2014-09-27T01:00:00", "value": {"PM2.5": 27.83}}, {"timestamp": "2014-09-27T02:00:00", "value": {"PM2.5": 62.01}}, {"timestamp": "2014-09-27T03:00:00", "value": {"PM2.5": 43.96}}, {"timestamp": "2014-09-27T04:00:00", "value": {"PM2.5": 26.89}}, {"timestamp": "2014-09-27T05:00:00", "value": {"PM2.5": 26.23}}, {"timestamp": "2014-09-27T06:00:00", "value": {"PM2.5": 21.32}}, {"timestamp": "2014-09-27T07:00:00", "value": {"PM2.5": 20.81}}, {"timestamp": "2014-09-27T08:00:00", "value": {"PM2.5": 24.04}}, {"timestamp": "2014-09-27T09:00:00", "value": {"PM2.5": 21.65}}, {"timestamp": "2014-09-27T10:00:00", "value": {"PM2.5": 10.51}}, {"timestamp": "2014-09-27T11:00:00", "value": {"PM2.5": 8.92}}, {"timestamp": "2014-09-27T12:00:00", "value": {"PM2.5": 6.97}}, {"timestamp": "2014-09-27T13:00:00", "value": {"PM2.5": 4.3}}, {"timestamp": "2014-09-27T14:00:00", "value": {"PM2.5": 5.38}}, {"timestamp": "2014-09-27T15:00:00", "value": {"PM2.5": 12.7}}, {"timestamp": "2014-09-27T16:00:00", "value": {"PM2.5": 11.07}}, {"timestamp": "2014-09-27T17:00:00", "value": {"PM2.5": 26.12}}, {"timestamp": "2014-09-27T18:00:00", "value": {"PM2.5": 155.54}}, {"timestamp": "2014-09-27T19:00:00", "value": {"PM2.5": 16.69}}, {"timestamp": "2014-09-27T20:00:00", "value": {"PM2.5": 10.73}}, {"timestamp": "2014-09-27T21:00:00", "value": {"PM2.5": 10.09}}, {"timestamp": "2014-09-27T22:00:00", "value": {"PM2.5": 17.9}}, {"timestamp": "2014-09-27T23:00:00", "value": {"PM2.5": 21.24}}, {"timestamp": "2014-09-28T00:00:00", "value": {"PM2.5": 22.61}}, {"timestamp": "2014-09-28T01:00:00", "value": {"PM2.5": 27.05}}, {"timestamp": "2014-09-28T02:00:00", "value": {"PM2.5": 24.34}}, {"timestamp": "2014-09-28T03:00:00", "value": {"PM2.5": 19.63}}, {"timestamp": "2014-09-28T04:00:00", "value": {"PM2.5": 26.33}}, {"timestamp": "2014-09-28T05:00:00", "value": {"PM2.5": 23.62}}, {"timestamp": "2014-09-28T06:00:00", "value": {"PM2.5": 21.46}}, {"timestamp": "2014-09-28T07:00:00", "value": {"PM2.5": 24.73}}, {"timestamp": "2014-09-28T08:00:00", "value": {"PM2.5": 44.34}}, {"timestamp": "2014-09-28T09:00:00", "value": {"PM2.5": 35.01}}, {"timestamp": "2014-09-28T10:00:00", "value": {"PM2.5": 33.54}}, {"timestamp": "2014-09-28T11:00:00", "value": {"PM2.5": 38.61}}, {"timestamp": "2014-09-28T12:00:00", "value": {"PM2.5": 80.41}}, {"timestamp": "2014-09-28T13:00:00", "value": {"PM2.5": 77.11}}, {"timestamp": "2014-09-28T14:00:00", "value": {"PM2.5": 74.43}}, {"timestamp": "2014-09-28T15:00:00", "value": {"PM2.5": 97.76}}, {"timestamp": "2014-09-28T16:00:00", "value": {"PM2.5": 121.23}}, {"timestamp": "2014-09-28T17:00:00", "value": {"PM2.5": 151.39}}, {"timestamp": "2014-09-28T18:00:00", "value": {"PM2.5": 145.58}}, {"timestamp": "2014-09-28T19:00:00", "value": {"PM2.5": 133.08}}, {"timestamp": "2014-09-28T20:00:00", "value": {"PM2.5": 111.6}}, {"timestamp": "2014-09-28T21:00:00", "value": {"PM2.5": 118.36}}, {"timestamp": "2014-09-28T22:00:00", "value": {"PM2.5": 117.77}}, {"timestamp": "2014-09-28T23:00:00", "value": {"PM2.5": 125.95}}, {"timestamp": "2014-09-29T00:00:00", "value": {"PM2.5": 126.74}}, {"timestamp": "2014-09-29T01:00:00", "value": {"PM2.5": 121.47}}, {"timestamp": "2014-09-29T02:00:00", "value": {"PM2.5": 113.75}}, {"timestamp": "2014-09-29T03:00:00", "value": {"PM2.5": 117.12}}, {"timestamp": "2014-09-29T04:00:00", "value": {"PM2.5": 130.76}}, {"timestamp": "2014-09-29T05:00:00", "value": {"PM2.5": 126.4}}, {"timestamp": "2014-09-29T06:00:00", "value": {"PM2.5": 136.94}}, {"timestamp": "2014-09-29T07:00:00", "value": {"PM2.5": 129.97}}, {"timestamp": "2014-09-29T08:00:00", "value": {"PM2.5": 155.04}}, {"timestamp": "2014-09-29T09:00:00", "value": {"PM2.5": 112.96}}, {"timestamp": "2014-09-29T10:00:00", "value": {"PM2.5": 23.58}}, {"timestamp": "2014-09-29T11:00:00", "value": {"PM2.5": 15.25}}, {"timestamp": "2014-09-29T12:00:00", "value": {"PM2.5": 14.04}}, {"timestamp": "2014-09-29T13:00:00", "value": {"PM2.5": 10.1}}, {"timestamp": "2014-09-29T14:00:00", "value": {"PM2.5": 6.55}}, {"timestamp": "2014-09-29T15:00:00", "value": {"PM2.5": 5.64}}, {"timestamp": "2014-09-29T16:00:00", "value": {"PM2.5": 6.75}}, {"timestamp": "2014-09-29T17:00:00", "value": {"PM2.5": 7.12}}, {"timestamp": "2014-09-29T18:00:00", "value": {"PM2.5": 8.91}}, {"timestamp": "2014-09-29T19:00:00", "value": {"PM2.5": 9.57}}, {"timestamp": "2014-09-29T20:00:00", "value": {"PM2.5": 12.11}}, {"timestamp": "2014-09-29T21:00:00", "value": {"PM2.5": 10.14}}, {"timestamp": "2014-09-29T22:00:00", "value": {"PM2.5": 7.79}}, {"timestamp": "2014-09-29T23:00:00", "value": {"PM2.5": 6.14}}, {"timestamp": "2014-09-30T00:00:00", "value": {"PM2.5": 18.59}}, {"timestamp": "2014-09-30T01:00:00", "value": {"PM2.5": 22.16}}, {"timestamp": "2014-09-30T02:00:00", "value": {"PM2.5": 16.92}}, {"timestamp": "2014-09-30T03:00:00", "value": {"PM2.5": 25.11}}, {"timestamp": "2014-09-30T04:00:00", "value": {"PM2.5": 40.97}}, {"timestamp": "2014-09-30T05:00:00", "value": {"PM2.5": 45.79}}, {"timestamp": "2014-09-30T06:00:00", "value": {"PM2.5": 36.7}}, {"timestamp": "2014-09-30T07:00:00", "value": {"PM2.5": 14.18}}, {"timestamp": "2014-09-30T08:00:00", "value": {"PM2.5": 24.86}}, {"timestamp": "2014-09-30T09:00:00", "value": {"PM2.5": 20.39}}, {"timestamp": "2014-09-30T10:00:00", "value": {"PM2.5": 19.79}}, {"timestamp": "2014-09-30T11:00:00", "value": {"PM2.5": 19.46}}, {"timestamp": "2014-09-30T12:00:00", "value": {"PM2.5": 31.15}}, {"timestamp": "2014-09-30T13:00:00", "value": {"PM2.5": 24.06}}, {"timestamp": "2014-09-30T14:00:00", "value": {"PM2.5": 30.12}}, {"timestamp": "2014-09-30T15:00:00", "value": {"PM2.5": 31.57}}, {"timestamp": "2014-09-30T16:00:00", "value": {"PM2.5": 34.88}}, {"timestamp": "2014-09-30T17:00:00", "value": {"PM2.5": 41.16}}, {"timestamp": "2014-09-30T18:00:00", "value": {"PM2.5": 47.41}}, {"timestamp": "2014-09-30T19:00:00", "value": {"PM2.5": 58.39}}, {"timestamp": "2014-09-30T20:00:00", "value": {"PM2.5": 42.18}}, {"timestamp": "2014-09-30T21:00:00", "value": {"PM2.5": 40.16}}, {"timestamp": "2014-09-30T22:00:00", "value": {"PM2.5": 39.45}}, {"timestamp": "2014-09-30T23:00:00", "value": {"PM2.5": 37.49}}, {"timestamp": "2014-10-01T00:00:00", "value": {"PM2.5": 42.77}}, {"timestamp": "2014-10-01T01:00:00", "value": {"PM2.5": 43.73}}, {"timestamp": "2014-10-01T02:00:00", "value": {"PM2.5": 41.56}}, {"timestamp": "2014-10-01T03:00:00", "value": {"PM2.5": 40.69}}, {"timestamp": "2014-10-01T04:00:00", "value": {"PM2.5": 42.65}}, {"timestamp": "2014-10-01T05:00:00", "value": {"PM2.5": 43.86}}, {"timestamp": "2014-10-01T06:00:00", "value": {"PM2.5": 40.06}}, {"timestamp": "2014-10-01T07:00:00", "value": {"PM2.5": 58.56}}, {"timestamp": "2014-10-01T08:00:00", "value": {"PM2.5": 57.51}}, {"timestamp": "2014-10-01T09:00:00", "value": {"PM2.5": 69.77}}, {"timestamp": "2014-10-01T10:00:00", "value": {"PM2.5": 76.35}}, {"timestamp": "2014-10-01T11:00:00", "value": {"PM2.5": 72.26}}, {"timestamp": "2014-10-01T12:00:00", "value": {"PM2.5": 95.8}}, {"timestamp": "2014-10-01T13:00:00", "value": {"PM2.5": 104.79}}, {"timestamp": "2014-10-01T14:00:00", "value": {"PM2.5": 93.45}}, {"timestamp": "2014-10-01T15:00:00", "value": {"PM2.5": 81.69}}, {"timestamp": "2014-10-01T16:00:00", "value": {"PM2.5": 88.27}}, {"timestamp": "2014-10-01T17:00:00", "value": {"PM2.5": 86.08}}, {"timestamp": "2014-10-01T18:00:00", "value": {"PM2.5": 78.72}}, {"timestamp": "2014-10-01T19:00:00", "value": {"PM2.5": 82.31}}, {"timestamp": "2014-10-01T20:00:00", "value": {"PM2.5": 73.06}}, {"timestamp": "2014-10-01T21:00:00", "value": {"PM2.5": 62.12}}, {"timestamp": "2014-10-01T22:00:00", "value": {"PM2.5": 54.43}}, {"timestamp": "2014-10-01T23:00:00", "value": {"PM2.5": 41.78}}, {"timestamp": "2014-10-02T00:00:00", "value": {"PM2.5": 34.93}}, {"timestamp": "2014-10-02T01:00:00", "value": {"PM2.5": 33.22}}, {"timestamp": "2014-10-02T02:00:00", "value": {"PM2.5": 33.72}}, {"timestamp": "2014-10-02T03:00:00", "value": {"PM2.5": 33.46}}, {"timestamp": "2014-10-02T04:00:00", "value": {"PM2.5": 25.31}}, {"timestamp": "2014-10-02T05:00:00", "value": {"PM2.5": 22.46}}, {"timestamp": "2014-10-02T06:00:00", "value": {"PM2.5": 22.94}}, {"timestamp": "2014-10-02T07:00:00", "value": {"PM2.5": 20.19}}, {"timestamp": "2014-10-02T08:00:00", "value": {"PM2.5": 26.69}}, {"timestamp": "2014-10-02T09:00:00", "value": {"PM2.5": 17.44}}, {"timestamp": "2014-10-02T10:00:00", "value": {"PM2.5": 14.73}}, {"timestamp": "2014-10-02T11:00:00", "value": {"PM2.5": 17.8}}, {"timestamp": "2014-10-02T12:00:00", "value": {"PM2.5": 19.19}}, {"timestamp": "2014-10-02T13:00:00", "value": {"PM2.5": 16.25}}, {"timestamp": "2014-10-02T14:00:00", "value": {"PM2.5": 18.47}}, {"timestamp": "2014-10-02T15:00:00", "value": {"PM2.5": 16.45}}, {"timestamp": "2014-10-02T16:00:00", "value": {"PM2.5": 30.11}}, {"timestamp": "2014-10-02T17:00:00", "value": {"PM2.5": 48.26}}, {"timestamp": "2014-10-02T18:00:00", "value": {"PM2.5": 38.79}}, {"timestamp": "2014-10-02T19:00:00", "value": {"PM2.5": 27.05}}, {"timestamp": "2014-10-02T20:00:00", "value": {"PM2.5": 14.22}}, {"timestamp": "2014-10-02T21:00:00", "value": {"PM2.5": 11.8}}, {"timestamp": "2014-10-02T22:00:00", "value": {"PM2.5": 10.11}}, {"timestamp": "2014-10-02T23:00:00", "value": {"PM2.5": 7.61}}, {"timestamp": "2014-10-03T00:00:00", "value": {"PM2.5": 8.89}}, {"timestamp": "2014-10-03T01:00:00", "value": {"PM2.5": 12.88}}, {"timestamp": "2014-10-03T02:00:00", "value": {"PM2.5": 19.39}}, {"timestamp": "2014-10-03T03:00:00", "value": {"PM2.5": 20.57}}, {"timestamp": "2014-10-03T04:00:00", "value": {"PM2.5": 18.02}}, {"timestamp": "2014-10-03T05:00:00", "value": {"PM2.5": 14.1}}, {"timestamp": "2014-10-03T06:00:00", "value": {"PM2.5": 10.78}}, {"timestamp": "2014-10-03T07:00:00", "value": {"PM2.5": 14.65}}, {"timestamp": "2014-10-03T08:00:00", "value": {"PM2.5": 17.8}}, {"timestamp": "2014-10-03T09:00:00", "value": {"PM2.5": 20.03}}, {"timestamp": "2014-10-03T10:00:00", "value": {"PM2.5": 18.75}}, {"timestamp": "2014-10-03T11:00:00", "value": {"PM2.5": 32.49}}, {"timestamp": "2014-10-03T12:00:00", "value": {"PM2.5": 21.53}}, {"timestamp": "2014-10-03T13:00:00", "value": {"PM2.5": 29.86}}, {"timestamp": "2014-10-03T14:00:00", "value": {"PM2.5": 54.58}}, {"timestamp": "2014-10-03T15:00:00", "value": {"PM2.5": 158.79}}, {"timestamp": "2014-10-03T16:00:00", "value": {"PM2.5": 201.58}}, {"timestamp": "2014-10-03T17:00:00", "value": {"PM2.5": 225.76}}, {"timestamp": "2014-10-03T18:00:00", "value": {"PM2.5": 276.68}}, {"timestamp": "2014-10-03T19:00:00", "value": {"PM2.5": 290.5}}, {"timestamp": "2014-10-03T20:00:00", "value": {"PM2.5": 296.66}}, {"timestamp": "2014-10-03T21:00:00", "value": {"PM2.5": 313.71}}, {"timestamp": "2014-10-03T22:00:00", "value": {"PM2.5": 329.96}}, {"timestamp": "2014-10-03T23:00:00", "value": {"PM2.5": 323.84}}, {"timestamp": "2014-10-04T00:00:00", "value": {"PM2.5": 311.63}}, {"timestamp": "2014-10-04T01:00:00", "value": {"PM2.5": 253.53}}, {"timestamp": "2014-10-04T02:00:00", "value": {"PM2.5": 195.69}}, {"timestamp": "2014-10-04T03:00:00", "value": {"PM2.5": 140.67}}, {"timestamp": "2014-10-04T04:00:00", "value": {"PM2.5": 111.06}}, {"timestamp": "2014-10-04T05:00:00", "value": {"PM2.5": 57.18}}, {"timestamp": "2014-10-04T06:00:00", "value": {"PM2.5": 50.87}}, {"timestamp": "2014-10-04T07:00:00", "value": {"PM2.5": 36.43}}, {"timestamp": "2014-10-04T08:00:00", "value": {"PM2.5": 26.89}}, {"timestamp": "2014-10-04T09:00:00", "value": {"PM2.5": 32.66}}, {"timestamp": "2014-10-04T10:00:00", "value": {"PM2.5": 28.13}}, {"timestamp": "2014-10-04T11:00:00", "value": {"PM2.5": 27.61}}, {"timestamp": "2014-10-04T12:00:00", "value": {"PM2.5": 23.81}}, {"timestamp": "2014-10-04T13:00:00", "value": {"PM2.5": 22.02}}, {"timestamp": "2014-10-04T14:00:00", "value": {"PM2.5": 57.46}}, {"timestamp": "2014-10-04T15:00:00", "value": {"PM2.5": 113.64}}, {"timestamp": "2014-10-04T16:00:00", "value": {"PM2.5": 160.12}}, {"timestamp": "2014-10-04T17:00:00", "value": {"PM2.5": 165.16}}, {"timestamp": "2014-10-04T18:00:00", "value": {"PM2.5": 173.02}}, {"timestamp": "2014-10-04T19:00:00", "value": {"PM2.5": 189.23}}, {"timestamp": "2014-10-04T20:00:00", "value": {"PM2.5": 196.8}}, {"timestamp": "2014-10-04T21:00:00", "value": {"PM2.5": 95.37}}, {"timestamp": "2014-10-04T22:00:00", "value": {"PM2.5": 61.04}}, {"timestamp": "2014-10-04T23:00:00", "value": {"PM2.5": 96.14}}, {"timestamp": "2014-10-05T00:00:00", "value": {"PM2.5": 159.21}}, {"timestamp": "2014-10-05T01:00:00", "value": {"PM2.5": 207.61}}, {"timestamp": "2014-10-05T02:00:00", "value": {"PM2.5": 248.96}}, {"timestamp": "2014-10-05T03:00:00", "value": {"PM2.5": 242.87}}, {"timestamp": "2014-10-05T04:00:00", "value": {"PM2.5": 249.19}}, {"timestamp": "2014-10-05T05:00:00", "value": {"PM2.5": 257.44}}, {"timestamp": "2014-10-05T06:00:00", "value": {"PM2.5": 100.41}}, {"timestamp": "2014-10-05T07:00:00", "value": {"PM2.5": 7.17}}, {"timestamp": "2014-10-05T08:00:00", "value": {"PM2.5": 16.69}}, {"timestamp": "2014-10-05T09:00:00", "value": {"PM2.5": 17.64}}, {"timestamp": "2014-10-05T10:00:00", "value": {"PM2.5": 4.41}}, {"timestamp": "2014-10-05T11:00:00", "value": {"PM2.5": 4.49}}, {"timestamp": "2014-10-05T12:00:00", "value": {"PM2.5": 3.34}}, {"timestamp": "2014-10-05T13:00:00", "value": {"PM2.5": 4.92}}, {"timestamp": "2014-10-05T14:00:00", "value": {"PM2.5": 3.15}}, {"timestamp": "2014-10-05T15:00:00", "value": {"PM2.5": 3.9}}, {"timestamp": "2014-10-05T16:00:00", "value": {"PM2.5": 4.24}}, {"timestamp": "2014-10-05T17:00:00", "value": {"PM2.5": 5.59}}, {"timestamp": "2014-10-05T18:00:00", "value": {"PM2.5": 10.31}}, {"timestamp": "2014-10-05T19:00:00", "value": {"PM2.5": 12.9}}, {"timestamp": "2014-10-05T20:00:00", "value": {"PM2.5": 8.41}}, {"timestamp": "2014-10-05T21:00:00", "value": {"PM2.5": 6.59}}, {"timestamp": "2014-10-05T22:00:00", "value": {"PM2.5": 5.58}}, {"timestamp": "2014-10-05T23:00:00", "value": {"PM2.5": 5.86}}, {"timestamp": "2014-10-06T00:00:00", "value": {"PM2.5": 5.76}}, {"timestamp": "2014-10-06T01:00:00", "value": {"PM2.5": 4.57}}, {"timestamp": "2014-10-06T02:00:00", "value": {"PM2.5": 15.34}}, {"timestamp": "2014-10-06T03:00:00", "value": {"PM2.5": 47.56}}, {"timestamp": "2014-10-06T04:00:00", "value": {"PM2.5": 14.69}}, {"timestamp": "2014-10-06T05:00:00", "value": {"PM2.5": 19.45}}, {"timestamp": "2014-10-06T06:00:00", "value": {"PM2.5": 26.48}}, {"timestamp": "2014-10-06T07:00:00", "value": {"PM2.5": 31.39}}, {"timestamp": "2014-10-06T08:00:00", "value": {"PM2.5": 31.24}}, {"timestamp": "2014-10-06T09:00:00", "value": {"PM2.5": 14.77}}, {"timestamp": "2014-10-06T10:00:00", "value": {"PM2.5": 15.32}}, {"timestamp": "2014-10-06T11:00:00", "value": {"PM2.5": 11.1}}, {"timestamp": "2014-10-06T12:00:00", "value": {"PM2.5": 9.58}}, {"timestamp": "2014-10-06T13:00:00", "value": {"PM2.5": 10.22}}, {"timestamp": "2014-10-06T14:00:00", "value": {"PM2.5": 12.62}}, {"timestamp": "2014-10-06T15:00:00", "value": {"PM2.5": 14.64}}, {"timestamp": "2014-10-06T16:00:00", "value": {"PM2.5": 16.44}}, {"timestamp": "2014-10-06T17:00:00", "value": {"PM2.5": 30.07}}, {"timestamp": "2014-10-06T18:00:00", "value": {"PM2.5": 37.81}}, {"timestamp": "2014-10-06T19:00:00", "value": {"PM2.5": 23.24}}, {"timestamp": "2014-10-06T20:00:00", "value": {"PM2.5": 24.93}}, {"timestamp": "2014-10-06T21:00:00", "value": {"PM2.5": 22.06}}, {"timestamp": "2014-10-06T22:00:00", "value": {"PM2.5": 22.0}}, {"timestamp": "2014-10-06T23:00:00", "value": {"PM2.5": 23.81}}, {"timestamp": "2014-10-07T00:00:00", "value": {"PM2.5": 35.09}}, {"timestamp": "2014-10-07T01:00:00", "value": {"PM2.5": 40.74}}, {"timestamp": "2014-10-07T02:00:00", "value": {"PM2.5": 42.5}}, {"timestamp": "2014-10-07T03:00:00", "value": {"PM2.5": 59.57}}, {"timestamp": "2014-10-07T04:00:00", "value": {"PM2.5": 56.78}}, {"timestamp": "2014-10-07T05:00:00", "value": {"PM2.5": 63.92}}, {"timestamp": "2014-10-07T06:00:00", "value": {"PM2.5": 69.31}}, {"timestamp": "2014-10-07T07:00:00", "value": {"PM2.5": 67.32}}, {"timestamp": "2014-10-07T08:00:00", "value": {"PM2.5": 78.97}}, {"timestamp": "2014-10-07T09:00:00", "value": {"PM2.5": 53.8}}, {"timestamp": "2014-10-07T10:00:00", "value": {"PM2.5": 51.59}}, {"timestamp": "2014-10-07T11:00:00", "value": {"PM2.5": 61.11}}, {"timestamp": "2014-10-07T12:00:00", "value": {"PM2.5": 77.53}}, {"timestamp": "2014-10-07T13:00:00", "value": {"PM2.5": 104.56}}, {"timestamp": "2014-10-07T14:00:00", "value": {"PM2.5": 97.35}}, {"timestamp": "2014-10-07T15:00:00", "value": {"PM2.5": 121.06}}, {"timestamp": "2014-10-07T16:00:00", "value": {"PM2.5": 189.34}}, {"timestamp": "2014-10-07T17:00:00", "value": {"PM2.5": 249.85}}, {"timestamp": "2014-10-07T18:00:00", "value": {"PM2.5": 273.11}}, {"timestamp": "2014-10-07T19:00:00", "value": {"PM2.5": 212.32}}, {"timestamp": "2014-10-07T20:00:00", "value": {"PM2.5": 205.69}}, {"timestamp": "2014-10-07T21:00:00", "value": {"PM2.5": 225.53}}, {"timestamp": "2014-10-07T22:00:00", "value": {"PM2.5": 266.97}}, {"timestamp": "2014-10-07T23:00:00", "value": {"PM2.5": 294.46}}, {"timestamp": "2014-10-08T00:00:00", "value": {"PM2.5": 310.99}}, {"timestamp": "2014-10-08T01:00:00", "value": {"PM2.5": 322.24}}, {"timestamp": "2014-10-08T02:00:00", "value": {"PM2.5": 333.67}}, {"timestamp": "2014-10-08T03:00:00", "value": {"PM2.5": 321.76}}, {"timestamp": "2014-10-08T04:00:00", "value": {"PM2.5": 331.7}}, {"timestamp": "2014-10-08T05:00:00", "value": {"PM2.5": 320.7}}, {"timestamp": "2014-10-08T06:00:00", "value": {"PM2.5": 309.12}}, {"timestamp": "2014-10-08T07:00:00", "value": {"PM2.5": 295.26}}, {"timestamp": "2014-10-08T08:00:00", "value": {"PM2.5": 302.19}}, {"timestamp": "2014-10-08T09:00:00", "value": {"PM2.5": 287.45}}, {"timestamp": "2014-10-08T10:00:00", "value": {"PM2.5": 273.93}}, {"timestamp": "2014-10-08T11:00:00", "value": {"PM2.5": 317.85}}, {"timestamp": "2014-10-08T12:00:00", "value": {"PM2.5": 322.9}}, {"timestamp": "2014-10-08T13:00:00", "value": {"PM2.5": 346.7}}, {"timestamp": "2014-10-08T14:00:00", "value": {"PM2.5": 393.7}}, {"timestamp": "2014-10-08T15:00:00", "value": {"PM2.5": 409.62}}, {"timestamp": "2014-10-08T16:00:00", "value": {"PM2.5": 441.96}}, {"timestamp": "2014-10-08T17:00:00", "value": {"PM2.5": 497.61}}, {"timestamp": "2014-10-08T18:00:00", "value": {"PM2.5": 542.4}}, {"timestamp": "2014-10-08T19:00:00", "value": {"PM2.5": 494.4}}, {"timestamp": "2014-10-08T20:00:00", "value": {"PM2.5": 505.14}}, {"timestamp": "2014-10-08T21:00:00", "value": {"PM2.5": 535.49}}, {"timestamp": "2014-10-08T22:00:00", "value": {"PM2.5": 602.83}}, {"timestamp": "2014-10-08T23:00:00", "value": {"PM2.5": 661.17}}, {"timestamp": "2014-10-09T00:00:00", "value": {"PM2.5": 667.53}}, {"timestamp": "2014-10-09T01:00:00", "value": {"PM2.5": 656.21}}, {"timestamp": "2014-10-09T02:00:00", "value": {"PM2.5": 644.98}}, {"timestamp": "2014-10-09T03:00:00", "value": {"PM2.5": 621.35}}, {"timestamp": "2014-10-09T04:00:00", "value": {"PM2.5": 611.46}}, {"timestamp": "2014-10-09T05:00:00", "value": {"PM2.5": 604.6}}, {"timestamp": "2014-10-09T06:00:00", "value": {"PM2.5": 602.84}}, {"timestamp": "2014-10-09T07:00:00", "value": {"PM2.5": 580.07}}, {"timestamp": "2014-10-09T08:00:00", "value": {"PM2.5": 585.6}}, {"timestamp": "2014-10-09T09:00:00", "value": {"PM2.5": 576.15}}, {"timestamp": "2014-10-09T10:00:00", "value": {"PM2.5": 562.81}}, {"timestamp": "2014-10-09T11:00:00", "value": {"PM2.5": 570.22}}, {"timestamp": "2014-10-09T12:00:00", "value": {"PM2.5": 568.22}}, {"timestamp": "2014-10-09T13:00:00", "value": {"PM2.5": 545.22}}, {"timestamp": "2014-10-09T14:00:00", "value": {"PM2.5": 545.43}}, {"timestamp": "2014-10-09T15:00:00", "value": {"PM2.5": 540.01}}, {"timestamp": "2014-10-09T16:00:00", "value": {"PM2.5": 531.11}}, {"timestamp": "2014-10-09T17:00:00", "value": {"PM2.5": 549.78}}, {"timestamp": "2014-10-09T18:00:00", "value": {"PM2.5": 539.85}}, {"timestamp": "2014-10-09T19:00:00", "value": {"PM2.5": 570.52}}, {"timestamp": "2014-10-09T20:00:00", "value": {"PM2.5": 611.39}}, {"timestamp": "2014-10-09T21:00:00", "value": {"PM2.5": 621.47}}, {"timestamp": "2014-10-09T22:00:00", "value": {"PM2.5": 619.53}}, {"timestamp": "2014-10-09T23:00:00", "value": {"PM2.5": 606.46}}, {"timestamp": "2014-10-10T00:00:00", "value": {"PM2.5": 620.15}}, {"timestamp": "2014-10-10T01:00:00", "value": {"PM2.5": 624.72}}, {"timestamp": "2014-10-10T02:00:00", "value": {"PM2.5": 619.74}}, {"timestamp": "2014-10-10T03:00:00", "value": {"PM2.5": 598.52}}, {"timestamp": "2014-10-10T04:00:00", "value": {"PM2.5": 597.64}}, {"timestamp": "2014-10-10T05:00:00", "value": {"PM2.5": 603.45}}, {"timestamp": "2014-10-10T06:00:00", "value": {"PM2.5": 624.04}}, {"timestamp": "2014-10-10T07:00:00", "value": {"PM2.5": 600.35}}, {"timestamp": "2014-10-10T08:00:00", "value": {"PM2.5": 603.37}}, {"timestamp": "2014-10-10T09:00:00", "value": {"PM2.5": 584.02}}, {"timestamp": "2014-10-10T10:00:00", "value": {"PM2.5": 554.25}}, {"timestamp": "2014-10-10T11:00:00", "value": {"PM2.5": 536.59}}, {"timestamp": "2014-10-10T12:00:00", "value": {"PM2.5": 507.22}}, {"timestamp": "2014-10-10T13:00:00", "value": {"PM2.5": 448.76}}, {"timestamp": "2014-10-10T14:00:00", "value": {"PM2.5": 447.68}}, {"timestamp": "2014-10-10T15:00:00", "value": {"PM2.5": 468.46}}, {"timestamp": "2014-10-10T16:00:00", "value": {"PM2.5": 476.16}}, {"timestamp": "2014-10-10T17:00:00", "value": {"PM2.5": 501.23}}, {"timestamp": "2014-10-10T18:00:00", "value": {"PM2.5": 476.19}}, {"timestamp": "2014-10-10T19:00:00", "value": {"PM2.5": 502.75}}, {"timestamp": "2014-10-10T20:00:00", "value": {"PM2.5": 488.49}}, {"timestamp": "2014-10-10T21:00:00", "value": {"PM2.5": 499.22}}, {"timestamp": "2014-10-10T22:00:00", "value": {"PM2.5": 513.88}}, {"timestamp": "2014-10-10T23:00:00", "value": {"PM2.5": 562.76}}, {"timestamp": "2014-10-11T00:00:00", "value": {"PM2.5": 532.6}}, {"timestamp": "2014-10-11T01:00:00", "value": {"PM2.5": 539.2}}, {"timestamp": "2014-10-11T02:00:00", "value": {"PM2.5": 539.5}}, {"timestamp": "2014-10-11T03:00:00", "value": {"PM2.5": 511.42}}, {"timestamp": "2014-10-11T04:00:00", "value": {"PM2.5": 494.12}}, {"timestamp": "2014-10-11T05:00:00", "value": {"PM2.5": 452.81}}, {"timestamp": "2014-10-11T06:00:00", "value": {"PM2.5": 449.28}}, {"timestamp": "2014-10-11T07:00:00", "value": {"PM2.5": 459.34}}, {"timestamp": "2014-10-11T08:00:00", "value": {"PM2.5": 476.61}}, {"timestamp": "2014-10-11T09:00:00", "value": {"PM2.5": 507.57}}, {"timestamp": "2014-10-11T10:00:00", "value": {"PM2.5": 458.59}}, {"timestamp": "2014-10-11T11:00:00", "value": {"PM2.5": 518.78}}, {"timestamp": "2014-10-11T12:00:00", "value": {"PM2.5": 522.39}}, {"timestamp": "2014-10-11T13:00:00", "value": {"PM2.5": 493.26}}, {"timestamp": "2014-10-11T14:00:00", "value": {"PM2.5": 448.23}}, {"timestamp": "2014-10-11T15:00:00", "value": {"PM2.5": 460.11}}, {"timestamp": "2014-10-11T16:00:00", "value": {"PM2.5": 513.12}}, {"timestamp": "2014-10-11T17:00:00", "value": {"PM2.5": 544.66}}, {"timestamp": "2014-10-11T18:00:00", "value": {"PM2.5": 530.0}}, {"timestamp": "2014-10-11T19:00:00", "value": {"PM2.5": 52.09}}, {"timestamp": "2014-10-11T20:00:00", "value": {"PM2.5": 10.52}}, {"timestamp": "2014-10-11T21:00:00", "value": {"PM2.5": 9.99}}, {"timestamp": "2014-10-11T22:00:00", "value": {"PM2.5": 6.62}}, {"timestamp": "2014-10-11T23:00:00", "value": {"PM2.5": 12.42}}, {"timestamp": "2014-10-12T00:00:00", "value": {"PM2.5": 6.05}}, {"timestamp": "2014-10-12T01:00:00", "value": {"PM2.5": 4.86}}, {"timestamp": "2014-10-12T02:00:00", "value": {"PM2.5": 4.78}}, {"timestamp": "2014-10-12T03:00:00", "value": {"PM2.5": 4.75}}, {"timestamp": "2014-10-12T04:00:00", "value": {"PM2.5": 6.49}}, {"timestamp": "2014-10-12T05:00:00", "value": {"PM2.5": 4.48}}, {"timestamp": "2014-10-12T06:00:00", "value": {"PM2.5": 4.0}}, {"timestamp": "2014-10-12T07:00:00", "value": {"PM2.5": 7.4}}, {"timestamp": "2014-10-12T08:00:00", "value": {"PM2.5": 44.28}}, {"timestamp": "2014-10-12T09:00:00", "value": {"PM2.5": 11.98}}, {"timestamp": "2014-10-12T10:00:00", "value": {"PM2.5": 7.86}}, {"timestamp": "2014-10-12T11:00:00", "value": {"PM2.5": 5.37}}, {"timestamp": "2014-10-12T12:00:00", "value": {"PM2.5": 4.19}}, {"timestamp": "2014-10-12T13:00:00", "value": {"PM2.5": 8.0}}, {"timestamp": "2014-10-12T14:00:00", "value": {"PM2.5": 4.62}}, {"timestamp": "2014-10-12T15:00:00", "value": {"PM2.5": 5.06}}, {"timestamp": "2014-10-12T16:00:00", "value": {"PM2.5": 4.29}}, {"timestamp": "2014-10-12T17:00:00", "value": {"PM2.5": 7.34}}, {"timestamp": "2014-10-12T18:00:00", "value": {"PM2.5": 7.85}}, {"timestamp": "2014-10-12T19:00:00", "value": {"PM2.5": 6.72}}, {"timestamp": "2014-10-12T20:00:00", "value": {"PM2.5": 5.16}}, {"timestamp": "2014-10-12T21:00:00", "value": {"PM2.5": 7.82}}, {"timestamp": "2014-10-12T22:00:00", "value": {"PM2.5": 10.13}}, {"timestamp": "2014-10-12T23:00:00", "value": {"PM2.5": 7.02}}, {"timestamp": "2014-10-13T00:00:00", "value": {"PM2.5": 5.91}}, {"timestamp": "2014-10-13T01:00:00", "value": {"PM2.5": 4.43}}, {"timestamp": "2014-10-13T02:00:00", "value": {"PM2.5": 4.17}}, {"timestamp": "2014-10-13T03:00:00", "value": {"PM2.5": 4.26}}, {"timestamp": "2014-10-13T04:00:00", "value": {"PM2.5": 4.16}}, {"timestamp": "2014-10-13T05:00:00", "value": {"PM2.5": 3.49}}, {"timestamp": "2014-10-13T06:00:00", "value": {"PM2.5": 3.22}}, {"timestamp": "2014-10-13T07:00:00", "value": {"PM2.5": 3.78}}, {"timestamp": "2014-10-13T08:00:00", "value": {"PM2.5": 6.02}}, {"timestamp": "2014-10-13T09:00:00", "value": {"PM2.5": 5.49}}, {"timestamp": "2014-10-13T10:00:00", "value": {"PM2.5": 3.18}}, {"timestamp": "2014-10-13T11:00:00", "value": {"PM2.5": 2.84}}, {"timestamp": "2014-10-13T12:00:00", "value": {"PM2.5": 4.08}}, {"timestamp": "2014-10-13T13:00:00", "value": {"PM2.5": 4.16}}, {"timestamp": "2014-10-13T14:00:00", "value": {"PM2.5": 5.6}}, {"timestamp": "2014-10-13T15:00:00", "value": {"PM2.5": 8.37}}, {"timestamp": "2014-10-13T16:00:00", "value": {"PM2.5": 11.02}}, {"timestamp": "2014-10-13T17:00:00", "value": {"PM2.5": 44.35}}, {"timestamp": "2014-10-13T18:00:00", "value": {"PM2.5": 59.91}}, {"timestamp": "2014-10-13T19:00:00", "value": {"PM2.5": 13.51}}, {"timestamp": "2014-10-13T20:00:00", "value": {"PM2.5": 11.44}}, {"timestamp": "2014-10-13T21:00:00", "value": {"PM2.5": 9.64}}, {"timestamp": "2014-10-13T22:00:00", "value": {"PM2.5": 15.66}}, {"timestamp": "2014-10-13T23:00:00", "value": {"PM2.5": 25.69}}, {"timestamp": "2014-10-14T00:00:00", "value": {"PM2.5": 21.18}}, {"timestamp": "2014-10-14T01:00:00", "value": {"PM2.5": 40.7}}, {"timestamp": "2014-10-14T02:00:00", "value": {"PM2.5": 29.56}}, {"timestamp": "2014-10-14T03:00:00", "value": {"PM2.5": 32.76}}, {"timestamp": "2014-10-14T04:00:00", "value": {"PM2.5": 51.26}}, {"timestamp": "2014-10-14T05:00:00", "value": {"PM2.5": 39.45}}, {"timestamp": "2014-10-14T06:00:00", "value": {"PM2.5": 38.68}}, {"timestamp": "2014-10-14T07:00:00", "value": {"PM2.5": 50.31}}, {"timestamp": "2014-10-14T08:00:00", "value": {"PM2.5": 31.9}}, {"timestamp": "2014-10-14T09:00:00", "value": {"PM2.5": 22.37}}, {"timestamp": "2014-10-14T10:00:00", "value": {"PM2.5": 20.02}}, {"timestamp": "2014-10-14T11:00:00", "value": {"PM2.5": 22.58}}, {"timestamp": "2014-10-14T12:00:00", "value": {"PM2.5": 24.72}}, {"timestamp": "2014-10-14T13:00:00", "value": {"PM2.5": -1.0}}, {"timestamp": "2014-10-14T14:00:00", "value": {"PM2.5": 37.88}}, {"timestamp": "2014-10-14T15:00:00", "value": {"PM2.5": 44.28}}, {"timestamp": "2014-10-14T16:00:00", "value": {"PM2.5": 76.53}}, {"timestamp": "2014-10-14T17:00:00", "value": {"PM2.5": 112.3}}, {"timestamp": "2014-10-14T18:00:00", "value": {"PM2.5": 117.97}}, {"timestamp": "2014-10-14T19:00:00", "value": {"PM2.5": 64.34}}, {"timestamp": "2014-10-14T20:00:00", "value": {"PM2.5": 55.34}}, {"timestamp": "2014-10-14T21:00:00", "value": {"PM2.5": 50.97}}, {"timestamp": "2014-10-14T22:00:00", "value": {"PM2.5": 48.59}}, {"timestamp": "2014-10-14T23:00:00", "value": {"PM2.5": 52.1}}, {"timestamp": "2014-10-15T00:00:00", "value": {"PM2.5": 52.31}}, {"timestamp": "2014-10-15T01:00:00", "value": {"PM2.5": 56.92}}, {"timestamp": "2014-10-15T02:00:00", "value": {"PM2.5": 54.36}}, {"timestamp": "2014-10-15T03:00:00", "value": {"PM2.5": 54.43}}, {"timestamp": "2014-10-15T04:00:00", "value": {"PM2.5": 142.32}}, {"timestamp": "2014-10-15T05:00:00", "value": {"PM2.5": 80.46}}, {"timestamp": "2014-10-15T06:00:00", "value": {"PM2.5": 105.69}}, {"timestamp": "2014-10-15T07:00:00", "value": {"PM2.5": 103.53}}, {"timestamp": "2014-10-15T08:00:00", "value": {"PM2.5": 106.21}}, {"timestamp": "2014-10-15T09:00:00", "value": {"PM2.5": 89.81}}, {"timestamp": "2014-10-15T10:00:00", "value": {"PM2.5": 109.88}}, {"timestamp": "2014-10-15T11:00:00", "value": {"PM2.5": 115.99}}, {"timestamp": "2014-10-15T12:00:00", "value": {"PM2.5": 33.9}}, {"timestamp": "2014-10-15T13:00:00", "value": {"PM2.5": 18.13}}, {"timestamp": "2014-10-15T14:00:00", "value": {"PM2.5": 21.07}}, {"timestamp": "2014-10-15T15:00:00", "value": {"PM2.5": 23.38}}, {"timestamp": "2014-10-15T16:00:00", "value": {"PM2.5": 12.68}}, {"timestamp": "2014-10-15T17:00:00", "value": {"PM2.5": 11.12}}, {"timestamp": "2014-10-15T18:00:00", "value": {"PM2.5": 11.13}}, {"timestamp": "2014-10-15T19:00:00", "value": {"PM2.5": 11.22}}, {"timestamp": "2014-10-15T20:00:00", "value": {"PM2.5": 10.27}}, {"timestamp": "2014-10-15T21:00:00", "value": {"PM2.5": 11.33}}, {"timestamp": "2014-10-15T22:00:00", "value": {"PM2.5": 12.96}}, {"timestamp": "2014-10-15T23:00:00", "value": {"PM2.5": 10.63}}, {"timestamp": "2014-10-16T00:00:00", "value": {"PM2.5": 6.99}}, {"timestamp": "2014-10-16T01:00:00", "value": {"PM2.5": 21.17}}, {"timestamp": "2014-10-16T02:00:00", "value": {"PM2.5": 7.95}}, {"timestamp": "2014-10-16T03:00:00", "value": {"PM2.5": 18.09}}, {"timestamp": "2014-10-16T04:00:00", "value": {"PM2.5": 19.63}}, {"timestamp": "2014-10-16T05:00:00", "value": {"PM2.5": 28.84}}, {"timestamp": "2014-10-16T06:00:00", "value": {"PM2.5": 30.77}}, {"timestamp": "2014-10-16T07:00:00", "value": {"PM2.5": 35.48}}, {"timestamp": "2014-10-16T08:00:00", "value": {"PM2.5": 41.14}}, {"timestamp": "2014-10-16T09:00:00", "value": {"PM2.5": 19.42}}, {"timestamp": "2014-10-16T10:00:00", "value": {"PM2.5": 19.65}}, {"timestamp": "2014-10-16T11:00:00", "value": {"PM2.5": 34.61}}, {"timestamp": "2014-10-16T12:00:00", "value": {"PM2.5": 46.08}}, {"timestamp": "2014-10-16T13:00:00", "value": {"PM2.5": 46.72}}, {"timestamp": "2014-10-16T14:00:00", "value": {"PM2.5": 47.4}}, {"timestamp": "2014-10-16T15:00:00", "value": {"PM2.5": 51.82}}, {"timestamp": "2014-10-16T16:00:00", "value": {"PM2.5": 68.41}}, {"timestamp": "2014-10-16T17:00:00", "value": {"PM2.5": 67.81}}, {"timestamp": "2014-10-16T18:00:00", "value": {"PM2.5": 200.82}}, {"timestamp": "2014-10-16T19:00:00", "value": {"PM2.5": 49.54}}, {"timestamp": "2014-10-16T20:00:00", "value": {"PM2.5": 60.66}}, {"timestamp": "2014-10-16T21:00:00", "value": {"PM2.5": 61.39}}, {"timestamp": "2014-10-16T22:00:00", "value": {"PM2.5": 61.92}}, {"timestamp": "2014-10-16T23:00:00", "value": {"PM2.5": 64.39}}]}
        return JsonResponse(output);


    params = {
        'stats': stats,
        'key': key,
        'page_route': 'heatmap',
        'type_options': type_options,
        'viz_type': key,
    }
    return TemplateResponse(request, 'dataviz/heatmap.html', params)


@staff_member_required
def viz_index(request):
    params = {}
    return TemplateResponse(request, 'dataviz/index.html', params)


@staff_member_required
def viz_circles(request, _type):
    return viz_sunburst(request, _type, 'circles')


def data_viz_helper_merge_json_trees(output):
    new_output = {
        'name': output['name'],
    }
    if not output.get('children'):
        new_output['size'] = output['size']
        return new_output

    # merge in names that are equal
    new_output['children'] = []
    processed_names = {}
    length = len(output['children'])
    for i in range(0, length):
        this_child = output['children'][i]
        name = this_child['name']
        if name in processed_names.keys():
            target_idx = processed_names[name]
            print(target_idx)
            for this_childs_child in this_child['children']:
                new_output['children'][target_idx]['children'].append(this_childs_child)
        else:
            processed_names[name] = len(new_output['children'])
            new_output['children'].append(this_child)

    # merge further down the line
    length = len(new_output['children'])
    for i in range(0, length):
        new_output['children'][i] = data_viz_helper_merge_json_trees(new_output['children'][i])

    return new_output

def data_viz_helper_get_json_output(key, value, depth=0):
    key = key.replace('_', '')
    keys = key.split('-')
    result = {}
    result['name'] = keys[0]
    if len(keys) > 1:
        result['children'] = [
            data_viz_helper_get_json_output("-".join(keys[1:]), value, depth + 1)
        ]
    else:
        result['size'] = int(value)
    return result


@staff_member_required
def viz_sunburst(request, _type, template='sunburst'):
    _type_options = [
        'status_progression',
        'repos',
        'fulfillers',
        'funders',
        ]
    if _type not in _type_options:
        _type = _type_options[0]

    if _type == 'status_progression':
        title = "Status Progression Viz"
        comment = 'of statuses begin with this sequence of status'
        categories = list(Bounty.objects.distinct('idx_status').values_list('idx_status', flat=True)) + ['_']
    if _type == 'repos':
        title = "Github Structure of All Bounties"
        comment = 'of bounties value with this github structure'
        categories = [bounty.org_name.replace('-','') for bounty in Bounty.objects.filter(network='mainnet')]
        categories += [bounty.github_repo_name.replace('-','') for bounty in Bounty.objects.filter(network='mainnet')]
        categories += [str(bounty.github_issue_number) for bounty in Bounty.objects.filter(network='mainnet')]
    if _type == 'fulfillers':
        title = "Fulfillers"
        comment = 'of bounties value with this fulfiller'
        categories = []
        for bounty in Bounty.objects.filter(network='mainnet'):
            for fulfiller in bounty.fulfillments.all():
                categories.append(fulfiller.fulfiller_github_username.replace('-',''))
    if _type == 'funders':
        title = "Funders"
        comment = 'of bounties value with this funder'
        categories = []
        for bounty in Bounty.objects.filter(network='mainnet'):
            categories.append(bounty.bounty_owner_github_username.replace('-',''))


    if request.GET.get('data'):
        data_dict = data_viz_helper_get_data_responses(request, _type)

        _format = request.GET.get('format', 'csv')
        if _format == 'csv':
            rows = []
            for key, value in data_dict.items():
                row = ",".join([key, str(value)])
                rows.append(row)

            output = "\n".join(rows)
            return HttpResponse(output);

        if _format == 'json':
            output = {
                'name': 'data',
                'children': [
                ]
            }
            for key, val in data_dict.items():
                if val:
                    output['children'].append(data_viz_helper_get_json_output(key, val))
            output = data_viz_helper_merge_json_trees(output)
            return JsonResponse(output);


    params = {
        'title': title,
        'comment': comment,
        'viz_type': _type,
        'page_route': template,
        'type_options': _type_options,
        'categories': json.dumps(list(categories)),
    }
    return TemplateResponse(request, f'dataviz/{template}.html', params)


@staff_member_required
def viz_graph(request):
    title = 'Graph of Gitcoin Network'
    if request.GET.get('data'):
        # setup response
        output = {
          "nodes": [
            ],
          "links": [
            ]
        }

        # gather info
        types = {}
        names = {}
        values = {}
        edges = []
        for bounty in Bounty.objects.filter(network='mainnet', current_bounty=True):
            if bounty.value_in_usdt_then:
                weight = bounty.value_in_usdt_then
                source = bounty.org_name
                if source:
                    for fulfillment in bounty.fulfillments.all():
                        target = fulfillment.fulfiller_github_username.lower()
                        types[source] = 'source'
                        types[target] = 'target_accepted' if fulfillment.accepted else 'target'
                        names[source] = None
                        names[target] = None
                        edges.append((source, target, weight))

                        value = values.get(source, 0)
                        value += weight
                        values[source] = value
                        value = values.get(target, 0)
                        value += weight
                        values[target] = value

        for profile in Profile.objects.exclude(github_access_token='').all():
            node = profile.handle.lower()
            if node not in names.keys():
                names[node] = None
                types[node] = 'independent'

        # build output
        for name in set(names.keys()):
            names[name] = len(output['nodes'])
            value = int(math.sqrt(math.sqrt(values.get(name, 1))))
            output['nodes'].append({"name": name, 'value': value, 'type': types.get(name)})
        for edge in edges:
            source, target, weight = edge
            weight = math.sqrt(weight)
            source = names[source]
            target = names[target]
            output['links'].append({
                'source': source,
                'target': target,
                'weight': weight,
                })

        return JsonResponse(output);

    params = {
        'title': title,
    }
    return TemplateResponse(request, f'dataviz/graph.html', params)


@staff_member_required
def cohort(request):
    cohorts = {}

    data_source = request.GET.get('data_source', 'slack-online')
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


def funnel_helper_get_data(key, k, daily_source, weekly_source, start_date, end_date):
    if key == 'sessions':
        return sum(daily_source.filter(key='google_analytics_sessions_gitcoin', created_on__gte=start_date, created_on__lt=end_date).values_list('val', flat=True))
    if key == 'email_subscribers':
        return weekly_source.filter(key='email_subscriberse')[k].val - weekly_source.filter(key='email_subscriberse')[k+1].val
    if key == 'bounties_alltime':
        return weekly_source.filter(key='bounties')[k].val - weekly_source.filter(key='bounties')[k+1].val
    if key == 'bounties_fulfilled':
        return weekly_source.filter(key='bounties_fulfilled')[k].val - weekly_source.filter(key='bounties_fulfilled')[k+1].val
    if key == 'email_processed':
        return weekly_source.filter(key='email_processed')[k].val - weekly_source.filter(key='email_processed')[k+1].val
    if key == 'slack_users':
        return weekly_source.filter(key='slack_users')[k].val - weekly_source.filter(key='slack_users')[k+1].val
    if key == 'email_open':
        return weekly_source.filter(key='email_open')[k].val - weekly_source.filter(key='email_open')[k+1].val
    if key == 'email_click':
        return weekly_source.filter(key='email_click')[k].val - weekly_source.filter(key='email_click')[k+1].val
    try:
        return weekly_source.filter(key=key)[k].val - weekly_source.filter(key=key)[k+1].val
    except:
        return 0


@staff_member_required
def funnel(request):

    weekly_source = Stat.objects.filter(created_on__hour=1, created_on__week_day=1).order_by('-created_on')
    daily_source = Stat.objects.filter(created_on__hour=1).order_by('-created_on')
    funnels = [
            {
                'title': 'web => bounties_posted => bounties_fulfilled',
                'keys': [
                    'sessions',
                    'bounties_alltime',
                    'bounties_fulfilled',
                ],
                'data': []
            },
            {
                'title': 'web => bounties_posted => bounties_fulfilled (detail)',
                'keys': [
                    'sessions',
                    'bounties_alltime',
                    'bounties_started_total',
                    'bounties_submitted_total',
                    'bounties_done_total',
                    'bounties_expired_total',
                    'bounties_cancelled_total',
                ],
                'data': []
            },
            {
                'title': 'web session => email_subscribers',
                'keys': [
                    'sessions',
                    'email_subscribers',
                ],
                'data': []
            },
            {
                'title': 'web session => slack',
                'keys': [
                    'sessions',
                    'slack_users',
                ],
                'data': []
            },
            {
                'title': 'web session => create dev grant',
                'keys': [
                    'sessions',
                    'dev_grant',
                ],
                'data': []
            },
            {
                'title': 'email funnel',
                'keys': [
                    'email_processed',
                    'email_open',
                    'email_click',
                ],
                'data': []
            },
    ]

    for funnel in range(0, len(funnels)):
        keys=funnels[funnel]['keys']
        title=funnels[funnel]['title']
        for k in range(0, 10):
            try:
                stats = []
                end_date = weekly_source.filter(key='email_subscriberse')[k].created_on
                start_date = weekly_source.filter(key='email_subscriberse')[k+1].created_on

                for key in keys:
                    stats.append({
                        'key': key,
                        'val': funnel_helper_get_data(key, k, daily_source, weekly_source, start_date, end_date),
                    })

                for i in range(1, len(stats)):
                    try:
                        stats[i]['pct'] = round((stats[i]['val'])/stats[i-1]['val']*100, 1)
                    except:
                        stats[i]['pct'] = 0
                for i in range(0, len(stats)):
                    stats[i]['idx'] = i

                funnels[funnel]['data'].append({
                    'meta': {
                        'start_date': start_date,
                        'end_date': end_date,
                    },
                    'stats': stats,
                    'idx': k,
                })
            except Exception as e:
                print(key, k, e)

    params = {
        'title': "Funnel Analysis",
        'funnels': funnels,
    }
    return TemplateResponse(request, 'funnel.html', params)

settings_navs = [
    {
        'body': 'Email',
        'href': '/settings/email',
    },
    {
        'body': 'Privacy',
        'href': '/settings/privacy',
    },
    {
        'body': 'Matching',
        'href': '/settings/matching',
    },
    {
        'body': 'Feedback',
        'href': '/settings/feedback',
    },
]


def settings_helper_get_auth(request, key=None):

    # setup
    github_handle = request.user.username if request.user.is_authenticated else False
    is_logged_in = bool(request.user.is_authenticated)
    es = EmailSubscriber.objects.none()

    # find the user info
    if not key:
        email = request.user.email if request.user.is_authenticated else None
        if not email:
            github_handle = request.user.username if request.user.is_authenticated else None
        if hasattr(request.user, 'profile'):
            if request.user.profile.email_subscriptions.exists():
                es = request.user.profile.email_subscriptions.first()
            if not es or es and not es.priv:
                es = get_or_save_email_subscriber(
                    request.user.email, 'settings', profile=request.user.profile)
    else:
        try:
            es = EmailSubscriber.objects.get(priv=key)
            email = es.email
            level = es.preferences.get('level', False)
        except EmailSubscriber.DoesNotExist:
            pass

    # lazily create profile if needed
    profiles = Profile.objects.filter(handle__iexact=github_handle).exclude(email='') if github_handle else Profile.objects.none()
    profile = None if not profiles.exists() else profiles.first()
    if not profile and github_handle:
        profile = sync_profile(github_handle, user=request.user)

    # lazily create email settings if needed
    if not es:
        if request.user.is_authenticated and request.user.email:
            es = EmailSubscriber.objects.create(
                email=request.user.email,
                source='settings_page',
            )
            es.set_priv()
            es.save()

    return profile, es, request.user, is_logged_in


def privacy_settings(request):

    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    suppress_leaderboard = profile.suppress_leaderboard if profile else False
    if not profile:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''
    if request.POST and request.POST.get('submit'):
        if profile:
            profile.suppress_leaderboard = bool(request.POST.get('suppress_leaderboard', False))
            suppress_leaderboard = profile.suppress_leaderboard
            profile.save()

    context = {
        'suppress_leaderboard': suppress_leaderboard,
        'nav': 'internal',
        'active': '/settings/privacy',
        'title': _('Privacy Settings'),
        'navs': settings_navs,
        'is_logged_in': is_logged_in,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/privacy.html', context)


def matching_settings(request):

    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''

    if request.POST and request.POST.get('submit'):
        github = request.POST.get('github', '')
        keywords = request.POST.get('keywords').split(',')
        es.github = github
        es.keywords = keywords
        ip = get_ip(request)
        if not es.metadata.get('ip', False):
            es.metadata['ip'] = [ip]
        else:
            es.metadata['ip'].append(ip)
        es.save()
        msg = "Updated your preferences.  "

    context = {
        'keywords': ",".join(es.keywords),
        'is_logged_in': is_logged_in,
        'autocomplete_keywords': json.dumps(
            [str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
        'nav': 'internal',
        'active': '/settings/matching',
        'title': _('Matching Settings'),
        'navs': settings_navs,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/matching.html', context)


def feedback_settings(request):

    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''
    if request.POST and request.POST.get('submit'):
        comments = request.POST.get('comments', '')[:255]
        has_comment_changed = comments != es.metadata.get('comments','')
        if has_comment_changed:
            new_feedback(es.email, comments)
        es.metadata['comments'] = comments
        ip = get_ip(request)
        if not es.metadata.get('ip', False):
            es.metadata['ip'] = [ip]
        else:
            es.metadata['ip'].append(ip)
        es.save()
        msg = "We've received your feedback. "

    context = {
        'nav': 'internal',
        'active': '/settings/feedback',
        'title': _('Feedback'),
        'navs': settings_navs,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/feedback.html', context)


def email_settings(request, key):

    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request, key)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    # handle 'noinput' case
    suppress_leaderboard = False
    email = ''
    level = ''
    msg = ''

    if request.POST and request.POST.get('submit'):
        email = request.POST.get('email')
        level = request.POST.get('level')
        validation_passed = True
        try:
            validate_email(email)
        except Exception as e:
            print(e)
            validation_passed = False
            msg = _('Invalid Email')

        if level not in ['lite', 'lite1', 'regular', 'nothing']:
            validation_passed = False
            msg = _('Invalid Level')
        if validation_passed:
            key = get_or_save_email_subscriber(email, 'settings')
            es.preferences['level'] = level
            es.email = email
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
        'active': '/settings/email',
        'title': _('Email Settings'),
        'es': es,
        'msg': msg,
        'navs': settings_navs,
    }
    return TemplateResponse(request, 'settings/email.html', context)


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
        'quarterly_payers': _('Top Payers'),
        'quarterly_earners': _('Top Earners'),
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
