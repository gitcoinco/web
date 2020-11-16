'''
    Copyright (C) 2020 Gitcoin Core
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
from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import HackathonEvent
from marketing.mails import convert_project_grant


class Command(BaseCommand):
    help = 'sends emails to let hackathon project buidlers know they can convert their projects to grant'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        hackathons_ended_yesterday = HackathonEvent.objects.filter(end_date__date=(date.today()-timedelta(days=1)))
        
        if hackathons_ended_yesterday:
            try:
                convert_project_grant(hackathons_ended_yesterday)
            except:
                pass