# -*- coding: utf-8 -*-
"""Define the Grants application configuration.

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

"""
import copy
import time

from django.db import transaction
from django.utils import timezone

import numpy as np
from grants.clr_data_src import fetch_contributions, fetch_grants, fetch_summed_contributions
from grants.models import GrantCLRCalculation


def populate_data_for_clr(grants, contributions, clr_round):
    '''
        Populate Data needed to calculate CLR

        Args:
            grants                  : grants list
            contributions           : contributions list for those grants
            clr_round               : GrantCLR

        Returns:
            contrib_data_list: {
                'id': grant_id,
                'contributions': summed_contributions
            }

    '''

    contrib_data_list = []

    if not clr_round:
        print('Error: populate_data_for_clr - missing clr_round')
        return contrib_data_list

    clr_start_date = clr_round.start_date
    clr_end_date = clr_round.end_date

    mechanism="profile"

    # 3-4s to get all the contributions
    _contributions = list(contributions.filter(created_on__gte=clr_start_date, created_on__lte=clr_end_date).prefetch_related('profile_for_clr', 'subscription'))
    _contributions_by_id = {}
    for ele in _contributions:
        key = ele.grant_id
        if key not in _contributions_by_id.keys():
            _contributions_by_id[key] = []
        _contributions_by_id[key].append(ele)

    # set up data to load contributions for each grant
    for grant in grants:
        grant_id = grant.defer_clr_to.pk if grant.defer_clr_to else grant.id

        # contributions
        contribs = _contributions_by_id.get(grant.id, [])

        # create arrays
        contributing_profile_ids = []
        contributions_by_id = {}
        for c in contribs:
            prof = c.profile_for_clr
            if prof:
                key = prof.id
                if key not in contributions_by_id.keys():
                    contributions_by_id[key] = []
                contributions_by_id[key].append(c)
                contributing_profile_ids.append((prof.id, prof.final_trust_bonus))

        contributing_profile_ids = list(set(contributing_profile_ids))

        summed_contributions = []

        # contributions
        if len(contributing_profile_ids) > 0:
            for profile_id, trust_bonus in contributing_profile_ids:
                sum_of_each_profiles_contributions = sum(ele.amount_per_period_usdt for ele in contributions_by_id[profile_id]) * clr_round.contribution_multiplier

                summed_contributions.append({
                    'id': str(profile_id),
                    'sum_of_each_profiles_contributions': sum_of_each_profiles_contributions,
                    'profile_trust_bonus': trust_bonus
                })

            contrib_data_list.append({
                'id': grant_id,
                'contributions': summed_contributions
            })

    return contrib_data_list


def translate_data(grants_data):
    '''
        translates django grant data structure to a list of lists

        args:
            django grant data structure
                {
                    'id': (string) ,
                    'contributions' : [
                        {
                            contributor_profile (str) : summed_contributions
                        }
                    ]
                }

        returns:
            list of lists of grant data
                [[grant_id (str), user_id (str), contribution_amount (float)]]
            dictionary of profile_ids and trust scores
                {user_id (str): trust_score (float)}
    '''
    trust_dict = {}
    grants_list = []
    for g in grants_data:
        grant_id = g.get('id')
        for c in g.get('contributions'):
            profile_id = int(c.get('id'))
            trust_bonus = c.get('profile_trust_bonus')
            if profile_id:
                val = [grant_id] + [profile_id] + [c.get('sum_of_each_profiles_contributions')]
                grants_list.append(val)
                trust_dict[profile_id] = trust_bonus

    return grants_list, trust_dict


def aggregate_contributions(grant_contributions):
    '''
        aggregates contributions by contributor, and calculates total contributions by unique pairs

        args:
            list of lists of grant data
                [[grant_id (str), user_id (str), verification_status (str), trust_bonus (float), contribution_amount (float)]]

        returns:
            aggregated contributions by pair nested dict
                {
                    grant_id (str): {
                        user_id (str): aggregated_amount (float)
                    }
                }
    '''
    contrib_dict = {}
    for proj, user, amount in grant_contributions:
        if proj not in contrib_dict:
            contrib_dict[proj] = {}
        contrib_dict[proj][user] = contrib_dict[proj].get(user, 0) + amount

    return contrib_dict


