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
from django.utils import timezone

from dashboard.models import Tip
from dashboard.utils import get_web3
from kudos.models import KudosTransfer

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_tx_status(txid, network, created_on):
    try:
        web3 = get_web3(network)
        tx = web3.eth.getTransactionReceipt(txid)
        if not tx:
            drop_dead_date = created_on + timezone.timedelta(days=3)
            if timezone.now() > drop_dead_date:
                return 'dropped'
            else:
                return 'pending'
        elif tx.status == 1:
            return 'success'
        elif tx.status == 0:
            return 'error'
        return 'unknown'
    except:
        return 'unknown'


class Command(BaseCommand):

    help = 'gets the tx status of all SendCryptoAssets'

    def handle(self, *args, **options):
        non_terminal_states = ['pending', 'na', 'unknown']
        for obj_type in [Tip, KudosTransfer]:
            sent_txs = obj_type.objects.filter(tx_status__in=non_terminal_states).send_success()
            receive_txs = obj_type.objects.filter(receive_tx_status__in=non_terminal_states).send_success().exclude(receive_txid='')
            objects = (sent_txs | receive_txs).distinct('id')
            for obj in objects:
                print(f"syncing {obj_type} / {obj.pk} / {obj.network}")
                if obj.tx_status in non_terminal_states:
                    obj.tx_status = get_tx_status(obj.txid, obj.network, obj.created_on)
                    print(f" - updated {obj.txid} to {obj.tx_status}")
                if obj.receive_tx_status in non_terminal_states:
                    obj.receive_tx_status = get_tx_status(obj.receive_txid, obj.network, obj.created_on)
                    print(f" - updated {obj.receive_txid} to {obj.receive_tx_status}")
                obj.save()
