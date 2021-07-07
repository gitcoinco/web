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

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from grants.models import Contribution
from grants.tasks import update_grant_metadata
from grants.utils import sync_payout


class Command(BaseCommand):

    help = 'checks if pending contributions are confirmed on the tokens explorer'


    def handle(self, *args, **options):
        pending_contribution = Contribution.objects.filter(
            tx_cleared = False
        )

        # Auto expire pending transactions
        timeout_period = timezone.now() - timedelta(minutes=60)

        tenants = ['ZCASH', 'ZIL', 'CELO', 'POLKADOT', 'HARMONY', 'BINANCE', 'KUSAMA', 'RSK', 'ALGORAND']

        for tenant in tenants:
            tenant_pending_contributions = pending_contribution.filter(subscription__tenant=tenant)
            contrib_to_be_expired = tenant_pending_contributions.filter(created_on__lt=timeout_period)
            contrib_to_be_expired.update(
                success=False,
                tx_cleared=False
            )
            for contribution in contrib_to_be_expired:
                update_grant_metadata.delay(contribution.subscription.grant.pk)

            for contribution in tenant_pending_contributions.all():
                sync_payout(contribution)
