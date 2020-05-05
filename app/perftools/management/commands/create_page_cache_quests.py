'''
    Copyright (C) 2020 Gitcoin Core

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

from django.conf import settings
from django.core.management.base import BaseCommand

from economy.models import EncodeAnything, SuperModel
from perftools.models import JSONStore


def create_quests_cache():
    from quests.helpers import generate_leaderboard
    from quests.views import current_round_number
    for i in range(1, current_round_number+1):
        print(f'quests_{i}')
        view = 'quests'
        keyword = f'leaderboard_{i}'
        data = generate_leaderboard(round_number=i)
        JSONStore.objects.create(
            view=view,
            key=keyword,
            data=json.loads(json.dumps(data, cls=EncodeAnything)),
            )

    from quests.models import Quest
    for quest in Quest.objects.filter(visible=True):
        quest.save()



class Command(BaseCommand):

    help = 'generates /results data for quests'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            create_quests_cache()
