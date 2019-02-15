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

from django.core.management.base import BaseCommand
from django.db import transaction

import requests
from gas.models import GasProfile

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'pulls gas prices from ether gas station'

    def handle(self, *args, **options):
        with transaction.atomic():
            url = 'https://ethgasstation.info/json/predictTable.json'
            response = requests.get(url)
            elements = response.json()
            print(f'syncing {len(elements)} elements')

            if len(elements) < 10:
                logger.warning(
                    'In: sync_gas_prices - Malformed Response: (%s) - Status Code: {%s}', response, response.status_code
                )
                print(f'Malformed Response: ({response}) - Status Code: {response.status_code}')
                return

            for element in elements:
                try:
                    gas_price = str(element['gasprice'])
                    if gas_price[-2:] == '.0':
                        gas_price = gas_price.replace('.0', '')
                    mean_time_to_confirm_blocks = 0
                    mean_time_to_confirm_minutes = str(round(element['expectedTime'], 1))
                    _99confident_confirm_time_blocks = 0
                    _99confident_confirm_time_mins = str(round(element['expectedTime'] * 2.5, 1))
                    GasProfile.objects.create(
                        gas_price=gas_price,
                        mean_time_to_confirm_blocks=mean_time_to_confirm_blocks,
                        mean_time_to_confirm_minutes=mean_time_to_confirm_minutes,
                        _99confident_confirm_time_blocks=_99confident_confirm_time_blocks,
                        _99confident_confirm_time_mins=_99confident_confirm_time_mins,
                    )
                except KeyError:
                    logger.warning('In: sync_gas_prices - Malformed response - Code: %s', response.status_code)
