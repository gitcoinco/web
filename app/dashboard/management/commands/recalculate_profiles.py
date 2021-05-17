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

from django.conf import settings
from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Profile, ProfileView
from dashboard.tasks import profile_dict


class Command(BaseCommand):

    help = 'Recalculates all stale profiles'

    def handle(self, *args, **options):
        minutes = 1 if not settings.DEBUG else 100000
        then = timezone.now() - timezone.timedelta(minutes=minutes)

        profile_pks = list(Profile.objects.filter(created_on__gte=then).values_list('pk', flat=True))
        profile_pks += list(ProfileView.objects.filter(created_on__gte=then).values_list('target__pk', flat=True))
        print(profile_pks)
        for pk in profile_pks:
            profile_dict.delay(pk)
            pass        
