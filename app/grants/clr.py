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

from django.conf import settings
from django.utils import timezone

import pytz
from grants.models import Contribution, Grant, PhantomFunding
from marketing.models import Stat
from perftools.models import JSONStore

PREV_CLR_START_DATE = dt.datetime(2020, 3, 23, 12, 0)
PREV_CLR_END_DATE = dt.datetime(2020, 4, 7, 12, 0)
CLR_START_DATE = dt.datetime(2020, 6, 15, 12, 0)

# TODO: MOVE TO DB
V_THRESHOLD_TECH = 25.0
V_THRESHOLD_MEDIA = 25.0
V_THRESHOLD_HEALTH = 25.0
V_THRESHOLD_CHANGE = 25.0
V_THRESHOLD_MATIC = 25.0

UV_THRESHOLD_TECH = 5.0
UV_THRESHOLD_MEDIA = 5.0
UV_THRESHOLD_HEALTH = 5.0
UV_THRESHOLD_CHANGE = 5.0
UV_THRESHOLD_MATIC = 5.0

TOTAL_POT_TECH = 100000.0
TOTAL_POT_MEDIA = 50000.0
TOTAL_POT_HEALTH = 0.0
TOTAL_POT_CHANGE = 25000.0
TOTAL_POT_MATIC = 0.0


'''
    translates django grant data structure to a list of lists

    args:
        django grant data structure
            {
                'id': (string) ,
                'contibutions' : [
                    {
                        contributor_profile (str) : contribution_amount (int)
                    }
                ]
            }

    returns:
        list of lists of grant data
            [[grant_id (str), user_id (str), verification_status (boolean), contribution_amount (float)]]
'''
def translate_data(grants_data):
    grants_list = []
    for g in grants_data:
        grant_id = g.get('id')
        for c in g.get('contributions'):
            profile_id = c.get('id')
            if profile_id:
                val = [grant_id] + [c.get('id')] + [c.get('is_verified')] + [c.get('sum_of_each_profiles_contributions')]
                grants_list.append(val)

    return grants_list



'''
    gets list of verified profile ids

    args:
        list of lists of grant data
            [[grant_id (str), user_id (str), verification_status (str), contribution_amount (float)]]

    returns:
        set list of verified user_ids
            [user_id (str)]

'''
def get_verified_list(grant_contributions):
    verified_list = []
    for _, user, ver_stat, _ in grant_contributions:
        if ver_stat and user not in verified_list:
            verified_list.append(user)

    return verified_list



'''
    aggregates contributions by contributor, and calculates total contributions by unique pairs

    args:
        list of lists of grant data
            [[grant_id (str), user_id (str), verification_status (boolean), contribution_amount (float)]]
        round
            str ('current' or 'previous') only

    returns:
        aggregated contributions by pair in nested list
            {
                round: {
                    grant_id (str): {
                        user_id (str): aggregated_amount (float)
                    }
                }
            }
'''
def aggregate_contributions(grant_contributions, _round='current'):
    round_dict = {}
    contrib_dict = {}
    for proj, user, _, amount in grant_contributions:
        if _round == 'previous':
            amount = amount / 3
        if proj not in contrib_dict:
            contrib_dict[proj] = {}
        contrib_dict[proj][user] = contrib_dict[proj].get(user, 0) + amount
    round_dict[_round] = contrib_dict

    return round_dict



'''
    gets pair totals between current round, current and previous round

    args:
        aggregated contributions by pair in nested dict
            {
                round: {
                    grant_id (str): {
                        user_id (str): aggregated_amount (float)
                    }
                }
            }

    returns:
        pair totals between current round, current and previous round
            {user_id (str): {user_id (str): pair_total (float)}}

'''
def get_totals_by_pair(contrib_dict):
    tot_overlap = {}

    # start pairwise match
    for proj, contribz in contrib_dict['current'].items():
        for k1, v1 in contribz.items():
            if k1 not in tot_overlap:
                tot_overlap[k1] = {}

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                if k2 not in tot_overlap[k1]:
                    tot_overlap[k1][k2] = 0
                tot_overlap[k1][k2] += (v1 * v2) ** 0.5

            # pairwise matches to last round
            if contrib_dict['previous'].get(proj):
                for x1, y1 in contrib_dict['previous'][proj].items():
                    if x1 not in tot_overlap[k1]:
                        tot_overlap[k1][x1] = 0
                    tot_overlap[k1][x1] += (v1 * y1) ** 0.5

    return tot_overlap



