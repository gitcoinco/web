# -*- coding: utf-8 -*-
"""Define the Grants application configuration.

Copyright (C) 2020 Gitcoin Core

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
import copy
import datetime as dt
import json
import math
import time
from itertools import combinations

from django.utils import timezone

from grants.models import Contribution, Grant, PhantomFunding
from perftools.models import JSONStore

LOWER_THRESHOLD = 0.0
CLR_START_DATE = dt.datetime(2020, 1, 6, 0, 0)



'''
    Helper function that translates existing grant data structure
    to a list of lists.

    Args:
        {
            'id': (string) ,
            'contibutions' : [
                {
                    contributor_profile (str) : contribution_amount (int)
                }
            ]
        }

    Returns:
        [[grant_id (str), user_id (str), contribution_amount (float)]]
'''
def translate_data(grants):
    grants_list = []
    for grant in grants:
        grant_id = grant.get('id')
        for contribution in grant.get('contributions'):
            val = [grant_id] + [list(contribution.keys())[0], list(contribution.values())[0]]
            grants_list.append(val)
    return grants_list


'''
    Helper function that aggregates contributions by contributor, and then
    uses the aggregated contributors by contributor and calculates total
    contributions by unique pairs.

    Args:
        from translate_data:
        [[grant_id (str), user_id (str), contribution_amount (float)]]

    Returns:
        {grant_id (str): {user_id (str): aggregated_amount (float)}}
        {user_id (str): {user_id (str): pair_total (float)}}
'''
def aggregate_contributions(grant_contributions):
    contrib_dict = {}
    for proj, user, amount in grant_contributions:
        if proj not in contrib_dict:
            contrib_dict[proj] = {}
        contrib_dict[proj][user] = contrib_dict[proj].get(user, 0) + amount

    tot_overlap = {}
    for proj, contribz in contrib_dict.items():
        for k1, v1 in contribz.items():
            if k1 not in tot_overlap:
                tot_overlap[k1] = {}
            for k2, v2 in contribz.items():
                if k2 not in tot_overlap[k1]:
                    tot_overlap[k1][k2] = 0
                tot_overlap[k1][k2] += (v1 * v2) ** 0.5
    return contrib_dict, tot_overlap



'''
    Helper function that aggregates contributions by contributor, and then uses the aggregated contributors by contributor and calculates total contributions by unique pairs.

    Args:
        from get_data or translate_data: [[grant_id (str), user_id (str), contribution_amount (float)]]

        grant_id: grant being donated to

        live_user: user doing the donation

    Returns:
        {grant_id (str): {user_id (str): aggregated_amount (float)}}

        and

        {user_id (str): {user_id (str): pair_total (float)}}
'''
def aggregate_contributions_live(grant_contributions, grant_id=86.0, live_user=99999999.0):
    contrib_dict = {}
    for proj, user, amount in grant_contributions:
        if proj not in contrib_dict:
            contrib_dict[proj] = {}
        contrib_dict[proj][user] = contrib_dict[proj].get(user, 0) + amount
    contrib_dict_list = []
    tot_overlap_list = []
    for amount in [0, 1, 10, 100, 1000]:
        contrib_dict_copy = copy.deepcopy(contrib_dict)
        contrib_dict_copy[grant_id][live_user] = contrib_dict_copy[grant_id].get(live_user, 0) + amount
        contrib_dict_list.append(contrib_dict_copy)
        tot_overlap = {}
        for proj, contribz in contrib_dict_copy.items():
            for k1, v1 in contribz.items():
                if k1 not in tot_overlap:
                    tot_overlap[k1] = {}
                for k2, v2 in contribz.items():
                    if k2 not in tot_overlap[k1]:
                        tot_overlap[k1][k2] = 0
                    tot_overlap[k1][k2] += (v1 * v2) ** 0.5
        tot_overlap_list.append(tot_overlap)
        # print(f'finished predicting {amount}')
    return contrib_dict_list, tot_overlap_list



'''
    Helper function that runs the pairwise clr formula while "binary" searching for the correct threshold.

    Args:
    
        aggregated_contributions: {grant_id (str): {user_id (str): aggregated_amount (float)}}
        pair_totals: {user_id (str): {user_id (str): pair_total (float)}}
        threshold: pairwise coefficient
        total_pot: total pot for the tech or media round, default tech

    Returns:
        totals: total clr award by grant, normalized by the normalization factor
'''
def calculate_new_clr(aggregated_contributions, pair_totals, threshold=25.0, total_pot=125000.0):
    bigtot = 0
    totals = []
    # single donation doesn't get a match
    for proj, contribz in aggregated_contributions.items():
        tot = 0
        for k1, v1 in contribz.items():
            for k2, v2 in contribz.items():
                if k2 > k1:  # remove pairs
                    # # pairwise matching formula
                    # tot += (v1 * v2) ** 0.5 * min(1, threshold / pair_totals[k1][k2])
                    # vitalik's division formula
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / threshold + 1)
        bigtot += tot
        totals.append({'id': proj, 'clr_amount': tot})
    # find normalization factor
    normalization_factor = bigtot / total_pot
    # modify totals
    for result in totals:
        result['clr_amount'] = result['clr_amount'] / normalization_factor
    # # check total = pot
    # print(f'total pot check = {sum([x["clr_amount"] for x in totals])}')
    return bigtot, totals 



'''
    Clubbed function that intakes grant data, calculates necessary
    intermediate calculations, and spits out clr calculations.

    Args:
        grant_contributions:    {
            'id': (string) ,
            'contributions' : [
                {
                    contributor_profile (str) : contribution_amount (int)
                }
            ]
        }
        total_pot       (float)
        lower_bound     (float)

    Returns:
        bigtot: should equal total pot
        totals: clr totals
'''
def grants_clr_calculate (grant_contributions, total_pot, threshold=25.0, total_pot=125000.0):
    grants_list = translate_data(grant_contributions)
    aggregated_contributions, pair_totals = aggregate_contributions(grants_list)
    bigtot, totals = calculate_new_clr(aggregated_contributions, pair_totals, threshold=threshold, total_pot=total_pot)
    return bigtot, totals



'''
    Function that intakes the clr start date, the grant that is currently being looked at, the user who is looking at it, the grant clr type, and the clr amount and predicts the current CLR reward amount, and incremental additions to the CLR amount given a 1, 10, 100, and 1000 donation.

    Args:
        from_date
        clr_type
        network
        grant_id
        live_user

    Returns:
        debug output: clr prediction curve
'''
def predict_clr(from_date=None, clr_type=None, network='mainnet', grant_id=86.0, live_user=99999999.0): 
    # setup
    debug_output = []

    # determine grant type in question
    if clr_type == 'tech':
        grants = Grant.objects.filter(network=network, hidden=False, grant_type='tech', link_to_new_grant=None)
    elif clr_type == 'media':
        grants = Grant.objects.filter(network=network, hidden=False, grant_type='media', link_to_new_grant=None)
    else:
        grants = Grant.objects.filter(network=network, hidden=False, link_to_new_grant=None)

    # translate grant data structure
    grants = translate_data(grants)

    # get aggregated contributions and pair total amounts with a hypothetical 1, 10, 100, 1000
    aggregated_contributions_list = pair_totals_list = aggregate_contributions_live(grants, grant_id=grant_id, live_user=live_user)

    # calculate the curve
    clr_curve = []
    for x, y in zip(aggregated_contributions_list, pair_totals_list):
        res = calculate_new_clr(x, y)
        pred = list(filter(lambda x: x['id'] == grant_id, res))[0]['clr_amount']
        clr_curve.append(pred)
    # [grant_clr, additional CLR granted with 1, 10, 100, 1000 donations], 5 elements total
    clr_curve = [clr_curve[0]] + [x - clr_curve[0] for x in clr_curve[1:]]

    debug_output.append({'grant': grant.id, "clr_prediction_curve": ([1, 10, 100, 1000], clr_curve[1:]), "grants_clr": clr_curve[0]})
    return debug_output
