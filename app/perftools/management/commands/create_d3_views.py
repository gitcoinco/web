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
from django.db import transaction

from dataviz.d3_views import get_all_type_options, viz_graph_data_helper, viz_scatterplot_data_helper
from perftools.models import JSONStore
from retail.utils import programming_languages


class Command(BaseCommand):

    help = 'generates d3 dataviz jsonstores'

    def handle(self, *args, **options):
        keywords = [''] + programming_languages
        type_options = get_all_type_options()
        # DEBUG OPTIONS
        # keywords = [''] 
        # type_options = ['all']
        with transaction.atomic():
            items = []
            JSONStore.objects.filter(view__startswith='d3').all().delete()

            ## Scatterplot
            for keyword in keywords:
                for hide_username in [True, False]:
                    view = 'd3_scatterplot'
                    key = f"{keyword}_{hide_username}"
                    print(f"- executing {view} {key}")
                    data = viz_scatterplot_data_helper(keyword, hide_username)
                    print("- creating")
                    items.append(JSONStore(
                        view=view,
                        key=key,
                        data=data,
                        ))

            ## Graph
            for keyword in keywords:
                for _type in type_options:
                    for hide_pii in [True, False]:
                        view = 'd3_graph'
                        key = f"{_type}_{keyword}_{hide_pii}"
                        print(f"- executing {view} {key}")
                        data = viz_graph_data_helper(_type, keyword, hide_pii)
                        print("- creating")
                        items.append(JSONStore(
                            view=view,
                            key=key,
                            data=data,
                            ))

            JSONStore.objects.bulk_create(items)
