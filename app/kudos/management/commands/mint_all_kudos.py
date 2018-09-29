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

from django.conf import settings
from django.core.management.base import BaseCommand

from kudos.utils import KudosContract

from web3.exceptions import BadFunctionCallOutput

import oyaml as yaml
import ipfsapi

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

default_start_id = 0 if not settings.DEBUG else 402

logger = logging.getLogger(__name__)
formatter = '%(levelname)s:%(name)s.%(funcName)s:%(message)s'
logging.basicConfig(level=logging.INFO)


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

        kudos_contract = KudosContract(network=network)

        yaml_file = options['yaml_file']
        # ipfs = ipfsapi.connect(settings.IPFS_HOST)

        with open(yaml_file) as f:
            all_kudos = yaml.load(f)

        for kudos in all_kudos:
            image_name = kudos.get('image')
            if image_name:
                image_path = 'v2/images/kudos/' + image_name
            else:
                image_path = ''

            metadata = {
                'name': kudos['name'],
                'image': image_path,
                'description': kudos['description'],
                'external_url': 'https://gitcoin.co/kudos',  # Might want to link to the exact address
                'background_color': '00FFFF',
                'attributes': {
                    'tags': kudos['tags'],
                    'rarity': kudos['rarity'],
                }
            }

            tokenURI_url = kudos_contract.create_tokenURI_url(**metadata)

            args = (kudos['priceFinney'], kudos['numClonesAllowed'], tokenURI_url)

            kudos_contract.mint(*args, account=account, private_key=private_key)
