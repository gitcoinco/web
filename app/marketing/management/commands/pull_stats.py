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


def slack_users():
    sc = SlackClient(settings.SLACK_TOKEN)
    ul = sc.api_call("users.list")
    Stat.objects.create(
        key='slack_users',
        val=len(ul['members']),
        )


def bounties():
    from dashboard.models import Bounty

    Stat.objects.create(
        key='bounties',
        val=(Bounty.objects.filter(current_bounty=True).count()),
        )


def tips():
    from dashboard.models import Tip

    Stat.objects.create(
        key='tips',
        val=(Tip.objects.count()),
        )


def subs():
    from marketing.models import EmailSubscriber

    Stat.objects.create(
        key='email_subscriberse',
        val=(EmailSubscriber.objects.count()),
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

        fs = [slack_users, bounties, tips, subs, whitepaper_access, whitepaper_access_request]

        for f in fs:
            try:
                print(str(f.__name__))
                f()
            except Exception as e:
                print(e)
