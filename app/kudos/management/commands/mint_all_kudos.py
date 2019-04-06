"""Define the mint all kudos management command.

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

"""
import logging
import urllib
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

import oyaml as yaml
from kudos.utils import KudosContract, get_rarity_score, humanize_name

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
formatter = '%(levelname)s:%(name)s.%(funcName)s:%(message)s'


def mint_kudos(kudos_contract, kudos, account, private_key, gas_price_gwei, mint_to=None, live=False, skip_sync=True):
    image_name = urllib.parse.quote(kudos.get('image'))
    if image_name:
        # Support Open Sea
        if kudos_contract.network == 'rinkeby':
            image_path = f'https://ss.gitcoin.co/static/v2/images/kudos/{image_name}'
            external_url = f'https://stage.gitcoin.co/kudos/{kudos_contract.address}/{kudos_contract.getLatestId() + 1}'
        elif kudos_contract.network == 'mainnet':
            image_path = f'https://s.gitcoin.co/static/v2/images/kudos/{image_name}'
            external_url = f'https://gitcoin.co/kudos/{kudos_contract.address}/{kudos_contract.getLatestId() + 1}'
        elif kudos_contract.network == 'localhost':
            image_path = f'v2/images/kudos/{image_name}'
            external_url = f'http://localhost:8000/kudos/{kudos_contract.address}/{kudos_contract.getLatestId() + 1}'
        else:
            raise RuntimeError('Need to set the image path for that network')
    else:
        image_path = ''

    attributes = []
    # "trait_type": "investor_experience",
    # "value": 20,
    # "display_type": "boost_number",
    # "max_value": 100
    rarity = {
        "trait_type": "rarity",
        "value": get_rarity_score(kudos['numClonesAllowed']),
    }
    attributes.append(rarity)

    artist = {
        "trait_type": "artist",
        "value": kudos.get('artist')
    }
    attributes.append(artist)

    platform = {
        "trait_type": "platform",
        "value": kudos.get('platform')
    }
    attributes.append(platform)

    tags = kudos['tags']
    price_finney = kudos['priceFinney']

    # append tags
    if price_finney < 2:
        tags.append('budget')
    if price_finney < 5:
        tags.append('affordable')
    if price_finney > 20:
        tags.append('premium')
    if price_finney > 200:
        tags.append('expensive')

    for tag in tags:
        attributes.append({"trait_type": "tag", "value": tag})

    readable_name = humanize_name(kudos['name'])
    metadata = {
        'name': readable_name,
        'image': image_path,
        'description': kudos['description'],
        'external_url': external_url,
        'background_color': 'fbfbfb',
        'attributes': attributes
    }

    if kudos.get('to_address', None):
        mint_to = kudos_contract._w3.toChecksumAddress(kudos.get('to_address'))
    elif mint_to:
        mint_to = kudos_contract._w3.toChecksumAddress(mint_to)
    else:
        mint_to = kudos_contract._w3.toChecksumAddress(settings.KUDOS_OWNER_ACCOUNT)

    is_live = live
    if is_live:
        try:
            token_uri_url = kudos_contract.create_token_uri_url(**metadata)
            args = (mint_to, kudos['priceFinney'], kudos['numClonesAllowed'], token_uri_url)
            kudos_contract.mint(
                *args,
                account=account,
                private_key=private_key,
                skip_sync=skip_sync,
                gas_price_gwei=gas_price_gwei,
            )
            print('Live run - Name: ', readable_name, ' - Account: ', account, 'Minted!')
        except Exception as e:
            print(f'Error minting: {readable_name} - {e}')
    else:
        print('Dry run - Name: ', readable_name, ' - Account: ', account, 'Skipping!')



class Command(BaseCommand):

    help = 'mints the initial kudos gen0 set'

    def add_arguments(self, parser):
        parser.add_argument('network', default='localhost', type=str)
        parser.add_argument('yaml_file', help='absolute path to kudos.yaml file', type=str)
        parser.add_argument('--mint_to', help='address to mint the kudos to', type=str)
        parser.add_argument('--gas_price_gwei', help='the gas price for mining', type=int)
        parser.add_argument('--skip_sync', action='store_true')
        parser.add_argument('--gitcoin_account', action='store_true', help='use account stored in .env file')
        parser.add_argument('--account', help='public account address to use for transaction', type=str)
        parser.add_argument('--private_key', help='private key for signing transactions', type=str)
        parser.add_argument('--debug', help='turn on debug statements', action='store_true')
        parser.add_argument('--live', help='whether or not to deploy the proposed changes live', action='store_true')
        parser.add_argument('--filter', default='', type=str, dest='kudos_filter')
        parser.add_argument('--filter_svg', default='', type=str, dest='kudos_filter_svg')

    def handle(self, *args, **options):
        # config
        if options['debug']:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        network = options['network']
        gitcoin_account = options['gitcoin_account']
        gas_price_gwei = options['gas_price_gwei']
        kudos_filter = options['kudos_filter']
        kudos_filter_svg = options['kudos_filter_svg']

        if gitcoin_account:
            account = settings.KUDOS_OWNER_ACCOUNT
            private_key = settings.KUDOS_PRIVATE_KEY
        else:
            account = options['account']
            private_key = options['private_key']
        skip_sync = options['skip_sync']

        kudos_contract = KudosContract(network=network)

        yaml_file = options['yaml_file']

        with open(yaml_file) as f:
            all_kudos = yaml.load(f)

        for __, kudos in enumerate(all_kudos):
            is_match = (kudos_filter and kudos_filter in kudos['name']) or (kudos_filter_svg and kudos_filter_svg in kudos.get('image', ''))
            if not kudos_filter and not kudos_filter_svg:
                is_match = True
            if not is_match:
                continue
            mint_kudos(
                kudos_contract, kudos, account, private_key, gas_price_gwei, options['mint_to'], options['live'],
                skip_sync
            )
