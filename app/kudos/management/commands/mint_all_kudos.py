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
import time

from django.conf import settings
from django.core.management.base import BaseCommand

from kudos.utils import KudosContract, humanize_name, computerize_name

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
        parser.add_argument('--skip_sync', action='store_true')
        parser.add_argument('--account', help='public account address to use for transaction', type=str)
        parser.add_argument('--private_key', help='private key for signing transactions', type=str)

    def handle(self, *args, **options):
        # config
        network = options['network']
        account = options['account']
        private_key = options['private_key']
        skip_sync = options['skip_sync']

        kudos_contract = KudosContract(network=network)

        yaml_file = options['yaml_file']
        # ipfs = ipfsapi.connect(settings.IPFS_HOST)

        with open(yaml_file) as f:
            all_kudos = yaml.load(f)

        for idx, kudos in enumerate(all_kudos):
            # Only mint new gen0 Kudos
            # if idx + 1 <= kudos_contract.getLatestKudosId():
            #     logger.warning(f'{kudos["name"]} already exists on the blockchain.  Not minting...')
            #     continue
            image_name = kudos.get('image')
            if image_name:
                # Support Open Sea
                if kudos_contract.network == 'rinkeby':
                    image_path = 'http://kudosdemo.gitcoin.co/static/v2/images/kudos/' + image_name
                else:
                    image_path = 'v2/images/kudos/' + image_name
            else:
                image_path = ''

            attributes = []
            # "trait_type": "investor_experience",
            # "value": 20,
            # "display_type": "boost_number",
            # "max_value": 100
            rarity = {
                "trait_type": "rarity",
                "value": kudos['rarity'],
                "max_value": 100
            }
            attributes.append(rarity)
            tags = list({tag.strip() for tag in kudos['tags'].split(',')})
            # append tags
            if kudos['rarity'] > 98:
                tags.append('unique')
            if kudos['rarity'] > 80:
                tags.append('extremely rare')
            elif kudos['rarity'] > 70:
                tags.append('very rare')
            elif kudos['rarity'] > 60:
                tags.append('rare')
            elif kudos['rarity'] > 40:
                tags.append('common')
            elif kudos['rarity'] > 20:
                tags.append('very common')
            elif kudos['rarity'] < 20:
                tags.append('extremely common')

            if kudos['priceFinney'] < 2:
                tags.append('budget')
            if kudos['priceFinney'] < 5:
                tags.append('affordable')
            if kudos['priceFinney'] > 20:
                tags.append('premium')
            if kudos['priceFinney'] > 200:
                tags.append('expensive')

            for tag in tags:
                if tag:
                    tag = {
                        "trait_type": "tag",
                        "value": tag
                    }
                    attributes.append(tag)

            metadata = {
                'name': humanize_name(kudos['name']),
                'image': image_path,
                'description': kudos['description'],
                'external_url': f'http://kudosdemo.gitcoin.co/kudos/{idx + 1}/{kudos["name"]}',
                'background_color': '#fbfbfb',
                'attributes': attributes
            }

            tokenURI_url = kudos_contract.create_tokenURI_url(**metadata)

            args = (kudos['priceFinney'], kudos['numClonesAllowed'], tokenURI_url)
            for x in range(1, 4):
                try:
                    kudos_contract.mint(*args, account=account, private_key=private_key, skip_sync=skip_sync)
                except Exception as e:
                    logger.warning(e)
                    logger.info("Trying the mint again...")
                    time.sleep(2)
                    continue
                else:
                    break