def get_totals_by_pair(curr_agg):
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
                {
                    user_id (str): {
                        user_id (str): pair_total (float)
                    }
                }
            curr_agg_sqrts
                {
                    grantId (int): {
                        user_id (float): sqrt(aggregated_amount) (float)
                    }
                }
            pairs_tot
                int: the number of cycles it took to construct the pairs
    '''
    pairs_tot = 0
    pair_totals = {}
    curr_agg_sqrts = {}
    # start pairwise match
    for proj, contribz in curr_agg.items():
        # build inner layer against contributors
        contributors = []
        # cache sqrts of each contribution to make pairing easier
        curr_agg_sqrts[proj] = {}
        # iterate on the contributions and set default state
        for k1, v1 in contribz.items():
            # cache the sqrt of the given value (v1 = total contribution to this grant by this user)
            curr_agg_sqrts[proj][k1] = float(v1) ** 0.5

            # iterate on the contributions again to create pairs
            for k2 in contributors:
                # fix direction of comparison
                u_k1 = k1 if k2 > k1 else k2
                u_k2 = k2 if k2 > k1 else k1
                # never pair against matching contribs
                if k2 != k1:
                    # count how many pairs we're constructing
                    pairs_tot += 1
                    # only store pairs in this direction to match clr calc usage
                    if u_k1 not in pair_totals:
                        pair_totals[u_k1] = {}

                    if u_k2 not in pair_totals[u_k1]:
                        pair_totals[u_k1][u_k2] = 0

                    # sum the multiple of the pair of sqrts every time a pair of users contribute to the same grant
                    pair_totals[u_k1][u_k2] += curr_agg_sqrts[proj][u_k1] * curr_agg_sqrts[proj][u_k2]

            # record each item in the dict to a copy
            contributors.append(k1)

    return pair_totals, curr_agg_sqrts, pairs_tot


def calculate_clr(curr_agg, trust_dict, pair_totals, curr_agg_sqrts, v_threshold, total_pot):
    '''
        calculates the clr amount at the given threshold and total pot
        args:
            curr_agg
                {
                    grant_id (str): {
                        user_id (str): aggregated_amount (float)
                    }
                }
            pair_totals
                {
                    user_id (str): {user_id (str): pair_total (float)}
                }
            curr_agg_sqrts
                {
                    grantId (int): {
                        k1 (float): sqrt(v1) (float)
                    }
                }
            trust_dict
                {
                    user_id (str): trust_score (float)
                }
            v_threshold
                float
            total_pot
                float
        returns:
            total clr award by grant, analytics, normalized by the normalization factor
                [{'id': proj, 'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}]
            saturation point
                boolean
    '''
    bigtot = 0
    totals = {}

    for proj, contribz in curr_agg.items():
        tot = 0
        _num = 0
        _sum = 0
        # record contributors to reduce time complexity of the inner contribz iteration
        contributors = []
        # get the sqrts of this projects contributions
        sqrts = curr_agg_sqrts[proj]
        # start pairwise matches
        for k1, v1 in contribz.items():
            _num += 1
            _sum += v1

            # pairwise matches to current round
            for k2 in contributors:
                # fix direction of comparison
                u_k1 = k1 if k2 > k1 else k2
                u_k2 = k2 if k2 > k1 else k1
                # never pair against matching contribs
                if k2 != k1:
                    tot += (sqrts[u_k1] * sqrts[u_k2]) / (pair_totals[u_k1][u_k2] / (v_threshold * float(max(trust_dict[u_k1], trust_dict[u_k2]))) + 1)

            # record each item in the dict to a copy
            contributors.append(k1)

        if type(tot) == complex:
            tot = float(tot.real)

        bigtot += tot
        totals[proj] = {'id': proj, 'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}

    return bigtot, totals


def calculate_clr_for_prediction(bigtot, totals, curr_agg, trust_dict, curr_agg_sqrts, v_threshold, total_pot, grant_id, amount, match_cap_per_grant):
    '''
        clubbed function that runs all calculation functions and returns the result for a single grant_id

        args:
            bigtot     :   float
            totals     :
                {
                    grantId (int): {
                        number_contributions (int),
                        contribution_amount (float),
                        clr_amount (float),
                    }
                }
            curr_agg   :
                {
                    grantId (int): {
                        profileId (str): amount (float)
                    }
                }
            trust_dict  :
                {
                    profileId (str): trust_bonus (float)
                }
            curr_agg_sqrts
                {
                    grantId (int): {
                        k1 (float): sqrt(v1) (float)
                    }
                }
            v_threshold :   float
            total_pot   :   float
            grant_id    ;   int
            amount      ;   int

        returns:
            (grant clr award amounts (dict), clr_amount (float), number_contributions (int), contribution_amount (float))
    '''

    # make sure contributions exist
    if curr_agg.get(grant_id):
        # find grant in contributions list and add donation
        if amount:
            # take a copy to isolate changes
            totals = copy.deepcopy(totals)

            # get the contributions for this grant only
            contribz = curr_agg.get(grant_id)

            # unpack state from the selected grants totals entry
            total = totals.get(grant_id, {})

            # we use these as a basis for the prediction
            tot = total.get('clr_amount', 0)
            _num = total.get('number_contributions', 0) + 1
            _sum = total.get('contribution_amount', 0) + amount

            # remove old total from bigtot
            bigtot -= tot

            # get sqrt for the prediction
            amount_sqrt = float(amount) ** 0.5

            # get the sqrts of this projects contributions
            sqrts = curr_agg_sqrts[grant_id]

            # we can simplify this section of the algorithm as we know that only one additional contribution (amount) is being presented,
            # which will only be paired with other contributions for this grant - because of this we can skip rebuilding the pair_total
            # and only have to consider the curr grants contributions and the prediction amount - this saves a huge amount of compute O(n)
            for k2, v2 in contribz.items():
                pt =  amount_sqrt * sqrts[k2]
                tot +=  pt / (pt / (v_threshold * float(max(trust_dict[k2], 1))) + 1)

            if type(tot) == complex:
                tot = float(tot.real)

            totals[grant_id] = {'id': grant_id, 'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}

            # normalise the result
            grants_clr = normalise(bigtot + tot, totals, total_pot, match_cap_per_grant)

        # find grant we added the contribution to and get the new clr amount
        grant_clr = grants_clr.get(grant_id)
        return (
            grant_clr,
            grant_clr['clr_amount'],
            grant_clr['number_contributions'],
            grant_clr['contribution_amount']
        )
    else:
        grants_clr = None

    # print(f'info: no contributions found for grant {grant}')
    return (grants_clr, 0.0, 0, 0.0)


def normalise(bigtot, totals, total_pot, match_cap_per_grant):
    '''
        given the total amount distributed (bigtot) and the total_pot size normalise the distribution
        args:
            bigtot    : float
            totals    : [{'id': proj, 'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}]
            total_pot : float
        returns:
            normalised total clr award by grant:
                [{'id': proj, 'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}]

    '''
    # check if saturation is reached
    is_saturated = bigtot >= total_pot
    # check for saturation and normalise if reached
    if is_saturated:
        # print(f'saturation reached. Total Pot: ${total_pot} | Total Allocated ${bigtot}. Normalizing')
        for key, t in totals.items():
            t['clr_amount'] = ((t['clr_amount'] / bigtot) * total_pot)
    else:
        if bigtot == 0:
            bigtot = 1
        percentage_increase = np.log(total_pot / bigtot) / 100
        for key, t in totals.items():
            t['clr_amount'] = t['clr_amount'] * (1 + percentage_increase)

    # apply the match cap post-normalisation
    totals = apply_cap(totals, match_cap_per_grant, is_saturated)

    return totals


def apply_cap(totals, match_cap_per_grant, should_spread):
    # work out how much of the pool is remaining after capping each grant
    remainder = 0   # amount left to be redistributed after cap
    uncapped = 0    # total amount matched for grants which haven't capped

    # cap each of the clr_amounts
    for key, t in totals.items():
        if t['clr_amount'] >= match_cap_per_grant:
            # grant has exceeded the cap
            #  - so cap the clr_amount
            #  - add the extra funds to remainder
            remainder += t['clr_amount'] - match_cap_per_grant
            #  - apply the cap
            t['clr_amount'] = match_cap_per_grant

        else:
            # grant has not exceed cap so add amount to uncapped
            uncapped += t['clr_amount']

    # check that we have both capped and uncapped grants and that we should be spreading the remainder
    if should_spread and remainder > 0 and uncapped > 0:
        # div so we can spread the remainder proportionally
        per_remainder = remainder / uncapped
        # reset remainder to check if any grants enter the cap region after spreading the remainder
        remainder = 0
        # spread the remainder
        for key, t in totals.items():
            if t['clr_amount'] < match_cap_per_grant:
                t['clr_amount'] += per_remainder * t['clr_amount']
                # check if the cap is hit after spreading the remainder
                if t['clr_amount'] >= match_cap_per_grant:
                    remainder += t['clr_amount'] - match_cap_per_grant

        # apply the cap again (recursively)
        if remainder > 0:
            apply_cap(totals, match_cap_per_grant, should_spread)

    return totals

@transaction.atomic
def predict_clr(save_to_db=False, from_date=None, clr_round=None, network='mainnet', only_grant_pk=None, what='full', use_sql=False):
    # setup
    counter = 0
    debug_output = []
    clr_calc_start_time = timezone.now()

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)

    print(f"- starting fetch_grants at {round(time.time(),1)}")
    grants = fetch_grants(clr_round, network)

    # collect data using sql or django (to group+sum)
    if use_sql:
        print(f"- starting get data and sum at {round(time.time(),1)}")
        curr_agg, trust_dict = fetch_summed_contributions(grants, clr_round, network)
    else:
        print(f"- starting fetch_contributions at {round(time.time(),1)}")
        contributions = fetch_contributions(clr_round, network)

        print(f"- starting sum (of {contributions.count()} contributions) at {round(time.time(),1)}")
        grant_contributions_curr = populate_data_for_clr(grants, contributions, clr_round)
        curr_round, trust_dict = translate_data(grant_contributions_curr)
        # this aggregates the data into the expected format
        curr_agg = aggregate_contributions(curr_round)

    if len(curr_agg) == 0:
        print(f'- done - no Contributions for CLR {clr_round.round_num}. Exiting')
        print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")
        return

    # aggregate pairs and run calculation to get current distribution
    print(f"- starting pairwise component with {len(trust_dict)} contributors at {round(time.time(),1)}")
    pair_totals, curr_agg_sqrts, pairs_tot = get_totals_by_pair(curr_agg)

    print(f"- starting current distributions calc with {pairs_tot} pairs at {round(time.time(),1)}")
    grant_clr_percentage_cap = clr_round.grant_clr_percentage_cap if clr_round.grant_clr_percentage_cap else 100
    bigtot, totals = calculate_clr(curr_agg, trust_dict, pair_totals, curr_agg_sqrts, v_threshold, total_pot)

    # $ value of the percentage cap
    match_cap_per_grant = total_pot * (float(grant_clr_percentage_cap) / 100)

    # normalise against a deepcopy of the totals to avoid mutations
    curr_grants_clr = normalise(bigtot, copy.deepcopy(totals), total_pot, match_cap_per_grant)

    # for slim calc - only update the current distribution and skip calculating predictions
    if what == 'slim':
        print(f"- saving slim grant calc at {round(time.time(),1)}")
        total_count = len(curr_grants_clr.items())
        for pk, grant_calc in curr_grants_clr.items():
            counter += 1
            if counter % 10 == 0 or True:
                print(f"- {counter}/{total_count} grants iter, pk:{pk}, at {round(time.time(),1)}")

            # update latest calcs with current distribution
            grant_calc = curr_grants_clr[pk]
            grant = clr_round.grants.using('default').get(pk=pk)
            latest_calc = grant.clr_calculations.using('default').filter(latest=True, grantclr=clr_round).order_by('-pk').first()
            if not latest_calc:
                print(f"- - could not find latest clr calc for {grant.pk} ")
                continue
            clr_prediction_curve = copy.deepcopy(latest_calc.clr_prediction_curve)
            clr_prediction_curve[0][1] = grant_calc['clr_amount'] # update only the existing match estimate
            print(clr_prediction_curve)
            clr_round.record_clr_prediction_curve(grant, clr_prediction_curve)
            grant.save()
        # if we are only calculating slim CLR calculations, return here and save 97% compute power
        print(f"- done calculating at {round(time.time(),1)}")
        print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")
        return

    # only perform predictions for this grant if provided
    if only_grant_pk:
        grants = grants.filter(pk=only_grant_pk)

    print(f"- starting grants iter at {round(time.time(),1)}")
    # for full calc - calculate the clr for each grant given additional potential_donations
    total_count = grants.count()

    # select all latest results which match this round
    invalid_clr_calculations = GrantCLRCalculation.objects.filter(latest=True, grantclr=clr_round.pk)

    for grant in grants:
        # exclude grants which will have a result saved in this run
        invalid_clr_calculations = invalid_clr_calculations.exclude(grant=grant.pk)

        # five potential additional donations plus the base case of 0
        potential_donations = [0, 1, 10, 100, 1000, 10000]

        # debug the run...
        counter += 1
        if counter % 10 == 0 or True:
            print(f"- {counter}/{total_count} grants iter, pk:{grant.id}, at {round(time.time(),1)}")

        # if no contributions have been made for this grant then the pairwise will fail and there will be no matching for this grant
        if not curr_agg.get(grant.id):
            grants_clr = None
            potential_clr = [0.0 for x in range(0, 6)]
        else:
            potential_clr = []
            for amount in potential_donations:
                # no need to run the calculation multiple times for amount=0 (will always be the same result)
                if amount == 0:
                    # use the current distribution calc
                    grants_clr = curr_grants_clr.get(grant.id)
                    predicted_clr = grants_clr['clr_amount'] if grants_clr else 0.0
                else:
                    raw_grants_clr = totals.get(grant.id)
                    # final will save the current distribution for every grant (ie without predictions)
                    if what == 'final' or raw_grants_clr['clr_amount'] == match_cap_per_grant:
                        # ignore the other ones
                        grants_clr = None
                        predicted_clr = 0.0
                    else:
                        # calculate clr with additional donation amount
                        grants_clr, predicted_clr, _, _ = calculate_clr_for_prediction(
                            bigtot, totals, curr_agg, trust_dict, curr_agg_sqrts, v_threshold, total_pot, grant.id, amount, match_cap_per_grant
                        )

                # record each point of the prediction
                potential_clr.append(predicted_clr)

        # calculate the prediction curve
        clr_prediction_curve = list(zip(potential_donations, potential_clr))
        base = clr_prediction_curve[0][1]
        grant.last_clr_calc_date = timezone.now()
        grant.next_clr_calc_date = timezone.now() + timezone.timedelta(minutes=60)

        # check that we have enough data to set the curve
        can_estimate = True if base or clr_prediction_curve[1][1] or clr_prediction_curve[2][1] or clr_prediction_curve[3][1] else False
        if can_estimate:
            clr_prediction_curve  = [[ele[0], ele[1], ele[1] - base if ele[1] != 0 else 0.0] for ele in clr_prediction_curve ]
        else:
            clr_prediction_curve = [[0.0, 0.0, 0.0] for x in range(0, 6)]

        print(clr_prediction_curve)

        # save the result of the prediction
        if save_to_db and from_date > (clr_calc_start_time - timezone.timedelta(hours=1)):
            clr_round.record_clr_prediction_curve(grant, clr_prediction_curve)
            grant.save()

        debug_output.append({'grant': grant.id, "title": grant.title, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})

    # update the state on any past results which are no longer included in this round
    if save_to_db:
        invalid_clr_calculations.update(latest=False, active=False)

    print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")

    return debug_output
