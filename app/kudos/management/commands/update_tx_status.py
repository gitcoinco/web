"""Define the mint all kudos management command.

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
    def add_arguments(self, parser):
        parser.add_argument(
            'hours',
            default=12,
            type=int,
            help="How many hours back should we look"
        )

    # processes grant contributions
    def process_grants_contribs(self, hours):
        from grants.models import Contribution
        created_gt = timezone.now()-timezone.timedelta(hours=hours)
        created_lt = timezone.now()-timezone.timedelta(hours=0)

        contributions = Contribution.objects.filter(created_on__gt=created_gt, created_on__lt=created_lt, tx_cleared=False).order_by('-pk')
        contributions_retry = Contribution.objects.filter(created_on__gt=created_gt, created_on__lt=created_lt, tx_cleared=True, success=False)

        print(f"got {contributions.count()} grants contributions to try , {contributions_retry.count()} to retry")
        for contrib in contributions:
            contrib.tx_id
            contrib.update_tx_status()
            print(f"- syncing contrib / {contrib.pk} / {contrib.subscription.network}")
            contrib.save()

        # retry contributions that failed
        for contrib in contributions_retry:
            contrib.update_tx_status()
            contrib.save()

    # processes all crypto assets
    def process_acm(self, hours):
        created_gt = timezone.now()-timezone.timedelta(hours=hours)
        created_lt = timezone.now()-timezone.timedelta(hours=0)
        non_terminal_states = ['pending', 'na', 'unknown']
        for obj_type in all_sendcryptoasset_models():
            sent_txs = obj_type.objects.filter(created_on__gt=created_gt, created_on__lt=created_lt, tx_status__in=non_terminal_states).exclude(txid='').exclude(txid='pending_celery')
            receive_txs = obj_type.objects.filter(created_on__gt=created_gt, created_on__lt=created_lt, receive_tx_status__in=non_terminal_states).exclude(txid='').exclude(receive_txid='').exclude(receive_txid='pending_celery')
            objects = (sent_txs | receive_txs).distinct('id')
            print(f"got {objects.count()} {obj_type} to try")
            for obj in objects:
                print(f"- syncing {obj_type} / {obj.pk} / {obj.network}")
                if obj.tx_status in non_terminal_states:
                    obj.update_tx_status()
                    print(f" -- updated {obj.txid} to {obj.tx_status}")
                if obj.receive_tx_status in non_terminal_states:
                    obj.update_receive_tx_status()
                    print(f" -- updated {obj.receive_txid} to {obj.receive_tx_status}")
                obj.save()

    def handle(self, *args, **options):
        hours = options['hours']
        self.process_grants_contribs(hours)
        self.process_acm(hours)
