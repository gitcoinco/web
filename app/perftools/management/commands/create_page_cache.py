'''
    Copyright (C) 2017 Gitcoin Core

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

import json

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction, models
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.utils.encoding import force_text
from django.utils.functional import Promise
from economy.models import SuperModel
from perftools.models import JSONStore
from retail.utils import build_stat_results, programming_languages


class LazyEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Promise):
            return force_text(obj)
        if isinstance(obj, SuperModel):
            return (obj.to_standard_dict())
        if isinstance(obj, models.Model):
            return (model_to_dict(obj))
        if isinstance(obj, models.Model):
            return (model_to_dict(obj))
        if isinstance(obj, QuerySet):
            if obj.count() and type(obj.first()) == str:
                return obj[::1]
            return [LazyEncoder(instance) for instance in obj]
        if isinstance(obj, list):
            return [LazyEncoder(instance) for instance in obj]
        if(callable(obj)):
            return None
        return super(LazyEncoder, self).default(obj)

def create_results_cache():
    print('results')
    keywords = [''] + programming_languages
    view = 'results'
    with transaction.atomic():
        items = []
        JSONStore.objects.filter(view=view).all().delete()
        for keyword in keywords:
            key = keyword
            print(f"- executing {keyword}")
            data = build_stat_results(keyword)
            print("- creating")
            items.append(JSONStore(
                view=view,
                key=key,
                data=json.loads(json.dumps(data, cls=LazyEncoder)),
                ))
        JSONStore.objects.bulk_create(items)


def create_contributor_landing_page_context():
    print('create_contributor_landing_page_context')
    keywords = [''] + programming_languages
    # TODO
    keywords = ['']
    view = 'contributor_landing_page'
    from retail.views import get_contributor_landing_page_context
    with transaction.atomic():
        items = []
        JSONStore.objects.filter(view=view).all().delete()
        for keyword in keywords:
            key = keyword
            print(f"- executing {keyword}")
            data = get_contributor_landing_page_context(keyword)
            print("- creating")
            items.append(JSONStore(
                view=view,
                key=key,
                data=json.loads(json.dumps(data, cls=LazyEncoder)),
                ))
        JSONStore.objects.bulk_create(items)



class Command(BaseCommand):

    help = 'generates some /results data'

    def handle(self, *args, **options):
        # TODO
        # create_results_cache()
        create_contributor_landing_page_context()
