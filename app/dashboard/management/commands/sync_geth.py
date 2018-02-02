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

import warnings

from django.core.management.base import BaseCommand

from dashboard.helpers import UnsupportedSchemaException
from dashboard.utils import BountyNotFoundException, get_bounty, process_bounty, start_ipfs

warnings.filterwarnings("ignore", category=DeprecationWarning) 


class Command(BaseCommand):

    help = 'syncs bounties with geth'

    def add_arguments(self, parser):
        parser.add_argument('network')

    def handle(self, *args, **options):

        # config
        network = options['network']

        # setup
        start_ipfs()

        # iterate through all the bounties
        bounty_enum = 0
        more_bounties = True
        while more_bounties:
            try:

                # pull and process each bounty
                bounty = get_bounty(bounty_enum, network)
                print(f"Processing bounty {bounty_enum}")
                process_bounty(bounty)

            except BountyNotFoundException:
                more_bounties = False
            except UnsupportedSchemaException as e:
                print(f"* {e}")
            finally:
                # prepare for next loop
                bounty_enum += 1
