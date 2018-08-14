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

import rollbar
from dashboard.helpers import UnsupportedSchemaException
from kudos.utils import clone_and_transfer_kudos_web3
from eth_utils import to_checksum_address

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
# logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
default_start_id = 0 if not settings.DEBUG else 402


class Command(BaseCommand):

    help = 'clone a new kudos and transfer it to a different address'

    def add_arguments(self, parser):
        parser.add_argument('network', default='ropsten', type=str)
        parser.add_argument('name', type=str)
        parser.add_argument('receiver', type=str)
        parser.add_argument('--numClonesRequested', default=1, type=str)
        parser.add_argument('--private_key', help='private key for signing transactions', type=str)

    def handle(self, *args, **options):
        # config

        args = (options['name'], options['numClonesRequested'],
                to_checksum_address(options['receiver']),
                )

        clone_and_transfer_kudos_web3(options['network'], options['private_key'], *args)
