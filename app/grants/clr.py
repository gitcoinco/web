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

import numpy as np
import pytz
from grants.models import Contribution, Grant, PhantomFunding
from marketing.models import Stat
from perftools.models import JSONStore

CLR_PERCENTAGE_DISTRIBUTED = 0

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
            [[grant_id (str), user_id (str), verification_status (str), contribution_amount (float)]]
'''
def translate_data(grants_data):
    grants_list = []
    for g in grants_data:
        grant_id = g.get('id')
        for c in g.get('contributions'):
            profile_id = c.get('id')
            verification_status = None
            if c.get('is_sms_verified'):
                verification_status = 'sms'
            elif c.get('is_brightid_verified'):
                verification_status = 'brightid'
            if profile_id:
                val = [grant_id] + [c.get('id')] + [verification_status] + [c.get('sum_of_each_profiles_contributions')]
                grants_list.append(val)

    return grants_list



'''
    gets list of verified profile ids

    args:
        list of lists of grant data
            [[grant_id (str), user_id (str), verification_status (str), contribution_amount (float)]]

    returns:
        set list of sms verified user_ids
            [user_id (str)]
        set list of bright verified user_ids
            [user_id (str)]


'''
def get_verified_list(grant_contributions):
    sms_verified_list = []
    bright_verified_list = []
    for _, user, ver_stat, _ in grant_contributions:
        if ver_stat == 'sms' and user not in sms_verified_list:
            sms_verified_list.append(user)
        elif ver_stat == 'brightid' and user not in bright_verified_list:
            bright_verified_list.append(user)

    return sms_verified_list, bright_verified_list



'''
    aggregates contributions by contributor, and calculates total contributions by unique pairs

    args:
        list of lists of grant data
            [[grant_id (str), user_id (str), verification_status (boolean), contribution_amount (float)]]

    returns:
        aggregated contributions by pair nested dict
            {
                grant_id (str): {
                    user_id (str): aggregated_amount (float)
                }
            }
'''
def aggregate_contributions(grant_contributions):
    contrib_dict = {}
    for proj, user, _, amount in grant_contributions:
        if proj not in contrib_dict:
            contrib_dict[proj] = {}
        contrib_dict[proj][user] = contrib_dict[proj].get(user, 0) + amount

    return contrib_dict



'''
    gets pair totals between current round, current round

    args:
        aggregated contributions by pair nested dict
            {
                grant_id (str): {
                    user_id (str): aggregated_amount (float)
                }
            }

    returns:
        pair totals between current round
            {user_id (str): {user_id (str): pair_total (float)}}

