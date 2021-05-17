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
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import HackathonEvent
from marketing.mails import tribe_hackathon_prizes


class Command(BaseCommand):
    help = 'sends emails for tribe members about hackathon prizes sponsored by the tribe org'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return
        
        no_of_days = 3
        next_date = timezone.now() + timezone.timedelta(days=no_of_days)

        upcoming_hackthons = HackathonEvent.objects.filter(start_date__date=next_date)

        for upcoming_hackthon in upcoming_hackthons:
            try:
                tribe_hackathon_prizes(upcoming_hackthon)
            except:
                pass
