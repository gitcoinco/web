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

from dashboard.utils import get_web3
from kudos.utils import KudosContract

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'listens for kudos token changes '

    def add_arguments(self, parser):
        parser.add_argument('--network', default='localhost', type=str)
        parser.add_argument('--usefilter', default=False, type=bool)

    def filter_listener(self, kudos_contract):

        event_filter = kudos_contract._contract.events.Transfer.createFilter(fromBlock='latest')
        while True:
            for event in event_filter.get_new_entries():
                msg = dict(blockNumber=event.blockNumber,
                           _tokenId=event.args._tokenId,
                           transactionHash=event.transactionHash.hex()
                           )
                logger.info(f'Transfer event:  {msg}')
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'Raw Transfer event: {event}')
                kudos_contract._w3.eth.waitForTransactionReceipt(msg['transactionHash'])
                logger.debug(f"Tx hash: {msg['transactionHash']}")
                kudos_contract.sync_db(kudos_id=msg['_tokenId'], txid=msg['transactionHash'])
            time.sleep(1)

    def block_listener(self, kudos_contract):
        block = 'latest'
        last_block_hash = None
        while True:
            # wait for a new block
            # logger.info(f'block: {block}')
            block = kudos_contract._w3.eth.getBlock('latest')
            block_hash = block['hash']
            block_number = block['number']

            # logger.info(f'last_block_hash: {last_block_hash}')
            # logger.info(f'block_hash: {block_hash}')
            if last_block_hash == block_hash:
                time.sleep(1)
                continue

            logger.info('got new block %s' % kudos_contract._w3.toHex(block_hash))
            logger.info(f'block id: {block_number}')

            # get txs
            transactions = block['transactions']
            for tx in transactions:
                tx = kudos_contract._w3.eth.getTransaction(tx)
                if not tx or tx['to'] != kudos_contract.address:
                    continue

                logger.info('found a kudos tx')
                # logger.info(dir(tx))
                # logger.info(tx.keys())
                data = tx['input']
                method_id = data[:10]
                logger.info(f'method_id:  {method_id}')

                # Check if its a Clone or cloneAndTransfer function call
                if method_id == '0xdaa6eb1d' or method_id == '0x8a94e433':
                    kudos_contract._w3.eth.waitForTransactionReceipt(tx['hash'])
                    kudos_id = kudos_contract._contract.functions.totalSupply().call()
                    kudos_contract.sync_db(kudos_id=kudos_id, txid=tx['hash'].hex())
                    # # Get the kudos_id of the newly cloned Kudos
                    # kudos_id = kudos_contract.functions.totalSupply().call()
                    # # Update the database with the newly cloned Kudos
                    # update_kudos_db(kudos_id, network)
                    # # Find the name of the Kudos that was cloned
                    # kudos = get_kudos_from_web3(kudos_id, network)
                    # kudos_map = get_kudos_map(kudos)
                    # # Find the ID of the Gen0 Kudos that was cloned
                    # gen0_id = get_gen0_id_from_web3(kudos_map['name'], network)
                    # # Update the Gen0 Kudos in the database
                    # update_kudos_db(gen0_id, network)

            last_block_hash = block_hash

    def handle(self, *args, **options):
        # setup
        network = options['network']
        usefilter = options['usefilter']

        kudos_contract = KudosContract(network=network)
        # w3 = get_web3(network)
        # contract_address = getKudosContractAddress(network)
        # logger.info(f'Contract address: {contract_address}')

        # kudos_contract = getKudosContract(network)

        # logger.info(dir(kudos_contract))

        if usefilter:
            self.filter_listener(kudos_contract)
        else:
            self.block_listener(kudos_contract)
