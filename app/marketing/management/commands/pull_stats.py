'''
    Copyright (C) 2017 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation,either version 3 of the License,or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not,see <http://www.gnu.org/licenses/>.

'''
import logging
import warnings

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from marketing.models import Stat
from slackclient import SlackClient

warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def gitter():
    from gitterpy.client import GitterClient

    # Once create instance
    gitter = GitterClient(settings.GITTER_TOKEN)

    # Check_my id
    val = gitter.rooms.grab_room('gitcoinco/Lobby')['userCount']

    Stat.objects.create(
        key='gitter_users',
        val=val,
        )


def google_analytics():
    from marketing.google_analytics import run

    view_id = '166793585'  # ethwallpaer
    val = run(view_id)
    print(val)
    Stat.objects.create(
        key='google_analytics_sessions_ethwallpaper',
        val=val,
        )

    view_id = '154797887'  # gitcoin
    val = run(view_id)
    print(val)
    Stat.objects.create(
        key='google_analytics_sessions_gitcoin',
        val=val,
        )


def slack_users():
    sc = SlackClient(settings.SLACK_TOKEN)
    ul = sc.api_call("users.list")
    Stat.objects.create(
        key='slack_users',
        val=len(ul['members']),
        )


def slack_users_active():
    from marketing.models import SlackUser

    one_day_ago = timezone.now() - timezone.timedelta(hours=24)
    num_active = SlackUser.objects.filter(last_seen__gt=one_day_ago).count()
    num_away = SlackUser.objects.filter(last_seen__lt=one_day_ago).count()
    num_away += SlackUser.objects.filter(last_seen=None).count()

    # create broader Stat object
    Stat.objects.create(
        key='slack_users_active',
        val=num_active,
        )

    Stat.objects.create(
        key='slack_users_away',
        val=num_away,
        )


def profiles_ingested():
    from dashboard.models import Profile

    Stat.objects.create(
        key='profiles_ingested',
        val=Profile.objects.count(),
        )


def faucet():
    from faucet.models import FaucetRequest

    Stat.objects.create(
        key='FaucetRequest',
        val=FaucetRequest.objects.count(),
        )

    Stat.objects.create(
        key='FaucetRequest_rejected',
        val=FaucetRequest.objects.filter(rejected=True).count(),
        )

    Stat.objects.create(
        key='FaucetRequest_fulfilled',
        val=FaucetRequest.objects.filter(fulfilled=True).count(),
        )

    Stat.objects.create(
        key='FaucetRequest_pending',
        val=FaucetRequest.objects.filter(fulfilled=False, rejected=False).count(),
        )


def user_actions():
    from dashboard.models import UserAction

    action_types = UserAction.objects.distinct('action').values_list('action', flat=True)
    for action_type in action_types:

        val = UserAction.objects.filter(
            action=action_type,
            ).count()

        Stat.objects.create(
            key=f'user_action_{action_type}',
            val=val,
        )


def github_stars():
    from github.utils import get_user
    reops = get_user('gitcoinco', '/repos')
    forks_count = sum([repo['forks_count'] for repo in reops])

    Stat.objects.create(
        key='github_forks_count',
        val=forks_count,
        )

    stargazers_count = sum([repo['stargazers_count'] for repo in reops])

    Stat.objects.create(
        key='github_stargazers_count',
        val=stargazers_count,
        )


def github_issues():
    from github.utils import get_issues, get_user
    repos = []

    for org in ['bitcoin', 'gitcoinco', 'ethereum']:
        for repo in get_user(org, '/repos'):
            repos.append((org, repo['name']))

    for org, repo in repos:
        issues = []
        cont = True
        page = 1
        while cont:
            new_issues = get_issues(org, repo, page, 'all')
            issues = issues + new_issues
            page += 1
            cont = len(new_issues)

        val = len(issues)
        key = f"github_issues_{org}_{repo}"
        try:
            Stat.objects.create(
                created_on=timezone.now(),
                key=key,
                val=(val),
                )
        except Exception:
            pass
        if not val:
            break
        print(key, val)


def chrome_ext_users():
    import requests
    from bs4 import BeautifulSoup

    url = 'https://chrome.google.com/webstore/detail/gitcoin/gdocmelgnjeejhlphdnoocikeafdpaep'
    html_response = requests.get(url)
    soup = BeautifulSoup(html_response.text, 'html.parser')
    classname = 'e-f-ih'
    eles = soup.findAll("span", {"class": classname})
    num_users = eles[0].text.replace(' users', '')
    Stat.objects.create(
        key='browser_ext_chrome',
        val=num_users,
        )


