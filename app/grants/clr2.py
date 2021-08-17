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
from dashboard.models import Profile
from grants.models import Grant, GrantCollection
from townsquare.models import SquelchProfile

CLR_PERCENTAGE_DISTRIBUTED = 0


def get_summed_contribs_query(grants, created_after, created_before, multiplier, network):
    # only consider contribs from current grant set
    grantIds = ''
    for i in range(len(grants)):
        grantIds += "'" + str(grants[i].id) + "'" + (', ' if i+1 != len(grants) else '')

    summedContribs = f'''
        -- drop the table if it exists
        DROP TABLE IF EXISTS tempUserTotals;
 
        -- group by ... sum the contributions $ value for each user
        SELECT  
            grants.use_grant_id as grant_id, 
            grants_contribution.profile_for_clr_id as user_id,
            SUM((grants_contribution.normalized_data ->> 'amount_per_period_usdt')::FLOAT * {float(multiplier)}),
            MAX(dashboard_profile.as_dict ->> 'trust_bonus')::FLOAT as trust_bonus
        INTO TEMP TABLE tempUserTotals
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
            WHERE grants_grant.id IN ({grantIds})
        ) grants ON ((grants_contribution.normalized_data ->> 'id')::FLOAT = grants.grant_id)
        WHERE (
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

        -- index before joining in clr_query
        CREATE INDEX ON tempUserTotals (grant_id, user_id);

        SELECT * FROM tempUserTotals;
    '''

    return summedContribs


def add_prediction_contrib_query(grant_id, amount):
    predictionContrib = f'''
        -- delete any previous prediction values from the contributions table
        DELETE FROM tempUserTotals WHERE user_id = 999999999;

        -- insert the prediction value into contributions (grant_id, user_id, amount, trust_bonus)
        {"INSERT INTO tempUserTotals VALUES(" + str(grant_id) + ", 999999999, " + str(amount) + ", 1);" if amount != 0 else ""}
    '''
    return predictionContrib


def get_calc_query(v_threshold):
    pairwise = '''
        -- produce the pairwise sums
        SELECT
            c1.user_id,
            c2.user_id as user_id_2,
            SUM((c1.sum * c2.sum) ^ 0.5) pairwise
        FROM tempUserTotals c1
        INNER JOIN tempUserTotals c2 ON (c1.grant_id = c2.grant_id AND c2.user_id > c1.user_id)
        GROUP BY c1.user_id, c2.user_id
        '''

    clrAmount = f'''
        -- calculate the CLR amount for each grant
        SELECT
            c1.grant_id,
            -- add trust scores and threshold here
            SUM((c1.sum * c2.sum) ^ 0.5 / (pw.pairwise / ({v_threshold} * GREATEST(c2.trust_bonus, c1.trust_bonus)) + 1)) final_clr
        FROM tempUserTotals c1
        INNER JOIN tempUserTotals c2 ON (c1.grant_id = c2.grant_id AND c2.user_id > c1.user_id)
        INNER JOIN ({pairwise}) pw ON (c1.user_id = pw.user_id AND c2.user_id = pw.user_id_2)
        GROUP BY c1.grant_id
        ORDER BY c1.grant_id;
        '''

    # # CTE of pairwise, clrAmount and clrResult (this will return the clr_amount, number_contribtions and contribution_amount for each grant)
    # clrResult = f'''
    #     -- group by ... sum the contributions $ value for each grant and place the clr
    #     SELECT
    #         c1.grant_id,
    #         -- use MAX/MIN because we know we will only match a single CLR here
    #         MAX(clr.final_clr) clr_amount,
    #         SUM(1) number_contributions,
    #         SUM(c1.sum) contribution_amount
    #     FROM tempUserTotals c1
    #     INNER JOIN ({clrAmount}) clr ON (c1.grant_id = clr.grant_id)
    #     GROUP BY c1.grant_id;
    #     '''

    return clrAmount


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


