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

import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.utils.encoding import force_text
from django.utils.functional import Promise

from economy.models import EncodeAnything, SuperModel
from perftools.models import JSONStore
from retail.utils import build_stat_results, programming_languages


def create_avatar_cache():
    from avatar.models import AvatarTheme, CustomAvatar
    for at in AvatarTheme.objects.all():
        at.popularity = CustomAvatar.objects.filter(config__theme=[at.name]).count()
        if at.name == 'classic':
            at.popularity = CustomAvatar.objects.filter(config__icontains='"Ears"').count()
        at.save()


def create_activity_cache():
    from django.utils import timezone
    from dashboard.models import Activity
    hours = 24 if not settings.DEBUG else 1000

    print('activity.1')
    view = 'activity'
    keyword = '24hcount'
    data = Activity.objects.filter(created_on__gt=timezone.now() - timezone.timedelta(hours=hours)).count()
    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=json.loads(json.dumps(data, cls=EncodeAnything)),
        )

    print('activity.2')
    from retail.views import get_specific_activities
    from townsquare.views import tags
    for tag in tags:
        keyword = tag[2]
        data = get_specific_activities(keyword, False, None, None).filter(created_on__gt=timezone.now() - timezone.timedelta(hours=hours)).count()
        JSONStore.objects.filter(view=view, key=keyword).all().delete()
        JSONStore.objects.create(
            view=view,
            key=keyword,
            data=json.loads(json.dumps(data, cls=EncodeAnything)),
            )



def create_grants_cache():
    from grants.utils import generate_leaderboard
    print('grants')
    view = 'grants'
    keyword = 'leaderboard'
    data = generate_leaderboard()
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=json.loads(json.dumps(data, cls=EncodeAnything)),
        )


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


def create_results_cache():
    print('results')
    keywords = ['']
    if settings.DEBUG:
        keywords = ['']
    view = 'results'
    with transaction.atomic():
        items = []
        JSONStore.objects.filter(view=view).all().delete()
        for keyword in keywords:
            print(f"- executing {keyword}")
            data = build_stat_results(keyword)
            print("- creating")
            items.append(JSONStore(
                view=view,
                key=keyword,
                data=json.loads(json.dumps(data, cls=EncodeAnything)),
                ))
        JSONStore.objects.bulk_create(items)


def create_contributor_landing_page_context():
    print('create_contributor_landing_page_context')
    keywords = [''] + programming_languages
    if settings.DEBUG:
        keywords = ['']
    view = 'contributor_landing_page'
    from retail.views import get_contributor_landing_page_context
    with transaction.atomic():
        items = []
        JSONStore.objects.filter(view=view).all().delete()
        for keyword in keywords:
            print(f"- executing {keyword}")
            data = get_contributor_landing_page_context(keyword)
            print("- creating")
            items.append(JSONStore(
                view=view,
                key=keyword,
                data=json.loads(json.dumps(data, cls=EncodeAnything)),
                ))
        JSONStore.objects.bulk_create(items)



class Command(BaseCommand):

    help = 'generates some /results data'

    def handle(self, *args, **options):
        create_avatar_cache()
        if not settings.DEBUG:
            create_activity_cache()
            create_results_cache()
            create_quests_cache()
            create_grants_cache()
            create_contributor_landing_page_context()
