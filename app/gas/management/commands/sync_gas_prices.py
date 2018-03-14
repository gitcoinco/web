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
from bs4 import BeautifulSoup
from gas.models import GasProfile


class Command(BaseCommand):

    help = 'pulls gas prices from ether gas station'

    def handle(self, *args, **options):

        with transaction.atomic():

            response = requests.get('http://ethgasstation.info/predictionTable.php')
            soup = BeautifulSoup(response.text, 'html.parser')
            eles = soup.findAll("tr",)
            print(f'syncing {len(eles)} eles')
            if len(eles) < 10:
                raise
            for ele in eles:
                if ele.find('th'):
                    continue
                tds = ele.findAll('td')
                # TODO: refactor this all to use an API instead of webscraping
                gas_price = tds[0].text
                mean_time_to_confirm_blocks = 0
                mean_time_to_confirm_minutes = str(tds[5].text).replace('> 2 hours', '120')
                _99confident_confirm_time_blocks = 0
                _99confident_confirm_time_mins = str(tds[6].text).replace('> 2 hours', '120')
                GasProfile.objects.create(
                    gas_price=gas_price,
                    mean_time_to_confirm_blocks=mean_time_to_confirm_blocks,
                    mean_time_to_confirm_minutes=mean_time_to_confirm_minutes,
                    _99confident_confirm_time_blocks=_99confident_confirm_time_blocks,
                    _99confident_confirm_time_mins=_99confident_confirm_time_mins,
                    )
