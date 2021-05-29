# -*- coding: utf-8 -*-
"""

For any Subscription objects that have a contributor address of "N/A", put in the transaction's from address

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

from django.core.management.base import BaseCommand

import requests
from dashboard.utils import get_web3
from grants.models import Subscription
from web3 import Web3


class Command(BaseCommand):

    help = "Inserts missing subscriptions and contributions into the database"

    def add_arguments(self, parser):
        parser.add_argument('network',
            default='mainnet',
            type=str,
            help="Network can be mainnet or rinkeby"
        )

    def handle(self, *args, **options):
        # Parse inputs / setup
        network = options['network']
        w3 = get_web3(network)
        if network != 'mainnet' and network != 'rinkeby':
            raise Exception('Invalid network: Must be mainnet or rinkeby')

        # Get array of subscriptions with N/A contributor address
        bad_subscriptions = Subscription.objects.filter(contributor_address="N/A")

        # For each one, find the from address and use that to replace the N/A
        for subscription in bad_subscriptions:
            try:
                tx_hash = subscription.split_tx_id
                if tx_hash[0:8].lower() == 'sync-tx:':
                    # zkSync transaction, so use zkSync's API: https://zksync.io/api/v0.1.html#transaction-details
                    tx_hash = tx_hash.replace('sync-tx:', '0x')
                    base_url = 'https://rinkeby-api.zksync.io/api/v0.1' if network == 'rinkeby' else 'https://api.zksync.io/api/v0.1'
                    r = requests.get(f"{base_url}/transactions_all/{tx_hash}")
                    r.raise_for_status()
                    tx_data = r.json() # zkSync transaction data
                    if not tx_data:
                        print(f'Skipping, zkSync receipt not found for transaction {subscription.split_tx_id}')
                        continue
                    from_address = tx_data['from']
                elif len(tx_hash) == 66:
                    # Standard L1 transaction
                    receipt = w3.eth.getTransactionReceipt(tx_hash)
                    if not receipt:
                        print(f'Skipping, L1 receipt not found for transaction {subscription.split_tx_id}')
                        continue
                    from_address = receipt['from']
                else:
                    print(f'Skipping unknown transaction hash format, could not parse {subscription.split_tx_id}')
                    continue

                if not from_address:
                    print(f'Skipping invalid from address {from_address} for transaction hash {subscription.split_tx_id}')

                # Note: This approach does not guarantee the correct contributor address. Because we are using the sender
                # of the transaction as the contributor, we get the wrong address for users with wallet's that use
                # a relayer or meta-transactions, such as Argent. In those cases, the relayer address is incorrectly
                # listed as the sender. A more robust approach would take a non-trivial amount of work since it
                # requires recognizing relayed transaction and parsing them to find the wallet address, and there's no
                # universal standard for relayed transaction format
                from_address = Web3.toChecksumAddress(from_address)
                subscription.contributor_address = from_address
                subscription.save()
            except Exception as e:
                print(f'Skipping: Error when fetching from_address for transaction hash {subscription.split_tx_id}')
                print(e)
                print("\n")
