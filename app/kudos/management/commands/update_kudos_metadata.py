"""Define the update kudos metadata management command.

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
import time
import warnings

from django.core.management.base import BaseCommand

from kudos.utils import KudosContract, get_rarity_score, humanize_name

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):

    help = 'syncs database with kudos on the blockchain'

    def add_arguments(self, parser):
        parser.add_argument('network', type=str, choices=['localhost', 'rinkeby', 'ropsten', 'mainnet'],
                            help='ethereum network to use')
        parser.add_argument('--start_id', default=1, type=int,
                            help='kudos_id to or kudos block to start syncing at.  Lowest kudos_id is 1.')
        parser.add_argument('--end_id', type=int,
                            help='kudos_id to stop syncing at.  By default it will sync to the latest token.')

    def handle(self, *args, **options):
        # config
        network = options['network']
        start_id = options['start_id']

        kudos_contract = KudosContract(network)

        if options['end_id']:
            end_id = options['end_id']
        else:
            end_id = kudos_contract._w3.functions.getLatestId().call()

        for kudos_id in range(start_id, end_id + 1):
            kudos = kudos_contract.getKudosById(kudos_id, to_dict=True)

            # Copied from mint_all_kudos
            image_name = kudos.get('image')
            if image_name:
                # Support Open Sea
                if kudos_contract.network == 'mainnet':
                    image_path = 'http://kudosdemo.gitcoin.co/static/v2/images/kudos/' + image_name
                else:
                    image_path = 'v2/images/kudos/' + image_name
            else:
                image_path = ''

            attributes = []
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
            # append tags
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
                'external_url': f'http://kudosdemo.gitcoin.co/kudos',
                'background_color': '#fbfbfb',
                'attributes': attributes
            }

            for __ in range(1, 4):
                try:
                    kudos_contract.create_token_uri_url(**metadata)
                    args = ()
                except Exception as e:
                    logger.error(e)
                    logger.info("Trying the mint again...")
                    time.sleep(2)
                    continue
                else:
                    break
