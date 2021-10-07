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

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import ActivityIndex

class Command(BaseCommand):

    help = 'cleans up activity index older than 400 days'

    def handle(self, *args, **options):
        purge_activity_index = timezone.now() - timedelta(days=400)
        ActivityIndex.objects.filter(created_on__lt=purge_activity_index).delete()
        print('deleted')