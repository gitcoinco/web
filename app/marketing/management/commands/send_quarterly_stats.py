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
import time
import warnings
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand

from dashboard.models import Bounty, BountyFulfillment, Profile
from marketing.mails import quarterly_stats
from marketing.models import EmailSubscriber

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
        parser.add_argument(
            '--exclude_startswith',
            dest='exclude_startswith',
            type=str,
            default=None,
            help="exclude_startswith (optional)",
        )
        parser.add_argument(
            '--filter_startswith',
            dest='filter_startswith',
            type=str,
            default=None,
            help="filter_startswith (optional)",
        )

    def handle(self, *args, **options):

        exclude_startswith = options['exclude_startswith']
        filter_startswith = options['filter_startswith']

        queryset = EmailSubscriber.objects.filter(newsletter=True)
        if exclude_startswith:
            queryset = queryset.exclude(email__startswith=exclude_startswith)
        if filter_startswith:
            queryset = queryset.filter(email__startswith=filter_startswith)
        queryset = queryset.order_by('email')
        email_list = set(queryset.values_list('email', flat=True))

        print("got {} emails".format(len(email_list)))

        # TODO: get platform wide stats from a service here
        # TODO: Move this service to appropriate place
        platform_wide_stats = get_platform_wide_stats()

        counter = 0
        for to_email in email_list:
            counter += 1
            print("-sending {} / {}".format(counter, to_email))
            if options['live']:
                try:
                    quarterly_stats([to_email], platform_wide_stats)
                    time.sleep(1)
                except Exception as e:
                    print(e)
                    time.sleep(5)


def get_platform_wide_stats():
    """
    get platform wide stats for quarterly stats email
    """
    last_quarter = datetime.now() - timedelta(days=90)
    bounties = Bounty.objects.stats_eligible().filter(created_on__gte=last_quarter)
    total_bounties = bounties.count()
    completed_bounties = bounties.filter(idx_status__in=['completed'])
    num_completed_bounties = completed_bounties.count()
    bounties_completion_percent = (num_completed_bounties / total_bounties) * 100

    completed_bounties_fund = sum([
        bounty.value_in_usdt if bounty.value_in_usdt else 0
        for bounty in completed_bounties
    ])
    if num_completed_bounties:
        avg_fund_per_bounty = completed_bounties_fund / num_completed_bounties
    else:
        avg_fund_per_bounty = 0

    largest_bounty = Bounty.objects.filter(created_on__gte=last_quarter).order_by('-value_in_token').first()

    bounty_fulfillments = BountyFulfillment.objects.filter(
        accepted_on__gte=last_quarter).order_by('-bounty__value_in_token')[:5]
    profiles = bounty_fulfillments.values_list('profile')
    hunters = Profile.objects.filter(id__in=profiles)
    hunters = [h.handle for h in hunters]

    return {
        'total_funded_bounties': total_bounties,
        'bounties_completion_percent': bounties_completion_percent,
        'no_of_hunters': len(hunters),
        'num_completed_bounties': num_completed_bounties,
        'completed_bounties_fund': completed_bounties_fund,
        'avg_fund_per_bounty': avg_fund_per_bounty,
        'hunters': hunters,
        'largest_bounty': largest_bounty
    }
