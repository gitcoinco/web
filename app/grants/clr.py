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

from grants.models import Contribution, Grant, PhantomFunding

CLR_DISTRIBUTION_AMOUNT = 100000
CLR_START_DATE = dt.datetime(2019, 1, 15, 0, 0)


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

    _clrs = []

    for grant in grants:
        grant_clr = 0
        lr_contributions = []
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

        _clrs.append({
            'id': grant["id"],
            'clr_amount': grant_clr
        })

    return total_clr, _clrs


'''
    Given the total pot and grants and it's contirbutions,
    it uses binary search to find out the threshold so
    that the entire pot can be distributed based on it's contributions

    Args:
        total_pot:          (int),
        grant_contributions: object,
        min_threshold:      (int)
        max_threshold:      (int)
        iterations:         (int)
        previous_threshold: (int)

    Returns:
        grants_clr         (object)
        total_clr          (int)
        threshold          (int)
        iterations         (int)
'''
def grants_clr_calculate (total_pot, grant_contributions, min_threshold, max_threshold, iterations = 0, previous_threshold=None):
    if len(grant_contributions) == 0:
        return 0, 0, 0, 0

    iterations += 1
    threshold = (max_threshold + min_threshold) / 2
    total_clr, grants_clrs = calculate_clr(threshold, grant_contributions)

    if iterations == 100 or total_pot == threshold or previous_threshold == threshold:
        # No more accuracy to be had
        return grants_clrs, total_clr, threshold, iterations
    if total_clr > total_pot:
        max_threshold = threshold
    elif total_clr < total_pot:
        min_threshold = threshold
    else:
        return grants_clrs, total_clr, threshold, iterations

    return grants_clr_calculate(total_pot, grant_contributions, min_threshold, max_threshold, iterations, threshold)

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
        contrib_data.append({'id': grant_id,
                             'contributions': [{str(profile_id): random.randint(low_donation, high_donation)} for profile_id in range(random.randint(1, number_of_profiles))]})
    return contrib_data


def calculate_clr_for_donation(donation_grant, donation_amount, total_pot, base_grant_contributions):
    grant_contributions = copy.deepcopy(base_grant_contributions)
    # find grant in contributions list and add donation
    if donation_amount != 0:
        for grant_contribution in grant_contributions:
            if grant_contribution['id'] == donation_grant.id:
                # add this donation with a new profile (id 99999999999) to get impact
                grant_contribution['contributions'].append({'999999999999': donation_amount})

    grants_clr, _, _, _ = grants_clr_calculate(CLR_DISTRIBUTION_AMOUNT, grant_contributions, 0, CLR_DISTRIBUTION_AMOUNT)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == donation_grant.id:
            return (grant_clr['clr_amount'], grants_clr)

    print('error: could not find grant in final grants_clr data')
    return (None, None)

def predict_clr(random_data=False, save_to_db=False):
    # get all the eligible contributions and calculate total
    contributions = Contribution.objects.prefetch_related('subscription').filter(created_on__gte=CLR_START_DATE)
    debug_output = []
    grants = Grant.objects.all()

    # set up data to load contributions for each grant
    if not random_data:
        contrib_data = []

        for grant in grants:
            # go through all the individual contributions for each grant
            g_contributions = copy.deepcopy(contributions).filter(subscription__grant_id=grant.id)

            # put in correct format
            phantom_funding_profiles = PhantomFunding.objects.filter(grant_id=grant.id, created_on__gte=CLR_START_DATE)
            all_contributing_profile_ids = list(set([c.subscription.contributor_profile.id for c in g_contributions] + [p.profile_id for p in phantom_funding_profiles]))
            all_summed_contributions = []

            for profile_id in all_contributing_profile_ids:
                # get sum of contributions per grant for each profile
                profile_g_contributions = g_contributions.filter(subscription__contributor_profile_id=profile_id)
                sum_of_each_profiles_contributions = float(sum([c.subscription.get_converted_monthly_amount() for c in profile_g_contributions]))

                phantom_funding = PhantomFunding.objects.filter(created_on__gte=CLR_START_DATE, grant_id=grant.id, profile_id=profile_id)
                if phantom_funding.exists():
                    sum_of_each_profiles_contributions = sum_of_each_profiles_contributions + phantom_funding.first().value

                all_summed_contributions.append({str(profile_id): sum_of_each_profiles_contributions})

            # for each grant, list the contributions in key value pairs like {'profile id': sum of contributions}
            contrib_data.append({'id': grant.id, 'contributions': all_summed_contributions})

    else:
        # use random contribution data for testing
        contrib_data = generate_random_contribution_data()

    print('\n\ncontributions data:')
    print(contrib_data)

    # calculate clr given additional donations
    for grant in grants:
        # five potential additional donations plus the base case of 0
        potential_donations = [0, 1, 10, 100, 1000, 10000]
        potential_clr = []

        for donation_amount in potential_donations:
            # calculate clr with each additional donation and save to grants model
            predicted_clr, grants_clr = calculate_clr_for_donation(grant, donation_amount, CLR_DISTRIBUTION_AMOUNT, contrib_data)
            potential_clr.append(predicted_clr)

        if save_to_db:
            grant.clr_prediction_curve = list(zip(potential_donations, potential_clr))
            grant.save()

        debug_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})
    return debug_output
