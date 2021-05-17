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

from django.core.management.base import BaseCommand

from dashboard.utils import (
    get_bounty, get_web3, getBountyContract, getStandardBountiesContractAddresss, web3_process_bounty,
)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def process_bounty(bounty_id, network):
    bounty = get_bounty(bounty_id, network)
    return web3_process_bounty(bounty)


class Command(BaseCommand):
    help = 'listens for bounty changes '

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)

    def handle(self, *args, **options):
        # config
        block = 'latest'

        # setup
        network = options['network']
        web3 = get_web3(network)
        contract_address = getStandardBountiesContractAddresss(network)
        contract = getBountyContract(network)
        last_block_hash = None

        while True:
            # wait for a new block
            block = web3.eth.getBlock('latest')
            block_hash = block['hash']

            if last_block_hash == block_hash:
                time.sleep(1)
                continue

            print('got new block %s' % web3.toHex(block_hash))

            # get txs
            transactions = block['transactions']
            for tx in transactions:
                tx = web3.eth.getTransaction(tx)
                if not tx or tx['to'] != contract_address:
                    continue

                print('found a stdbounties tx')
                data = tx['input']
                method_id = data[:10]
                if method_id == '0x7e9e511d':
                    # issueAndActivateBounty
                    bounty_id = contract.functions.getNumBounties().call() - 1
                else:
                    # any other method
                    bounty_id = int(data[10:74], 16)
                print('process_bounty %d' % bounty_id)
                process_bounty(bounty_id, network)
                print('done process_bounty %d' % bounty_id)

            last_block_hash = block_hash
