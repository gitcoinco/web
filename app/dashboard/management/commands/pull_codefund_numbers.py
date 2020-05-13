'''
    Copyright (C) 2018 Gitcoin Core

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

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import requests
from bs4 import BeautifulSoup
from marketing.models import ManualStat


class Command(BaseCommand):

    help = 'pulls the ad number from codefund.io'

    def handle(self, *args, **options):

        url = "https://codefund.io"
        html_response = requests.get(url)
        soup = BeautifulSoup(html_response.text, 'html.parser')
        title = soup.findAll("h1")[0].text
        number = int(title.replace(',', '').replace('+', ''))
        ms = ManualStat.objects.get(key='ads_served')
        ms.val = number
        ms.comment = f"Updated at {timezone.now().strftime('%Y-%m-%dT%H:00:00')}"
        ms.save()
        print(number)
