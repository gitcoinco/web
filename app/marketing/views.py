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
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from marketing.models import Stat, EmailSubscriber, LeaderboardRank
from chartit import DataPool, Chart
from marketing.utils import get_or_save_email_subscriber
from django.core.validators import validate_email
from retail.helpers import get_ip
from django.http import Http404
# Create your views here.


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

    # types
    types = list(Stat.objects.distinct('key').values_list('key', flat=True))
    types.sort()

    # filters
    if _filter == 'Activity':
        _filters = ['tip', 'bount']
        types = filter_types(types, _filters)
    if _filter == 'Marketing':
        _filters = ['slack', 'email', 'whitepaper', 'twitter']
        types = filter_types(types, _filters)
    if _filter == 'KPI':
        _filters = ['slack', 'email_subscribers_active', 'bounties_open']
        types = filter_types(types, _filters)

    # params
    params = {
        'types': types,
        'chart_list': [],
        'filter_params': "?filter={}&rollup={}".format(_filter, rollup),
    }

    for t in types:

        source = Stat.objects.filter(key=t)
        if rollup == 'daily':
            source = source.filter(created_on__hour=1)
        elif rollup == 'weekly':
            source = source.filter(created_on__hour=1, created_on__week_day=1)
        
        source = source[30:]

        #compute avg
        total = 0
        count = source.count() - 1
        avg = "NA"
        if count > 1:
            for i in range(0, count):
                total += (source[i+1].val - source[i].val)
            avg = round(total / count, 1)
            avg = str("+{}".format(avg) if avg > 0 else avg)


        chartdata = \
            DataPool(
               series=
                [{'options': {
                   'source': source},
                  'terms': [
                    'created_on',
                    'val']}
                 ])

        cht = Chart(
                datasource=chartdata,
                series_options=
                  [{'options':{
                      'type': 'line',
                      'stacking': False},
                    'terms':{
                      'created_on': [
                        'val']
                      }}],
                chart_options =
                  {'title': {
                       'text': t + ' trend ({} avg)'.format(avg) },
                   'xAxis': {
                        'title': {
                           'text': 'Time'}}})

        params['chart_list'].append(cht)
    
    params['chart_list_str'] = ",".join(types)
    return TemplateResponse(request, 'stats.html', params)


def email_settings(request, key):
    email = ''
    level = ''
    msg = ''
    es = EmailSubscriber.objects.filter(priv=key)
    if es.exists():
        email = es.first().email
        level = es.first().preferences.get('level', False)

    if request.POST.get('email', False):
        level = request.POST.get('level')
        comments = request.POST.get('comments')[:255]
        email = request.POST.get('email')
        print(email)
        validation_passed = True
        try:
            validate_email(email)
        except Exception as e:
            print(e)
            validation_passed = False
            msg = 'Invalid Email'

        if level not in ['lite', 'regular', 'nothing']:
            validation_passed = False
            msg = 'Invalid Level'

        if validation_passed:
            key = get_or_save_email_subscriber(email, 'settings')
            es = EmailSubscriber.objects.get(priv=key)
            es.preferences['level'] = level
            es.metadata['comments'] = comments
            ip = get_ip(request)
            es.active = level != 'nothing'
            es.newsletter = level == 'regular'
            if not es.metadata.get('ip', False):
                es.metadata['ip'] = [ip]
            else:
                es.metadata['ip'].append(ip)
            es.save()
            msg = "Updated your preferences.  "

    context = {
      'email': email,
      'level': level,
      'msg': msg,
    }
    return TemplateResponse(request, 'email_settings.html', context)

def leaderboard(request, key):
    if not key:
        key = 'weekly_fulfilled'


    titles = {
        'weekly_fulfilled': 'Weekly Leaderboard: Fulfilled Funded Issues',
        'weekly_all': 'Weekly Leaderboard: All Funded Issues',
        'monthly_fulfilled': 'Monthly Leaderboard: Fulfilled Funded Issues',
        'monthly_all': 'Monthly Leaderboard: All Funded Issues',
        'yearly_fulfilled': 'Yearly Leaderboard: Fulfilled Funded Issues',
        'yearly_all': 'Yearly Leaderboard: All Funded Issues',
        'all_fulfilled': 'All-Time Leaderboard: Fulfilled Funded Issues',
        'all_all': 'All-Time Leaderboard: All Funded Issues',
    }
    if key not in titles.keys():
        raise Http404

    context = {
        'items': LeaderboardRank.objects.filter(active=True, leaderboard=key).order_by('-amount'),
        'titles': titles,
        'title': titles[key],
        'action_past_tense': 'Transacted' if 'fulfilled' in key else 'bountied',
    }


    return TemplateResponse(request, 'leaderboard.html', context)


