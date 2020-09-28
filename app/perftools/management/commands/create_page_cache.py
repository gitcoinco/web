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
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise

from app.services import RedisService
from avatar.models import AvatarTheme, CustomAvatar
from dashboard.models import Activity, HackathonEvent, Profile
from dashboard.utils import set_hackathon_event
from economy.models import EncodeAnything, SuperModel
from grants.models import Contribution, Grant, GrantCategory
from grants.utils import generate_leaderboard
from grants.views import next_round_start, round_types
from marketing.models import Stat
from perftools.models import JSONStore
from quests.helpers import generate_leaderboard
from quests.models import Quest
from quests.views import current_round_number
from retail.utils import build_stat_results, programming_languages
from retail.views import get_contributor_landing_page_context, get_specific_activities
from townsquare.views import tags


def create_grant_clr_cache():
    print('create_grant_clr_cache')
    pks = Grant.objects.values_list('pk', flat=True)
    for pk in pks:
        grant = Grant.objects.get(pk=pk)
        clr_round = None

        if grant.in_active_clrs.count() > 0 and grant.is_clr_eligible:
            clr_round = grant.in_active_clrs.first()

        if clr_round:
            grant.is_clr_active = True
            grant.clr_round_num = clr_round.round_num
        else:
            grant.is_clr_active = False
            grant.clr_round_num = ''
        grant.save()

def create_grant_type_cache():
    print('create_grant_type_cache')
    from grants.views import get_grant_types
    for network in ['rinkeby', 'mainnet']:
        view = f'get_grant_types_{network}'
        keyword = view
        data = get_grant_types('mainnet', None)
        with transaction.atomic():
            JSONStore.objects.filter(view=view).all().delete()
            JSONStore.objects.create(
                view=view,
                key=keyword,
                data=data,
                )


def create_grant_active_clr_mapping():
    print('create_grant_active_clr_mapping')
    # Upate grants mppping to active CLR rounds
    from grants.models import Grant, GrantCLR

    grants = Grant.objects.all()
    clr_rounds = GrantCLR.objects.all()

    # remove all old mapping
    for clr_round in clr_rounds:
        _grants = clr_round.grants
        for _grant in grants:
            _grant.in_active_clrs.remove(clr_round)
            _grant.save()

    # update new mapping
    active_clr_rounds = clr_rounds.filter(is_active=True)
    for clr_round in active_clr_rounds:
        grants_in_clr_round = grants.filter(**clr_round.grant_filters)

        for grant in grants_in_clr_round:
            grant_has_mapping_to_round = grant.in_active_clrs.filter(pk=clr_round.pk).exists()

            if not grant_has_mapping_to_round:
                grant.in_active_clrs.add(clr_round)
                grant.save()


def create_grant_category_size_cache():
    print('create_grant_category_size_cache')
    redis = RedisService().redis
    for category in GrantCategory.objects.all():
        key = f"grant_category_{category.category}"
        val = Grant.objects.filter(categories__category__contains=category.category).count()
        redis.set(key, val)

def create_top_grant_spenders_cache():
    for round_type in round_types:
        contributions = Contribution.objects.filter(
            success=True,
            created_on__gt=next_round_start,
            subscription__grant__grant_type__name=round_type
            ).values_list('subscription__contributor_profile__handle', 'subscription__amount_per_period_usdt')
        count_dict = {ele[0]:0 for ele in contributions}
        sum_dict = {ele[0]:0 for ele in contributions}
        for ele in contributions:
            if ele[1]:
                count_dict[ele[0]] += 1
                sum_dict[ele[0]] += ele[1]

        from_date = timezone.now()
        for key, val in count_dict.items():
            if val:
                #print(key, val)
                Stat.objects.create(
                    created_on=from_date,
                    key="count_" + round_type + "_" + key,
                    val=val,
                    )

        for key, val in sum_dict.items():
            if val:
                #print(key, val)
                Stat.objects.create(
                    created_on=from_date,
                    key="sum_" + round_type + "_" + key,
                    val=val,
                    )



