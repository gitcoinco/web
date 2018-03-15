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

from django.core.management.base import BaseCommand

import rollbar
from dashboard.helpers import UnsupportedSchemaException
from dashboard.utils import BountyNotFoundException, get_bounty, web3_process_bounty

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'syncs bounties with geth'

    def add_arguments(self, parser):
        parser.add_argument('network')
        parser.add_argument('start_id', default=0, type=int)
        parser.add_argument('end_id', default=99999999999, type=int)

    def handle(self, *args, **options):

        # config
        network = options['network']
        hour = datetime.datetime.now().hour
        day = datetime.datetime.now().day
        month = datetime.datetime.now().month

        # iterate through all the bounties
        bounty_enum = int(options['start_id'])
        more_bounties = True
        while more_bounties:
            try:
                # pull and process each bounty
                print(f"[{month}/{day} {hour}:00] Getting bounty {bounty_enum}")
                bounty = get_bounty(bounty_enum, network)
                print(f"[{month}/{day} {hour}:00] Processing bounty {bounty_enum}")
                web3_process_bounty(bounty)

            except BountyNotFoundException:
                more_bounties = False
            except UnsupportedSchemaException as e:
                logger.info(f"* Unsupported Schema => {e}")
            except Exception as e:
                extra_data = {
                    'bounty_enum': bounty_enum,
                    'more_bounties': more_bounties,
                    'network': network
                }
                rollbar.report_exc_info(sys.exc_info(), extra_data=extra_data)
                logger.error(f"* Exception in sync_geth => {e}")
            finally:
                # prepare for next loop
                bounty_enum += 1

                if bounty_enum > int(options['end_id']):
                    more_bounties = False
