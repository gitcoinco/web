'''
    Copyright (C) 2019 Gitcoin Core

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
from django.db.models import Max

import requests
import web3
from kudos.models import Token
from kudos.utils import KudosContract
from python_http_client.exceptions import HTTPError

# from web3.middleware import local_filter_middleware

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):

    help = 'syncs database with kudos on the blockchain'

    def add_arguments(self, parser):
        parser.add_argument('network', type=str, choices=['localhost', 'rinkeby', 'mainnet'],
                            help='ethereum network to use')
        parser.add_argument('syncmethod', type=str, choices=['filter', 'id', 'block', 'opensea'],
                            help='sync method to use')
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('-s', '--start', type=str,
                           help='kudos_id to or kudos block to start syncing at.  Lowest kudos_id is 1.\
                           Options for block are: block number (int), "earliest", or "latest"')
        group.add_argument('-r', '--rewind', type=int,
                           help='Sync the lastest <rewind> Kudos Ids or block transactions.')
        group.add_argument('--catchup', action='store_true',
                           help='Attempt to sync up the newest kudos to the database')

    def opensea_sync(self, kudos_contract, start_id):
        if kudos_contract.network == 'rinkeby':
            url = 'https://rinkeby-api.opensea.io/api/v1/events'
        elif kudos_contract.network == 'mainnet':
            url = 'https://api.opensea.io/api/v1/events'
        else:
            raise RuntimeError('The Open Sea API is only supported for contracts on rinkeby and mainnet.')

        end_id = kudos_contract._contract.functions.getLatestId().call()
        token_ids = range(start_id, end_id + 1)

        headers = {'X-API-KEY': settings.OPENSEA_API_KEY}

        # Event API
        for token_id in token_ids:
            payload = {'asset_contract_address': kudos_contract.address, 'token_id': token_id}
            r = requests.get(url, params=payload, headers=headers)
            r.raise_for_status()
            try:
                asset_token_id = r.json()['asset_events'][0]['asset']['token_id']
                transaction_hash = r.json()['asset_events'][0]['transaction']['transaction_hash']
                logger.info(f'token_id: {asset_token_id}, txid: {transaction_hash}')
                kudos_contract.sync_db(kudos_id=int(asset_token_id), txid=transaction_hash)
            except IndexError:
                continue
            except HTTPError:
                logger.debug(e)
            except Exception as e:
                logger.error(e)

    def filter_sync(self, kudos_contract, fromBlock):
        event_filter = kudos_contract._contract.events.Transfer.createFilter(fromBlock=fromBlock)
        logger.info(event_filter)
        for event in event_filter.get_all_entries():
            msg = dict(
                blockNumber=event.blockNumber,
                _tokenId=event.args._tokenId,
                transactionHash=event.transactionHash.hex()
            )
            logger.info(f'Transfer event:  {msg}')
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'Raw Transfer event: {event}')
            kudos_contract.sync_db(kudos_id=event.args._tokenId, txid=event.transactionHash.hex())

    def id_sync(self, kudos_contract, start_id):
        # iterate through all the kudos
        # kudos_contract.reconcile_db(start_id=start_id)
        end_id = kudos_contract._contract.functions.getLatestId().call()
        kudos_enum = start_id
        more_kudos = True

        while more_kudos:
            kudos_contract.sync_db_without_txid(kudos_id=kudos_enum)
            kudos_enum += 1

            if kudos_enum > end_id:
                more_kudos = False

    def block_sync(self, kudos_contract, fromBlock):
        raise NotImplementedError('block_sync does not work properly')
        block = fromBlock
        last_block_number = kudos_contract._w3.eth.getBlock('latest')['number']
        # for block_num in range(block, last_block_number + 1)
        while True:
            # wait for a new block
            block = kudos_contract._w3.eth.getBlock(block)
            if not block:
                break
            block_hash = block['hash']
            block_number = block['number']

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

                # Check if its a Clone or cloneAndTransfer function call
                valid_method_ids = ['0xed74de9d']
                if method_id in valid_method_ids:
                    kudos_contract._w3.eth.waitForTransactionReceipt(tx['hash'])
                    kudos_id = kudos_contract._contract.functions.getLatestId().call()
                    if kudos_contract.network == 'localhost':
                        # On localhost, the tx syncs faster than the website loads
                        time.sleep(3)
                    kudos_contract.sync_db(kudos_id=kudos_id, txid=tx['hash'].hex())

            block = block_number + 1
            if block == last_block_number:
                break

    def handle(self, *args, **options):
        # config
        network = options['network']
        syncmethod = options['syncmethod']

        start = options['start']
        rewind = options['rewind']
        catchup = options['catchup']

        kudos_contract = KudosContract(network, sockets=True)
        # kudos_contract._w3.middleware_stack.add(local_filter_middleware())

        # Handle the filter sync
        if syncmethod == 'filter':
            if start:
                if start.isdigit():
                    raise RuntimeError('This option is unstable if not on web3py 4.7.2.  May crash testrpc.')
                if start in ['earliest', 'latest']:
                    fromBlock = start
                else:
                    raise ValueError('--fromBlock must be "earliest", or "latest"')
            elif rewind:
                if web3.__version__ != '4.7.2':
                    raise RuntimeError('This option is unstable if not on web3py 4.7.2.  May crash testrpc.')
                fromBlock = kudos_contract._w3.eth.getBlock('latest')['number'] - rewind
            elif catchup:
                raise ValueError('--catchup option is not valid for filter syncing')

            logger.info(fromBlock)
            self.filter_sync(kudos_contract, fromBlock)
            return

        # Handle the block sync
        if syncmethod == 'block':
            if start:
                if start.isdigit():
                    fromBlock = start
                elif start in ['earliest', 'latest']:
                    fromBlock = start
                else:
                    raise ValueError('--fromBlock must be "earliest", or "latest"')
            elif rewind:
                fromBlock = kudos_contract._w3.eth.getBlock('latest')['number'] - rewind
            elif catchup:
                raise ValueError('--catchup option is not valid for block syncing')

            logger.info(fromBlock)
            self.block_sync(kudos_contract, fromBlock)
            return

        # Handle the other sync methods
        if start:
            start_id = start
        elif rewind:
            start_id = kudos_contract._contract.functions.getLatestId().call() - rewind
        elif catchup:
            start_id = Token.objects.filter(contract__address=kudos_contract.address).aggregate(
                Max('token_id'))['token_id__max']

        if start_id is None or isinstance(start_id, int) and start_id < 0:
            start_id = 1

        if syncmethod == 'id':
            self.id_sync(kudos_contract, int(start_id))
        elif syncmethod == 'opensea':
            self.opensea_sync(kudos_contract, int(start_id))
        return
