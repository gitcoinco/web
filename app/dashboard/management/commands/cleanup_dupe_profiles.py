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

from django.core.management.base import BaseCommand
from dashboard.models import Profile
from django.db.models import Count


def combine_profiles(p1, p2):
    # p2 is the delete profile, p1 is the save profile
    # switch if p2 has the user
    if p2.user:
        tmp = p2
        p2 = p1
        p1 = tmp

    p1.github_access_token = p2.github_access_token if p2.github_access_token else p1.github_access_token
    p1.slack_token = p2.slack_token if p2.slack_token else p1.slack_token
    p1.slack_repos = p2.slack_repos if p2.slack_repos else p1.slack_repos
    p1.slack_channel = p2.slack_channel if p2.slack_channel else p1.slack_channel
    p1.email = p2.email if p2.email else p1.email
    p1.preferred_payout_address = p2.preferred_payout_address if p2.preferred_payout_address else p1.preferred_payout_address
    p1.max_tip_amount_usdt_per_tx = max(p1.max_tip_amount_usdt_per_tx, p2.max_tip_amount_usdt_per_tx)
    p1.max_tip_amount_usdt_per_week = max(p1.max_tip_amount_usdt_per_week, p2.max_tip_amount_usdt_per_week)
    p1.max_num_issues_start_work = max(p1.max_num_issues_start_work, p2.max_num_issues_start_work)
    p1.trust_profile = any([p1.trust_profile, p2.trust_profile])
    p1.hide_profile = any([p1.hide_profile, p2.hide_profile])
    p1.suppress_leaderboard = any([p1.suppress_leaderboard, p2.suppress_leaderboard])
    p1.save()
    p2.delete()

class Command(BaseCommand):

    help = 'cleans up users who have duplicate profiles'

    def handle(self, *args, **options):

        handles = Profile.objects.values('handle').annotate(num_profiles=Count('handle'))

        for handle in handles:
            if handle['num_profiles'] > 1:
                handle = handle['handle']
                profiles = Profile.objects.filter(handle=handle)
                print(f"combining {profiles[0].pk} and {profiles[1].pk})")
                combine_profiles(profiles[0], profiles[1])
