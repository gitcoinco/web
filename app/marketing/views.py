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
from marketing.models import Stat
from chartit import DataPool, Chart
# Create your views here.

@staff_member_required
def stats(request):
    types = Stat.objects.distinct('key').values_list('key', flat=True)
    params = {
        'types': types,
        'chart_list': [],
    }

    for t in types:
        chartdata = \
            DataPool(
               series=
                [{'options': {
                   'source': Stat.objects.filter(key=t).all()},
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
                       'text': t + ' over time'},
                   'xAxis': {
                        'title': {
                           'text': 'Time'}}})

        params['chart_list'].append(cht)
    
    params['chart_list_str'] = ",".join(types)
    return TemplateResponse(request, 'stats.html', params)
