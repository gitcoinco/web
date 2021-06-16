"""
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

from ptokens.models import PTokenEvent, PurchasePToken, RedemptionToken

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Command(BaseCommand):
    help = 'gets the tx status of Time Tokens'

    def process_ptokens(self):
        non_terminal_states = ['pending', 'na', 'unknown']
        from ptokens.models import PersonalToken
        for ptoken in PersonalToken.objects.filter(tx_status__in=non_terminal_states):
            ptoken.update_tx_status()
            print(f"syncing ptoken / {ptoken.pk} / {ptoken.network}")
            ptoken.save()

        for purchase in PurchasePToken.objects.filter(tx_status__in=non_terminal_states):
            purchase.update_tx_status()
            print(f"syncing purchase / {purchase.pk} / {purchase.network}")
            purchase.save()

        for redemption in RedemptionToken.objects.filter(tx_status__in=non_terminal_states):
            redemption.update_tx_status()
            print(f"syncing ptoken / {redemption.pk} / {redemption.network}")
            redemption.save()

        for event in PTokenEvent.objects.filter(tx_status__in=non_terminal_states):
            event.update_tx_status()
            print(f"syncing event ptoken / {event.pk} / {event.network}")
            event.save()

    def handle(self, *args, **options):
        self.process_ptokens()
