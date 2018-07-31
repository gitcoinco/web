'''
    Copyright (C) 2017 Gitcoin Core

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

from marketing.mails import funder_stale
from dashboard.models import Bounty


class Command(BaseCommand):

    help = 'solicits feedback from stale funders'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        # config
        days = 30 # TODO: do we want to send another variant of this email at 90 days, 180 days?
        time_as_str = 'about a month'

        start_time = timezone.now() - timezone.timedelta(days=(days+1))
        end_time = timezone.now() - timezone.timedelta(days=(days))
        base_bounties = Bounty.objects.filter(
            network='mainnet',
            current_bounty=True,
            )

        candidate_bounties = base_bounties.filter(
            web3_created__gt=start_time,
            web3_created__lt=end_time,
            )

        for bounty in candidate_bounties.distinct('bounty_owner_github_username'):
            handle = bounty.bounty_owner_github_username
            email = bounty.bounty_owner_email

            if not handle:
                continue
                
            print(handle)

            has_posted_in_last_days_days = base_bounties.filter(
                web3_created__gt=end_time,
                bounty_owner_github_username=handle,
                ).exists()

            if not has_posted_in_last_days_days:
                # TODO: do we want to suppress the email if the user 
                # has received this specific email before

                # send the email
                funder_stale(email, handle, days, time_as_str)
            else:
                print(" - has posted recently; not sending")



