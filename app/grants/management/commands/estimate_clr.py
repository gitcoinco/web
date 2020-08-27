# -*- coding: utf-8 -*-
"""Define the Grant subminer management command.

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

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.utils import get_tx_status, has_tx_mined
from grants.clr import predict_clr
from grants.models import Contribution, Grant, GrantCLR
from marketing.mails import warn_subscription_failed


class Command(BaseCommand):

    help = 'calculate CLR estimates for all grants'

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
                print(f"CALCULATING CLR estimates for ROUND: {clr_round.round_num}")
                a = predict_clr(
                    save_to_db=True,
                    from_date=timezone.now(),
                    clr_round=clr_round,
                    network=network
                )
                print(f"finished CLR estimates for {clr_round.round_num}")

        else:
            print("No active CLRs found")

        # Upate grants mppping to active CLR rounds
        grants = Grant.objects.all()
        clr_rounds = GrantCLR.objects.all()
        for clr_round in clr_rounds:
            grants_in_clr_round = grants.filter(**clr_round.grant_filters)

            for grant in grants_in_clr_round:
                grant_has_mapping_to_round = grant.in_active_clrs.filter(pk=clr_round.pk).exists()

                if clr_round.is_active and not grant_has_mapping_to_round:
                    grant.in_active_clrs.add(clr_round)
                    grant.save()
                elif not clr_round.is_active and grant_has_mapping_to_round:
                    grant.in_active_clrs.remove(clr_round)
                    grant.save()
