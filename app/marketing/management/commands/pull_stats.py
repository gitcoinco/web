'''
    Copyright (C) 2021 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation,either version 3 of the License,or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not,see <http://www.gnu.org/licenses/>.

'''
import logging
import warnings

from django.core.management.base import BaseCommand

from marketing.tasks import get_stats

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Command(BaseCommand):

    help = 'pulls all stats'

    def handle(self, *args, **options):

        fns = [
            'get_bounty_keyword_counts',
            'get_skills_keyword_counts',
            'github_issues',
            'gitter',
            'medium_subscribers',
            'google_analytics',
            'github_stars',
            'profiles_ingested',
            'chrome_ext_users',
            'firefox_ext_users',
            'slack_users',
            'slack_users_active',
            'twitter_followers',
            'bounties',
            'grants',
            'subs',
            'whitepaper_access',
            'whitepaper_access_request',
            'sendcryptoassets',
            'tips_received',
            'bounties_fulfilled',
            'bounties_open',
            'bounties_by_status_and_keyword',
            'subs_active',
            'joe_dominance_index',
            'avg_time_bounty_turnaround',
            'user_actions',
            'email_events',
            'bounties_hourly_rate'
        ]

        for fn in fns:
            print("*"+fn+"*")
            get_stats(fn)
