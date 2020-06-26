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

from grants.models import Contribution, Grant, PhantomFunding
from marketing.models import Stat
from perftools.models import JSONStore

CLR_START_DATE = dt.datetime(2020, 5, 6, 0, 0)

ROUND_5_5_GRANTS = [656, 493, 494, 502, 504, 662]

# TODO: MOVE TO DB
THRESHOLD_TECH = 20.0
THRESHOLD_MEDIA = 20.0
THRESHOLD_HEALTH = 20.0

TOTAL_POT_TECH = 101000.0
TOTAL_POT_MEDIA = 50120.0 #50k + 120 from negative voting per https://twitter.com/owocki/status/1249420758167588864
TOTAL_POT_HEALTH = 50000.0

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
    totals = []
    if positive:  # positive
        for proj, contribz in aggregated_contributions.items():
            tot = 0
            for k1, v1 in contribz.items():
                for k2, v2 in contribz.items():
                    if k2 > k1:  # removes single donations, vitalik's formula
                        tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / threshold + 1)
            totals.append({'id': proj, 'clr_amount': tot})

    if not positive:  # negative
        for proj, contribz in aggregated_contributions.items():
            tot = 0
            for k1, v1 in contribz.items():
                for k2, v2 in contribz.items():
                    if k2 > k1:  # removes single donations but adds it in below, vitalik's formula
                        tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / threshold + 1)
                    if k2 == k1:  # negative vote will count less if single, but will count
                        tot += ((v1 * v2) ** 0.5)
            totals.append({'id': proj, 'clr_amount': tot})

    return totals



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
    # print(f'+ve {len(totals_pos)} {totals_pos}')
    # print(f'-ve {len(totals_neg)} {totals_neg}')
    neg_ids = [y['id'] for y in totals_neg]
    [totals_neg.append({'id': x['id'], 'clr_amount': 0}) for x in totals_pos if x['id'] not in neg_ids]

    pos_ids = [x['id'] for x in totals_pos]
    [totals_pos.append({'id': y['id'], 'clr_amount': 0}) for y in totals_neg if y['id'] not in pos_ids]

    totals = []
    for x in totals_pos:
        for y in totals_neg:
            if x['id'] == y['id'] and (x['clr_amount'] == 0 or x['clr_amount'] < y['clr_amount']):
                totals.append({'id': x['id'], 'clr_amount': 0})
            elif x['id'] == y['id']:
                totals.append({'id': x['id'], 'clr_amount': (math.sqrt(x['clr_amount']) - math.sqrt(y['clr_amount']))**2})

    bigtot = 0
    # find normalization factor
    for x in totals:
        bigtot += x['clr_amount']
    normalization_factor = bigtot / total_pot
    # modify totals
    if normalization_factor != 0:
        for x in totals:
            x['clr_amount'] = x['clr_amount'] / normalization_factor
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
        totals: clr totals
'''
def grants_clr_calculate(grant_contributions, total_pot=0.0, threshold=0.0, positive=True):
    grants_list = translate_data(grant_contributions)
    aggregated_contributions, pair_totals = aggregate_contributions(grants_list)
    totals = calculate_new_clr(aggregated_contributions, pair_totals, threshold=threshold, total_pot=total_pot, positive=positive)
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
    final_bigtot, final_totals = calculate_new_clr_final(pos_totals, neg_totals, total_pot=total_pot)
    return final_bigtot, final_totals


def calculate_clr_for_donation(grant, amount, positive_grant_contributions, negative_grant_contributions, total_pot, threshold):

    _positive_grant_contributions = copy.deepcopy(positive_grant_contributions)
    # find grant in contributions list and add donation
    if amount != 0:
        for grant_contribution in _positive_grant_contributions:
            if grant_contribution['id'] == grant.id:
                # add this donation with a new profile (id 99999999999) to get impact
                grant_contribution['contributions'].append({'999999999999': amount})

    pos_totals = grants_clr_calculate(_positive_grant_contributions, total_pot=total_pot, threshold=threshold, positive=True)
    neg_totals = grants_clr_calculate(negative_grant_contributions, total_pot=total_pot, threshold=threshold, positive=False)
    _, grants_clr = grants_clr_calculate_pos_neg(pos_totals, neg_totals, total_pot=total_pot)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == grant.id:
            return (grant_clr['clr_amount'], grants_clr)

    # print(f'info: no contributions found for grant {grant}')
    return (None, None)


'''
    Populate Data needed to calculate CLR

    Args:
        clr_type    :   media | tech | None
        network     :   mainnet | rinkeby

    Returns:
        grants: list of grants based on clr_type
        positive_contrib_data: [{'id': <int>, 'contributions': <Object>}]
        negative_contrib_data: [{'id': <int>, 'contributions': <Object>}]
        total_pot: float
        threshold : int
