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
from django.utils import timezone

from dashboard.models import Activity


class Command(BaseCommand):
    help = 'deletes the None None activity feed items in the newsfeed.  No idea where they come from, but this at least keeps them from showing up too long'

    def handle(self, *args, **options):
        then = timezone.now() - timezone.timedelta(minutes=60)
        activities = Activity.objects.filter(activity_type='status_update', metadata__title=None, created_on__gt=then).order_by('-pk')
        print(activities.count())
        activities.delete()
