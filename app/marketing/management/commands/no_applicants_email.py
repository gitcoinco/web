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
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone

from dashboard.models import Bounty
from marketing.mails import no_applicant_reminder


class Command(BaseCommand):

    help = 'sends reminder emails to funders whose bounties have 0 applications'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        start_time_3_days = timezone.now() - timezone.timedelta(hours=24 * 3)
        end_time_3_days = timezone.now() - timezone.timedelta(hours=24 * 4)

        start_time_7_days = timezone.now() - timezone.timedelta(hours=24 * 7)
        end_time_7_days = timezone.now() - timezone.timedelta(hours=24 * 8)
        bounties = Bounty.objects.current().filter(
            (Q(created_on__range=[end_time_3_days, start_time_3_days]) | Q(created_on__range=[end_time_7_days, start_time_7_days])),
            idx_status='open',
            network='mainnet'
            )

        for bounty in [b for b in bounties if b.no_of_applicants == 0]:
            no_applicant_reminder(bounty.bounty_owner_email, bounty)