def firefox_ext_users():
    import requests
    from bs4 import BeautifulSoup

    url = 'https://addons.mozilla.org/en-US/firefox/addon/gitcoin/'
    html_response = requests.get(url)
    soup = BeautifulSoup(html_response.text, 'html.parser')
    eles = soup.findAll("div", {"class": 'AddonMeta'})[0].findAll('dt', {"class": 'MetadataCard-title'})
    num_users = eles[0].text.replace(' Users', '').replace('No', '0')
    Stat.objects.create(
        key='browser_ext_firefox',
        val=num_users,
        )


def medium_subscribers():
    import requests
    import json

    url = 'https://medium.com/gitcoin?format=json'
    html_response = requests.get(url)
    data = json.loads(html_response.text.replace('])}while(1);</x>', ''))
    num_users = data['payload']['references']['Collection']['d414fce43ce1']['metadata']['followerCount']
    print(num_users)
    Stat.objects.create(
        key='medium_subscribers',
        val=num_users,
        )


def twitter_followers():
    if settings.DEBUG:
        return
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

    for username in ['owocki', 'gitcoinfeed']:
        user = api.GetUser(screen_name=username)

        Stat.objects.create(
            key='twitter_followers_{}'.format(username),
            val=(user.followers_count),
            )


def bounties():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties',
        val=(Bounty.objects.filter(current_bounty=True, network='mainnet').count()),
        )


def bounties_hourly_rate():
    from dashboard.models import Bounty
    that_time = timezone.now()
    bounties = Bounty.objects.filter(
        fulfillment_accepted_on__gt=(that_time - timezone.timedelta(hours=24)),
        fulfillment_accepted_on__lt=that_time)
    hours = 0
    value = 0
    for bounty in bounties:
        try:
            hours += bounty.fulfillments.filter(accepted=True).first().fulfiller_hours_worked
            value += bounty.value_in_usdt
        except Exception:
            pass
    print(that_time, bounties.count(), value, hours)
    if value and hours:
        val = round(float(value)/float(hours), 2)
        try:
            key = 'bounties_hourly_rate_inusd_last_24_hours'
            Stat.objects.create(
                created_on=that_time,
                key=key,
                val=(val),
                )
        except Exception:
            pass


def bounties_by_status():
    from dashboard.models import Bounty
    statuses = Bounty.objects.distinct('idx_status').values_list('idx_status', flat=True)
    for status in statuses:
        eligible_bounties = Bounty.objects.filter(current_bounty=True, network='mainnet', web3_created__lt=(timezone.now() - timezone.timedelta(days=7)))
        numerator_bounties = eligible_bounties.filter(idx_status=status)
        val = int(100 * (numerator_bounties.count()) / (eligible_bounties.count()))

        Stat.objects.create(
            key='bounties_{}_pct'.format(status),
            val=val,
            )

        Stat.objects.create(
            key='bounties_{}_total'.format(status),
            val=numerator_bounties.count(),
            )


def joe_dominance_index():
    from dashboard.models import Bounty

    joe_addresses = ['0x4331B095bC38Dc3bCE0A269682b5eBAefa252929'.lower(), '0xe93d33CF8AaF56C64D23b5b248919EabD8c3c41E'.lower()]  # kevin
    joe_addresses = joe_addresses + ['0x28e21609ca8542Ce5A363CBf339529204b043eDe'.lower()]  # eric
    joe_addresses = joe_addresses + ['0x60206c1F2B51Ac470cB0f71323474f7f9e4772e1'.lower()]  # vivek
    joe_addresses = joe_addresses + ['0x93d0deF1d76B510e2a7A6d01Cf18c54ec23f4253'.lower()]  # mark beacom
    joe_addresses = joe_addresses + ['0x58dC037f0A5c6C03D0f9477aea3198648CF0D263'.lower()]  # alisa

    for days in [7, 30, 90, 360]:
        all_bounties = Bounty.objects.filter(current_bounty=True, network='mainnet', web3_created__gt=(timezone.now() - timezone.timedelta(days=days)))
        joe_bounties = all_bounties.filter(bounty_owner_address__in=joe_addresses)
        if not all_bounties.count():
            continue

        val = int(100 * (joe_bounties.count()) / (all_bounties.count()))

        Stat.objects.create(
            key='joe_dominance_index_{}_count'.format(days),
            val=val,
            )

        val = int(100 * sum([(b.value_in_usdt_now if b.value_in_usdt_now else 0) for b in joe_bounties]) / sum([(b.value_in_usdt_now if b.value_in_usdt_now else 0) for b in all_bounties]))
        Stat.objects.create(
            key='joe_dominance_index_{}_value'.format(days),
            val=val,
            )


