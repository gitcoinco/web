# -*- coding: utf-8 -*-
"""Define data visualization related D3 views.

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
import json
import math
import random
import time

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone

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


@staff_member_required
def viz_spiral(request, key='email_open'):
    """Render a spiral graph visualization.

    Args:
        key (str): The key type to visualize.

    Returns:
        TemplateResponse: The populated spiral data visualization template.

    """
    stats = Stat.objects.filter(created_on__hour=1)
    type_options = stats.distinct('key').values_list('key', flat=True)
    stats = stats.filter(key=key).order_by('created_on')
    params = {'stats': stats, 'key': key, 'page_route': 'spiral', 'type_options': type_options, 'viz_type': key, }
    return TemplateResponse(request, 'dataviz/spiral.html', params)


@staff_member_required
def viz_chord(request, key='bounties_paid'):
    """Render a chord graph visualization.

    Args:
        key (str): The key type to visualize.

    Returns:
        TemplateResponse: The populated chord data visualization template.

    """
    type_options = ['bounties_paid']

    if request.GET.get('data'):
        rows = [['creditor', 'debtor', 'amount', 'risk']]
        network = 'mainnet'
        for bounty in Bounty.objects.current().filter(network=network, web3_type='bounties_network', idx_status='done'):
            weight = bounty.value_in_usdt_then
            if weight:
                for fulfillment in bounty.fulfillments.filter(accepted=True):
                    length = (fulfillment.created_on - bounty.web3_created).seconds
                    target = fulfillment.fulfiller_github_username.lower()
                    source = bounty.bounty_owner_github_username.lower()
                    if source and target:
                        rows.append((helper_hide_pii(source), helper_hide_pii(target), str(weight), str(length)))

        output_rows = []
        for row in rows:
            row = ",".join(row)
            output_rows.append(row)

        output = "\n".join(output_rows)
        return HttpResponse(output)

    params = {'key': key, 'page_route': 'spiral', 'type_options': type_options, 'viz_type': key, }
    return TemplateResponse(request, 'dataviz/chord.html', params)


@staff_member_required
def viz_steamgraph(request, key='open'):
    """Render a steamgraph graph visualization.

    Args:
        key (str): The key type to visualize.

    Returns:
        TemplateResponse: The populated steamgraph data visualization template.

    """
    type_options = Bounty.objects.all().distinct('idx_status').values_list('idx_status', flat=True)
    if key not in type_options:
        key = type_options[0]

    if request.GET.get('data'):
        rows = [['key', 'value', 'date']]
        network = 'mainnet'
        bounties = Bounty.objects.filter(network=network, web3_type='bounties_network', idx_status=key)
        org_names = set([bounty.org_name for bounty in bounties])
        #start_date = bounties.order_by('web3_created').first().web3_created
        start_date = timezone.now() - timezone.timedelta(days=30)
        end_date = timezone.now()
        current_date = start_date
        while current_date < end_date:
            next_date = current_date + timezone.timedelta(days=1)
            for org_name in org_names:
                if org_name:
                    _bounties = bounties.filter(github_url__contains=org_name)
                    weight = round(
                        sum(
                            bounty.value_in_usdt_then for bounty in _bounties
                            if bounty.value_in_usdt_then and bounty.was_active_at(current_date)
                        ), 2
                    )
                    output_date = current_date.strftime(('%m/%d/%y'))
                    rows.append([org_name, str(weight), output_date])
            current_date = next_date

        output_rows = []
        for row in rows:
            row = ",".join(row)
            output_rows.append(row)

        output = "\n".join(output_rows)
        return HttpResponse(output)

    params = {'key': key, 'page_route': 'steamgraph', 'type_options': type_options, 'viz_type': key, }
    return TemplateResponse(request, 'dataviz/steamgraph.html', params)


@staff_member_required
def viz_calendar(request, key='email_open', template='calendar'):
    return viz_heatmap(request, key, template)


@staff_member_required
def viz_heatmap(request, key='email_open', template='heatmap'):
    """Render a heatmap graph visualization.

    Args:
        key (str): The key type to visualize.

    Returns:
        JsonResponse: If data param provided, return a JSON representation of data to be graphed.
        TemplateResponse: If data param not provided, return the populated data visualization template.

    """
    time_now = timezone.now()
    stats = Stat.objects.filter(created_on__lt=time_now, )
    if template == 'calendar':
        stats = stats.filter(created_on__hour=1)
    else:
        stats = stats.filter(created_on__gt=(time_now - timezone.timedelta(weeks=2)))

    type_options = stats.distinct('key').values_list('key', flat=True)
    stats = stats.filter(key=key).order_by('-created_on')

    if request.GET and request.GET.get('data'):
        if request.GET.get('format', '') == 'json':
            _max = max([stat.val_since_hour for stat in stats])
            output = {
                # {"timestamp": "2014-10-16T22:00:00", "value": {"PM2.5": 61.92}}
                "data": [{
                    'timestamp': stat.created_on.strftime("%Y-%m-%dT%H:00:00"),
                    'value': stat.val_since_hour * 800.0 / _max,
                } for stat in stats]
            }
            # Example output: https://gist.github.com/mbeacom/44f0114666d69bb5bf2756216c43b64d
            return JsonResponse(output)
        #csv
        rows = [['Date', 'Value']]
        _max = max([stat.val_since_yesterday for stat in stats])
        for stat in stats:
            date = stat.created_on.strftime("%Y-%m-%d")
            value = str(stat.val_since_yesterday / _max) if _max else str(0)
            rows.append([date, value])
        output_rows = []
        for row in rows:
            row = ",".join(row)
            output_rows.append(row)

        output = "\n".join(output_rows)
        return HttpResponse(output)
    params = {'stats': stats, 'key': key, 'page_route': template, 'type_options': type_options, 'viz_type': key, }
    return TemplateResponse(request, f'dataviz/{template}.html', params)


@staff_member_required
def viz_index(request):
    """Render the visualization index.

    Returns:
        TemplateResponse: The visualization index template response.

    """
    return TemplateResponse(request, 'dataviz/index.html', {})


@staff_member_required
def viz_circles(request, visual_type):
    """Render a circle graph visualization.

    Args:
        visual_type (str): The visualization type.

    Returns:
        JsonResponse: If data param provided, return a JSON representation of data to be graphed.
        TemplateResponse: If data param not provided, return the populated data visualization template.

    """
    return viz_sunburst(request, visual_type, 'circles')


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


@staff_member_required
def viz_sunburst(request, visual_type, template='sunburst'):
    """Render a sunburst graph visualization.

    Args:
        visual_type (str): The visualization type.
        template (str): The template type to be used. Defaults to: sunburst.

    TODO:
        * Reduce the number of local variables in this method from 18 to 15.

    Returns:
        JsonResponse: If data param provided, return a JSON representation of data to be graphed.
        TemplateResponse: If data param not provided, return the populated data visualization template.

    """
    visual_type_options = ['status_progression', 'repos', 'fulfillers', 'funders', ]
    if visual_type not in visual_type_options:
        visual_type = visual_type_options[0]

    if visual_type == 'status_progression':
        title = "Status Progression Viz"
        comment = 'of statuses begin with this sequence of status'
        categories = list(Bounty.objects.distinct('idx_status').values_list('idx_status', flat=True)) + ['_']
    elif visual_type == 'repos':
        title = "Github Structure of All Bounties"
        comment = 'of bounties value with this github structure'
        categories = [
            bounty.org_name.replace('-', '') for bounty in Bounty.objects.filter(network='mainnet') if bounty.org_name
        ]
        categories += [
            bounty.github_repo_name.replace('-', '') for bounty in Bounty.objects.filter(network='mainnet')
            if bounty.github_repo_name
        ]
        categories += [str(bounty.github_issue_number) for bounty in Bounty.objects.filter(network='mainnet')]
    elif visual_type == 'fulfillers':
        title = "Fulfillers"
        comment = 'of bounties value with this fulfiller'
        categories = []
        for bounty in Bounty.objects.filter(network='mainnet'):
            for fulfiller in bounty.fulfillments.all():
                categories.append(fulfiller.fulfiller_github_username.replace('-', ''))
    elif visual_type == 'funders':
        title = "Funders"
        comment = 'of bounties value with this funder'
        categories = []
        for bounty in Bounty.objects.filter(network='mainnet'):
            categories.append(bounty.bounty_owner_github_username.replace('-', ''))

    if request.GET.get('data'):
        data_dict = data_viz_helper_get_data_responses(request, visual_type)

        _format = request.GET.get('format', 'csv')
        if _format == 'csv':
            rows = []
            for key, value in data_dict.items():
                row = ",".join([key, str(value)])
                rows.append(row)

            output = "\n".join(rows)
            return HttpResponse(output)

        if _format == 'json':
            output = {'name': 'data', 'children': []}
            for key, val in data_dict.items():
                if val:
                    output['children'].append(data_viz_helper_get_json_output(key, val))
            output = data_viz_helper_merge_json_trees(output)
            return JsonResponse(output)

    params = {
        'title': title,
        'comment': comment,
        'viz_type': visual_type,
        'page_route': template,
        'type_options': visual_type_options,
        'categories': json.dumps(list(categories)),
    }
    return TemplateResponse(request, f'dataviz/{template}.html', params)


@staff_member_required
def viz_sankey(request, _type, template='square_graph'):
    return viz_graph(request, _type, template)


def helper_hide_pii(username, num_chars=3):
    if not username:
        return None
    new_username = str(username)[0:num_chars] + "*******"
    return new_username


def viz_graph_data_helper(_type, keyword, hide_pii):
    # setup response
    output = {"nodes": [], "links": []}

    # gather info
    types = {}
    names = {}
    values = {}
    avatars = {}
    edges = []
    bounties = Bounty.objects.current().filter(network='mainnet')
    if keyword:
        bounties = bounties.filter(raw_data__icontains=keyword)

    for bounty in bounties:
        if bounty.value_in_usdt_then:
            weight = bounty.value_in_usdt_then
            source = bounty.org_name
            if source:
                for fulfillment in bounty.fulfillments.all():
                    created = fulfillment.created_on.strftime("%s")
                    if _type != 'fulfillments_accepted_only' or fulfillment.accepted:
                        target = fulfillment.fulfiller_github_username.lower()
                        if hide_pii:
                            target = helper_hide_pii(target)
                        types[source] = 'source'
                        types[target] = 'target_accepted' if fulfillment.accepted else 'target'
                        names[source] = None
                        names[target] = None
                        edges.append((source, target, weight, created))

                        value = values.get(source, 0)
                        value += weight
                        values[source] = value
                        value = values.get(target, 0)
                        value += weight
                        values[target] = value

    for tip in Tip.objects.filter(network='mainnet'):
        weight = tip.value_in_usdt
        created = tip.created_on.strftime("%s")
        if weight:
            source = tip.username.lower()
            if hide_pii:
                source = helper_hide_pii(source)
            target = tip.from_username.lower()
            if hide_pii:
                target = helper_hide_pii(target)
            if source and target:
                if source not in names.keys():
                    types[source] = 'source'
                    names[source] = None
                if source not in types.keys():
                    types[target] = 'target'
                    names[target] = None
                edges.append((source, target, weight, created))

    if _type in ['what_future_could_look_like', 'all']:
        last_node = None
        created = 1525147679
        nodes = Profile.objects.exclude(github_access_token='').all()
        for profile in nodes:
            node = profile.handle.lower()
            if hide_pii:
                node = helper_hide_pii(node)
            if node not in names.keys():
                names[node] = None
                types[node] = 'independent'
            if last_node and _type == 'what_future_could_look_like':  # and random.randint(0, 2) == 0:
                weight = random.randint(1, 10)
                # edges.append((node, last_node, weight))
                # edges.append((nodes.order_by('?').first().handle.lower(), node, weight))
                target = nodes.order_by('?').first().handle.lower()
                if hide_pii:
                    target = helper_hide_pii(target)
                edges.append((target, node, weight, created))
            last_node = node

    for key, val in values.items():
        if val > 40:
            avatar_key = key if key and "*" not in key else "None"
            avatars[key] = f'https://gitcoin.co/dynamic/avatar/{avatar_key}'

    # build output
    for name in set(names.keys()):
        names[name] = len(output['nodes'])
        value = int(math.sqrt(math.sqrt(values.get(name, 1))))
        output['nodes'].append({"name": name, 'value': value, 'type': types.get(name), 'avatar': avatars.get(name)})
    for edge in edges:
        source, target, weight, created = edge
        weight = math.sqrt(weight)
        if names.get(source) and names.get(target):
            source = names[source]
            target = names[target]
            output['links'].append({
                'source': source,
                'target': target,
                'value': value,
                'weight': weight,
                'created': created,
            })
    return output


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


@staff_member_required
def viz_draggable(request, key='email_open'):
    """Render a draggable graph visualization.

    Args:
        key (str): The key type to visualize.

    Returns:
        TemplateResponse: The populated draggable data visualization template.

    """
    stats = []
    type_options = []
    bfs = BountyFulfillment.objects.filter(accepted=True)
    limit = 50
    usernames = list(
        bfs.exclude(fulfiller_github_username=''
                    ).distinct('fulfiller_github_username').values_list('fulfiller_github_username', flat=True)
    )[0:limit]
    if request.GET.get('data'):
        output = []
        for username in usernames:
            these_bounties = bfs.filter(fulfiller_github_username=username)
            start_date = timezone.now() - timezone.timedelta(days=180)
            income = []
            lifeExpectancy = []
            population = []
            val_usdt = 0
            for i in range(1, 180):
                current_date = start_date + timezone.timedelta(days=i)
                prev_date = start_date + timezone.timedelta(days=(i - 1))
                these_bounties_before_date = these_bounties.filter(created_on__lt=current_date)
                these_bounties_in_range = these_bounties.filter(created_on__lt=current_date, created_on__gt=prev_date)
                val_usdt += sum(bf.bounty.value_in_usdt for bf in these_bounties_in_range if bf.bounty.value_in_usdt)
                num_bounties = these_bounties_before_date.distinct('bounty').count()
                income.append([i, val_usdt])  # x axis
                lifeExpectancy.append([i, num_bounties])  # y axis
                population.append([i, 10000000 * num_bounties])  # size
                #print(username, i, num_bounties, val_usdt)
            output.append({
                'name': username,
                'region': username,
                'income': income,
                'population': population,
                'lifeExpectancy': lifeExpectancy,
            })

        return JsonResponse(output, safe=False)

    params = {
        'stats': stats,
        'key': key,
        'usernames': json.dumps(usernames),
        'page_route': 'draggable',
        'type_options': type_options,
        'viz_type': key,
    }
    return TemplateResponse(request, 'dataviz/draggable.html', params)


def viz_scatterplot_stripped(request, key='hourly_rate'):
    return viz_scatterplot_helper(request, 'hourly_rate', 'dataviz/scatterplot_stripped.html', True)


@staff_member_required
def viz_scatterplot(request, key='hourly_rate', template='dataviz/scatterplot.html', hide_usernames=False):
    return viz_scatterplot_helper(request, key, template, hide_usernames)


def viz_scatterplot_data_helper(keyword, hide_usernames=False):
    rows = [['hourlyRate', 'daysBack', 'username', 'weight']]
    fulfillments = BountyFulfillment.objects.filter(accepted=True).exclude(fulfiller_hours_worked=None)
    if keyword:
        filter_bounties = Bounty.objects.filter(raw_data__icontains=keyword)
        fulfillments = fulfillments.filter(bounty__in=filter_bounties)
    for bf in fulfillments:
        #print(bf.pk, bf.created_on)
        try:
            weight = math.log(bf.bounty.value_in_usdt, 10) / 4
            username = bf.bounty.org_name
            if hide_usernames:
                username = "repo: " + helper_hide_pii(username.lower(), 1)
            row = [str(bf.bounty.hourly_rate), str((timezone.now() - bf.accepted_on).days), username, str(weight), ]
            if bf.bounty.hourly_rate:
                rows.append(row)
        except Exception:
            pass

    output_rows = []
    for row in rows:
        output_rows.append(",".join(row))

    output = "\n".join(output_rows)
    return output


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