'''
def populate_data_for_clr(clr_type=None, network='mainnet', mechanism='profile'):
    import pytz

    from_date = timezone.now()
    # get all the eligible contributions and calculate total
    contributions = Contribution.objects.prefetch_related('subscription').filter(match=True, created_on__gte=CLR_START_DATE, created_on__lte=from_date, success=True)

    if ROUND_5_5_GRANTS:
        grants = Grant.objects.filter(id__in=ROUND_5_5_GRANTS)
        threshold = THRESHOLD_HEALTH
        total_pot = TOTAL_POT_HEALTH
    elif clr_type == 'tech':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='tech', link_to_new_grant=None)
        threshold = THRESHOLD_TECH
        total_pot = TOTAL_POT_TECH
    elif clr_type == 'media':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='media', link_to_new_grant=None)
        threshold = THRESHOLD_MEDIA
        total_pot = TOTAL_POT_MEDIA
    elif clr_type == 'health':
        grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type='health', link_to_new_grant=None)
        threshold = THRESHOLD_HEALTH
        total_pot = TOTAL_POT_HEALTH
    else:
        # print('error: populate_data_for_clr missing clr_type')
        return None, None, None, None

    # set up data to load contributions for each grant
    positive_contrib_data = []
    negative_contrib_data = []

    for grant in grants:
        grant_id = grant.defer_clr_to.pk if grant.defer_clr_to else grant.id

        # Get the +ve and -ve contributions
        positive_contributions = copy.deepcopy(contributions).filter(subscription__grant_id=grant.id, subscription__is_postive_vote=True)
        negative_contributions = copy.deepcopy(contributions).filter(subscription__grant_id=grant.id, subscription__is_postive_vote=False)

        # Generate list of profiles who've made +ve and -ve contributions to the grant
        phantom_funding_profiles = PhantomFunding.objects.filter(grant_id=grant.id, created_on__gte=CLR_START_DATE, created_on__lte=from_date)

        # filter out new github profiles
        positive_contribution_ids = [ele.pk for ele in positive_contributions if ele.subscription.contributor_profile.github_created_on.replace(tzinfo=pytz.UTC) < CLR_START_DATE.replace(tzinfo=pytz.UTC)] # only allow github profiles created after CLR Round
        positive_contributions = positive_contributions.filter(pk__in=positive_contribution_ids)
        negative_contribution_ids = [ele.pk for ele in negative_contributions if ele.subscription.contributor_profile.github_created_on.replace(tzinfo=pytz.UTC) < CLR_START_DATE.replace(tzinfo=pytz.UTC)] # only allow github profiles created after CLR Round
        negative_contributions = negative_contributions.filter(pk__in=negative_contribution_ids)
        phantom_funding_profiles = [ele for ele in phantom_funding_profiles if ele.profile.github_created_on.replace(tzinfo=pytz.UTC) < CLR_START_DATE.replace(tzinfo=pytz.UTC)] # only allow github profiles created after CLR Round

        positive_contributing_profile_ids = list(set([c.identity_identifier(mechanism) for c in positive_contributions] + [p.profile_id for p in phantom_funding_profiles]))
        negative_contributing_profile_ids = list(set([c.identity_identifier(mechanism) for c in negative_contributions]))

        # print(f'positive contrib profiles : {positive_contributing_profile_ids}')
        # print(f'negative contrib profiles : {negative_contributing_profile_ids}')
        # print(f'positive contributions : {positive_contributions}')
        # print(f'negative contributions : {negative_contributions}')

        positive_summed_contributions = []
        negative_summed_contributions = []

        # POSITIVE CONTRIBUTIONS
        if len(positive_contributing_profile_ids) > 0:
            for profile_id in positive_contributing_profile_ids:
                # get sum of contributions per grant for each profile
                if mechanism == 'originated_address':
                    profile_positive_contributions = positive_contributions.filter(originated_address=profile_id)
                else:
                    profile_positive_contributions = positive_contributions.filter(subscription__contributor_profile_id=profile_id)
                sum_of_each_profiles_contributions = float(sum([c.subscription.amount_per_period_usdt for c in profile_positive_contributions if c.subscription.amount_per_period_usdt]))

                if mechanism != 'originated_address':
                    phantom_funding = PhantomFunding.objects.filter(created_on__gte=CLR_START_DATE, grant_id=grant.id, profile_id=profile_id, created_on__lte=from_date)
                    if phantom_funding.exists():
                        sum_of_each_profiles_contributions = sum_of_each_profiles_contributions + phantom_funding.first().value

                positive_summed_contributions.append({str(profile_id): sum_of_each_profiles_contributions})

            # for each grant, list the contributions in key value pairs like {'profile id': sum of contributions}
            positive_contrib_data.append({
                'id': grant_id,
                'contributions': positive_summed_contributions
            })

        # NEGATIVE CONTRIBUTIONS
        if len(negative_contributing_profile_ids) > 0:
            for profile_id in negative_contributing_profile_ids:
                if mechanism == 'originated_address':
                    profile_negative_contributions = negative_contributions.filter(originated_address=profile_id)
                else:
                    profile_negative_contributions = negative_contributions.filter(subscription__contributor_profile_id=profile_id)
                sum_of_each_negative_contributions = float(sum([c.subscription.amount_per_period_usdt for c in profile_negative_contributions if c.subscription.amount_per_period_usdt]))
                negative_summed_contributions.append({str(profile_id): sum_of_each_negative_contributions})

            negative_contrib_data.append({
                'id': grant_id,
                'contributions': negative_summed_contributions
            })

    # print(f'\n positive contributions data: {positive_contrib_data} \n')
    # print(f'\n negative contributions data: {negative_contrib_data} \n')
    return (grants, positive_contrib_data, negative_contrib_data, total_pot, threshold)


def predict_clr(save_to_db=False, from_date=None, clr_type=None, network='mainnet', mechanism='profile'):
    # setup
    clr_calc_start_time = timezone.now()
    debug_output = []
    grants, positive_contrib_data, negative_contrib_data, total_pot, threshold = populate_data_for_clr(clr_type, network, mechanism=mechanism)

    # print(f'GRANT {len(grants)}')
    # print(f'CONTRIB {len(positive_contrib_data)}')

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
                positive_contrib_data,
                negative_contrib_data,
                total_pot,
                threshold
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
                if _grant.negative_round_contributor_count:
                    Stat.objects.create(
                        created_on=from_date,
                        key=_grant.title[0:43] + "_nctrbs",
                        val=_grant.negative_round_contributor_count,
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


'''
###########################################
LIVE GRANTS FUNDING PAGE METHODS START HERE
###########################################
'''

'''
    Predicts the new clr distribution when a contributor wants to fund a grant
    for a certain amount

    Args:
        grant: <Grant> - grant to be funded
        contributor: <Profile> - contributor making a contribution
        amount: <float> - amount with which is grant is to be funded
        is_postive_vote: <boolean>
        positive_grant_contributions: [Object]
        negative_grant_contributions: [Object]
        total_pot: <float>
        threshold: <float>

    Returns:
        clr_amount
