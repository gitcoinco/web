"""
    Copyright (C) 2021 Gitcoin Core

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

import json

from django.conf import settings
from django.core.management.base import BaseCommand

import requests
from economy.models import EncodeAnything
from perftools.models import JSONStore


def polygon():
    res = requests.get(
        f"https://api.polygonscan.com/api?module=gastracker&action=gasoracle&apikey={settings.POLYGON_API_KEY}"
    )
    data = res.json()['result']
    print(data)
    view = "gas_prices"
    keyword = "polygon"

    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    data = json.loads(json.dumps(data, cls=EncodeAnything))
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=data,
    )


class Command(BaseCommand):

    help = "get gas prices for networks"

    def handle(self, *args, **options):
        try:
            print("Polygon")
            polygon()
        except Exception as e:
            print(e)
