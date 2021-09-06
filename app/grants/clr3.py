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

from django.db import connection
from django.utils import timezone

import numpy as np
from grants.models import Contribution, Grant, GrantCollection
from grants.tasks import save_clr_prediction_curve
from townsquare.models import SquelchProfile


def fetch_grants(clr_round, network='mainnet'):
    grant_filters = clr_round.grant_filters
    collection_filters = clr_round.collection_filters

    grants = clr_round.grants.filter(network=network, hidden=False, active=True, is_clr_eligible=True, link_to_new_grant=None)

    if grant_filters:
        # Grant Filters (grant_type, category)
        grants = grants.filter(**grant_filters)
    elif collection_filters:
        # Collection Filters
        grant_ids = GrantCollection.objects.filter(**collection_filters).values_list('grants', flat=True)
        grants = grants.filter(pk__in=grant_ids)

    return grants


def get_summed_contribs_query(grants, created_after, created_before, multiplier, network):
    # only consider contribs from current grant set
    grantIds = ''
    for i in range(len(grants)):
        grantIds += "'" + str(grants[i].id) + "'" + (', ' if i+1 != len(grants) else '')

    summedContribs = f'''
        -- group by ... sum the contributions $ value for each user
        SELECT
            grants.use_grant_id as grant_id,
            grants_contribution.profile_for_clr_id as user_id,
            SUM((grants_contribution.normalized_data ->> 'amount_per_period_usdt')::FLOAT * {float(multiplier)}),
            MAX(dashboard_profile.as_dict ->> 'trust_bonus')::FLOAT as trust_bonus
        FROM grants_contribution
        INNER JOIN dashboard_profile ON (grants_contribution.profile_for_clr_id = dashboard_profile.id)
        INNER JOIN grants_subscription ON (grants_contribution.subscription_id = grants_subscription.id)
        RIGHT JOIN (
            SELECT
                grants_grant.id as grant_id,
                (
                    CASE
                    WHEN grants_grant.defer_clr_to_id IS NOT NULL THEN grants_grant.defer_clr_to_id
                    ELSE grants_grant.id
                    END
                ) as use_grant_id
            FROM grants_grant
        ) grants ON ((grants_contribution.normalized_data ->> 'id')::FLOAT = grants.grant_id)
        WHERE (
            grants_contribution.normalized_data ->> 'id' IN ({grantIds}) AND
            grants_contribution.created_on >= '{created_after}' AND
            grants_contribution.created_on <= '{created_before}' AND
            grants_contribution.match = True AND
            grants_subscription.network = '{network}' AND
            grants_contribution.success = True AND
            (grants_contribution.normalized_data ->> 'amount_per_period_usdt')::FLOAT >= 0 AND
            NOT (
                grants_contribution.profile_for_clr_id IN (
                    SELECT squelched.profile_id FROM townsquare_squelchprofile squelched WHERE squelched.active = True
                ) AND grants_contribution.profile_for_clr_id IS NOT NULL
            )
        )
        GROUP BY grants.use_grant_id, grants_contribution.profile_for_clr_id;
    '''

    return summedContribs


def get_totals_by_pair(contrib_dict):
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
    pair_totals = {}

    # start pairwise match
    for _, contribz in contrib_dict.items():
        for k1, v1 in contribz.items():
            if k1 not in pair_totals:
                pair_totals[k1] = {}

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                if k2 not in pair_totals[k1]:
                    pair_totals[k1][k2] = 0
                pair_totals[k1][k2] += (v1 * v2) ** 0.5

    return pair_totals