'''
    calculates the clr amount at the given threshold and total pot
    args:
        aggregated_contributions by pair in nested dict
            {
                round: {
                    grant_id (str): {
                        user_id (str): aggregated_amount (float)
                    }
                }
            }
        pair_totals   :   {user_id (str): {user_id (str): pair_total (float)}}
        v_threshold   :   float
        uv_threshold  :   float
        total_pot     :   float

    returns:
        total clr award by grant, normalized by the normalization factor
            [{'id': proj, 'clr_amount': tot}]
        saturation point
            boolean
'''
def calculate_clr(aggregated_contributions, pair_totals, verified_list, v_threshold, uv_threshold, total_pot):
    saturation_point = False
    bigtot = 0
    totals = []
    for proj, contribz in aggregated_contributions['current'].items():
        tot = 0

        # start pairwise matches
        for k1, v1 in contribz.items():

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                if k2 > k1 and all(i in verified_list for i in [k2, k1]):
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / v_threshold + 1)
                else:
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / uv_threshold + 1)

            # pairwise matches to last round
            if aggregated_contributions['previous'].get(proj):
                for x1, y1 in aggregated_contributions['previous'][proj].items():
                    if x1 != k1 and all(i in verified_list for i in [x1, k1]):
                        tot += ((v1 * y1) ** 0.5) / (pair_totals[k1][x1] / v_threshold + 1)
                    else:
                        tot += ((v1 * y1) ** 0.5) / (pair_totals[k1][x1] / uv_threshold + 1)

        bigtot += tot
        totals.append({'id': proj, 'clr_amount': tot})

    if bigtot >= total_pot:
        saturation_point = True

    if saturation_point == True:
        # find normalization factor
        normalization_factor = bigtot / total_pot
        # modify totals
        for result in totals:
            result['clr_amount'] = result['clr_amount'] / normalization_factor

    return totals, saturation_point



'''
    clubbed function that runs all calculation functions

    args:
        grant_contribs_curr
            {
                'id': (string) ,
                'contibutions' : [
                    {
                        contributor_profile (str) : contribution_amount (int)
                    }
                ]
            }
        grant_contribs_prev
            {
                'id': (string) ,
                'contibutions' : [
                    {
                        contributor_profile (str) : contribution_amount (int)
                    }
                ]
            }
        threshold   :   float
        total_pot   :   float

    returns:
        grants clr award amounts
'''
def run_clr_calcs(grant_contribs_curr, grant_contribs_prev, v_threshold, uv_threshold, total_pot):

    # get data
    curr_round = translate_data(grant_contribs_curr)
    prev_round = translate_data(grant_contribs_prev)

    vlist = get_verified_list(curr_round + prev_round)

    # aggregate data
    curr_agg = aggregate_contributions(curr_round, 'current')
    prev_agg = aggregate_contributions(prev_round, 'previous')
    combinedagg = {**prev_agg, **curr_agg}

    # get pair totals
    ptots = get_totals_by_pair(combinedagg)

    # clr calcluation
    totals, _ = calculate_clr(combinedagg, ptots, vlist, v_threshold, uv_threshold, total_pot)

    return totals



def calculate_clr_for_donation(grant, amount, grant_contributions_curr, grant_contributions_prev, total_pot, v_threshold, uv_threshold):

    _grant_contributions_curr = copy.deepcopy(grant_contributions_curr)
    _grant_contributions_prev = copy.deepcopy(grant_contributions_prev)

    # find grant in contributions list and add donation
    if amount != 0:
        for grant_contribution in _grant_contributions_curr:
            if grant_contribution['id'] == grant.id:
                # add this donation with a new profile (id 99999999999) to get impact
                grant_contribution['contributions'].append({
                    'id': '999999999999',
                    'sum_of_each_profiles_contributions': amount,
                    'is_verified': True
                })

    grants_clr = run_clr_calcs(_grant_contributions_curr, _grant_contributions_prev, v_threshold, uv_threshold, total_pot)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == grant.id:
            return (grant_clr['clr_amount'], grants_clr)

    # print(f'info: no contributions found for grant {grant}')
    return (None, None)



