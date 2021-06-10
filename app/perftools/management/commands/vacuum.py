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

import time

from django.core.management.base import BaseCommand
from django.db import connection

SLEEP_TIME_BETWEEN_VACUUMS_S = 10


class Command(BaseCommand):

    help = 'vacuums all the postgres tables; on our schedule (auto vacuumer cant take site down anymore'

    def handle(self, *args, **options):
        tables = connection.introspection.table_names()
        seen_models = connection.introspection.installed_models(tables)
        cursor = connection.cursor()

        for model in seen_models:
            table = model._meta.db_table
            query = f"VACUUM {table};"

            start_time = time.time()
            cursor.execute(query)
            end_time = time.time()

            total_time = round(end_time - start_time, 2)
            print(f"{table} took {total_time}s")

            time.sleep(SLEEP_TIME_BETWEEN_VACUUMS_S)
