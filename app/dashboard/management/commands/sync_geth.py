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

from django.core.management.base import BaseCommand
from dashboard.utils import get_bounty, process_bounty, BountyNotFoundException, startIPFS


class Command(BaseCommand):

    help = 'syncs bounties with geth'

    def add_arguments(self, parser):
        parser.add_argument('network')

    def handle(self, *args, **options):
        network = options['network']

        # setup
        startIPFS()

        # iterate through all the bounties
        bounty_enum = 0
        more_bounties = True
        while more_bounties:
            try:

                # pull and process each bounty
                bounty = get_bounty(bounty_enum, network)
                process_bounty(bounty)
                print("TODO: process this bounty")

            except BountyNotFoundException:
                more_bounties = False
