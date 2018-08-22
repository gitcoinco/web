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
from gas.models import GasGuzzler


class Command(BaseCommand):

    help = 'pulls gas guzzlers from ether gas station'

    def handle(self, *args, **options):

        with transaction.atomic():
            url = 'https://ethgasstation.info/json/gasguzz.json'
            response = requests.get(url)
            eles = response.json()
            print(f'syncing {len(eles)} eles')
            for ele in eles:
                GasGuzzler.objects.create(
                    ID=ele['ID'],
                    pct_total=ele['pcttot'],
                    address=ele['to_address'],
                    gas_used=ele['gasused'],
                    )
