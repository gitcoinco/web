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

from app.dashboard.models import Activity
from app.marketing.mails import bounty_not_submitted


class Command(BaseCommand):
    help = 'sends more timed hackathon emails'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        # TODO: Probably not the most efficient way, need instead use self-join.
        # However once per day only for users started work on a bounty not extremely slow.
        bounties = Bounty.objects.filter(event__isnull=False)
        activities = Activity.objects.filter(bounty__in=bounties, activity_type='start_work')
        activities = (activity for activity in activities \
                      if not Activity.objects.filter(bounty__profile=activity.bounty.profile,
                                                     activity_type='work_submitted').exists())
        for activity in activities:
            if datetime.now() - datetime.timedelta(days=5) <= bounty.end_date < datetime.timedelta(days=4):
                for bounty in activities.bounty.distinct():
                    bounty_not_submitted(bounty, activity.profile)
