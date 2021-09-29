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

import datetime
import json
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.templatetags.static import static
from django.utils import timezone

from dashboard.models import Bounty
from economy.models import EncodeAnything
from grants.models import Grant
from marketing.models import LeaderboardRank
from perftools.models import JSONStore

logger = logging.getLogger(__name__)


def fetch_jtbd_hackathons():
    db = JSONStore.objects.get(key='hackathons', view='hackathons')
    status = db.data[0]
    hackathons = db.data[1][0:3]
    fields = ['logo', 'name', 'slug', 'summary', 'start_date', 'end_date', 'sponsor_profiles', 'background_color' ]
    return [{k: v for k, v in event.items() if k in fields} for event in hackathons if status == 'upcoming' or status == 'current']


def create_jtbd_earn_cache():
    print('create_jtbd_earn_cache')

    top_earners = list(LeaderboardRank.objects.active().filter(
        product='bounties', leaderboard='monthly_earners'
    ).values('rank', 'amount', 'github_username').order_by('-amount')[0:4].cache())

    thirty_days_ago = timezone.now() - datetime.timedelta(days=30)

    bounties = list(Bounty.objects.filter(
        network='mainnet', event=None, idx_status='open', created_on__gt=thirty_days_ago,
        current_bounty=True
    ).order_by('-_val_usd_db').extra(
        select={'val_usd_db': '_val_usd_db'}
    ).values(
        'val_usd_db', 'title', 'token_name', 'value_true', 'bounty_owner_github_username', 'metadata'
    )[0:4])

    featured_grant = None

    if not settings.DEBUG:
        # WalletConnect
        grant_id = 275
    else:
        grant_id = 1

    try:
        grant_data = Grant.objects.filter(pk=grant_id).values(
            'id', 'logo', 'title', 'admin_profile__handle',
            'description', 'amount_received', 'amount_received_in_round', 'contributor_count',
            'positive_round_contributor_count', 'in_active_clrs', 'clr_prediction_curve'
        ).first()
    except Grant.DoesNotExist:
        grant_data = None

    featured_grant = grant_data

    data = {
        'top_earners': top_earners,
        'hackathons': fetch_jtbd_hackathons(),
        'bounties': bounties,
        'featured_grant': featured_grant,
        'testimonial': {
            'handle': '@cryptomental',
            'comment': "I think the great thing about Gitcoin is how easy it is for projects to reach out to worldwide talent. Gitcoin helps to find people who have time to contribute and increase speed of project development. Thanks to Gitcoin a bunch of interesting OpenSource projects got my attention!",
            'avatar_url': '',
            'github_handle': 'cryptomental',
            'twitter_handle': '',
            'role': 'Front End Developer',
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
            'role': '@ljxie',
            'avatar_url': static('v2/images/jtbd/ljxie.png'),
        },
        {
            'name': 'Simona Pop',
            'role': '@sim_pop',
            'avatar_url': static('v2/images/jtbd/simonapop.png'),
        },
        {
            'name': 'Sebnem Rusitschka',
            'role': '@sebnem',
            'avatar_url': static('v2/images/jtbd/sebnem.png'),
        },
        {
            'name': 'Pranay Valson',
            'role': '@valsonay',
            'avatar_url': static('v2/images/jtbd/valsonay.png'),
        }
    ]

    data = {
        'hackathons': fetch_jtbd_hackathons(),
        'alumni': alumni,
        'testimonial': {
            'handle': 'Arya Soltanieh',
            'role': 'Founder, Myco Ex-Coinbase',
            'comment': "I’ve done a handful of these type of programs... but KERNEL has definitely felt the best.\r\n The community started at the top, has been so welcoming/ positive/ insightful/ AWESOME. Thank you to all the community members, and especially thank you to the team at the top, who’s personalities, content, and personal efforts helped create such a positive culture the last several weeks during KERNEL ❤️ I for one know that I will continue spreading the positive culture in everything I work on (myco).",
            'avatar_url': static('v2/images/jtbd/arya.png'),
            'github_handle': 'lostcodingsomewhere',
            'twitter_handle': '',
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
            'avatar_url': static('v2/images/jtbd/alexmasmej.png'),
        },
        {
            'name': 'Simona Pop',
            'role': 'Status',
            'avatar_url': static('v2/images/jtbd/simonapop.png'),
        },
        {
            'name': 'Devin Walsh',
            'role': 'Ex-Coinfund',
            'avatar_url': static('v2/images/jtbd/devinwalsh.png'),
        },
        {
            'name': 'Val Mack',
            'role': 'Cornell Alum',
            'avatar_url': static('v2/images/jtbd/valmack.png'),
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
            'handle': 'Magenta Ceiba',
            'role': 'Developer',
            'comment': "I was surprised to learn I could progres on building the next phase of Bloom Network in parallel to deep dive of learning more about Web3 quickly. This fellowship has so far been the fastest skill upleveling experience I’ve ever had. Also wins - developing deeper relationships with people and projects I already knew of.",
            'avatar_url': '',
            'github_handle': 'magentaceiba',
            'twitter_handle': '',
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
    if not settings.DEBUG:
        # WalletConnect / ethers.js / TheDefiant
        id_tuple= (275,13,567)
    else:
        id_tuple= (6,13,4)

    projects = list(Grant.objects.filter(id__in=id_tuple).values(
        'id', 'logo', 'title', 'admin_profile__handle',
        'description', 'amount_received', 'amount_received_in_round', 'contributor_count',
        'positive_round_contributor_count', 'in_active_clrs', 'clr_prediction_curve'
    ).order_by('id', '-created_on').distinct('id'))

    data = {
        'projects': projects,
        'builders': ['austintgriffith', 'alexmasmej', 'cryptomental', 'samczsun'],
        'testimonial': {
            'handle': 'Austin Griffith',
            'role': 'Javascript Developer',
            'comment': "As one of the first quadratic freelancers to go through the platform, I know from personal experience that Gitcoin Grants empowers builders to create the future on Ethereum. My grant enabled me to leave my job and build open source tutorials and prototypes for the open internet. Super excited to see quadratic funding continue to help high leverage outliers find their place in our ecosystem",
            'avatar_url': '',
            'github_handle': 'austintgriffith',
            'twitter_handle': 'austingriffith',
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


def create_about_cache():
    print('create_about_cache')

    three_months_ago = timezone.now() - datetime.timedelta(days=360)
    grants_bubbles = list(Grant.objects.filter(
        network='mainnet', hidden=False, visible=True, active=True
    ).values('logo', 'id').order_by('weighted_shuffle', 'pk')[:33])

    top_earners = list(LeaderboardRank.objects.active().filter(
        product='bounties', leaderboard='monthly_earners'
    ).values('profile__handle', 'profile__organizations', 'profile__data').order_by('-amount')[0:16])

    data = {
        'grants_bubbles': grants_bubbles,
        'top_earners': top_earners
    }

    view = 'about'
    keyword = 'general'
    JSONStore.objects.filter(view=view, key=keyword).all().delete()
    data = json.loads(json.dumps(data, cls=EncodeAnything))
    JSONStore.objects.create(
        view=view,
        key=keyword,
        data=data,
    )


class Command(BaseCommand):

    help = 'generates jtbd data'

    def handle(self, *args, **options):
        operations = []
        # generate jtbd data
        operations.append(create_jtbd_earn_cache)
        operations.append(create_jtbd_learn_cache)
        operations.append(create_jtbd_connect_cache)
        operations.append(create_jtbd_fund_cache)
        operations.append(create_about_cache)

        for func in operations:
            try:
                print(f'running {func}')
                func()
            except Exception as e:
                logger.exception(e)