def calculate_clr_for_donation(grant_id, amount, cursor, total_pot, v_threshold):
    # collect results
    bigtot = 0
    totals = {}

    # find grant in contributions list and add donation
    clr_query = add_prediction_contrib_query(grant_id, amount) + get_calc_query(v_threshold)
    cursor.execute(clr_query)
    for _row in cursor.fetchall():
        bigtot += _row[1] if _row[1] else 0
        totals[_row[0]] = {'clr_amount': _row[1]}

    global CLR_PERCENTAGE_DISTRIBUTED

    # check if saturation is reached
    if bigtot >= total_pot: # saturation reached
        # print(f'saturation reached. Total Pot: ${total_pot} | Total Allocated ${bigtot}. Normalizing')
        CLR_PERCENTAGE_DISTRIBUTED = 100
        for pk, grant_calc in totals.items():
            grant_calc['clr_amount'] = ((grant_calc['clr_amount'] / bigtot) * total_pot)
    else:
        CLR_PERCENTAGE_DISTRIBUTED = (bigtot / total_pot) * 100
        if bigtot == 0:
            bigtot = 1
        percentage_increase = np.log(total_pot / bigtot) / 100
        for pk, grant_calc in totals.items():
            grant_calc['clr_amount'] = grant_calc['clr_amount'] * (1 + percentage_increase) if grant_calc['clr_amount'] else 0

    # find grant we added the contribution to and get the new clr amount
    if grant_id and totals.get(grant_id):
        clr = totals[grant_id]
        return (
            clr,
            clr['clr_amount']
        )

    # print(f'info: no contributions found for grant {grant_id}')
    return (totals, 0.0)


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

    # override the grants list to the one selected
    if only_grant_pk:
        grants = grants.filter(pk=only_grant_pk)

    print(f"- starting get data and sum at {round(time.time(),1)}")
    # collect contributions for clr_round into temp table
    initial_query = get_summed_contribs_query(grants, clr_round.start_date, clr_round.end_date, clr_round.contribution_multiplier, network)
    # open cursor and execute the groupBy sum for the round
    with connection.cursor() as cursor:
        counter = 0
        curr_agg = {}
        # execute to populate shared state for the round
        cursor.execute(initial_query) # (we could potential do better here by sharing this temp table between rounds)
        for _row in cursor.fetchall():
            if not curr_agg.get(_row[0]):
                curr_agg[_row[0]] = {}
            curr_agg[_row[0]][_row[1]] = _row[2]

        if len(curr_agg) == 0:
            print(f'- done - No Contributions for CLR {clr_round.round_num}. Exiting')
            print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")
            return
            
        print(f"- starting current grant calc (free of predictions) at {round(time.time(),1)}")
        curr_grants_clr, _ = calculate_clr_for_donation(
            None, 0, cursor, total_pot, v_threshold
        )

        if what == 'slim':
            # if we are only calculating slim CLR calculations, return here and save 97% compute power
            print(f"- saving slim grant calc at {round(time.time(),1)}")
            total_count = len(curr_grants_clr.items())
            for grant_id, grant_calc in curr_grants_clr.items():
                counter += 1
                if counter % 10 == 0 or True:
                    print(f"- {counter}/{total_count} grants iter, pk:{grant_id}, at {round(time.time(),1)}")

                # update latest calcs with current distribution
                grant = clr_round.grants.using('default').get(pk=grant_id)
                latest_calc = grant.clr_calculations.using('default').filter(latest=True, grantclr=clr_round).order_by('-pk').first()
                if not latest_calc:
                    print(f"- - could not find latest clr calc for {grant_id} ")
                    continue
                clr_prediction_curve = copy.deepcopy(latest_calc.clr_prediction_curve)
                clr_prediction_curve[0][1] = grant_calc['clr_amount'] if grant_calc else 0.0 # update only the existing match estimate
                print(clr_prediction_curve)
                clr_round.record_clr_prediction_curve(grant, clr_prediction_curve)
                grant.save()
            # if we are only calculating slim CLR calculations, return here and save 97% compute power
            print(f"- done calculating at {round(time.time(),1)}")
            print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")
            return

        # calculate clr given additional donations
        total_count = grants.count()

        print(f"- starting grants iter at {round(time.time(),1)}")
        # calculate each grant as a distinct input
        for grant in grants:
            # five potential additional donations plus the base case of 0
            potential_donations = [0, 1, 10, 100, 1000, 10000]

            # debug the run...
            counter += 1
            if counter % 10 == 0 or True:
                print(f"- {counter}/{total_count} grants iter, pk:{grant.id}, at {round(time.time(),1)}")

            # if no contributions have been made for this grant then the pairwise will fail and no match will be discovered
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
                            # calculate clr with each additional donation
                            grants_clr, predicted_clr = calculate_clr_for_donation(
                                grant.id, amount, cursor, total_pot, v_threshold
                            )
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
                clr_round.record_clr_prediction_curve(_grant, clr_prediction_curve)
                _grant.save()

            debug_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})

    print(f"\nTotal execution time: {(timezone.now() - clr_calc_start_time)}\n")

    return debug_output
