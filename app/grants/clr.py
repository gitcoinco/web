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
    Helper function that runs the pairwise clr formula while "binary"
    searching for the correct threshold.

    Args:

        aggregated_contributions : {
            grant_id (str): {
                user_id (str): aggregated_amount (float)
            }
        }
        pair_totals : { user_id (str): { user_id (str): pair_total (float) } }
        total_pot   :      (float)
        lower_bound :    (float)

    Returns:
        bigtot: (float)
        totals: [
            {
                id: (str),
                clr_amount: (float)
            }
        ]
'''
def iter_threshold(aggregated_contributions, pair_totals, total_pot, lower_bound):
    lower = lower_bound
    upper = total_pot
    iterations = 0

    while iterations < 100:
        threshold = (lower + upper) / 2
        iterations += 1
        if iterations == 100:
            break # break at 100th iteration
        bigtot = 0
        totals = []

        for proj, contribz in aggregated_contributions.items():
            tot = 0
            for k1, v1 in contribz.items():
                for k2, v2 in contribz.items():
                    if k2 > k1:  # ensure (k1,k2) and (k2,k1) are counted only once
                        tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / threshold + 1)
            bigtot += tot
            totals.append({'id': proj, 'clr_amount': tot})
        if bigtot == total_pot:
            break
        elif bigtot < total_pot:
            lower = threshold
        elif bigtot > total_pot:
            upper = threshold
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
def grants_clr_calculate (grant_contributions, total_pot, lower_bound):
    grants_list = translate_data(grant_contributions)
    aggregated_contributions, pair_totals = aggregate_contributions(grants_list)
    bigtot, totals = iter_threshold(aggregated_contributions, pair_totals, total_pot, lower_bound)
    return bigtot, totals


def generate_random_contribution_data():
    import random
    contrib_data = []
    # whatever the range is here, you should have that many grants locally to test with
    # this function generates fake contribution data, but assumes the grants are in the db

    grants_to_use = 33
    low_donation = 3000
    high_donation = 6890
    number_of_profiles = 17

    for grant_id in range(grants_to_use):
        contrib_data.append({
            'id': grant_id,
            'contributions': [
                {
                    str(profile_id): random.randint(low_donation, high_donation)
                } for profile_id in range(random.randint(1, number_of_profiles))
            ]
        })
    return contrib_data


def calculate_clr_for_donation(donation_grant, donation_amount, total_pot, base_grant_contributions):
    grant_contributions = copy.deepcopy(base_grant_contributions)
    # find grant in contributions list and add donation
    if donation_amount != 0:
        for grant_contribution in grant_contributions:
            if grant_contribution['id'] == donation_grant.id:
                # add this donation with a new profile (id 99999999999) to get impact
                grant_contribution['contributions'].append({'999999999999': donation_amount})

    _, grants_clr = grants_clr_calculate(grant_contributions, total_pot, LOWER_THRESHOLD)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == donation_grant.id:
            return (grant_clr['clr_amount'], grants_clr)

    print(f'info: no contributions found for grant {donation_grant}')
    return (None, None)

def predict_clr(random_data=False, save_to_db=False, from_date=None, clr_type=None, network='mainnet', clr_amount=0):
    # setup
    clr_calc_start_time = timezone.now()

    # get all the eligible contributions and calculate total
    contributions = Contribution.objects.prefetch_related('subscription').filter(created_on__gte=CLR_START_DATE, created_on__lte=from_date, success=True)
    debug_output = []

    if clr_type == 'tech':
        grants = Grant.objects.filter(network=network, hidden=False, grant_type='tech', link_to_new_grant=None)
    elif clr_type == 'media':
        grants = Grant.objects.filter(network=network, hidden=False, grant_type='media', link_to_new_grant=None)
    else:
        grants = Grant.objects.filter(network=network, hidden=False, link_to_new_grant=None)

    # set up data to load contributions for each grant
    if not random_data:
        contrib_data = []

        for grant in grants:
            # go through all the individual contributions for each grant
            g_contributions = copy.deepcopy(contributions).filter(subscription__grant_id=grant.id)

            # put in correct format
            phantom_funding_profiles = PhantomFunding.objects.filter(grant_id=grant.id, created_on__gte=CLR_START_DATE, created_on__lte=from_date)
            all_contributing_profile_ids = list(set([c.subscription.contributor_profile.id for c in g_contributions] + [p.profile_id for p in phantom_funding_profiles]))
            all_summed_contributions = []

            for profile_id in all_contributing_profile_ids:
                # get sum of contributions per grant for each profile
                profile_g_contributions = g_contributions.filter(subscription__contributor_profile_id=profile_id)
                sum_of_each_profiles_contributions = float(sum([c.subscription.get_converted_monthly_amount() for c in profile_g_contributions]))

                phantom_funding = PhantomFunding.objects.filter(created_on__gte=CLR_START_DATE, grant_id=grant.id, profile_id=profile_id, created_on__lte=from_date)
                if phantom_funding.exists():
                    sum_of_each_profiles_contributions = sum_of_each_profiles_contributions + phantom_funding.first().value

                all_summed_contributions.append({str(profile_id): sum_of_each_profiles_contributions})

            # for each grant, list the contributions in key value pairs like {'profile id': sum of contributions}
            grant_id = grant.defer_clr_to.pk if grant.defer_clr_to else grant.id
            contrib_data.append({'id': grant_id, 'contributions': all_summed_contributions})

    else:
        # use random contribution data for testing
        contrib_data = generate_random_contribution_data()

    #print(f'\n contributions data: {contrib_data} \n')

    # calculate clr given additional donations
    for grant in grants:
        # five potential additional donations plus the base case of 0
        potential_donations = [0, 1, 10, 100, 1000, 10000]
        potential_clr = []

        for donation_amount in potential_donations:
            # calculate clr with each additional donation and save to grants model
            predicted_clr, grants_clr = calculate_clr_for_donation(grant, donation_amount, clr_amount, contrib_data)
            potential_clr.append(predicted_clr)

        if save_to_db:
            grant.clr_prediction_curve = list(zip(potential_donations, potential_clr))
            base = grant.clr_prediction_curve[0][1]
            grant.last_clr_calc_date = timezone.now()
            grant.next_clr_calc_date = timezone.now() + timezone.timedelta(hours=4)
            if base:
                grant.clr_prediction_curve  = [[ele[0], ele[1], ele[1] - base] for ele in grant.clr_prediction_curve ]
            else:
                grant.clr_prediction_curve = [[0.0, 0.0, 0.0] for x in range(0, 6)]

            JSONStore.objects.create(
                created_on=from_date,
                view='clr_contribution',
                key=f'{grant.id}',
                data=grant.clr_prediction_curve,
            )
            if from_date > (clr_calc_start_time - timezone.timedelta(hours=1)):
                grant.save()

        debug_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})
    return debug_output
