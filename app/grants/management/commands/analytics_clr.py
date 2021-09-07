# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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

from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from grants.clr import calculate_clr, fetch_grants, get_summed_contribs_query, get_totals_by_pair, normalise
from grants.models import GrantCLR


def analytics_clr(from_date=None, clr_round=None, network='mainnet'):
    # setup
    # clr_calc_start_time = timezone.now()
    debug_output = [['grant_id', 'grant_title', 'number_contributions', 'contribution_amount', 'clr_amount']]

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)

    print(total_pot)

    grants = fetch_grants(clr_round, network)

    # collect contributions for clr_round into temp table
    initial_query = get_summed_contribs_query(grants, clr_round.start_date, clr_round.end_date, clr_round.contribution_multiplier, network)

    # open cursor and execute the groupBy sum for the round
    with connection.cursor() as cursor:
        curr_agg = {}
        trust_dict = {}
        # execute to populate shared state for the round
        cursor.execute(initial_query) # (we could potential do better here by sharing this temp table between rounds)
        for _row in cursor.fetchall():
            if not curr_agg.get(_row[0]):
                curr_agg[_row[0]] = {}

            trust_dict[_row[1]] = _row[3]
            curr_agg[_row[0]][_row[1]] = _row[2]

        ptots = get_totals_by_pair(curr_agg)
        bigtot, totals = calculate_clr(curr_agg, ptots, trust_dict, v_threshold, total_pot)

        # normalise against a deepcopy of the totals to avoid mutations
        curr_grants_clr = normalise(bigtot, totals, total_pot)
        
        # calculate clr analytics output
        for grant in grants:
            num_contribs, contrib_amount, clr_amount = curr_grants_clr.get(grant.id, {'num_contribs': 0, 'contrib_amount': 0, 'clr_amount': None}).values()
            # debug_output.append([grant.id, grant.title, num_contribs, contrib_amount, clr_amount])
            debug_output.append([grant.id, grant.title, grant.positive_round_contributor_count, float(grant.amount_received_in_round), clr_amount])

    return debug_output



class Command(BaseCommand):

    help = 'calculate clr base analytic results for all clr rounds or for a specific clr round'

    def add_arguments(self, parser):
        parser.add_argument('network', type=str, default='mainnet', choices=['rinkeby', 'mainnet'])
        parser.add_argument('clr_pk', type=str, default="all")


    def handle(self, *args, **options):

        network = options['network']
        clr_pk = options['clr_pk']

        if clr_pk == "all":
            active_clr_rounds = GrantCLR.objects.filter(is_active=True)
        else:
            active_clr_rounds = GrantCLR.objects.filter(pk=clr_pk)

        if active_clr_rounds:
            for clr_round in active_clr_rounds:
                print(f"calculating CLR results for round: {clr_round.round_num} {clr_round.sub_round_slug}")
                analytics = analytics_clr(
                    from_date=timezone.now(),
                    clr_round=clr_round,
                    network=network
                )
                print(analytics)
                print(f"finished CLR results for round: {clr_round.round_num} {clr_round.sub_round_slug}")

        else:
            print("No active CLRs found")
