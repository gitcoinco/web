"""Define the burn kudos management command.

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
import time

from django.core.management.base import BaseCommand

from kudos.models import KudosTransfer
from kudos.tasks import redeem_bulk_kudos
from kudos.utils import KudosContract


class Command(BaseCommand):

    help = 'clone a kudos to an address'

    def add_arguments(self, parser):
        parser.add_argument('num_to_pull', type=int, help='num_to_pull')
        parser.add_argument('num_to_process', type=int, help='num_to_process')
        parser.add_argument('override_gas_price', type=int, help='override_gas_price (0 if none)')
        parser.add_argument('async', type=int, help='async')
        parser.add_argument('order_by', type=str, help='order_by')

    def handle(self, *args, **options):
        # config
        num_to_process = options['num_to_process']
        num_to_pull = options['num_to_pull']
        _async = options['async']
        override_gas_price = options['override_gas_price']
        order_by = options['order_by'].replace('_', '-')
        delay_if_gas_prices_gt_redeem = 200
        send_notif_email = True
        send_on_xdai = True
        gitcoin_owner_addr = '0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F'
        
        counter_processed = 0
        counter_pulled = 0
        start_time = int(time.time())

        kudos_transfers = KudosTransfer.objects.filter(txid='pending_celery', kudos_token_cloned_from__owner_address=gitcoin_owner_addr).order_by(order_by)
        for kt in kudos_transfers:
            counter_pulled += 1
            if counter_pulled < num_to_pull:
                run_time = max(1, int(time.time()) - start_time)
                avg_processing = round(counter_pulled / run_time, 1)
                print(f"({avg_processing}/s)")
                print(f"PULL - {counter_pulled}/{num_to_pull} - {counter_processed}/{num_to_process} - {kt}")
                counter_processed += 1
                print(f"PROCESS - {counter_pulled}/{num_to_pull} - {counter_processed}/{num_to_process} - {kt}")
                print(kt.admin_url)
                if counter_processed < num_to_process:
                    if send_on_xdai:
                        kt.network = 'xdai'
                        kt.kudos_token_cloned_from = kt.kudos_token_cloned_from.on_xdai
                        if not kt.kudos_token_cloned_from:
                            print("target token not found on xdai network :/")
                            continue
                        kt.save()
                    func = redeem_bulk_kudos.delay if _async else redeem_bulk_kudos
                    try:
                        func(kt.id, delay_if_gas_prices_gt_redeem=delay_if_gas_prices_gt_redeem, override_gas_price=override_gas_price, send_notif_email=send_notif_email, override_lock_timeout=1)
                        kt.update_tx_status()
                        kt.save()
                    except Exception as e:
                        print(e)
