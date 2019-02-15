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
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
default_start_id = 0 if not settings.DEBUG else 402


class Command(BaseCommand):

    help = 'syncs database with kudos on the blockchain'

    def add_arguments(self, parser):
        parser.add_argument('network', default='ropsten', type=str)
        parser.add_argument('name', type=str)
        parser.add_argument('--description', default='', type=str)
        parser.add_argument('--rarity', default=50, type=int)
        parser.add_argument('--price', default=1, type=int)
        parser.add_argument('--numClonesAllowed', default=10, type=int)
        parser.add_argument('--tags', default='', type=str)
        parser.add_argument('--image', default='', type=str, help='absolute path to Kudos image')
        parser.add_argument('--private_key', help='private key for signing transactions', type=str)

    def handle(self, *args, **options):
        # config
        network = options['network']
        private_key = options['private_key']
        logging.info(options)

        image = options.get('image')
        if image:
            image_path = image
        else:
            image_path = ''

        args = (options['name'], options['description'], options['rarity'], options['price'],
                options['numClonesAllowed'], options['tags'], image_path)