'''
    Populate Data needed to calculate CLR

    Args:
        clr_type        :   media | tech | None
        network         :   mainnet | rinkeby
        clr_end_date    :   datetime
        clr_end_date    :   datetime
    Returns:
        contributions               : contributions data object
        grants                      : list of grants based on clr_type
        phantom_funding_profiles    : phantom funding data object
        total_pot                   : total pot for clr_type
        v_threshold                 : verified threshold for clr_type
        uv_threshold                : unverified threshold for clr_type

'''
def fetch_data(clr_type=None, network='mainnet', clr_start_date=None, clr_end_date=timezone.now()):

    if not clr_start_date:
        print('error: fetch_data - missing start_date')
        return None, None, None, None

    contributions = Contribution.objects.prefetch_related('subscription').filter(match=True, created_on__gte=clr_start_date, created_on__lte=clr_end_date, success=True)

    if clr_type == 'tech':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='tech', is_clr_eligible=True, link_to_new_grant=None)
        v_threshold = V_THRESHOLD_TECH
        uv_threshold = UV_THRESHOLD_TECH
        total_pot = TOTAL_POT_TECH

    elif clr_type == 'media':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='media', is_clr_eligible=True, link_to_new_grant=None)
        v_threshold = V_THRESHOLD_MEDIA
        uv_threshold = UV_THRESHOLD_MEDIA
        total_pot = TOTAL_POT_MEDIA

    elif clr_type == 'health':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='health', is_clr_eligible=True, link_to_new_grant=None)
        v_threshold = V_THRESHOLD_HEALTH
        uv_threshold = UV_THRESHOLD_HEALTH
        total_pot = TOTAL_POT_HEALTH

    elif clr_type == 'change':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='change', is_clr_eligible=True, link_to_new_grant=None)
        v_threshold = V_THRESHOLD_CHANGE
        uv_threshold = UV_THRESHOLD_CHANGE
        total_pot = TOTAL_POT_CHANGE

    elif clr_type == 'matic':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='matic', is_clr_eligible=True, link_to_new_grant=None)
        v_threshold = V_THRESHOLD_MATIC
        uv_threshold = UV_THRESHOLD_MATIC
        total_pot = TOTAL_POT_MATIC

    else:
        return None, None, None, None, None, None

    phantom_funding_profiles = PhantomFunding.objects.filter(created_on__gte=clr_start_date, created_on__lte=clr_end_date)

    return grants, contributions, phantom_funding_profiles, total_pot, v_threshold, uv_threshold



'''
    Populate Data needed to calculate CLR

    Args:
        grants                  : grants list
        contributions           : contributions list for thoe grants
        phantom_funding_profiles: phantom funding for those grants
        mechanism               : verification mechanism (profile_
        clr start date          : datetime
        clr end date            : datetime

    Returns:
        contrib_data_list: {
            'id': grant_id,
            'contributions': summed_contributions
        }

'''
def populate_data_for_clr(grants, contributions, phantom_funding_profiles, mechanism, clr_start_date=None, clr_end_date=timezone.now()):

    if not clr_start_date:
        print('Error: populate_data_for_clr - missing clr_start_date')

    # set up data to load contributions for each grant
    contrib_data_list = []

    for grant in grants:
        grant_id = grant.defer_clr_to.pk if grant.defer_clr_to else grant.id

        # contributions
        contribs = copy.deepcopy(contributions).filter(subscription__grant_id=grant.id, subscription__is_postive_vote=True, created_on__gte=clr_start_date, created_on__lte=clr_end_date)

        # phantom funding
        grant_phantom_funding_profiles = phantom_funding_profiles.filter(grant_id=grant.id, created_on__gte=clr_start_date, created_on__lte=clr_end_date)

        # verified profiles
        verified_profile_ids = [ele.pk for ele in contribs if ele.subscription.contributor_profile.sms_verification]
        verified_phantom_funding_profile_ids = [ele.profile_id for ele in grant_phantom_funding_profiles if ele.profile.sms_verification]
        verified_profile = list(set(verified_profile_ids + verified_phantom_funding_profile_ids))

        # combine
        contributing_profile_ids = list(set([c.identity_identifier(mechanism) for c in contribs] + [p.profile_id for p in grant_phantom_funding_profiles]))

        summed_contributions = []

        # contributions
        if len(contributing_profile_ids) > 0:
            for profile_id in contributing_profile_ids:
                profile_contributions = contribs.filter(subscription__contributor_profile_id=profile_id)
                sum_of_each_profiles_contributions = float(sum([c.subscription.amount_per_period_usdt for c in profile_contributions if c.subscription.amount_per_period_usdt]))
                phantom_funding = grant_phantom_funding_profiles.filter(profile_id=profile_id)
                if phantom_funding.exists():
                    sum_of_each_profiles_contributions = sum_of_each_profiles_contributions + phantom_funding.first().value

                summed_contributions.append({
                    'id': str(profile_id),
                    'sum_of_each_profiles_contributions': sum_of_each_profiles_contributions,
                    'is_verified': True if profile_id in verified_profile else False
                })

            contrib_data_list.append({
                'id': grant_id,
                'contributions': summed_contributions
            })

    return contrib_data_list



