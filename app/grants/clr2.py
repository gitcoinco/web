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


def get_contribs_query(created_after, created_before, network):
    contribs = f'''
        -- move the contribs into a temp table (is this necessary? we can likely go straight to get_summed_contribs)
        SELECT 
            grants_contribution.normalized_data, 
            grants_contribution.profile_for_clr_id
        INTO TEMP TABLE contributions
        FROM grants_contribution
        INNER JOIN grants_subscription 
        ON (grants_contribution.subscription_id = grants_subscription.id) 
        WHERE (
            grants_contribution.created_on >= '{created_after}' AND 
            grants_contribution.created_on <= '{created_before}' AND 
            grants_contribution.match = True AND 
            grants_subscription.network = '{network}' AND 
            grants_contribution.success = True AND
            NOT (
                grants_contribution.profile_for_clr_id IN (
                    SELECT squelched.profile_id FROM townsquare_squelchprofile squelched WHERE squelched.active = True
                ) AND grants_contribution.profile_for_clr_id IS NOT NULL
            )
        );
    '''
    return contribs


def get_summed_contribs_query(clr_round):
    summedContribs = f'''
        -- clean up from last iteration
        DROP TABLE IF EXISTS tempUserTotals;

        -- group by ... sum the contributions $ value for each user
        SELECT 
            contributions.normalized_data ->> 'id' as grant_id, 
            contributions.profile_for_clr_id as user_id, 
            SUM((contributions.normalized_data ->> 'amount_per_period_usdt')::FLOAT * {float(clr_round.contribution_multiplier)}),
            CAST(NULL as DECIMAL) as trust_bonus
        INTO TEMP TABLE tempUserTotals
        FROM contributions 
        GROUP BY contributions.normalized_data ->> 'id', contributions.profile_for_clr_id;

        -- index before joining in clr_query
        CREATE INDEX ON tempUserTotals (grant_id, user_id);

        -- return the data here so that we can populate the trust_bonus
        SELECT * FROM tempUserTotals;
    '''
    return summedContribs


def add_prediction_contrib_query(grant_id, amount):    
    predictionContrib = f'''
        -- delete any previous predicition values from the contributions table
        DELETE FROM tempUserTotals WHERE user_id = 999999999;

        -- insert the prediction value into contributions
        {"INSERT INTO tempUserTotals VALUES(" + str(grant_id) + ", 999999999, " + str(amount) + ", 1)" if amount != 0 else ""};
    '''
    return predictionContrib


def get_calc_query(grant_id, v_threshold):
    pairwise = '''
        DROP TABLE IF EXISTS tempPairTotals;
        -- produce the pairwise sums
        SELECT 
            c1.user_id, 
            c2.user_id as user_id_2, 
            SUM((c1.sum * c2.sum) ^ 0.5) pairwise
        INTO TEMP TABLE tempPairTotals
        FROM tempUserTotals c1 
        LEFT JOIN tempUserTotals c2 ON (c1.grant_id = c2.grant_id AND c2.user_id > c1.user_id)
        WHERE c2.user_id IS NOT NULL
        GROUP BY c1.user_id, c2.user_id;

        -- index before join
        CREATE INDEX ON tempPairTotals (user_id);
        '''

    clrCalc = f'''
        DROP TABLE IF EXISTS tempCLR;
        -- calculate the CLR amount for each grant
        SELECT 
            c1.grant_id,
            -- add trust scores and threshold here
            SUM((c1.sum * c2.sum) ^ 0.5 / (pw.pairwise / ({v_threshold} * GREATEST(c2.trust_bonus, c1.trust_bonus)) + 1)) final_clr
        INTO TEMP TABLE tempCLR
        FROM tempUserTotals c1 
        LEFT JOIN tempUserTotals c2 ON (c1.grant_id = c2.grant_id and c2.user_id > c1.user_id)
        LEFT JOIN tempPairTotals pw ON (c1.user_id = pw.user_id and c2.user_id = pw.user_id_2)
        WHERE c2.user_id IS NOT NULL
        GROUP BY c1.grant_id;

        -- index before join
        CREATE INDEX on tempCLR (grant_id);
        '''

    result = f'''
        -- group by ... sum the contributions $ value for each grant and place the clr
        SELECT 
            c1.grant_id,
            -- use MAX/MIN because we know we will only match a single CLR here
            MAX(clr.final_clr) clr_amount,
            SUM(1) number_contributions, 
            SUM(c1.sum) contribution_amount
        FROM tempUserTotals c1 
        LEFT JOIN tempCLR clr ON (c1.grant_id = clr.grant_id)
        {"WHERE c1.grant_id = '" + str(grant_id) + "'" if grant_id else ''}
        GROUP BY c1.grant_id
        ORDER BY c1.grant_id;
        '''

    return pairwise + clrCalc + result


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


