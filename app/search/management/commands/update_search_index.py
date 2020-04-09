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
from django.core.management.base import BaseCommand
from django.utils import timezone

from search.models import SearchResult


class Command(BaseCommand):

    help = 'uploads latest search results into elasticsearch'

    def handle(self, *args, **options):
        then = timezone.now() - timezone.timedelta(hours=1)
        for sr in SearchResult.objects.filter(modified_on__gt=then):
            print(sr.pk)
            sr.put_on_elasticsearch()
