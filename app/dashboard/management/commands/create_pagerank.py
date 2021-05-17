'''
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

'''

import math
import random
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Earning, Profile, ProfileStatHistory


def get_exponent(num, base=5):
    i = 1
    while base**i < num:
        i += 1
    return i


def choose_edge(edges):
    entropy = random.random()
    cursor = 0
    last_edge = edges[0]
    for edge in edges:
        last_edge = edge
        last_cursor = cursor
        this_weight = edge[2]
        cursor += this_weight
        if entropy >= last_cursor and entropy < cursor:
            return edge[0]
    return last_edge[0]


class Command(BaseCommand):

    help = 'create pagerank graph and update the pagerank profiles of each'

    def handle(self, *args, **options):

        # setup
        top_range_pagerank = 10
        num_traversals_of_graph = 4 if settings.DEBUG else 500
        percent_that_go_to_random_walk = 20
        final_results = {}

        for direction in ['funder', 'coder', 'org']:

            # config
            random_edge = '**__random__**'

            # pull edges
            earnings = Earning.objects.filter(network='mainnet').exclude(to_profile__isnull=True).exclude(from_profile__isnull=True).exclude(value_usd__isnull=True)
            edges = earnings.values_list('from_profile__handle', 'to_profile__handle', 'value_usd')
            if direction == 'funder':
                edges = earnings.values_list('to_profile__handle', 'from_profile__handle', 'value_usd')
            if direction == 'org':
                earnings = earnings.exclude(org_profile__isnull=True)
                edges = earnings.values_list('from_profile__handle', 'org_profile__handle', 'value_usd')

            # remove self links
            edges = [ele for ele in edges if ele[1] != ele[0]]

            # print("*")
            # setup node map
            nodes_map = {}
            for edge in edges:
                nodes_map[edge[1]] = []
                nodes_map[edge[0]] = []

            # setup DAG
            for edge in edges:
                nodes_map[edge[0]].append((edge[1], edge[2]))

            # add in percent_that_go_to_random_walk to dag
            weighted_node_map = {}
            grand_total_weight = 0
            for key in nodes_map.keys():
                weighted_node_map[key] = {'weight': 0, 'edges': []}
            for key, forward_edges in nodes_map.items():

                # calculate random walk edge
                edge_total = float(sum([ele[1] for ele in forward_edges]))
                if edge_total:
                    amount_to_go_to_random_walk = float(edge_total) * float(percent_that_go_to_random_walk) * 0.01
                else:
                    amount_to_go_to_random_walk = 1

                # collapse dupe edges (repeat relationships) into one edge
                inner_edges = {ele[0]: 0 for ele in forward_edges }
                for ele in forward_edges:
                    inner_edges[ele[0]] += ele[1]

                # update edges with percentage
                edge_total += float(amount_to_go_to_random_walk)
                grand_total_weight += edge_total
                inner_edges[random_edge] = amount_to_go_to_random_walk
                for node, value in inner_edges.items():
                    weight_as_pct = float(value) / edge_total
                    new_edge = [node, value, weight_as_pct]
                    weighted_node_map[key]['edges'].append(new_edge)
                    weighted_node_map[key]['weight'] = edge_total

            # print("****stats****")
            # print(f"nodes: {len(nodes_map.items())}")
            # print(f"total_weight: {round(grand_total_weight,2)}")
            # print(f"avg_weight: {round(grand_total_weight/len(nodes_map.items()), 2)}")

            total_owocki = sum([ele[2] for ele in weighted_node_map['owocki']['edges']])

            # walk the pagerank
            all_nodes = weighted_node_map.keys()
            all_nodes_mins_random = [ele for ele in weighted_node_map.keys() if ele != random_edge]
            pagerank = {ele:0 for ele in all_nodes}
            for i in range(1, num_traversals_of_graph):

                # print(f"iteration {i}")
                print(".", end='')

                # gotta start somewhere
                random.shuffle(all_nodes_mins_random)
                starter_node = all_nodes_mins_random[0]
                #print(f"staring with {starter_node}")
                current_node = starter_node
                keep_walking = True

                # walk the graph
                total_weight_this_iteration = 0
                start_time = time.time()
                while keep_walking:

                    # setup
                    this_node = weighted_node_map[current_node]
                    forward_edges = this_node['edges']
                    weight = this_node['weight']

                    # find the next edge
                    next_edge = choose_edge(forward_edges)
                    if next_edge == random_edge:
                        random.shuffle(all_nodes_mins_random)
                        next_edge = all_nodes_mins_random[0]

                    # adjust rank
                    pagerank[next_edge] += weight
                    total_weight_this_iteration += weight

                    # continue or dont
                    keep_walking = total_weight_this_iteration < grand_total_weight
                    current_node = next_edge
                    #print(f'({weight},{total_weight_this_iteration},{next_edge})')
                    #print(".", end='')
                end_time = time.time()
                execution_time = end_time - start_time

                # print(f"iteration in {execution_time}s")
                # print(f"iamonuwa pagerank: {round(pagerank['iamonuwa'])}, avg {round(pagerank['iamonuwa']/i)}")
                # print(f"gutsal-arsen pagerank: {round(pagerank['gutsal-arsen'])}, avg {round(pagerank['gutsal-arsen']/i)}")
                # print(f"owocki pagerank: {round(pagerank['owocki'])}, avg {round(pagerank['owocki']/i)}")

            max_pagerank = max([val for key, val in pagerank.items()])
            bucket_size = max_pagerank / 100

            for key in pagerank.keys():
                pagerank[key] = get_exponent(pagerank[key]/num_traversals_of_graph)

            print("")
            print("***************")
            #print(f"onuwa {direction} pagerank: {round(pagerank['iamonuwa'])}")
            #print(f"gutsal-arsen {direction} pagerank: {round(pagerank['gutsal-arsen'])}")
            #print(f"owocki {direction} pagerank: {round(pagerank['owocki'])}")

            sorted_pr = [(k, pagerank[k]) for k in sorted(pagerank, key=pagerank.get, reverse=True)]
            print(f"{direction} pagerank:")
            for i in range(0, 10):
                print(f"{i} {sorted_pr[i]}")

            final_results[direction] = pagerank

        # update
        # print(f"-{len(final_results['funder'])}-")
        # print(f"-{len(final_results['org'])}-")
        # print(f"-{len(final_results['funder'])}-")
        all_keys = []
        max_pagerank = 0
        for direction in ['funder', 'coder', 'org']:
            all_keys = all_keys + list(final_results[direction].keys())
            max_pagerank = max(max_pagerank, max(final_results[direction].values()))
        all_keys = set(all_keys)

        pagerank_offset = top_range_pagerank - max_pagerank
        print(f"offsetting all contributions by {pagerank_offset}")
        i = 0
        for handle in all_keys:
            i += 1
            profile = Profile.objects.get(handle=handle)
            profile.rank_funder = final_results['funder'].get(handle, 0) + pagerank_offset
            profile.rank_org = final_results['org'].get(handle, 0) + pagerank_offset
            profile.rank_coder = final_results['coder'].get(handle, 0) + pagerank_offset
            profile.save()

            ProfileStatHistory.objects.create(
                profile=profile,
                key='pagerank',
                payload={
                    'org': profile.rank_org,
                    'coder': profile.rank_coder,
                    'funder': profile.rank_funder,
                }
                )
        print("fin")
