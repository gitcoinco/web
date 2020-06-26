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

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Profile
from townsquare.models import SquelchProfile


def squelch_profile(profile):
    print("Turn off mini CLR")
    # noop - this is done in the logic of mini CLR
    print("Turn off Grants CLR")
    for subs in profile.grant_contributor:
        for contrib in subs.subscription_contribution:
            contrib.is_clr_eligible = False
            contrib.save()
    print("TODO: Other places to squelch user?")
    # todo: decide what this is; maybe in a v2

#TODO: call me
def un_squelch_profile(profile):
    print("Turn off mini CLR")
    # noop - this is done in the logic of mini CLR
    print("Turn off Grants CLR")
    for subs in profile.grant_contributor:
        for contrib in subs.subscription_contribution:
            contrib.is_clr_eligible = FTrue
            contrib.save()
    print("TODO: Other places to squelch user?")
    # todo: decide what this is; maybe in a v2

class Command(BaseCommand):

    help = 'Auto squelches users within a certain sybil attack threshold'

    def handle(self, *args, **options):
        score_threshold = 2
        profiles = Profile.objects.filter(sybil_score__gte=score_threshold)
        for profile in profiles:
            squelches = profile.squelches
            active_squelches = squelches.filter(active=True)
            if not active_squelches.exists():
                print(f'squelching {profile.pk}')
                if not squelches.exists():
                    SquelchProfile.objects.create(
                        profile=profile,
                        comments=f'Auto Squelch on {timezone.now()}',
                        active=True,
                        )
                else:
                    squelch = squelches.first()
                    squelch.active=True
                    squelch.comments += f"Auto Squelched on {timezone.now()}"
            squelch_profile(profile)
