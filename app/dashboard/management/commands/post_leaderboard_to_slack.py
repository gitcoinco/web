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

import logging
import warnings
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from marketing.models import LeaderboardRank
from slackclient import SlackClient

warnings.filterwarnings("ignore", category=DeprecationWarning) 
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def post_to_slack(channel, msg):
    try:
        sc = SlackClient(settings.SLACK_TOKEN)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            icon_url=settings.GITCOIN_SLACK_ICON_URL,
        )
        return True
    except Exception as e:
        print(e)
        return False


class Command(BaseCommand):

    help = 'posts leaderboards to slack once a week'

    def handle(self, *args, **options):
        #config
        num_items = 5
        channel = 'community-general'

        titles = {
            'weekly_earners': _('Top Earners'),
            'weekly_payers': _('Top Payers'),
            'weekly_orgs': _('Top Orgs'),
            'weekly_tokens': _('Top Tokens'),
        }
        msg = "**Gitcoin Leaderboard for the Past Week**\n"
        for key, title in titles.items():
            msg += f"\n{title}\n"
            leadeboardranks = LeaderboardRank.objects.active().filter(leaderboard=key).order_by('-amount')[0:num_items]
            counter = 1
            for lr in leadeboardranks:
                msg += f"{counter}. {lr.github_username}: ${round(lr.amount,2)}\n"
                counter += 1
        msg += "\n View Leaderboard: https://gitcoin.co/leaderboard "
        print(msg)
        success = post_to_slack(channel, msg)
        print(success)
