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

from grants.clr2 import predict_clr
from grants.models import GrantCLR
from grants.tasks import process_predict_clr


class Command(BaseCommand):

    help = 'calculate CLR estimates for all grants'

    def add_arguments(self, parser):
        parser.add_argument('network', type=str, default='mainnet', choices=['rinkeby', 'mainnet'])
        parser.add_argument('clr_pk', type=str, default="all")
        parser.add_argument('what', type=str, default="full")
        parser.add_argument('sync', type=str, default="false")
        # slim = just run 0 contribution match upcate calcs
        # full, run [0, 1, 10, 100, calcs across all grants]


    def handle(self, *args, **options):

        network = options['network']
        clr_pk = options['clr_pk']
        what = options['what']
        sync = options['sync']
        print ('clr2', network, clr_pk, what, sync)

        if clr_pk and clr_pk.isdigit():
            active_clr_rounds = GrantCLR.objects.filter(pk=clr_pk)
        else:
            active_clr_rounds = GrantCLR.objects.filter(is_active=True)

        if active_clr_rounds:
            for clr_round in active_clr_rounds:
                if sync == 'true':
                    # run it sync -> useful for payout / debugging
                    predict_clr(
                        save_to_db=True,
                        from_date=timezone.now(),
                        clr_round=clr_round,
                        network=network,
                        what=what,
                    )
                else:
                    # runs it as celery task.
                    process_predict_clr(
                        save_to_db=True,
                        from_date=timezone.now(),
                        clr_round=clr_round,
                        network=network,
                        what=what,
                    )
        else:
            print("No active CLRs found")
