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
from django.utils import timezone

from dashboard.models import Bounty
from marketing.common.utils import handle_bounty_feedback
from marketing.mails import bounty_feedback


class Command(BaseCommand):

    help = 'sends feedback emails to bounties that were closed in last xx hours, but only if its the first time a bounty has been accepted by taht persona'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        start_time = timezone.now() - timezone.timedelta(hours=36)
        end_time = timezone.now() - timezone.timedelta(hours=12)
        bounties_fulfilled_last_timeperiod = Bounty.objects.current().filter(
            network='mainnet',
            fulfillment_accepted_on__gt=start_time,
            fulfillment_accepted_on__lt=end_time,
            idx_status='done'
            ).values_list('pk', flat=True)
        bounties_cancelled_last_timeperiod = Bounty.objects.current().filter(
            network='mainnet',
            canceled_on__gt=start_time,
            canceled_on__lt=end_time,
            idx_status='cancelled'
            ).values_list('pk', flat=True)
        bounty_pks = list(bounties_cancelled_last_timeperiod) + list(bounties_fulfilled_last_timeperiod)
        bounties_to_process = Bounty.objects.filter(pk__in=bounty_pks)
        print(bounties_to_process.count())

        for bounty in bounties_to_process:

            (to_fulfiller, to_funder, fulfiller_previous_bounties, funder_previous_bounties) = handle_bounty_feedback(bounty)

            if to_fulfiller:
                bounty_feedback(bounty, 'fulfiller', fulfiller_previous_bounties)

            if to_funder:
                bounty_feedback(bounty, 'funder', funder_previous_bounties)
