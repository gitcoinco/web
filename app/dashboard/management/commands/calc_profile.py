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
from django.utils import timezone

from dashboard.models import Profile, UserAction
from dashboard.tasks import profile_dict


class Command(BaseCommand):

    help = 'updates profile info for all recent profiles'

    def handle(self, *args, **options):
        start_time = timezone.now()-timezone.timedelta(hours=1)
        profiles = Profile.objects.filter(modified_on__gt=start_time)
        profiles = profiles | Profile.objects.filter(pk__in=UserAction.objects.filter(created_on__gt=start_time).values_list('pk', flat=True))
        profiles = profiles.filter(modified_on__gt=F('last_calc_date'))
        print(profiles.count())
        for instance in profiles:
            profile_dict.delay(instance.pk)
