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
    Helper function that aggregates contributions by contributor, and then uses the aggregated contributors by contributor and calculates total contributions by unique pairs.

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
    Helper function that runs the pairwise clr formula for positive or negative instances, depending on the switch.

    Args:
        aggregated_contributions: {grant_id (str): {user_id (str): aggregated_amount (float)}}
        pair_totals: {user_id (str): {user_id (str): pair_total (float)}}
        threshold: pairwise coefficient
        total_pot: total pot set for the round category
        positive: positive or negative contributions

    Returns:
        totals: total clr, positive or negative sum and award by grant
'''
def calculate_new_clr(aggregated_contributions, pair_totals, threshold=0.0, total_pot=0.0, positive=True):
    bigtot = 0
    totals = []
    if positive:  # positive
        for proj, contribz in aggregated_contributions.items():
            tot = 0
            for k1, v1 in contribz.items():
                for k2, v2 in contribz.items():
                    if k2 > k1:  # removes single donations, vitalik's formula
                        tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / threshold + 1)
            bigtot += tot
            totals.append({'id': proj, 'clr_amount': tot})
    
    if not positive:  # negative
        for proj, contribz in aggregated_contributions.items():
            tot = 0
            for k1, v1 in contribz.items():
                for k2, v2 in contribz.items():
                    if k2 > k1:  # removes single donations but adds it in below, vitalik's formula
                        tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / threshold + 1)
                    if k2 == k1:  # negative vote will count less if single, but will count
                        tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / 1 + 1)
            bigtot += tot
            totals.append({'id': proj, 'clr_amount': tot})

    return bigtot, totals



'''
    Helper function that calculates the final difference between positive and negative totals and finds the final clr reward amount. The amount is also normalized as well. 

    ### UNCOMMENTING CHANGES HERE MAY BE NECESSARY HERE FOR NORMALIZATION ###

    Args:
        totals_pos: [{'id': proj, 'clr_amount': tot}]
        totals_neg: [{'id': proj, 'clr_amount': tot}]
        total_pot: total pot for the category round

    Returns:
        totals: total clr award by grant pos less neg, normalized by the normalization factor
'''
def calculate_new_clr_final(totals_pos, totals_neg, total_pot=0.0):
    # calculate final totals
    totals = [{'id': x['id'], 'clr_amount': (math.sqrt(x['clr_amount']) - math.sqrt(y['clr_amount']))**2} for x in totals_pos for y in totals_neg if x['id'] == y['id']]
    for x in totals:
        if x['clr_amount'] < 0:
            x['clr_amount'] = 0
    
    # # find normalization factor
    # bigtot = 0 
    # for x in totals:
    #     bigtot += x['clr_amount']
    # normalization_factor = bigtot / total_pot

    # # modify totals
    # for x in totals:
    #     x['clr_amount'] = x['clr_amount'] / normalization_factor

    return bigtot, totals



'''
    Clubbed function that intakes grant data, calculates necessary intermediate calculations, and spits out clr calculations. This function is re-used for positive and negative contributions
    
    Args:
        grant_contributions: {
            'id': (string) ,
            'contributions' : [
                {
                    contributor_profile (str) : contribution_amount (int)
                }
            ]
        }
        threshold: pairwise coefficient
        total_pot: total pot set for the round category
        positive: positive or negative contributions

    Returns:
        bigtot: should equal total pot
        totals: clr totals
'''
def grants_clr_calculate(grant_contributions, total_pot=0.0, threshold=0.0, positive=True):
    grants_list = translate_data(grant_contributions)
    aggregated_contributions, pair_totals = aggregate_contributions(grants_list)
    bigtot, totals = calculate_new_clr(aggregated_contributions, pair_totals, threshold=threshold, total_pot=total_pot, positive=positive)
    return totals



'''
    Clubbed function that intakes the result of grants_clr_calculate and calculates the final difference calculation between positive and negative grant contributions.

    Args:
        totals_pos: [{'id': proj, 'clr_amount': tot}]
        totals_neg: [{'id': proj, 'clr_amount': tot}]
        total_pot: total pot set for the round category

    Returns:
        final_bigtot: should equal total pot
        final_totals: final clr totals

    Final flow:
        grants_clr_calculate includes:
            translate_data
            aggregate_contributions
            calculate_new_clr
        and outputs: positive & negatives clr amounts
        grants_clr_calculate_pos_neg uses output from grants_clr_calculates to output final totals
