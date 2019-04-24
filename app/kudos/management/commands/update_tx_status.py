"""Define the mint all kudos management command.

Copyright (C) 2018 Gitcoin Core

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

import logging
import warnings

from django.core.management.base import BaseCommand

from dashboard.utils import all_sendcryptoasset_models

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Command(BaseCommand):

    help = 'gets the tx status of all SendCryptoAssets'

    def process_grants_contribs(self):
        from grants.models import Contribution
        for contrib in Contribution.objects.filter(tx_cleared=False):
            contrib.tx_id
            contrib.update_tx_status()
            print(f"syncing contrib / {contrib.pk} / {contrib.subscription.network}")
            contrib.save()

    def process_acm(self):
        non_terminal_states = ['pending', 'na', 'unknown']
        for obj_type in all_sendcryptoasset_models():
            sent_txs = obj_type.objects.filter(tx_status__in=non_terminal_states).exclude(txid='')
            receive_txs = obj_type.objects.filter(receive_tx_status__in=non_terminal_states).exclude(txid='').exclude(receive_txid='')
            objects = (sent_txs | receive_txs).distinct('id')
            for obj in objects:
                print(f"syncing {obj_type} / {obj.pk} / {obj.network}")
                if obj.tx_status in non_terminal_states:
                    obj.update_tx_status()
                    print(f" - updated {obj.txid} to {obj.tx_status}")
                if obj.receive_tx_status in non_terminal_states:
                    obj.update_receive_tx_status()
                    print(f" - updated {obj.receive_txid} to {obj.receive_tx_status}")
                obj.save()

    def handle(self, *args, **options):
        self.process_grants_contribs()
        self.process_acm()
