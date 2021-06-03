'''
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

'''
import time

from django.core.management.base import BaseCommand

from app.services import RedisService
from marketing.tasks import weekly_roundup

THROTTLE_S = 0.3
redis = RedisService().redis

class Command(BaseCommand):

    help = 're-sends queued emails after a queue has been flushed'

    def handle(self, *args, **options):

        try:
            while True:
                _next = redis.spop('weekly_roundup_retry').decode('utf-8')
                weekly_roundup.delay(_next)
                time.sleep(THROTTLE_S)
                print(round(time.time(), 2), _next)
        except Exception as e:
            print(e)