'''
def grants_clr_calculate_pos_neg(pos_totals, neg_totals, total_pot=0.0):
    bigtot, totals = calculate_new_clr_final(pos_totals, totals_neg, total_pot=total_pot)
    return final_bigtot, final_totals



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



def calculate_clr_for_donation(donation_grant, donation_amount, base_grant_contributions, total_pot=0.0, threshold=0.0, positive=True):
    
    ### ADD NEW GRANT CONTRIBUTIONS MODEL IS UPDATED AND PULL SEPARATE POSITIVE AND NEGATIVE CONTRIBUTIONS, INPUT VARIABLES IN THE METHOD grants_clr_calculate LINES 292 AND ON WILL NEED TO BE CHANGED

    grant_contributions = copy.deepcopy(base_grant_contributions)
    # find grant in contributions list and add donation
    if donation_amount != 0:
        for grant_contribution in grant_contributions:
            if grant_contribution['id'] == donation_grant.id:
                # add this donation with a new profile (id 99999999999) to get impact
                grant_contribution['contributions'].append({'999999999999': donation_amount})

    pos_totals = grants_clr_calculate(grant_contributions, total_pot=total_pot, threshold=threshold, positive=positive)
    neg_totals = grants_clr_calculate(grant_contributions, total_pot=total_pot, threshold=threshold, positive=False)
    _, grants_clr = grants_clr_calculate_pos_neg(pos_totals, neg_totals, total_pot=total_pot)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == donation_grant.id:
            return (grant_clr['clr_amount'], grants_clr)

    print(f'info: no contributions found for grant {donation_grant}')
    return (None, None)



def predict_clr(random_data=False, save_to_db=False, from_date=None, clr_type=None, network='mainnet', clr_amount=0.0, threshold=0.0):
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



'''
###########################################
LIVE GRANTS FUNDING PAGE METHODS START HERE
###########################################
'''



def calculate_clr_for_donation_live(donation_grant, donation_amount, base_grant_contributions, total_pot=0.0, threshold=0.0, positive=True):
    grant_contributions = copy.deepcopy(base_grant_contributions)
    # find grant in contributions list and add donation
    if donation_amount != 0:
        for grant_contribution in grant_contributions:
            if grant_contribution['id'] == donation_grant.id:
                # add this donation with a new profile (id 99999999999) to get impact
                grant_contribution['contributions'].append({'999999999999': donation_amount})

    ### PULL FRONTEND USER ID ON GRANT FUNDING PAGE

    pos_totals = grants_clr_calculate(grant_contributions, total_pot=total_pot, threshold=threshold, positive=positive)
    neg_totals = grants_clr_calculate(grant_contributions, total_pot=total_pot, threshold=threshold, positive=False)
    _, grants_clr = grants_clr_calculate_pos_neg(pos_totals, neg_totals, total_pot=total_pot)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == donation_grant.id:
            return (grant_clr['clr_amount'], grants_clr)

    print(f'info: no contributions found for grant {donation_grant}')
    return (None, None)



def predict_clr_live(random_data=False, save_to_db=False, from_date=None, clr_type=None, network='mainnet', clr_amount=0.0, threshold=0.0, amount):
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
        potential_donations = [amount]  ### PULL FRONTEND AMOUNT FROM GRANT FUNDING PAGE
        potential_clr = []

        ### PULL FRONTEND GRANT FROM GRANT FUNDING PAGE

        for donation_amount in potential_donations:
            # calculate clr with each additional donation and save to grants model
            predicted_clr, grants_clr = calculate_clr_for_donation_live(grant, donation_amount, clr_amount, contrib_data)
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