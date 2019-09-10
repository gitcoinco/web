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
from django.utils import timezone

class Command(BaseCommand):

    help = 'creates REP records for current acivity feeds'

    def handle(self, *args, **options):
        #REPEntry.objects.all().delete() 
        # exclude 3/5 to 3/6 where something wonky went on with activity feeds
        activities = Activity.objects.exclude(created_on__gt=timezone.datetime(2019,3,5),created_on__lt=timezone.datetime(2019,3,6)).order_by('created_on')
        for instance in activities:
            if instance.point_value() and instance.profile:
                print(instance.pk)
                REPEntry.objects.create(
                    created_on=instance.created_on,
                    why=instance.activity_type,
                    profile=instance.profile,
                    source=instance,
                    value=instance.point_value(),
                    )

        uas = UserAction.objects.exclude(created_on__gt=timezone.datetime(2019,3,5),created_on__lt=timezone.datetime(2019,3,6)).order_by('created_on')
        for instance in uas:
            if instance.point_value() and instance.profile:
                print(instance.pk)
                REPEntry.objects.create(
                    created_on=instance.created_on,
                    why=instance.action,
                    profile=instance.profile,
                    source=instance,
                    value=instance.point_value(),
                    )

        # make sure balances look ok
        for instance in REPEntry.objects.filter(profile__handle='owocki').order_by('created_on'):
            instance.save()