def fetchPost(qt='2'):
    import requests
    """Fetch last post from wordpress blog."""
    url = f"https://gitcoin.co/blog/wp-json/wp/v2/posts?_fields=excerpt,title,link,jetpack_featured_media_url&per_page={qt}"
    last_posts = requests.get(url=url).json()
    return last_posts

def create_hidden_profiles_cache():

    handles = list(Profile.objects.all().hidden().values_list('handle', flat=True))

    view = 'hidden_profiles'
    keyword = 'hidden_profiles'
    with transaction.atomic():
        JSONStore.objects.filter(view=view).all().delete()
        data = handles
        JSONStore.objects.create(
            view=view,
            key=keyword,
            data=data,
            )


def create_tribes_cache():

    _tribes = Profile.objects.filter(is_org=True).order_by('-follower_count')[:8]

    tribes = []

    for _tribe in _tribes:
        tribe = {
            'name': _tribe.handle,
            'img': _tribe.avatar_url,
            'followers_count': _tribe.follower_count
        }
        tribes.append(tribe)

    view = 'tribes'
    keyword = 'tribes'
    with transaction.atomic():
        JSONStore.objects.filter(view=view).all().delete()
        data = tribes
        JSONStore.objects.create(
            view=view,
            key=keyword,
            data=data,
            )


def create_post_cache():
    data = fetchPost()
    view = 'posts'
    keyword = 'posts'
    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    data = json.loads(json.dumps(data, cls=EncodeAnything))
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=data,
        )


def create_avatar_cache():
    for at in AvatarTheme.objects.all():
        at.popularity = at.popularity_cheat_by
        if at.name == 'classic':
            at.popularity += CustomAvatar.objects.filter(active=True, config__icontains='"Ears"').count()
        elif at.name == 'unisex':
            at.popularity += CustomAvatar.objects.filter(active=True, config__theme=["3d"]).count()
            at.popularity += CustomAvatar.objects.filter(active=True, config__icontains='hairTone').exclude(config__icontains="theme").count()
        else:
            at.popularity += CustomAvatar.objects.filter(active=True, config__theme=[at.name]).count()
        at.save()


def create_activity_cache():
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

    for quest in Quest.objects.filter(visible=True):
        quest.save()


def create_hackathon_cache():
    for hackathon in HackathonEvent.objects.filter(display_showcase=True):
        hackathon.get_total_prizes(force=True)
        hackathon.get_total_winners(force=True)


def create_hackathon_list_page_cache():
    print('create_hackathon_list_page_cache')

    view = 'hackathons'
    keyword = 'hackathons'
    current_hackathon_events = HackathonEvent.objects.current().filter(visible=True).order_by('-start_date')
    upcoming_hackathon_events = HackathonEvent.objects.upcoming().filter(visible=True).order_by('-start_date')
    finished_hackathon_events = HackathonEvent.objects.finished().filter(visible=True).order_by('-start_date')

    events = []

    if current_hackathon_events.exists():
        for event in current_hackathon_events:
            events.append(set_hackathon_event('current', event))

    if upcoming_hackathon_events.exists():
        for event in upcoming_hackathon_events:
            events.append(set_hackathon_event('upcoming', event))

    if finished_hackathon_events.exists():
        for event in finished_hackathon_events:
            events.append(set_hackathon_event('finished', event))

    default_tab = None

    if current_hackathon_events.exists():
        default_tab = 'current'
    elif upcoming_hackathon_events.exists():
        default_tab = 'upcoming'
    else:
        default_tab = 'finished'

    with transaction.atomic():
        JSONStore.objects.filter(view=view).all().delete()
        data = [default_tab, events]
        JSONStore.objects.create(
            view=view,
            key=keyword,
            data=data,
            )


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
        create_grant_type_cache()
        create_grant_clr_cache()
        create_grant_category_size_cache()
        create_grant_active_clr_mapping()
        if not settings.DEBUG:
            create_results_cache()
            create_hidden_profiles_cache()
            create_tribes_cache()
            create_activity_cache()
            create_post_cache()
            create_top_grant_spenders_cache()
            create_avatar_cache()
            create_quests_cache()
            create_grants_cache()
            create_contributor_landing_page_context()
            create_hackathon_cache()
            create_hackathon_list_page_cache()
