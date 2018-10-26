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
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from kudos.utils import KudosContract

warnings.simplefilter("ignore", category=DeprecationWarning)
warnings.simplefilter("ignore", category=UserWarning)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'listens for kudos token changes '

    def add_arguments(self, parser):
        parser.add_argument('network', type=str, choices=['localhost', 'rinkeby', 'mainnet'],
                            help='ethereum network to use')
        parser.add_argument('syncmethod', type=str, choices=['filter', 'block', 'opensea'],
                            help='sync method to use')
        parser.add_argument('-i', '--interval', default=1, type=int,
                            help='how often to poll for updates')

    def opensea_listener(self, kudos_contract, interval):
        if kudos_contract.network == 'rinkeby':
            url = 'https://rinkeby-api.opensea.io/api/v1/events'
        elif kudos_contract.network == 'mainnet':
            url = 'https://api.opensea.io/api/v1/events'
        else:
            raise RuntimeError('The Open Sea API is only supported for contracts on rinkeby and mainnet.')

        # Event API
        payload = dict(
            asset_contract_address=kudos_contract.address,
            event_type='transfer',
        )
        headers = {'X-API-KEY': settings.OPENSEA_API_KEY}
        asset_token_id = 0
        transaction_hash = 0
        while True:
            cache = (asset_token_id, transaction_hash)
            r = requests.get(url, params=payload, headers=headers)
            r.raise_for_status()

            asset_token_id = r.json()['asset_events'][0]['asset']['token_id']
            transaction_hash = r.json()['asset_events'][0]['transaction']['transaction_hash']
            # If the result is the same as last time, don't re-sync the database
            if cache == (asset_token_id, transaction_hash):
                continue
            logger.info(f'token_id: {asset_token_id}, txid: {transaction_hash}')
            kudos_contract.sync_db(kudos_id=int(asset_token_id), txid=transaction_hash)
            time.sleep(interval)

    def filter_listener(self, kudos_contract, interval):

        event_filter = kudos_contract._contract.events.Transfer.createFilter(fromBlock='latest')

        while True:
            for event in event_filter.get_new_entries():
                msg = dict(
                    blockNumber=event.blockNumber,
                    _tokenId=event.args._tokenId,
                    transactionHash=event.transactionHash.hex()
                )
                logger.info(f'Transfer event:  {msg}')
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f'Raw Transfer event: {event}')
                kudos_contract._w3.eth.waitForTransactionReceipt(msg['transactionHash'])
                logger.debug(f"Tx hash: {msg['transactionHash']}")
                if kudos_contract.network == 'localhost':
                    time.sleep(5)
                kudos_contract.sync_db(kudos_id=msg['_tokenId'], txid=msg['transactionHash'])
            time.sleep(interval)

    def block_listener(self, kudos_contract, interval):
        block = 'latest'
        last_block_hash = None
        while True:
            # wait for a new block
            block = kudos_contract._w3.eth.getBlock('latest')
            block_hash = block['hash']
            block_number = block['number']

            if last_block_hash == block_hash:
                time.sleep(interval)
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
                data = tx['input']
                method_id = data[:10]
                logger.info(f'method_id:  {method_id}')

                # Check if its a Clone or a Mint method.
                # NOTE:  These method_id's will change if a new contract is deployed.
                #        You will have to watch the logs to figure out the new method_id's.
                if method_id == '0xed74de9d' or method_id == '0xbb7fde71':
                    kudos_contract._w3.eth.waitForTransactionReceipt(tx['hash'])
                    kudos_id = kudos_contract._contract.functions.getLatestId().call()
                    if kudos_contract.network == 'localhost':
                        # On localhost, the tx syncs faster than the website loads
                        time.sleep(3)
                    kudos_contract.sync_db(kudos_id=kudos_id, txid=tx['hash'].hex())

            last_block_hash = block_hash

    def handle(self, *args, **options):
        network = options['network']
        syncmethod = options['syncmethod']
        interval = options['interval']

        kudos_contract = KudosContract(network)

        logger.info('Listening for new Kudos events...')
        if syncmethod == 'filter':
            kudos_contract = KudosContract(network, sockets=True)
            self.filter_listener(kudos_contract, interval)
        elif syncmethod == 'block':
            self.block_listener(kudos_contract, interval)
        elif syncmethod == 'opensea':
            self.opensea_listener(kudos_contract, interval)
