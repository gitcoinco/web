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

from dashboard.models import Profile
from grants.clr2 import calculate_clr_for_donation, fetch_grants, get_summed_contribs_query
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
        # execute to populate shared state for the round
        cursor.execute(initial_query)
        # calculate clr analytics output
        for grant in grants:
            _, clr_amount = calculate_clr_for_donation(
                grant.id,
                0,
                cursor,
                total_pot,
                v_threshold
            )
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
