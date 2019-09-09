'''
    Copyright (C) 2018 Gitcoin Core

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

from dashboard.models import Activity, REPEntry, UserAction


class Command(BaseCommand):

    help = 'creates REP records for current acivity feeds'

    def handle(self, *args, **options):
        for instance in Activity.objects.all().order_by('created_on'):
            if instance.point_value() and instance.profile:
                print(instance.pk)
                REPEntry.objects.create(
                    created_on=instance.created_on,
                    why=instance.activity_type,
                    profile=instance.profile,
                    source=instance,
                    value=instance.point_value(),
                    )

        for instance in UserAction.objects.all().order_by('created_on'):
            if instance.point_value() and instance.profile:
                print(instance.pk)
                REPEntry.objects.create(
                    created_on=instance.created_on,
                    why=instance.action,
                    profile=instance.profile,
                    source=instance,
                    value=instance.point_value(),
                    )
