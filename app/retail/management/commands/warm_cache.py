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
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from retail.utils import programming_languages

warnings.filterwarnings("ignore", category=DeprecationWarning) 
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Command(BaseCommand):

    help = 'warms the cache after a deploy'

    def warm_path(self, path):
        import requests
        import time
        start_time = time.time()
        url = settings.BASE_URL[:-1] + path
        requests.get(url)
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        print(f"warmed {url} in {execution_time}s")

    def handle(self, *args, **options):

        # build path list
        paths = []
        paths.append(reverse('activity'))
        paths.append(reverse('gas'))
        paths.append(reverse('gas_heatmap'))

        # warm the paths
        print(f"starting at {timezone.now()}")
        for path in paths:
            self.warm_path(path)
