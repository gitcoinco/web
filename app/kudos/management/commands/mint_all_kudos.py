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
import sys
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.helpers import UnsupportedSchemaException
from django.core.management import call_command
from kudos.utils import mint_kudos_on_web3_and_db, KudosContract

import oyaml as yaml

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
default_start_id = 0 if not settings.DEBUG else 402


class Command(BaseCommand):

    help = 'mints the initial kudos gen0 set'

    def add_arguments(self, parser):
        parser.add_argument('network', default='localhost', type=str)
        parser.add_argument('yaml_file', help='absolute path to kudos.yaml file', type=str)
        parser.add_argument('--account', help='public account address to use for transaction', type=str)
        parser.add_argument('--private_key', help='private key for signing transactions', type=str)

    def handle(self, *args, **options):
        # config
        network = options['network']
        account = options['account']
        private_key = options['private_key']
        # logger.info(options)
        hour = datetime.datetime.now().hour
        day = datetime.datetime.now().day
        month = datetime.datetime.now().month

        yaml_file = options['yaml_file']

        with open(yaml_file) as f:
            all_kudos = yaml.load(f)

        for kudos in all_kudos:
            image_name = kudos.get('image')
            if image_name:
                image_path = 'v2/images/kudos/' + image_name
                # image_path = yaml_file.replace('kudos.yaml', 'images/') + image_name
                # api = getIPFS()
                # image_ipfs = api.add(image_path)
                # image_hash = image_ipfs['Hash']
            else:
                image_path = ''

            args = (kudos['name'], kudos['description'], kudos['rarity'], kudos['priceFinney'],
                    kudos['numClonesAllowed'], kudos['tags'], image_path,
                    )

            logger.info(args)

            # try:
            #     mint_kudos_on_web3_and_db(network, private_key, *args)
            # except ValueError as e:
            #     logger.warning(e)

            try:
                # TODO:  Move the kudos_contract instantiation outside of the for loop
                kudos_contract = KudosContract(network=network, account=account, private_key=private_key)
                kudos_contract.mint(*args)
            except IndexError as e:
                logger.warning(e)
