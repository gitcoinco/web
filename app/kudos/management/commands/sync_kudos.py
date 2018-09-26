'''
    Copyright (C) 2017 Gitcoin Core

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

import datetime
import logging
import warnings

from django.core.management.base import BaseCommand

from kudos.utils import KudosContract

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):

    help = 'syncs database with kudos on the blockchain'

    def add_arguments(self, parser):
        parser.add_argument('--network', default='localhost', type=str,
                            help='Network such as "localhost", "ropsten", "mainnet"')
        parser.add_argument('--fromBlock', default='earliest', type=str,
                            help='This can be a block number (int), "earliest", or "latest"')

    def handle(self, *args, **options):
        # config
        network = options['network']
        fromBlock = options['fromBlock']
        try:
            fromBlock = int(fromBlock)
        except ValueError:
            acceptable = ['latest', 'earliest']
            if fromBlock not in acceptable:
                raise ValueError('--fromBlock must be block number (int), "earliest", or "latest"')
        logger.info(fromBlock)

        kudos_contract = KudosContract(network)
        event_filter = kudos_contract._contract.events.Transfer.createFilter(fromBlock=fromBlock)
        logger.info('test')
        logger.info(event_filter)
        for event in event_filter.get_all_entries():
            msg = dict(blockNumber=event.blockNumber,
                       _tokenId=event.args._tokenId,
                       transactionHash=event.transactionHash.hex()
                       )
            logger.info(f'Transfer event:  {msg}')
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f'Raw Transfer event: {event}')
            kudos_contract.sync_db(kudos_id=event.args._tokenId, txid=event.transactionHash.hex())

        # iterate through all the kudos
        # start_id = int(options['start_id'])
        # kudos_contract = KudosContract(network)
        # kudos_contract.reconcile_db(start_id=start_id)
        # more_kudos = True
        # while more_kudos:
        #     # pull and process each kudos
        #     # self.stdout.write(f"[{month}/{day} {hour}:00] Getting kudos {kudos_enum}")
        #     # kudos = get_kudos(kudos_enum, network)
        #     # self.stdout.write(f"[{month}/{day} {hour}:00] Processing kudos {kudos_enum}")
        #     # web3_process_kudos(kudos)
        #     if kudos_has_changed(kudos_enum, network):
        #         update_kudos_db(kudos_enum, network)

        #     kudos_enum += 1

        #     if kudos_enum > int(options['end_id']):
        #         more_kudos = False
