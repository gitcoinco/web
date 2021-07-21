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

from dashboard.models import HackathonEvent
from perftools.models import JSONStore


def create_activity_cache():

    print('activity')
    view = 'activity'
    from retail.views import get_specific_activities
    from townsquare.views import tags
    all_tags = tags + [
        [None, None, 'everywhere'],
        [None, None, 'kudos'],
        [None, None, 'connects'],
    ]
    hackathons = HackathonEvent.objects.all()
    for hackathon in hackathons:
        tab = f'hackathon:{hackathon.pk}'
        all_tags.append([None, None, tab])
    for tag in all_tags:
        keyword = tag[2]
        data = get_specific_activities(keyword, False, None, None)
        JSONStore.objects.filter(view=view, key=keyword).all().delete()
        JSONStore.objects.create(
            view=view,
            key=keyword,
            data=list(data.order_by('-pk').values_list('pk', flat=True)[:10]),
            )


class Command(BaseCommand):

    help = 'generates some activity cache data'

    def handle(self, *args, **options):
        create_activity_cache()
