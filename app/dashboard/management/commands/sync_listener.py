'''
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

'''

import logging
import time

from django.core.management.base import BaseCommand

from dashboard.utils import (
    Web3, get_bounty, get_web3, getBountyContract, getStandardBountiesContractAddresss, web3_process_bounty,
)

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3.RequestManager").setLevel(logging.WARNING)
logging.getLogger("web3.providers.WebsocketProvider").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)


EVENTS = [
    'BountyIssued',
    'BountyActivated',
    'ContributionAdded',
    'BountyFulfilled',
    'FulfillmentAccepted',
    'BountyChanged',
    'BountyKilled',
    'PayoutIncreased',
    'FulfillmentUpdated',
    'DeadlineExtended',
    'IssuerTransferred'
]


def process_entry(entry, network):
    event = entry.event
    tx_hash = Web3.toHex(entry.transactionHash)
    bounty_id = entry.args.get('bountyId') or entry.args.get('_bountyId')
    subdomain = ''
    if network != 'mainnet':
        subdomain = f'{network}.'
    print(f'{event} {bounty_id} https://{subdomain}etherscan.io/tx/{tx_hash}')
    print(entry.args)

    try:
        bounty = get_bounty(bounty_id, network)
        did_change, old_bounty, new_bounty = web3_process_bounty(bounty)
        tx_hashes = new_bounty.tx_hashes
        hashes_list = tx_hashes.get(event, [])
        if tx_hash not in hashes_list:
            hashes_list.append(tx_hash)
            tx_hashes[event] = hashes_list
            new_bounty.save()
        return True
    except Exception as e:
        print(e)
        return False

    return True


class Command(BaseCommand):
    help = 'listens for bounty changes '

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)
        parser.add_argument('block', default=-1, type=int)

    def handle(self, *args, **options):
        # config
        network = options['network']
        block = options['block']
        if block == -1:
            block = 'latest'

        # setup
        web3 = get_web3(network)
        contract = getBountyContract(network)
        # contract.eventFilter('FulfillmentAccepted', { 'fromBlock': block })
        event_listeners = {}

        while True:
            for event_name in EVENTS:
                bootstrap = False
                listener, last_block = event_listeners.get(event_name, (None, None))

                if not last_block:
                    last_block = block

                if not listener:
                    listener = contract.events[event_name].createFilter(fromBlock=last_block)
                    # bootstrap with get_all_entries
                    # because get_new_entries does not return events from 'old' transactions
                    bootstrap = True

                try:
                    if bootstrap:
                        entries = listener.get_all_entries()
                    else:
                        entries = listener.get_new_entries()

                    print(f'processing {event_name} bootstrap={bootstrap} len={len(entries)} last_block={last_block}')
                    for entry in entries:
                        process_entry(entry, network)
                        last_block = entry.blockNumber
                    print(f'last_block={last_block}')
                except Exception as e:
                    print(f'{event_name} : {e}')
                    listener = None

                event_listeners[event_name] = (listener, last_block)
                time.sleep(1)
