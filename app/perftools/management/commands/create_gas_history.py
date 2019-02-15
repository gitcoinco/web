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
from django.utils import timezone

from dashboard.gas_views import lines
from gas.utils import gas_history
from perftools.models import JSONStore


class Command(BaseCommand):

    help = 'generates some gas history objects for the gitcoin gas station'

    def handle(self, *args, **options):
        hour = int(timezone.now().strftime('%H'))
        day = int(timezone.now().weekday())
        print(hour, day)

        # hourly all the time
        # daily once a day
        # weekly once a week
        breakdowns = ['hourly']
        if hour <= 0:
            breakdowns.append('daily')
            if day <= 0:
                breakdowns.append('weekly')

        with transaction.atomic():
            items = []
            for breakdown in breakdowns:
                JSONStore.objects.filter(key__startswith=breakdown).all().delete()
                for i, __ in lines.items():
                    view = 'gas_history'
                    key = f"{breakdown}:{i}"
                    print(f"- executing {breakdown} {key}")
                    data = gas_history(breakdown, i)
                    print("- creating")
                    items.append(JSONStore(
                        view=view,
                        key=key,
                        data=data,
                        ))
            JSONStore.objects.bulk_create(items)
