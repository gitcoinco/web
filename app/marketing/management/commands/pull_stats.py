'''
    Copyright (C) 2017 Gitcoin Core 

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
from marketing.models import Stat
from slackclient import SlackClient
from django.conf import settings
from django.utils import timezone


def slack_users():
    sc = SlackClient(settings.SLACK_TOKEN)
    ul = sc.api_call("users.list")
    Stat.objects.create(
        key='slack_users',
        val=len(ul['members']),
        )


def slack_users_active():
    if settings.DEBUG:
        return

    sc = SlackClient(settings.SLACK_TOKEN)
    ul = sc.api_call("users.list")
    presence = [sc.api_call("users.getPresence", user=user['id']).get('presence',None) for user in ul['members']]
    num_active = len([item for item in presence if item == 'active'])
    num_away = len([item for item in presence if item == 'away'])

    Stat.objects.create(
        key='slack_users_active',
        val=num_active,
        )

    Stat.objects.create(
        key='slack_users_away',
        val=num_away,
        )


def twitter_followers():
    import twitter

    api = twitter.Api(
        consumer_key=settings.TWITTER_CONSUMER_KEY,
        consumer_secret=settings.TWITTER_CONSUMER_SECRET,
        access_token_key=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_SECRET,
    )
    user = api.GetUser(screen_name=settings.TWITTER_USERNAME)

    Stat.objects.create(
        key='twitter_followers',
        val=(user.followers_count),
        )


def bounties():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties',
        val=(Bounty.objects.filter(current_bounty=True).count()),
        )


def bounties_fulfilled_pct():
    from dashboard.models import Bounty
    for status in ['fulfilled', 'expired', 'open', 'claimed']:
        eligible_bounties = Bounty.objects.filter(current_bounty=True, web3_created__lt=(timezone.now() - timezone.timedelta(days=7)))
        fulfilled_bounties = eligible_bounties.filter(idx_status=status)
        val = int(100 * (fulfilled_bounties.count()) / (eligible_bounties.count()))

        Stat.objects.create(
            key='bounties_{}_pct'.format(status),
            val=val,
            )


def bounties_open():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties_open',
        val=(Bounty.objects.filter(current_bounty=True, idx_status='open').count()),
        )


def bounties_claimed():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties_claimed',
        val=(Bounty.objects.filter(current_bounty=True).exclude(claimeee_address='0x0000000000000000000000000000000000000000').count()),
        )


def bounties_fulfilled():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties_fulfilled',
        val=(Bounty.objects.filter(current_bounty=True,idx_status='fulfilled').count()),
        )


def tips():
    from dashboard.models import Tip

    Stat.objects.create(
        key='tips',
        val=(Tip.objects.count()),
        )


def tips_received():
    from dashboard.models import Tip

    Stat.objects.create(
        key='tips_received',
        val=(Tip.objects.exclude(receive_txid='').count()),
        )


def subs():
    from marketing.models import EmailSubscriber

    Stat.objects.create(
        key='email_subscriberse',
        val=(EmailSubscriber.objects.count()),
        )


def subs_active():
    from marketing.models import EmailSubscriber

    Stat.objects.create(
        key='email_subscribers_active',
        val=(EmailSubscriber.objects.filter(active=True).count()),
        )


def subs_newsletter():
    from marketing.models import EmailSubscriber

    Stat.objects.create(
        key='email_subscribers_newsletter',
        val=(EmailSubscriber.objects.filter(newsletter=True).count()),
        )


def whitepaper_access():
    from tdi.models import WhitepaperAccess

    Stat.objects.create(
        key='whitepaper_access',
        val=(WhitepaperAccess.objects.count()),
        )


def whitepaper_access_request():
    from tdi.models import WhitepaperAccessRequest

    Stat.objects.create(
        key='whitepaper_access_request',
        val=(WhitepaperAccessRequest.objects.count()),
        )


class Command(BaseCommand):

    help = 'pulls all stats'

    def handle(self, *args, **options):

        fs = [
            slack_users, 
            twitter_followers, 
            bounties, 
            tips, 
            subs, 
            whitepaper_access, 
            whitepaper_access_request, 
            tips_received, 
            bounties_claimed, 
            bounties_fulfilled, 
            bounties_open, 
            bounties_fulfilled_pct,
            subs_active, 
            subs_newsletter, 
            slack_users_active
        ]

        for f in fs:
            try:
                print(str(f.__name__))
                f()
            except Exception as e:
                print(e)
