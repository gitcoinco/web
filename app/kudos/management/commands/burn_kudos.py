"""Define the burn kudos management command.

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
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand

from kudos.utils import KudosContract

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
formatter = '%(levelname)s:%(name)s.%(funcName)s:%(message)s'
logging.basicConfig(level=logging.DEBUG)


class Command(BaseCommand):

    help = 'clone a kudos to an address'

    def add_arguments(self, parser):
        parser.add_argument('network', default='localhost', type=str)
        parser.add_argument('owner', type=str, help='The ETH address of the kudos.')
        parser.add_argument('token_id', type=int, help='The Kudos ID to burn.')
        parser.add_argument('--skip_sync', action='store_true')
        parser.add_argument('--gitcoin_account', action='store_true', help='use account stored in .env file')
        parser.add_argument('--account', help='public account address to use for transaction', type=str)
        parser.add_argument('--private_key', help='private key for signing transactions', type=str)

    def handle(self, *args, **options):
        # config
        network = options['network']
        token_id = options['token_id']

        skip_sync = options['skip_sync']
        gitcoin_account = options['gitcoin_account']
        if gitcoin_account:
            account = settings.KUDOS_OWNER_ACCOUNT
            private_key = settings.KUDOS_PRIVATE_KEY
        else:
            account = options['account']
            private_key = options['private_key']

        kudos_contract = KudosContract(network=network)
        owner = kudos_contract._w3.toChecksumAddress(options['owner'])

        args = (owner, token_id)
        kudos_contract.burn(*args, account=account, private_key=private_key, skip_sync=skip_sync)
