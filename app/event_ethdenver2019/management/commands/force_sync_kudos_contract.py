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
from event_ethdenver2019.models import KudosContractSync

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

# from web3.middleware import local_filter_middleware

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):

    help = 'sync eth-addr-kudos-link table'

    def add_arguments(self, parser):
        parser.add_argument('network', type=str, choices=['localhost','rinkeby', 'mainnet'],
                            help='ethereum network to use')

    def id_sync(self, kudos_contract, end_id):
        kudos_enum = 0
        more_kudos = True

        while more_kudos:

            result = kudos_contract._contract.functions.getKudosById(kudos_enum).call()
            kudos_enum += 1

            if kudos_enum > end_id:
                more_kudos = False

    def handle(self, *args, **options):
        # config
        network = options['network']
        kudos_contract = KudosContract(network, sockets=True)

        # Handle the filter sync
        highest_kudosId = kudos_contract._contract.functions.getLatestId().call()
        logger.info(f'syncing global kudos contract, highest minted kudos id is {highest_kudosId}')
        id_sync(kudos_contract,0)
        return
