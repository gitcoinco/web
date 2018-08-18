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
from django.db import transaction

import requests
from gas.models import GasProfile


class Command(BaseCommand):

    help = 'pulls gas prices from ether gas station'

    def handle(self, *args, **options):

        with transaction.atomic():
            url = 'https://ethgasstation.info/json/predictTable.json'
            response = requests.get(url)
            eles = response.json()
            print(f'syncing {len(eles)} eles')
            if len(eles) < 10:
                print(response)
                raise
            for ele in eles:
                gas_price = str(ele['gasprice'])
                if gas_price[-2:] == '.0':
                    gas_price = gas_price.replace('.0', '')
                mean_time_to_confirm_blocks = 0
                mean_time_to_confirm_minutes = str(round(ele['expectedTime'], 1))
                _99confident_confirm_time_blocks = 0
                _99confident_confirm_time_mins = str(round(ele['expectedTime'] * 2.5, 1))
                GasProfile.objects.create(
                    gas_price=gas_price,
                    mean_time_to_confirm_blocks=mean_time_to_confirm_blocks,
                    mean_time_to_confirm_minutes=mean_time_to_confirm_minutes,
                    _99confident_confirm_time_blocks=_99confident_confirm_time_blocks,
                    _99confident_confirm_time_mins=_99confident_confirm_time_mins,
                )
