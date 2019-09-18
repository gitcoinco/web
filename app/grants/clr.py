# -*- coding: utf-8 -*-
"""Define the Grants application configuration.

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
import copy
import datetime as dt
import json
import math
from itertools import combinations

from grants.models import Contribution, Grant

CLR_DISTRIBUTION_AMOUNT = 100000

grant_contributions = [
    {
        'id': '1',
        'contributions': [
            { '1': 5 },
            { '2': 10 },
            { '3': 25 }
        ]
    },
    {
        'id': '2',
        'contributions': [
            { '3': 20 },
            { '1': 2 },
            { '4': 2 },
            { '5': 5 },
            { '1': 15 }
        ]
    }
]

'''
    Helper function that generates all combinations of pair of grant
    contributions and the corresponding sqrt of the product pair

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
        {
            'id': (str),
            'profile_pairs': [tuples],
            'contribution_pairs': [tuples],
            'sqrt_of_product_pairs':  array
        }
'''
def generate_grant_pair(grant):
    grant_id = grant.get('id')
    grant_contributions = grant.get('contributions')
    unique_contributions = {}

    for contribution in grant_contributions:
        for profile, amount in contribution.items():
            if unique_contributions.get(profile):
                donation = unique_contributions[profile] + amount
                unique_contributions[profile] = donation
            else:
                unique_contributions[profile] = amount

    #print(f'Grant Contributions: {grant_contributions}')
    #print(f'Unique Contributions: {unique_contributions}')

    profile_pairs = list(combinations(unique_contributions.keys(), 2))
    contribution_pairs = list(combinations(unique_contributions.values(), 2))

    sqrt_of_product_pairs = []
    for contribution_1, contribution_2 in contribution_pairs:
        sqrt_of_product = round(math.sqrt(contribution_1 * contribution_2))
        sqrt_of_product_pairs.append(sqrt_of_product)


    grant = {
        'id': grant_id,
        'profile_pairs': profile_pairs,
        'contribution_pairs': contribution_pairs,
        'sqrt_of_product_pairs': sqrt_of_product_pairs
    }

    #print(f'Grant ID: {grant["id"]}')
    #print(f'Profile Pairs: {grant["profile_pairs"]}')
    #print(f'Contribution Pairs: {grant["contribution_pairs"]}')
    #print(f'Sqrt Of Product Pairs: {grant["sqrt_of_product_pairs"]}')

    #print('=================\n')

    return grant


'''
    Given a threshold and grant conributions, it calculates the
    total clr and how that would be split amongst the grants

    Args:
        threshold: (int),
        grant: {
            'id': (string),
            'contibutions' : [
                {
                    contributor_profile (str) : contribution_amount (int)
                }
            ]
        }

    Returns:
        {
            'total_clr': (int),
            '_clrs': [
                {
                    'id': (str),
                    'clr_amount': (int)
                }
            ]
        }
'''
def calculate_clr(threshold, grant_contributions):
    grants = []
    group_by_pair = {}

    total_clr = 0

    for grant_contribution in grant_contributions:
        grant = generate_grant_pair(grant_contribution)

        grants.append(grant)

        for index, profile_pair in enumerate(grant['profile_pairs']):
            pair = str('&'.join(profile_pair))
            pair_reversed = str('&'.join(profile_pair[::-1]))

            if group_by_pair.get(pair):
                group_by_pair[pair] += grant['sqrt_of_product_pairs'][index]
            elif group_by_pair.get(pair_reversed):
                group_by_pair[pair_reversed] += grant['sqrt_of_product_pairs'][index]
            else:
                group_by_pair[pair] = grant['sqrt_of_product_pairs'][index]

    # print(f'SUM OF GROUPED BY PAIRS {group_by_pair} \n=================\n')

    _clrs = []

    for grant in grants:
        grant_clr = 0
        lr_contributions = []
        #print(grant['profile_pairs'])
        for index, profile_pair in enumerate(grant['profile_pairs']):
            pair = str('&'.join(profile_pair))
            pair_reversed = str('&'.join(profile_pair[::-1]))
            _pair = None
            if group_by_pair.get(pair):
                _pair = pair
            elif group_by_pair.get(pair_reversed):
                _pair = pair_reversed

            lr_contribution = 0
            sqrt_of_product_pair = grant["sqrt_of_product_pairs"][index]

            if threshold >= sqrt_of_product_pair:
                lr_contribution = sqrt_of_product_pair
            else:
                lr_contribution = threshold * (sqrt_of_product_pair / group_by_pair.get(_pair))

            lr_contributions.append(lr_contribution)
            grant_clr += lr_contribution
            total_clr += lr_contribution
            # print(f'LR CONTRIBUTION {lr_contribution} | PAIR {profile_pair}')

        # print(f'\n+++++\nGRANT {grant["id"]} - CLR CONTRIBUTION {grant_clr} \n+++++')
        _clrs.append({
            'id': grant["id"],
            'clr_amount': grant_clr
        })
    # print(f'\n\n============ \nTOTAL CLR {total_clr} \n=============')

    return total_clr, _clrs


'''
    Given the total pot and grants and it's contirbutions,
    it uses binary search to find out the threshold so
    that the entire pot can be distributed based on it's contributions

    Args:
        total_pot:      (int),
        grant_contributions: object,
        min_threshold:  (int)
        max_threshold:  (int)
        iterations:     (int)

    Returns:
        grants_clr (object)
        total_clr  (int)
        threshold  (int)
        iterations (int)
'''
def grants_clr_calculate (total_pot, grant_contributions, min_threshold, max_threshold, iterations = 0):
    # print("seeing {} contributions".format(len(grant_contributions)))
    # print("calculating CLR for contributions:{}".format(grant_contributions))
    if len(grant_contributions) == 0:
        return 0, 0, 0, 0
    iterations += 1
    threshold = (max_threshold + min_threshold) / 2
    total_clr, grants_clrs = calculate_clr(threshold, grant_contributions)

    # print(f'************ POT:  {total_pot} | Calculated CLR:  {total_clr} | Threshold {threshold} | Iterations {iterations} | GRANT SPLIT {grants_clrs}')

    if iterations == 100:
        return grants_clrs, total_clr, threshold, iterations

    if total_pot == threshold:
        # EDGE CASE: when total_pot !== total_clr for any threshold
        return grants_clrs, total_clr, threshold, iterations
    if total_clr > total_pot:
        max_threshold = threshold
        # print(f'++ MIN {min_threshold} NEW MAX {max_threshold}')
    elif total_clr < total_pot:
        min_threshold = threshold
        #print(f'-- NEW MIN {min_threshold} MAX {max_threshold}')
    else:
        return grants_clrs, total_clr, threshold, iterations

    return grants_clr_calculate(total_pot, grant_contributions, min_threshold, max_threshold, iterations)

'''
total_pot = 50
max_threshold = total_pot
min_threshold= 0

grants_clr, total_clr, threshold, iterations = grants_clr_calculate(total_pot, grant_contributions, min_threshold, max_threshold)
print(f'\n\n\n=============== \nFINAL \nPOT:  {total_pot} \nCalculated CLR:  {total_clr} \nThreshold {threshold} \nIterations {iterations} \nCLR Breakup\n')
print(json.dumps(grants_clr, indent=2))
print('===============')
'''

def generate_random_contribution_data():
    import random
    contrib_data = []
    for grant_id in range(33):
        contrib_data.append({'id': grant_id, 'contributions': [{str(profile_id): random.randint(3000,6890)} for profile_id in range(random.randint(0,17))]})
    return contrib_data


def calculate_clr_for_donation(donation_grant, donation_amount, total_pot, base_grant_contributions):
    grant_contributions = copy.deepcopy(base_grant_contributions)
    # find grant in contributions list
    if donation_amount != 0:
        for grant_contribution in grant_contributions:
            if grant_contribution['id'] == donation_grant.id:
                # add this donation with a new profile to get impact
                grant_contribution['contributions'].append({'999999999999': donation_amount})
    grants_clr, _, _, _ = grants_clr_calculate(CLR_DISTRIBUTION_AMOUNT, grant_contributions, 0, CLR_DISTRIBUTION_AMOUNT)
    # print("GRANTS CLR: {}".format(grants_clr))
    # print("TOTAL CLR: {}".format(total_clr))
    # if grants_clr == 0:
    #    return 0
    for grant_clr in grants_clr:
        if grant_clr['id'] == donation_grant.id:
            return (grant_clr['clr_amount'], grants_clr)
    print('error: could not find grant in final grants_clr data')
    return (None, None)

def predict_clr(random_data=False):
    clr_start_date = dt.datetime(2019, 1, 15, 0, 0)
    # get all the eligible contributions and calculate total
    contributions = Contribution.objects.prefetch_related('subscription').filter(created_on__gte=clr_start_date)
    grants = Grant.objects.all()
    final_output = []
    contrib_data = []

    # set up data to load contributions for each grant
    if not random_data:
        for grant in grants:
            # go through all the individual contributions for each grant
            g_contributions = copy.deepcopy(contributions).filter(subscription__grant_id=grant.id)

            # put in correct format
            all_contributing_profile_ids = list(set([c.subscription.contributor_profile.id for c in g_contributions]))
            all_summed_contributions = []
            print("*** grant id:{} has contributions from profiles: {}".format(grant.id, all_contributing_profile_ids))
            for profile_id in all_contributing_profile_ids:
                profile_g_contributions = g_contributions.filter(subscription__contributor_profile_id=profile_id)
                sum_of_each_profiles_contributions = float(sum([c.subscription.get_converted_monthly_amount() for c in profile_g_contributions]))
                print("*** profile id:{} contributed total:{}".format(profile_id, sum_of_each_profiles_contributions))
                all_summed_contributions.append({str(profile_id): sum_of_each_profiles_contributions})
            #contrib_data.append({'id': grant.id, 'contributions': [{str(c.subscription.contributor_profile.id): c.subscription.get_converted_monthly_amount()} for c in g_contributions]})
            contrib_data.append({'id': grant.id, 'contributions': all_summed_contributions})
    else:
        contrib_data = generate_random_contribution_data()
    print('\n\ncontributions data:\n\n')
    print(contrib_data)
    # apply potential donations for each grant
    for grant in grants:
        # five potential additional donations
        potential_donations = [0, 1, 10, 100, 1000, 10000]
        potential_clr = []
        for donation_amount in potential_donations:
            # calculate impact for each additional donation and save as number to display
            predicted_clr, grants_clr = calculate_clr_for_donation(grant, donation_amount, CLR_DISTRIBUTION_AMOUNT, contrib_data)
            potential_clr.append(predicted_clr)
        # grant.clr_prediction_curve = zip(potential_donations, potential_clr)
        # grant.save()
        # print("grant: {} potential_clr: {}".format(grant.id, potential_clr))
        final_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})
    return final_output
# Test 1 iteration
# threshold = 10
# calculate_clr(threshold, grant_contributions)
