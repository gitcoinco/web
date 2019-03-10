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
from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Profile
from kudos.models import KudosTransfer


class Command(BaseCommand):

    help = 'stub for local testing'

    def handle(self, *args, **options):

        if not settings.DEBUG:
            print("cannot be run without settings.DEBUG")
            return

        usernames = KudosTransfer.objects.all().values_list('username', flat=True)
        for username in set(usernames):
            print(username)
            profiles = Profile.objects.filter(handle__iexact=username.replace('@', ''))
            if profiles.exists():
                print('-')
                profile = profiles.first()
                kudos = profile.get_my_kudos.order_by('-id')
                counter = 0
                for kudo in kudos:
                    counter += 1
                    if counter < 5:
                        kudo.pin_rank = counter;
                        kudo.save()
