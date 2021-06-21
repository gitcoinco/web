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

import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Earning, TransactionHistory
from dashboard.utils import get_tx_status_and_details
from economy.models import EncodeAnything


class Command(BaseCommand):

    help = 'pulls tx statuses and stores them in the DB to be queried later'

    def handle(self, *args, **options):
        earnings = Earning.objects.all().order_by('-pk')
        for earning in earnings:
            if earning.history.count():
                continue
            txid = earning.txid
            network = earning.network
            created_on = earning.created_on
            status, timestamp, tx = get_tx_status_and_details(txid, network, created_on)
            print(earning.pk, status)
            if status not in ['unknown', 'pending']:
                tx = tx if tx else {}
                TransactionHistory.objects.create(
                    earning=earning,
                    status=status,
                    payload=json.loads(json.dumps(dict(tx), cls=EncodeAnything)),
                    network=network,
                    txid=txid,
                    captured_at=timezone.now(),
                    )
