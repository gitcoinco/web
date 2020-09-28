"""Define the mint all kudos management command.

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

import logging
import warnings

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.utils import all_sendcryptoasset_models

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Command(BaseCommand):

    help = 'gets the tx status of all SendCryptoAssets'

    # processes grant contributions
    def process_grants_contribs(self):
        from grants.models import Contribution
        contributions = Contribution.objects.filter(tx_cleared=False)
        for contrib in contributions:
            contrib.tx_id
            contrib.update_tx_status()
            print(f"syncing contrib / {contrib.pk} / {contrib.subscription.network}")
            contrib.save()

        # retry contributions that failed
        created_before = timezone.now()-timezone.timedelta(hours=12)
        created_after = timezone.now()-timezone.timedelta(hours=1)
        contributions = Contribution.objects.filter(created_on__gt=created_before, created_on__lt=created_after, tx_cleared=True, success=False)
        for contrib in contributions:
            contrib.update_tx_status()
            contrib.save()

    # processes all crypto assets
    def process_acm(self):
        non_terminal_states = ['pending', 'na', 'unknown']
        for obj_type in all_sendcryptoasset_models():
            sent_txs = obj_type.objects.filter(tx_status__in=non_terminal_states).exclude(txid='').exclude(txid='pending_celery')
            receive_txs = obj_type.objects.filter(receive_tx_status__in=non_terminal_states).exclude(txid='').exclude(receive_txid='').exclude(receive_txid='pending_celery')
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
