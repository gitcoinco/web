# -*- coding: utf-8 -*-
"""Define data visualization related D3 views.

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
import json
import math
import random
import re
import time

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone

import pytz
from dashboard.models import Bounty, BountyFulfillment, Profile, Tip
from marketing.models import Stat
from perftools.models import JSONStore

from .models import DataPayload


@staff_member_required
def data_viz_helper_get_data_responses(request, visual_type):
    """Handle visualization of the request response data based on type.

    Args:
        visual_type (str): The visualization type.

    TODO:
        * Reduce complexity of this method to pass McCabe complexity check.

    Returns:
        dict: The JSON representation of the requested visual type data.

    """
    data_dict = {}
    network = 'mainnet'
    for bounty in Bounty.objects.current().filter(network=network, web3_type='bounties_network'):

        if visual_type == 'status_progression':
            max_size = 12
            value = 1
            if not value:
                continue
            response = []
            prev_bounties = Bounty.objects.filter(
                standard_bounties_id=bounty.standard_bounties_id, network=network
            ).exclude(pk=bounty.pk).order_by('created_on')
            if prev_bounties.exists() and prev_bounties.first().status == 'started':
                response.append('open')  # mock for status changes not mutating status
            last_bounty_status = None
            for prev_bounty in prev_bounties:
                if last_bounty_status != prev_bounty.status:
                    response.append(prev_bounty.status)
                last_bounty_status = prev_bounty.status
            if bounty.status != last_bounty_status:
                response.append(bounty.status)
            response = response[0:max_size]
            while len(response) < max_size:
                response.append('_')

        elif visual_type == 'repos':
            value = bounty.value_in_usdt_then
            bounty_org_name = getattr(bounty, 'org_name', '')
            bounty_repo_name = getattr(bounty, 'github_repo_name', '')

            response = [
                bounty_org_name.replace('-', ''),
                bounty_repo_name.replace('-', ''),
                str(bounty.github_issue_number),
            ]

        elif visual_type == 'fulfillers':
            response = []
            if bounty.status == 'done':
                for fulfillment in bounty.fulfillments.filter(accepted=1):
                    value = bounty.value_in_usdt_then

                    response = [fulfillment.fulfiller_github_username.replace('-', '')]

        elif visual_type == 'funders':
            value = bounty.value_in_usdt_then
            response = []
            if bounty.bounty_owner_github_username and value:
                response = [bounty.bounty_owner_github_username.replace('-', '')]

        if response:
            response = '-'.join(response)
            if value:
                if response in data_dict.keys():
                    data_dict[response] += value
                else:
                    data_dict[response] = value

    return data_dict

def data_viz_helper_merge_json_trees(output):
    """Handle merging the visualization data trees.

    Args:
        output (dict): The output data to be merged.

    Returns:
        dict: The merged data dictionary.

    """
    new_output = {'name': output['name'], }
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
            #print(target_idx)
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
    """Handle data visualization and build the JSON output.

    Args:
        key (str): The key to be formatted and parsed.
        value (float): The data value.
        depth (int): The depth of keys to parse. Defaults to: 0.

    Returns:
        dict: The JSON representation of the provided data.

    """
    keys = key.replace('_', '').split('-')
    result = {'name': keys[0]}
    if len(keys) > 1:
        result['children'] = [data_viz_helper_get_json_output("-".join(keys[1:]), value, depth + 1)]
    else:
        result['size'] = int(value)
    return result


def helper_hide_pii(username, num_chars=3):
    if not username:
        return None
    new_username = str(username)[0:num_chars] + "*******"
    return new_username


def get_all_type_options():
    return ['fulfillments_accepted_only', 'all', 'fulfillments', 'what_future_could_look_like']


# PUBLIC VIEW!
def viz_graph(request, _type, template='graph'):
    """Render a graph visualization of the Gitcoin Network.

    TODO:
        * Reduce the number of local variables from 16 to 15.

    Returns:
        JsonResponse: If data param provided, return a JSON representation of data to be graphed.
        TemplateResponse: If data param not provided, return the populated data visualization template.

    """
    show_controls = request.GET.get('show_controls', False)
    keyword = request.GET.get('keyword', '')
    hide_pii = True
    page_route = 'graph'
    if template == 'square_graph':
        _type_options = [
            'fulfillments_accepted_only'
        ]  # for performance reasons, since this graph can't handle too many nodes
    else:
        _type_options = get_all_type_options()
        _type_options = _type_options + list(
            DataPayload.objects.filter(key=page_route).values_list('report', flat=True)
        )
    _type_options.sort()
    datapayloads = DataPayload.objects.filter(key=page_route, report=_type)
    comments = '' if not datapayloads.exists() else datapayloads.first().comments

    if _type not in _type_options:
        _type = _type_options[0]
    title = 'Graph : Visualizer - {}'.format(_type)
    if request.GET.get('data'):

        if datapayloads.exists():
            output = datapayloads.first().get_payload_with_mutations()
            return JsonResponse(output)

        output = JSONStore.objects.get(view='d3_graph', key=f"{_type}_{keyword}_{hide_pii}").data
        return JsonResponse(output)

    params = {
        'title': title,
        'comments': comments,
        'viz_type': _type,
        'type_options': _type_options,
        'page_route': page_route,
        'max_time': int(time.time()),
        'keyword': keyword,
    }

    _template = 'graph' if not show_controls else 'admin_graph'
    response = TemplateResponse(request, f'dataviz/{_template}.html', params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response


def viz_scatterplot_stripped(request, key='hourly_rate'):
    return viz_scatterplot_helper(request, 'hourly_rate', 'dataviz/scatterplot_stripped.html', True)


def is_an_edge(handle, edges):
    for edge in edges:
        if handle == edge[0]:
            return True
        if handle == edge[1]:
            return True
    return False


def normalize_handle(handle):
    return re.sub(r'\W+', '', str(handle))


@staff_member_required
def mesh_network_viz(request, ):
    """Render a Mesh Network visualization

    Args:
        key (str): The key type to visualize.

    Returns:
        TemplateResponse: The populated  mesh data visualization template.

    """
    handles = []
    edges = []
    year = int(request.GET.get('year', timezone.now().strftime("%Y")))
    month = int(request.GET.get('month', timezone.now().strftime("%m")))
    day = int(request.GET.get('day', timezone.now().strftime("%d")))
    to_year = int(request.GET.get('to_year', timezone.now().strftime("%Y")))
    to_month = int(request.GET.get('to_month', timezone.now().strftime("%m")))
    to_day = int(request.GET.get('to_day', timezone.now().strftime("%d")))
    start_date = timezone.datetime(year, month, day, 1, tzinfo=pytz.UTC)
    end_date = timezone.datetime(to_year, to_month, to_day, 23, 59, tzinfo=pytz.UTC)
    _type = request.GET.get('type', 'all')
    theme = request.GET.get('theme', 'light')
    show_labels = request.GET.get('show_labels', '0')
    trim_pct = int(request.GET.get('trim_pct', '0')) - 1

    since = f"{year}/{month}/{day}"

    from dashboard.models import Earning
    earnings = Earning.objects.filter(created_on__gt=start_date, created_on__lt=end_date)
    if _type != 'all':
        from django.contrib.contenttypes.models import ContentType
        mapping = {
            'grant': ContentType.objects.get(app_label='grants', model='contribution'),
            'kudos': ContentType.objects.get(app_label='kudos', model='kudostransfer'),
            'tip': ContentType.objects.get(app_label='dashboard', model='tip'),
            'bounty': ContentType.objects.get(app_label='dashboard', model='bountyfulfillment'),
        }
        earnings = earnings.filter(source_type=mapping[_type])
    earnings = earnings.values_list('from_profile', 'to_profile')
    if trim_pct:
        earnings = earnings.extra(where=[f'MOD(id, 100) > {trim_pct}'])
    for obj in earnings:
        handle1 = obj[0]
        handle2 = obj[1]
        handles.append(handle1)
        handles.append(handle2)
        edges.append([handle1, handle2])

    # assemble and output
    handles = set(handles)
    handles = [handle for handle in handles if is_an_edge(handle, edges)]
    graph = ""
    print(len(handles))
    counter = 1
    for handle in handles:
        if handle:
            handle = normalize_handle(handle)
            counter += 1
            graph += (
                f'var user_{handle} = new GRAPHVIS.Node({counter}); user_{handle}.data.title = "user_{handle}";  graph.addNode(user_{handle}); drawNode(user_{handle});'
            )

    for edge in edges:
        handle1 = edge[0]
        handle2 = edge[1]
        if handle1 and handle2:
            handle1 = normalize_handle(handle1)
            handle2 = normalize_handle(handle2)
            if handle1 and handle2:
                graph += (f"graph.addEdge(user_{handle1}, user_{handle2}); drawEdge(user_{handle1}, user_{handle2}); ")

    params = {
        "type": _type,
        "graph": graph,
        "since": since,
        "year": year,
        "month": month,
        "show_labels": show_labels,
        "theme": theme,
        "themes": ['light', 'dark'],
        "show_labels_options": ['1', '0'],
        'trim_pct_options': range(0, 100),
        'trim_pct': trim_pct,
        "day": day,
        "to_year": to_year,
        "to_month": to_month,
        "to_day": to_day,
        "years": range(2017, 1 + int(timezone.now().strftime("%Y"))),
        "months": range(1, 13),
        "days": range(1, 31),
        'types': ['all', 'grant', 'bounty', 'tip', 'kudos']
    }
    response = TemplateResponse(request, 'dataviz/mesh.html', params)
    return response


def viz_scatterplot_helper(request, key='hourly_rate', template='dataviz/scatterplot.html', hide_usernames=False):
    """Render a scatterplot visualization.

    Args:
        key (str): The key type to visualize.

    Returns:
        TemplateResponse: The populated scatterplot data visualization template.

    """
    stats = []
    keyword = request.GET.get('keyword', None)
    type_options = ['hourly_rate']
    if request.GET.get('data'):
        output = JSONStore.objects.get(view='d3_scatterplot', key=f"{keyword}_{hide_usernames}").data
        return HttpResponse(output)

    params = {
        'stats': stats,
        'key': key,
        'page_route': 'scatterplot',
        'type_options': type_options,
        'viz_type': key,
        'keyword': keyword,
    }
    response = TemplateResponse(request, template, params)
    response['X-Frame-Options'] = 'SAMEORIGIN'
    return response
