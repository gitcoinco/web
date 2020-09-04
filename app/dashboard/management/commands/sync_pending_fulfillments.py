'''
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

'''


from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import BountyFulfillment
from dashboard.utils import sync_payout


class Command(BaseCommand):

    help = 'checks if pending fulfillments are confirmed on the tokens explorer'

    def handle(self, *args, **options):
        pending_fulfillments = BountyFulfillment.objects.filter(
            payout_status='pending'
        )

        # web3 modal
        web3_modal_pending_fulfillments = pending_fulfillments.filter(payout_type='web3_modal')
        if web3_modal_pending_fulfillments:
            for fulfillment in web3_modal_pending_fulfillments.all():
                sync_payout(fulfillment)

        # polkadot extension
        polkadot_pending_fulfillments = pending_fulfillments.filter(payout_type='polkadot_ext')
        if polkadot_pending_fulfillments:
            for fulfillment in polkadot_pending_fulfillments.all():
                sync_payout(fulfillment)


        # QR
        qr_pending_fulfillments = pending_fulfillments.filter(payout_type='qr')
        if qr_pending_fulfillments:
            # Auto expire pending transactions
            timeout_period = timezone.now() - timedelta(minutes=20)
            qr_pending_fulfillments.filter(created_on__lt=timeout_period).update(payout_status='expired')

            fulfillments = qr_pending_fulfillments.filter(payout_status='pending')
            for fulfillment in fulfillments.all():
                sync_payout(fulfillment)
