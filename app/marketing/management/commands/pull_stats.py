'''
    Copyright (C) 2019 Gitcoin Core

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

import marketing.stats as stats

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Command(BaseCommand):

    help = 'pulls all stats'

    def handle(self, *args, **options):

        fs = [
            stats.get_bounty_keyword_counts,
            stats.get_skills_keyword_counts,
            stats.github_issues,
            stats.gitter,
            stats.medium_subscribers,
            stats.google_analytics,
            stats.github_stars,
            stats.profiles_ingested,
            stats.chrome_ext_users,
            stats.firefox_ext_users,
            stats.slack_users,
            stats.slack_users_active,
            stats.twitter_followers,
            stats.bounties,
            stats.grants,
            stats.subs,
            stats.whitepaper_access,
            stats.whitepaper_access_request,
            stats.sendcryptoassets,
            stats.tips_received,
            stats.bounties_fulfilled,
            stats.bounties_open,
            stats.bounties_by_status_and_keyword,
            stats.subs_active,
            stats.joe_dominance_index,
            stats.avg_time_bounty_turnaround,
            stats.user_actions,
            stats.faucet,
            stats.email_events,
            stats.bounties_hourly_rate,
            stats.ens,
        ]

        for f in fs:
            try:
                print("*"+str(f.__name__)+"*")
                f()
            except Exception as e:
                print(e)
