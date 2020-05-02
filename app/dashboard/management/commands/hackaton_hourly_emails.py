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
from datetime import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment
from marketing.mails import bounty_feedback

from app.dashboard.models import HackathonEvent, Profile
from app.marketing.mails import hackathon_end


class Command(BaseCommand):

    help = 'sends timed hackathon emails'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        for hackathon in HackathonEvent.objects.filter(ends_soon_notified=False):
            if hackathon.end_date >= datetime.now() - datetime.timedelta(hours=48):
                for profile in Profile.objects.all():  # FIXME
                    hackathon_end(hackathon, profile)
                hackathon.ends_soon_notified = True  # Do not send it second time.
                hackathon.save()
