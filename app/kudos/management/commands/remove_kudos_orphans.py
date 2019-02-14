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

from django.core.management.base import BaseCommand

from kudos.utils import KudosContract

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):

    help = 'remove kudos orphans from the database'

    def add_arguments(self, parser):
        parser.add_argument('--network', default='localhost', type=str,
                            help='Network such as "localhost", "ropsten", "mainnet"')

    def handle(self, *args, **options):
        # config
        network = options['network']

        kudos_contract = KudosContract(network)
        kudos_contract.remove_kudos_orphans_db()