def avg_time_bounty_turnaround():
    import statistics
    from dashboard.models import Bounty

    for days in [7, 30, 90, 360]:
        all_bounties = Bounty.objects.filter(
            current_bounty=True,
            network='mainnet',
            idx_status='done',
            web3_created__gt=(timezone.now() - timezone.timedelta(days=days))
        )
        if not all_bounties.count():
            continue

        turnaround_times = [b.turnaround_time_submitted for b in all_bounties if b.turnaround_time_submitted]
        val = int(statistics.median(turnaround_times) / 60 / 60)  # seconds to hours

        Stat.objects.create(
            key=f'turnaround_time__submitted_hours_{days}_days_back',
            val=val,
        )

        turnaround_times = [b.turnaround_time_accepted for b in all_bounties if b.turnaround_time_accepted]
        val = int(statistics.median(turnaround_times) / 60 / 60)  # seconds to hours

        Stat.objects.create(
            key=f'turnaround_time__accepted_hours_{days}_days_back',
            val=val,
        )

        turnaround_times = [b.turnaround_time_started for b in all_bounties if b.turnaround_time_started]
        val = int(statistics.median(turnaround_times) / 60 / 60)  # seconds to hours

        Stat.objects.create(
            key=f'turnaround_time__started_hours_{days}_days_back',
            val=val,
        )


def bounties_open():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties_open',
        val=(Bounty.objects.filter(current_bounty=True, network='mainnet', idx_status='open').count()),
        )


def bounties_fulfilled():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties_fulfilled',
        val=(Bounty.objects.filter(current_bounty=True, network='mainnet', idx_status='done').count()),
        )


def tips():
    from dashboard.models import Tip

    Stat.objects.create(
        key='tips',
        val=(Tip.objects.filter(network='mainnet').count()),
        )


def tips_received():
    from dashboard.models import Tip

    Stat.objects.create(
        key='tips_received',
        val=(Tip.objects.filter(network='mainnet').exclude(receive_txid='').count()),
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


def get_skills_keyword_counts():
    from marketing.models import EmailSubscriber
    keywords = {}
    for es in EmailSubscriber.objects.all():
        for keyword in es.keywords:
            keyword = keyword.strip().lower().replace(" ", "_")
            if keyword not in keywords.keys():
                keywords[keyword] = 0
            keywords[keyword] += 1
    for keyword, val in keywords.items():
        print(keyword, val)
        Stat.objects.create(
            key=f"subscribers_with_skill_{keyword}",
            val=(val),
            )


def get_bounty_keyword_counts():
    from dashboard.models import Bounty
    keywords = {}
    for bounty in Bounty.objects.filter(current_bounty=True).all():
        for keyword in str(bounty.keywords).split(","):
            keyword = keyword.strip().lower().replace(" ", "_")
            if keyword not in keywords.keys():
                keywords[keyword] = 0
            keywords[keyword] += 1
    for keyword, val in keywords.items():
        print(keyword, val)
        Stat.objects.create(
            key=f"bounties_with_skill_{keyword}",
            val=(val),
            )


def email_events():
    from marketing.models import EmailEvent

    events = EmailEvent.objects.distinct('event').values_list('event',flat=True)
    for event in events:
        val = EmailEvent.objects.filter(event=event).count()
        print(val)
        Stat.objects.create(
            key='email_{}'.format(event),
            val=(val),
            )


class Command(BaseCommand):

    help = 'pulls all stats'

    def handle(self, *args, **options):

        fs = [
            get_bounty_keyword_counts,
            get_skills_keyword_counts,
            github_issues,
            gitter,
            medium_subscribers,
            google_analytics,
            github_stars,
            profiles_ingested,
            chrome_ext_users,
            firefox_ext_users,
            slack_users,
            slack_users_active,
            twitter_followers,
            bounties,
            tips,
            subs,
            whitepaper_access,
            whitepaper_access_request,
            tips_received,
            bounties_fulfilled,
            bounties_open,
            bounties_by_status,
            subs_active,
            subs_newsletter,
            joe_dominance_index,
            avg_time_bounty_turnaround,
            user_actions,
            faucet,
            email_events,
            bounties_hourly_rate,
        ]

        for f in fs:
            try:
                print("*"+str(f.__name__)+"*")
                f()
            except Exception as e:
                print(e)
