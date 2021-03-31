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
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models, transaction
from django.db.models import Count, Q
from django.db.models.query import QuerySet
from django.forms.models import model_to_dict
from django.templatetags.static import static
from django.utils import timezone
from django.utils.encoding import force_text
from django.utils.functional import Promise

from app.services import RedisService
from avatar.models import AvatarTheme, CustomAvatar
from dashboard.models import Activity, Bounty, HackathonEvent, Profile
from dashboard.utils import set_hackathon_event
from economy.models import EncodeAnything
from grants.models import Contribution, Grant, GrantCategory, GrantType
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

logger = logging.getLogger(__name__)


def fetch_jtbd_hackathons():
    db = JSONStore.objects.get(key='hackathons', view='hackathons')
    status = db.data[0]
    hackathons = db.data[1][0:2]
    fields = ['logo', 'name', 'slug', 'summary', 'start_date', 'end_date', 'sponsor_profiles']
    return [{k: v for k, v in event.items() if k in fields} for event in hackathons if status == 'upcoming' or status == 'current']


def create_jtbd_earn_cache():
    print('create_jtbd_earn_cache')
    import datetime
    from marketing.models import LeaderboardRank

    top_earners = list(LeaderboardRank.objects.active().filter(
        product='bounties', leaderboard='monthly_earners'
    ).values('rank', 'amount', 'github_username').order_by('-amount')[0:4].cache())

    thirty_days_ago = timezone.now() - datetime.timedelta(days=30)

    bounties = list(Bounty.objects.filter(
        network='mainnet', event=None, idx_status='open', created_on__gt=thirty_days_ago
    ).order_by('-_val_usd_db').values('_val_usd_db', 'title', 'issue_description')[0:2])

    # WalletConnect
    featured_grant = Grant.objects.filter(pk=275).first()

    data = {
        'top_earners': top_earners,
        'hackathons': fetch_jtbd_hackathons(),
        'bounties': bounties,
        'featured_grant': {
            'title': featured_grant.title,
            'description': featured_grant.description,
            'logo': featured_grant.logo.url if featured_grant.logo else None,
            'amount_received_in_round': featured_grant.amount_received_in_round,
            'amount_received': featured_grant.amount_received,
            'in_active_clrs': featured_grant.in_active_clrs,
        },
        'testimonial': {
            'handle': 'sebastian',
            'comment': "Since 2020 began, flipping bits on Gitcoin got me cool friends, a Macbook, rent without a 9 to 5 job, tons of fun, and crypto. Start hacking for the open internet folks. It’s the red pill.",
            'twitter': 'sebastian',
            'role': 'Python Developer',
        },
    }
    view = 'jtbd'
    keyword = 'earn'
    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    data = json.loads(json.dumps(data, cls=EncodeAnything))
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=data,
    )


def create_jtbd_learn_cache():
    print('create_jtbd_learn_cache')

    alumni = [
        {
            'name': 'Linda Xie',
            'role': 'Scalar Capital',
            'avatar_url': '',
        },
        {
            'name': 'Andy Tudhope',
            'role': 'Author of KERNEL Learn Track',
            'avatar_url': '',
        },
        {
            'name': 'Shawn Cheng',
            'role': 'Partner Consensys Mesh',
            'avatar_url': '',
        },
        {
            'name': 'Corey Petty',
            'role': 'CSO at Status',
            'avatar_url': '',
        }
    ]

    data = {
        'hackathons': fetch_jtbd_hackathons(),
        'alumni': alumni,
        'testimonial': {
            'name': 'Arya Soltanieh',
            'role': 'Founder, Myco Ex-Coinbase',
            'comment': "I’ve done a handful of these type of programs...but KERNEL has definitely felt the best. The community started at the top, has been so welcoming/ positive/ insightful/ AWESOME. Thank you to all the community members, and especially thank you to the team at the top, who’s personalities, content, and personal efforts helped create such a positive culture the last several weeks during KERNEL ❤️ I for one know that I will continue spreading the positive culture in everything I work on (myco)",
            'avatar_url': '',
            'twitter': '',
            'github': '',
        },
    }
    view = 'jtbd'
    keyword = 'learn'
    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    data = json.loads(json.dumps(data, cls=EncodeAnything))
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=data,
    )


def create_jtbd_connect_cache():
    print('create_jtbd_connect_cache')

    alumni = [
        {
            'name': 'Alex Masmej',
            'role': 'TryShowtime',
            'avatar_url': f'{settings.STATIC_URL}v2/images/jtbd/alexmasmej.png',
        },
        {
            'name': 'Simona Pop',
            'role': 'Status',
            'avatar_url': f'{settings.STATIC_URL}v2/images/jtbd/simonapop.png',
        },
        {
            'name': 'Devin Walsh',
            'role': 'Ex-Coinfund',
            'avatar_url': f'{settings.STATIC_URL}v2/images/jtbd/devinwalsh.png',
        },
        {
            'name': 'Val Mack',
            'role': 'Cornell Alum',
            'avatar_url': f'{settings.STATIC_URL}v2/images/jtbd/valmack.png',
        }
    ]

    data = {
        'projects': [
            {
                'name': 'Swivel Finance',
                'logo_url': static('v2/images/jtbd/swivel-finance.png'),
                'description': 'Swivel a the decentralized protocol for fixed-rate lending and interest-rate derivatives. Swivel v1 will facilitate trustless interest-rate swaps, allowing cautious lenders to lock in a guaranteed yield, and speculators to leverage their rate exposure.',
            },
            {
                'name': 'EPNS',
                'logo_url': static('v2/images/jtbd/epns.png'),
                'description': 'EPNS is a decentralized DeFi notifications protocol which enables users (wallet addresses) to receive notifications. Using the protocol, any dApp, smart contract or service can send notifications to users(wallet addresses) in a platform agnostic fashion (mobile, web, or user wallets)',
            },
        ],
        'alumni': alumni,
        'hackathons': fetch_jtbd_hackathons(),
        'testimonial': {
            'handle': 'John wilkinson',
            'role': 'Developer',
            'comment': "I LOVE IT… The community has been outstanding. I have made contact outside of slack with a couple people. William Schwab was kind enough to ZOOM with me for an hour and tell me his story, let me pick his brain, and he shared some valuable resources with me.",
            'avatar_url': '',
            'twitter': '',
            'github': '',
        },
    }
    view = 'jtbd'
    keyword = 'connect'
    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    data = json.loads(json.dumps(data, cls=EncodeAnything))
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=data,
    )