def predict_clr(save_to_db=False, from_date=None, clr_type=None, network='mainnet', mechanism='profile'):
    # setup
    clr_calc_start_time = timezone.now()
    debug_output = []

    # one-time data call
    grants, contributions, phantom_funding_profiles, total_pot, v_threshold, uv_threshold = fetch_data(clr_type, network, PREV_CLR_START_DATE)

    # one for previous, one for current
    grant_contributions_curr = populate_data_for_clr(grants, contributions, phantom_funding_profiles, mechanism=mechanism, clr_start_date=CLR_START_DATE)
    grant_contributions_prev = populate_data_for_clr(grants, contributions, phantom_funding_profiles, mechanism=mechanism, clr_start_date=PREV_CLR_START_DATE, clr_end_date=PREV_CLR_END_DATE)

    # calculate clr given additional donations
    for grant in grants:
        # five potential additional donations plus the base case of 0
        potential_donations = [0, 1, 10, 100, 1000, 10000]
        potential_clr = []

        for amount in potential_donations:
            # calculate clr with each additional donation and save to grants model
            predicted_clr, grants_clr = calculate_clr_for_donation(
                grant,
                amount,
                grant_contributions_curr,
                grant_contributions_prev,
                total_pot,
                v_threshold,
                uv_threshold
            )
            potential_clr.append(predicted_clr)

        if save_to_db:
            _grant = Grant.objects.get(pk=grant.pk)
            _grant.clr_prediction_curve = list(zip(potential_donations, potential_clr))
            base = _grant.clr_prediction_curve[0][1]
            _grant.last_clr_calc_date = timezone.now()
            _grant.next_clr_calc_date = timezone.now() + timezone.timedelta(minutes=10)

            can_estimate = True if base or _grant.clr_prediction_curve[1][1] or _grant.clr_prediction_curve[2][1] or _grant.clr_prediction_curve[3][1] else False

            if can_estimate :
                _grant.clr_prediction_curve  = [[ele[0], ele[1], ele[1] - base] for ele in _grant.clr_prediction_curve ]
            else:
                _grant.clr_prediction_curve = [[0.0, 0.0, 0.0] for x in range(0, 6)]

            JSONStore.objects.create(
                created_on=from_date,
                view='clr_contribution',
                key=f'{grant.id}',
                data=_grant.clr_prediction_curve,
            )
            try:
                if _grant.clr_prediction_curve[0][1]:
                    Stat.objects.create(
                        created_on=from_date,
                        key=_grant.title[0:43] + "_match",
                        val=_grant.clr_prediction_curve[0][1],
                        )
                    max_twitter_followers = max(_grant.twitter_handle_1_follower_count, _grant.twitter_handle_2_follower_count)
                    if max_twitter_followers:
                        Stat.objects.create(
                            created_on=from_date,
                            key=_grant.title[0:43] + "_admt1",
                            val=int(100 * _grant.clr_prediction_curve[0][1]/max_twitter_followers),
                            )

                if _grant.positive_round_contributor_count:
                    Stat.objects.create(
                        created_on=from_date,
                        key=_grant.title[0:43] + "_pctrbs",
                        val=_grant.positive_round_contributor_count,
                        )
                if _grant.amount_received_in_round:
                    Stat.objects.create(
                        created_on=from_date,
                        key=_grant.title[0:43] + "_amt",
                        val=_grant.amount_received_in_round,
                        )
            except:
                pass

            if from_date > (clr_calc_start_time - timezone.timedelta(hours=1)):
                _grant.save()

        debug_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})
    return debug_output
