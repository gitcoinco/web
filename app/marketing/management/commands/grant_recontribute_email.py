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
import datetime

from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Profile
from marketing.mails import grant_recontribute


class Command(BaseCommand):
    help = 'sends emails for grant contributors to recontribute in the next round'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return
        
        # Round 5: 3/23/2020 — 4/7/2020
        prev_round_start = (2020, 3, 23)
        prev_round_end = (2020, 4, 7)

        # Round 6: 6/15/2020 — 7/3/2020
        next_round = 6
        next_round_start = (2020, 6, 15)
        next_round_end = (2020, 7, 3)
        match_pool = '175k'

        contributor_profiles = Profile.objects.filter(grant_contributor__subscription_contribution__success=True, grant_contributor__subscription_contribution__created_on__gte=datetime.datetime(*prev_round_start), grant_contributor__subscription_contribution__created_on__lte=datetime.datetime(*prev_round_end)).distinct()
        
        for contributor_profile in contributor_profiles:
            try:
                grant_recontribute(contributor_profile, prev_round_start, prev_round_end, next_round, next_round_start, next_round_end, match_pool)
            except:
                pass