'''
def calculate_clr_for_donation_live(grant, contributor, amount, is_postive_vote, positive_grant_contributions, negative_grant_contributions, total_pot, threshold):

    if amount == 0:
        return 0

    _positive_grant_contributions = copy.deepcopy(positive_grant_contributions)
    _negative_grant_contributions = copy.deepcopy(negative_grant_contributions)

    profile_id = str(contributor.pk)

    if is_postive_vote:
        for grant_contribution in _positive_grant_contributions:
            if grant_contribution['id'] == grant.id:
                grant_contribution['contributions'].append({
                    profile_id: amount
                })
    else:
        for grant_contribution in _negative_grant_contributions:
            if grant_contribution['id'] == grant.id:
                grant_contribution['contributions'].append({
                    profile_id: amount
                })

    pos_totals = grants_clr_calculate(_positive_grant_contributions, total_pot=total_pot, threshold=threshold, positive=True)
    neg_totals = grants_clr_calculate(_negative_grant_contributions, total_pot=total_pot, threshold=threshold, positive=False)
    _, grants_clr = grants_clr_calculate_pos_neg(pos_totals, neg_totals, total_pot=total_pot)

    # find grant we added the contribution to and get the new clr amount
    for grant_clr in grants_clr:
        if grant_clr['id'] == grant.id:
            return grant_clr['clr_amount']

    print(f'info: no contributions found for grant {grant}')
    return None


'''
    Calculates potential CLR match based on the contributor + amount + grant
    they would like to contribute.

    Args:
        grant: <Grant>
        contributor: <Profile>
        amount: <float>
        is_postive_vote: <boolean>

    Returns:
        predicted_clr_match
'''
def predict_clr_live(grant, contributor, amount, is_postive_vote=True):

    if not grant or not contributor:
        print('error: predict_clr_live - missing parameters')
        return None

    if amount == 0:
        return 0

    clr_type = grant.grant_type
    network = grant.network
    _, positive_contrib_data, negative_contrib_data , total_pot, threshold = populate_data_for_clr(clr_type, network)

    predicted_clr_match = calculate_clr_for_donation_live(
        grant, contributor, amount, is_postive_vote, positive_contrib_data, negative_contrib_data, total_pot, threshold
    )

    return predicted_clr_match
