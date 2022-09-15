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
from django.core.management.base import BaseCommand

from django.db.models import F

from dashboard.models import Profile

class Command(BaseCommand):

    help = 'Align profile handles and user usernames'

    def handle(self, *args, **options):
        # all users who don't have the same handle on their profile and user
        profiles = Profile.objects.exclude(handle__iexact = F('user__username'))

        print(f"Need to fix - {profiles.count()} profiles")

        # for all copy the handle from the profile into the user
        for profile in profiles.all():
            print(profile.handle, "is not", profile.user.username)

            # update the users username
            profile.user.username = profile.handle
            profile.user.save()

            pass        