def calculate_clr_for_donation(grant, amount, cursor, total_pot, v_threshold, uv_threshold):
    # collect results
    bigtot = 0
    totals = []

    # find grant in contributions list and add donation
    clr_query = add_prediction_contrib_query(grant.pk, amount) + get_calc_query(None, v_threshold)
    cursor.execute(clr_query)
    for _row in cursor.fetchall():
        bigtot += _row[1] if _row[1] else 0
        totals.append({'id': _row[0], 'clr_amount': _row[1], 'number_contributions': _row[2], 'contribution_amount': _row[3]})

    global CLR_PERCENTAGE_DISTRIBUTED

    # check if saturation is reached
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
            t['clr_amount'] = t['clr_amount'] * (1 + percentage_increase) if t['clr_amount'] else 0

    # find grant we added the contribution to and get the new clr amount
    for clr in totals:
        if int(clr['id']) == grant.id:
            return (
                clr['clr_amount'],
                clr,
                clr['number_contributions'],
                clr['contribution_amount']
            )

    # print(f'info: no contributions found for grant {grant}')
    return (None, None, None, None)


def predict_clr(save_to_db=False, from_date=None, clr_round=None, network='mainnet', only_grant_pk=None, what='full'):
    import time

    # setup
    clr_calc_start_time = timezone.now()
    debug_output = []

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)
    uv_threshold = float(clr_round.unverified_threshold)

    # fetch the grants so that we have a basis to iterate on
    grants = fetch_grants(clr_round, network)

    # override the grants list to the one selected
    if only_grant_pk:
        grants = grants.filter(pk=only_grant_pk)

    # collect contributions for clr_round into temp table
    initial_query = get_contribs_query(clr_round.start_date, clr_round.end_date, network) + get_summed_contribs_query(clr_round)
    # open cursor and execute the groupBy sum for the round
    with connection.cursor() as cursor:
        # all of these rounds will be running at the same time - does it make sense to keep this table between calls?
        # we could stand it up and drop it in estimate_clr.py?
        cursor.execute(initial_query)
        for _row in cursor.fetchall():
            profile = Profile.objects.get(pk=_row[1])
            cursor.execute(f"UPDATE tempUserTotals SET trust_bonus = '{profile.trust_bonus}' WHERE user_id = {_row[1]}")

        if what == 'slim':
            # if we are only calculating slim CLR calculations, return here and save 97% compute power
            print(f"- starting slim grant calc at {round(time.time(),1)}")
            clr_query = add_prediction_contrib_query(0, 0) + get_calc_query(None, v_threshold)
            cursor.execute(clr_query)
            print(f"- saving slim grant calc at {round(time.time(),1)}")
            for grant_calc in cursor.fetchall():
                pk = grant_calc[0]
                grant = clr_round.grants.using('default').get(pk=pk)
                latest_calc = grant.clr_calculations.using('default').filter(latest=True, grantclr=clr_round).order_by('-pk').first()
                if not latest_calc:
                    print(f"- - could not find latest clr calc for {grant.pk} ")
                    continue
                clr_prediction_curve = copy.deepcopy(latest_calc.clr_prediction_curve)
                clr_prediction_curve[0][1] = grant_calc[1] # update only the existing match estimate
                clr_round.record_clr_prediction_curve(grant, clr_prediction_curve)
                grant.save()
            # if we are only calculating slim CLR calculations, return here and save 97% compute power
            print(f"- done calculating at {round(time.time(),1)}")
            return
        
        # calculate clr given additional donations
        counter = 0
        total_count = grants.count()

        # calculate each grant as a distinct input
        for grant in grants:
            # five potential additional donations plus the base case of 0
            potential_donations = [0, 1, 10, 100, 1000, 10000]
            potential_clr = []

            counter += 1
            if counter % 10 == 0 or True:
                print(f"- {counter}/{total_count} grants iter, pk:{grant.pk}, at {round(time.time(),1)}")

            if what == 'final':
                # this is used when you want to count final distribution and ignore the prediction
                for amount in potential_donations:
                    # default the prediction for any amount which is !0
                    predicted_clr = 0.0
                    # calculate clr for current state only
                    if amount == 0:
                        predicted_clr, _, _, _ = calculate_clr_for_donation(
                            grant, amount, cursor, total_pot, v_threshold, uv_threshold
                        )
                    potential_clr.append(predicted_clr)
            else:
                for amount in potential_donations:
                    # calculate clr with each additional donation and save to grants model
                    # print(f'using {total_pot_close}')
                    predicted_clr, grants_clr, _, _ = calculate_clr_for_donation(
                        grant, amount, cursor, total_pot, v_threshold, uv_threshold
                    )
                    potential_clr.append(predicted_clr)

            if save_to_db:
                _grant = Grant.objects.get(pk=grant.pk)
                clr_prediction_curve = list(zip(potential_donations, potential_clr))
                base = clr_prediction_curve[0][1]
                _grant.last_clr_calc_date = timezone.now()
                _grant.next_clr_calc_date = timezone.now() + timezone.timedelta(minutes=60)

                can_estimate = True if base or clr_prediction_curve[1][1] or clr_prediction_curve[2][1] or clr_prediction_curve[3][1] else False

                if can_estimate :
                    clr_prediction_curve  = [[ele[0], ele[1], ele[1] - base] for ele in clr_prediction_curve ]
                else:
                    clr_prediction_curve = [[0.0, 0.0, 0.0] for x in range(0, 6)]

                clr_round.record_clr_prediction_curve(_grant, clr_prediction_curve)

                if from_date > (clr_calc_start_time - timezone.timedelta(hours=1)):
                    _grant.save()

        debug_output.append({'grant': grant.id, "clr_prediction_curve": (potential_donations, potential_clr), "grants_clr": grants_clr})

    return debug_output