'''
def get_totals_by_pair(contrib_dict):
    tot_overlap = {}

    # start pairwise match
    for _, contribz in contrib_dict.items():
        for k1, v1 in contribz.items():
            if k1 not in tot_overlap:
                tot_overlap[k1] = {}

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                if k2 not in tot_overlap[k1]:
                    tot_overlap[k1][k2] = 0
                tot_overlap[k1][k2] += (v1 * v2) ** 0.5

    return tot_overlap



'''
    calculates the clr amount at the given threshold and total pot
    args:
        aggregated contributions by pair nested dict
            {
                grant_id (str): {
                    user_id (str): aggregated_amount (float)
                }
            }
        pair_totals
            {user_id (str): {user_id (str): pair_total (float)}}
        sms_verified_list
            [user_id (str)] 
        bright_verified_list
            [user_id (str)]
        v_threshold 
            float
        uv_threshold
            float
        total_pot
            float

    returns:
        total clr award by grant, analytics, normalized by the normalization factor
            [{'id': proj, 'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}]
        saturation point
            boolean
'''
def calculate_clr(aggregated_contributions, pair_totals, sms_verified_list, bright_verified_list, v_threshold, uv_threshold, total_pot):
    bigtot = 0
    totals = []
    
    for proj, contribz in aggregated_contributions.items():
        tot = 0
        _num = 0
        _sum = 0

        # start pairwise matches
        for k1, v1 in contribz.items():
            _num += 1
            _sum += v1

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                # both sms
                if k2 > k1 and all(i in sms_verified_list for i in [k2, k1]):
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / (v_threshold * 1.05) + 1)
                # both bright
                elif k2 > k1 and all(i in bright_verified_list for i in [k2, k1]):
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / (v_threshold * 1.2) + 1)
                # both none
                elif k2 > k1 and not any(i in sms_verified_list + bright_verified_list for i in [k2, k1]):
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / uv_threshold + 1)
                # one bright or sms, one none
                elif k2 > k1 and (((k2 in sms_verified_list + bright_verified_list) and (k1 not in sms_verified_list + bright_verified_list)) or ((k1 in sms_verified_list + bright_verified_list) and (k2 not in sms_verified_list + bright_verified_list))):
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / uv_threshold + 1)
                # one bright, one sms
                elif k2 > k1:
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / (v_threshold * 1.125) + 1)

        if type(tot) == complex:
            tot = float(tot.real)

        bigtot += tot
        totals.append({'id': proj, 'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot})
        # totals.append({'id': proj, 'clr_amount': tot})

    global CLR_PERCENTAGE_DISTRIBUTED

    if bigtot >= total_pot: # saturation reached
        # print(f'saturation reached. Total Pot: ${total_pot} | Total Allocated ${bigtot}. Normalizing')
        CLR_PERCENTAGE_DISTRIBUTED = 100
        for t in totals:
            t['clr_amount'] = ((t['clr_amount'] / bigtot) * total_pot)
    else:
        CLR_PERCENTAGE_DISTRIBUTED = (bigtot / total_pot) * 100
        if bigtot == 0:
            bigtot = 1
        percentage_increase = np.log(total_pot / bigtot) / 100
        for t in totals:
            t['clr_amount'] = t['clr_amount'] * (1 + percentage_increase)
    return totals



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
        threshold   :   float
        total_pot   :   float

    returns:
        grants clr award amounts
'''
def run_clr_calcs(grant_contribs_curr, v_threshold, uv_threshold, total_pot):

    # get data
    curr_round = translate_data(grant_contribs_curr)

    sms_list, bright_list = get_verified_list(curr_round)

    # aggregate data
    curr_agg = aggregate_contributions(curr_round)

    # get pair totals
    ptots = get_totals_by_pair(curr_agg)

    # clr calcluation
    totals = calculate_clr(curr_agg, ptots, sms_list, bright_list, v_threshold, uv_threshold, total_pot)

    return totals



def calculate_clr_for_donation(grant, amount, grant_contributions_curr, total_pot, v_threshold, uv_threshold):

    _grant_contributions_curr = copy.deepcopy(grant_contributions_curr)

    # find grant in contributions list and add donation
    if amount != 0:
        for grant_contribution in _grant_contributions_curr:
            if grant_contribution['id'] == grant.id:
                # add this donation with a new profile (id 99999999999) to get impact
                grant_contribution['contributions'].append({
                    'id': '999999999999',
                    'sum_of_each_profiles_contributions': amount,
                    'is_sms_verified': True,
                    'is_brightid_verified': True
                })

    grants_clr = run_clr_calcs(_grant_contributions_curr, v_threshold, uv_threshold, total_pot)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == grant.id:
            return (
                grant_clr['clr_amount'],
                grants_clr,
                grant_clr['number_contributions'],
                grant_clr['contribution_amount']
            )

    # print(f'info: no contributions found for grant {grant}')
    return (None, None, None, None)



'''
    Populate Data needed to calculate CLR

    Args:
        network     :   mainnet | rinkeby
        clr_round   :   GrantCLR
    Returns:
        contributions               : contributions data object
        grants                      : list of grants based on clr_type
        phantom_funding_profiles    : phantom funding data object

'''
def fetch_data(clr_round, network='mainnet'):

    clr_start_date = clr_round.start_date
    clr_end_date = clr_round.end_date
    grant_filters = clr_round.grant_filters
    subscription_filters = clr_round.subscription_filters

    contributions = Contribution.objects.prefetch_related('subscription').filter(match=True, created_on__gte=clr_start_date, created_on__lte=clr_end_date, success=True)
    if subscription_filters:
        contributions = contributions.filter(**subscription_filters)

    grants = Grant.objects.filter(network=network, hidden=False, active=True, is_clr_eligible=True, link_to_new_grant=None)
    grants = grants.filter(**grant_filters)

    phantom_funding_profiles = PhantomFunding.objects.filter(created_on__gte=clr_start_date, created_on__lte=clr_end_date)

    return grants, contributions, phantom_funding_profiles



'''
    Populate Data needed to calculate CLR

    Args:
        grants                  : grants list
        contributions           : contributions list for thoe grants
        phantom_funding_profiles: phantom funding for those grants
        clr_round               : GrantCLR

    Returns:
        contrib_data_list: {
            'id': grant_id,
            'contributions': summed_contributions
        }

'''
def populate_data_for_clr(grants, contributions, phantom_funding_profiles, clr_round):

    contrib_data_list = []

    if not clr_round:
        print('Error: populate_data_for_clr - missing clr_round')
        return contrib_data_list

    clr_start_date = clr_round.start_date
    clr_end_date = clr_round.end_date

    mechanism="profile"

    # set up data to load contributions for each grant
    for grant in grants:
        grant_id = grant.defer_clr_to.pk if grant.defer_clr_to else grant.id

        # contributions
        contribs = copy.deepcopy(contributions).filter(subscription__grant_id=grant.id, subscription__is_postive_vote=True, created_on__gte=clr_start_date, created_on__lte=clr_end_date)

        # phantom funding
        grant_phantom_funding_contributions = phantom_funding_profiles.filter(grant_id=grant.id, created_on__gte=clr_start_date, created_on__lte=clr_end_date)

        # SMS verified contributions
        sms_verified_contribution_ids = [ele.pk for ele in contribs if ele.profile_for_clr.sms_verification]
        sms_verified_phantom_funding_contribution_ids = [ele.profile_id for ele in grant_phantom_funding_contributions if ele.profile.sms_verification]
        sms_verified_profile = list(set(sms_verified_contribution_ids + sms_verified_phantom_funding_contribution_ids))

        # BrightID verified contributions
        brightid_verified_contribution_ids = [ele.pk for ele in contribs if ele.profile_for_clr.is_brightid_verified]
        brightid_verified_phantom_funding_contribution_ids = [ele.profile_id for ele in grant_phantom_funding_contributions if ele.profile.is_brightid_verified]
        brightid_verified_profile = list(set(brightid_verified_contribution_ids + brightid_verified_phantom_funding_contribution_ids))

        # combine
        contributing_profile_ids = list(set([c.identity_identifier(mechanism) for c in contribs] + [p.profile_id for p in grant_phantom_funding_contributions]))

        summed_contributions = []

        # contributions
        if len(contributing_profile_ids) > 0:
            for profile_id in contributing_profile_ids:
                profile_contributions = contribs.filter(profile_for_clr_id=profile_id)
                sum_of_each_profiles_contributions = float(sum([c.subscription.amount_per_period_usdt * clr_round.contribution_multiplier for c in profile_contributions if c.subscription.amount_per_period_usdt]))
                phantom_funding = grant_phantom_funding_contributions.filter(profile_id=profile_id)
                if phantom_funding.exists():
                    sum_of_each_profiles_contributions = sum_of_each_profiles_contributions + phantom_funding.first().value

                summed_contributions.append({
                    'id': str(profile_id),
                    'sum_of_each_profiles_contributions': sum_of_each_profiles_contributions,
                    'is_sms_verified': True if profile_id in sms_verified_profile else False,
                    'is_brightid_verified': True if profile_id in brightid_verified_profile else False
                })

            contrib_data_list.append({
                'id': grant_id,
                'contributions': summed_contributions
            })

    return contrib_data_list



def predict_clr(save_to_db=False, from_date=None, clr_round=None, network='mainnet'):
    # setup
    clr_calc_start_time = timezone.now()
    debug_output = []

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)
    uv_threshold = float(clr_round.unverified_threshold)

    grants, contributions, phantom_funding_profiles = fetch_data(clr_round, network)

    if contributions.count() == 0:
        print(f'No Contributions for CLR {clr_round.round_num}. Exiting')
        return

    grant_contributions_curr = populate_data_for_clr(grants, contributions, phantom_funding_profiles, clr_round)

    # calculate clr given additional donations
    for grant in grants:
        # five potential additional donations plus the base case of 0
        potential_donations = [0, 1, 10, 100, 1000, 10000]
        potential_clr = []

        for amount in potential_donations:
            # calculate clr with each additional donation and save to grants model
            # print(f'using {total_pot_close}')
            predicted_clr, grants_clr, _, _ = calculate_clr_for_donation(
                grant,
                amount,
                grant_contributions_curr,
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
            _grant.next_clr_calc_date = timezone.now() + timezone.timedelta(minutes=20)

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

    try :
        Stat.objects.create(
            key= clr_type + '_grants_round_6_saturation',
            val=int(CLR_PERCENTAGE_DISTRIBUTED),
        )
    except:
        pass

    return debug_output