def create_jtbd_fund_cache():
    print('create_jtbd_fund_cache')

    # WalletConnect / ethers.js / TheDefiant
        # Q(pk=275) | Q(pk=13) | Q(pk=567)
    id_tuple= (275,13,567)
    # id_tuple= (6,13,4)
    projects = list(Grant.objects.filter(id__in=id_tuple).values(
        'id', 'logo', 'title', 'admin_profile__handle',
        'description', 'amount_received', 'amount_received_in_round', 'contributor_count',
        'positive_round_contributor_count', 'in_active_clrs', 'clr_prediction_curve'
    ).order_by('id', '-created_on').distinct('id'))
    print(projects)
    data = {
        'projects': projects,
        'builders': ['austintgriffith', 'alexmasmej', 'cryptomental', 'samczsun'],
        'testimonial': {
            'handle': 'sebastian',
            'role': 'Python Developer',
            'comment': "Transitioning to a career in crypto can be tough, but Gitcoin was a big help for me. Completing Gitcoin bounties and participating in Hackathons were invaluable for gaining exposure, experience, and of course making some money!",
            'twitter': '',
            'github': '',
        },
    }
    view = 'jtbd'
    keyword = 'fund'
    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    data = json.loads(json.dumps(data, cls=EncodeAnything))
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=data,
    )


def create_email_inventory_cache():
    print('create_email_inventory_cache')
    from marketing.models import EmailEvent, EmailInventory
    for ei in EmailInventory.objects.all().exclude(email_tag=''):
        stats = {}
        for i in [1, 7, 30]:
            key = f'{i}d'
            stats[key] = {}
            after = timezone.now() - timezone.timedelta(days=i)
            for what in ['delivered', 'open', 'click']:
                num = EmailEvent.objects.filter(created_on__gt=after, event=what, category__contains=ei.email_tag).count()
                stats[key][what] = num
        ei.stats = stats
        ei.save()


def create_grant_clr_cache():
    print('create_grant_clr_cache')
    from grants.tasks import update_grant_metadata
    pks = Grant.objects.filter(active=True, hidden=False).values_list('pk', flat=True)
    for pk in pks:
        update_grant_metadata.delay(pk)


def create_grant_type_cache():
    print('create_grant_type_cache')
    from grants.views import get_grant_types
    for network in ['rinkeby', 'mainnet']:
        view = f'get_grant_types_{network}'
        keyword = view
        data = get_grant_types(network, None)
        with transaction.atomic():
            JSONStore.objects.filter(view=view).all().delete()
            JSONStore.objects.create(
                view=view,
                key=keyword,
                data=data,
                )


def create_grant_active_clr_mapping():
    print('create_grant_active_clr_mapping')

    # removes grants who are not in an active matching round from having a match prediction curve
    # waits 14 days from removing them tho
    from grants.models import GrantCLRCalculation
    from_date = timezone.now() - timezone.timedelta(days=14)
    gclrs = GrantCLRCalculation.objects.filter(latest=True, grantclr__is_active=False, grantclr__end_date__lt=from_date)
    for gclr in gclrs:
        gclr.latest = False
        gclr.save()
        grant = gclr.grant
        grant.calc_clr_round()
        grant.save()

    return


def create_hack_event_cache():
    from dashboard.models import HackathonEvent
    for he in HackathonEvent.objects.all():
        he.save()


def create_grant_category_size_cache():
    print('create_grant_category_size_cache')
    grant_types = GrantType.objects.all()
    redis = RedisService().redis
    for g_type in grant_types:
        for category in GrantCategory.objects.all():
            key = f"grant_category_{g_type.name}_{category.category}"
            val = Grant.objects.filter(active=True, hidden=False, grant_type=g_type, categories__category__contains=category.category).count()
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
        operations = []
        operations.append(create_grant_active_clr_mapping)
        operations.append(create_grant_type_cache)
        operations.append(create_grant_clr_cache)
        operations.append(create_grant_category_size_cache)

        if not settings.DEBUG:
            operations.append(create_results_cache)
            operations.append(create_hack_event_cache)
            operations.append(create_hidden_profiles_cache)
            operations.append(create_tribes_cache)
            operations.append(create_activity_cache)
            operations.append(create_post_cache)
            operations.append(create_top_grant_spenders_cache)
            operations.append(create_avatar_cache)
            operations.append(create_quests_cache)
            operations.append(create_grants_cache)
            operations.append(create_contributor_landing_page_context)
            operations.append(create_hackathon_cache)
            operations.append(create_hackathon_list_page_cache)

            # generate jtbd data
            operations.append(create_jtbd_earn_cache)
            operations.append(create_jtbd_learn_cache)
            operations.append(create_jtbd_connect_cache)
            operations.append(create_jtbd_fund_cache)

            hour = int(timezone.now().strftime('%H'))
            if hour < 4:
                # do daily updates
                operations.append(create_email_inventory_cache)
        for func in operations:
            try:
                print(f'running {func}')
                func()
            except Exception as e:
                logger.exception(e)
