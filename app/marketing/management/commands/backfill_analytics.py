# -*- coding: utf-8 -*-
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

from django.core.management.base import BaseCommand
from django.utils import timezone

import marketing.stats as stats
import pytz


class Command(BaseCommand):

    help = 'backfills analytics that havent been pull by pull stats'

    def handle(self, *args, **options):
        target_date = timezone.now() - timezone.timedelta(days=180)
        now = timezone.now()
        that_time = timezone.datetime(now.year, now.month, now.day, 1, 1, 1, tzinfo=pytz.UTC)
        while that_time > target_date:
            that_time = that_time - timezone.timedelta(days=1)
            stats.joe_dominance_index(that_time)
            stats.bounties_by_status_and_keyword(that_time)
