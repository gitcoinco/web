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

import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Investigation, Profile


class Command(BaseCommand):

    help = 'Investigates sybil attacks'

    def handle(self, *args, **options):
        then = timezone.now() - timezone.timedelta(minutes=120)
        profiles = Profile.objects.filter(last_visit__gt=then)
        for profile in profiles:
            start_time = time.time()
            print(f"{profile.pk} at {round(start_time,2)}")
            Investigation.investigate_sybil(profile)
            profile.save()
            the_time = time.time() - start_time
            print(f"END {profile.pk} after {round(the_time,2)} s")
