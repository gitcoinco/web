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
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from grants.models import Grant
from search.models import SearchResult

class Command(BaseCommand):
    help = 'uploads latest search results into elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument('index_name', type=str, help='the name of the new elastic index')

    def create_grant_records(self):
        for grant in Grant.objects.filter(active=True, hidden=False):
            SearchResult.objects.update_or_create(
                source_type=ContentType.objects.get(app_label='grants', model='grant'),
                source_id=grant.pk,
                defaults={
                    "created_on":grant.created_on,
                    "title":grant.title,
                    "description":grant.description,
                    "url":grant.url,
                    "visible_to":None,
                    'img_url': grant.logo.url if grant.logo else None,
                }
            )

    def handle(self, *args, **options):
        index_name = options['index_name']

        # delete existing grants from search results
        SearchResult.objects.filter(source_type_id=82).delete()
        print('deleted old grant search results')

        # Create rows for existing search results
        self.create_grant_records()
        print('created new search results for grants')

        for sr in SearchResult.objects.all():
            print(sr.pk)
            try:
                sr.put_on_elasticsearch(index_name)
            except Exception as e:
                print('failed:', e)

        print('indexing complete')
