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
from grants.models import Contribution, Grant
from grants.views import clr_active
from marketing.mails import warn_subscription_failed


class Command(BaseCommand):

    help = 'calculate CLR estimates for all grants'

    def add_arguments(self, parser):

        parser.add_argument('clr_type', type=str, default='tech', choices=['tech', 'media', 'health'])
        parser.add_argument('network', type=str, default='mainnet', choices=['rinkeby', 'mainnet'])

    def handle(self, *args, **options):
        if not clr_active:
            print('CLR round is not active according to grants.views.clr_active, so cowardly refusing to spend the CPU cycles + exiting instead')
            return

        clr_type = options['clr_type']
        network = options['network']
        mechanism = 'profile' if clr_type != 'health' else 'originated_address'

        predict_clr(
            save_to_db=True,
            from_date=timezone.now(),
            clr_type=clr_type,
            network=network,
            mechanism=mechanism,
        )

        print("finished CLR estimates")

        # TOTAL GRANT
        # grants = Grant.objects.filter(network=network, hidden=False, active=True, grant_type=clr_type, link_to_new_grant=None)
        # total_clr_distributed = 0
        # for grant in grants:
        #     total_clr_distributed += grant.clr_prediction_curve[0][1]

        # print(f'Total CLR allocated for {clr_type} - {total_clr_distributed}')
