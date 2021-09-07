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
from django.utils import timezone

from grants.clr_old import calculate_clr_for_donation, fetch_data, populate_data_for_clr
from grants.models import GrantCLR


def analytics_clr(from_date=None, clr_round=None, network='mainnet'):
    # setup
    # clr_calc_start_time = timezone.now()
    debug_output = [['grant_id', 'grant_title', 'number_contributions', 'contribution_amount', 'clr_amount']]

    # one-time data call
    total_pot = float(clr_round.total_pot)
    v_threshold = float(clr_round.verified_threshold)
    uv_threshold = float(clr_round.unverified_threshold)

    print(total_pot)

    grants, contributions = fetch_data(clr_round, network)

    grant_contributions_curr = populate_data_for_clr(grants, contributions,  clr_round)

    # calculate clr analytics output
    for grant in grants:
        clr_amount, _, num_contribs, contrib_amount = calculate_clr_for_donation(
            grant,
            0,
            grant_contributions_curr,
            total_pot,
            v_threshold,
            uv_threshold
        )
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
