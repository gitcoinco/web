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
import time
import warnings

from django.core.management.base import BaseCommand

from dashboard.models import Profile
from marketing.mails import quarterly_stats
from marketing.models import EmailSubscriber, LeaderboardRank
from marketing.utils import get_platform_wide_stats

warnings.filterwarnings("ignore", category=DeprecationWarning)


class Command(BaseCommand):

    help = 'the weekly roundup emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '-live', '--live',
            action='store_true',
            dest='live',
            default=False,
            help='Actually Send the emails'
        )


    def handle(self, *args, **options):

        keys = ['quarterly_earners', 'quarterly_payers']
        lrs = LeaderboardRank.objects.active().filter(leaderboard__in=keys).order_by('-amount')
        handles = lrs.values_list("github_username", flat=True)
        profiles = Profile.objects.filter(handle__in=handles)
        email_list = profiles.values_list('email', flat=True)
        email_list = list(set(email_list))

        print(len(email_list))
        platform_wide_stats = get_platform_wide_stats()

        for counter, to_email in enumerate(email_list):
            print(f"-sending {counter+1} / {to_email}")
            if options['live'] and to_email:
                try:
                    quarterly_stats([to_email], platform_wide_stats)
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    time.sleep(5)
