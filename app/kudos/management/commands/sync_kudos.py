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
from kudos.utils import get_kudos, web3_process_kudos

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
default_start_id = 0 if not settings.DEBUG else 402


class Command(BaseCommand):

    help = 'syncs database with kudos on the blockchain'

    def add_arguments(self, parser):
        parser.add_argument('network', default='rinkeby', type=str)
        parser.add_argument('start_id', default=default_start_id, type=int)
        parser.add_argument('end_id', default=99999999999, type=int)

    def handle(self, *args, **options):
        # config
        network = options['network']
        hour = datetime.datetime.now().hour
        day = datetime.datetime.now().day
        month = datetime.datetime.now().month

        # iterate through all the kudos
        kudos_enum = int(options['start_id'])
        more_kudos = True
        while more_kudos:
            # pull and process each kudos
            self.stdout.write(f"[{month}/{day} {hour}:00] Getting kudos {kudos_enum}")
            kudos = get_kudos(kudos_enum, network)
            self.stdout.write(f"[{month}/{day} {hour}:00] Processing kudos {kudos_enum}")
            # web3_process_kudos(kudos)

            kudos_enum += 1

            if kudos_enum > int(options['end_id']):
                more_kudos = False