def calculate_clr(curr_agg, pair_totals, trust_dict, v_threshold, total_pot):
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
                {user_id (str): {user_id (str): pair_total (float)}}
            trust_dict
                {user_id (str): trust_score (float)}
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

        # start pairwise matches
        for k1, v1 in contribz.items():
            _num += 1
            _sum += v1

            # pairwise matches to current round
            for k2, v2 in contribz.items():
                if int(k2) > int(k1):
                    tot += ((v1 * v2) ** 0.5) / (pair_totals[k1][k2] / (v_threshold * max(trust_dict[k2], trust_dict[k1])) + 1)

        if type(tot) == complex:
            tot = float(tot.real)

        bigtot += tot
        totals[proj] = {'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}

    return bigtot, totals


def calculate_clr_for_prediction(bigtot, totals, curr_agg, trust_dict, v_threshold, total_pot, grant_id, amount):
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
            v_threshold :   float
            total_pot   :   float
            grant_id    ;   int
            amount      ;   int

        returns:
            (grant clr award amounts (dict), clr_amount (float), number_contributions (int), contribution_amount (float))
    '''

    # make sure contributions exist
    if curr_agg.get(grant_id) or not grant_id:
        # find grant in contributions list and add donation
        if amount:
            # set predictions against this user
            dummy_user = '999999999999'
            # take a copy to isolate changes
            totals = copy.deepcopy(totals)

            # add prediction amount
            curr_agg[grant_id][dummy_user] = amount

            # get the contributions for this grant only
            contribz = curr_agg.get(grant_id)

            # unpack state from the selected grants totals entry
            total = totals.get(grant_id, {})

            tot = total.get('clr_amount', 0)
            _num = total.get('number_contributions', 0) + 1
            _sum = total.get('contribution_amount', 0) + amount

            # remove old total from bigtot
            bigtot -= tot

            # start pairwise matches
            for k2, v2 in contribz.items():
                # pairwise matches to current round
                if int(dummy_user) > int(k2):
                    tot += ((amount * v2) ** 0.5) / ((amount * v2) ** 0.5 / (v_threshold * max(trust_dict[k2], 1)) + 1)

          if type(tot) == complex:
                tot = float(tot.real)
            
            totals[grant_id] = {'number_contributions': _num, 'contribution_amount': _sum, 'clr_amount': tot}

            # normalise the result
            grants_clr = normalise(bigtot + tot, totals, total_pot)

        # find grant we added the contribution to and get the new clr amount
        if grants_clr.get(grant_id):
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
    

def normalise(bigtot, totals, total_pot):
    # check for saturation and normalise if reached
    if bigtot >= total_pot: 
        # print(f'saturation reached. Total Pot: ${total_pot} | Total Allocated ${bigtot}. Normalizing')
        for key, t in totals.items():
            t['clr_amount'] = ((t['clr_amount'] / bigtot) * total_pot)
    else:
        if bigtot == 0:
            bigtot = 1
        percentage_increase = np.log(total_pot / bigtot) / 100
        for key, t in totals.items():
            t['clr_amount'] = t['clr_amount'] * (1 + percentage_increase)

    return totals


def predict_clr(save_to_db=False, from_date=None, clr_round=None, network='mainnet', only_grant_pk=None, what='full'):
    import time

    # setup
    clr_calc_start_time = timezone.now()
    debug_output = []

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)

    print(f"- starting fetch_grants at {round(time.time(),1)}")
    grants = fetch_grants(clr_round, network)

    print(f"- starting get data and sum at {round(time.time(),1)}")
    # collect contributions for clr_round into temp table
    initial_query = get_summed_contribs_query(grants, clr_round.start_date, clr_round.end_date, clr_round.contribution_multiplier, network)

    if only_grant_pk:
        grants = grants.filter(pk=40)

    # open cursor and execute the groupBy sum for the round
    with connection.cursor() as cursor:
        counter = 0
        curr_agg = {}
        trust_dict = {}
        # execute to populate shared state for the round
        cursor.execute(initial_query) # (we could potential do better here by sharing this temp table between rounds)
        for _row in cursor.fetchall():
            if not curr_agg.get(_row[0]):
                curr_agg[_row[0]] = {}
            trust_dict[_row[1]] = _row[3]
            curr_agg[_row[0]][_row[1]] = _row[2]

        if len(curr_agg) == 0:
            print(f'- done - no Contributions for CLR {clr_round.round_num}. Exiting')
            print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")
            return

        print(f"- starting current distributions calc at {round(time.time(),1)}")
        # aggregate pairs and run calculation to get current distribution
        pair_totals = get_totals_by_pair(curr_agg)
        bigtot, totals = calculate_clr(curr_agg, pair_totals, trust_dict, v_threshold, total_pot)

        # normalise against a deepcopy of the totals to avoid mutations
        curr_grants_clr = normalise(bigtot, copy.deepcopy(totals), total_pot)

        if what == 'slim':
            # if we are only calculating slim CLR calculations, return here and save 97% compute power
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

        print(f"- starting grants iter at {round(time.time(),1)}")
        # calculate clr given additional donations
        total_count = grants.count()
        for grant in grants:
            # five potential additional donations plus the base case of 0
            potential_donations = [0, 1, 10, 100, 1000, 10000]

            # debug the run...
            counter += 1
            if counter % 10 == 0 or True:
                print(f"- {counter}/{total_count} grants iter, pk:{grant.id}, at {round(time.time(),1)}")

            # if no contributions have been made for this grant then the pairwise will fail and there will be no match for this grant
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
                        # this is used when you want to count final distribution and ignore the prediction
                        if what == 'final':
                            # ignore the other ones
                            grants_clr = None
                            predicted_clr = 0.0
                        else:
                            # calculate clr with additional donation amount
                            grants_clr, predicted_clr, _, _ = calculate_clr_for_prediction(
                                bigtot, totals, curr_agg, trust_dict, v_threshold, total_pot, grant.id, amount
                            )

                    # reset potential_donations
                    if amount and curr_agg.get(grant.id):
                        del curr_agg[grant.id]['999999999999']

                    # record each point of the predicition
                    potential_clr.append(predicted_clr)

            # save the result of the prediction
            if save_to_db:
                _grant = Grant.objects.get(pk=grant.id)
                clr_prediction_curve = list(zip(potential_donations, potential_clr))
                base = clr_prediction_curve[0][1]
                _grant.last_clr_calc_date = timezone.now()
                _grant.next_clr_calc_date = timezone.now() + timezone.timedelta(minutes=60)

                # check that we have enough data to set the curve
                can_estimate = True if base or clr_prediction_curve[1][1] or clr_prediction_curve[2][1] or clr_prediction_curve[3][1] else False
                if can_estimate:
                    clr_prediction_curve  = [[ele[0], ele[1], ele[1] - base] for ele in clr_prediction_curve ]
                else:
                    clr_prediction_curve = [[0.0, 0.0, 0.0] for x in range(0, 6)]
                    
                print(clr_prediction_curve)

                # save the new predicition curve via the model
                save_clr_prediction_curve.delay(grant.id, clr_prediction_curve)

            debug_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})

    print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")

    return debug_output
