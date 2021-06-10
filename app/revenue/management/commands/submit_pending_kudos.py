'''
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

'''

import logging
import time
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import requests
from dashboard.utils import has_tx_mined
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from kudos.models import KudosTransfer
from kudos.views import redeem_bulk_coupon

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

class Command(BaseCommand):

    help = 'submits pending kudos, when the gas prices are low enough to do so'

    def handle(self, *args, **options):
        network = 'mainnet'
        if int(recommend_min_gas_price_to_confirm_in_time(1)) > 10:
            return
        kts = KudosTransfer.objects.not_submitted().filter(network='mainnet')
        for kt in kts:
            redemption = kt.bulk_transfer_redemptions.first()
            address = kt.receive_address
            profile = kt.recipient_profile
            coupon = redemption.coupon
            ip_address = redemption.ip_address
            tx_id, _, _ = redeem_bulk_coupon(coupon, profile, address, ip_address, exit_after_sending_tx=True)
            print(tx_id)
            while not has_tx_mined(tx_id, network):
                time.sleep(1)

            kt.txid = txid
            kt.receive_txid = txid
            kt.receive_tx_status = 'success'
            kt.tx_status = 'success'
            kt.received_on = timezone.now()
            kt.tx_time = timezone.now()
            kt.save()
