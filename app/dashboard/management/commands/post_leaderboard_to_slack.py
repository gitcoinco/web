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
        token = settings.SLACK_TOKEN
        sc = SlackClient(token)
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg,
            icon_url=settings.GITCOIN_SLACK_ICON_URL,
            mrkdwn=True,
            username="gitcoinbot"
        )
        return True
    except Exception as e:
        print(e)
        return False


class Command(BaseCommand):

    help = 'posts leaderboards to slack once a week'

    def handle(self, *args, **options):
        #config
        num_items = 7
        channel = 'community-general' if not settings.DEBUG else 'testkevin'

        num_to_emoji = {
            1: 'first_place_medal',
            2: 'second_place_medal',
            3: 'third_place_medal',
        }

        titles = {
            'weekly_earners': _('Top Earners :money_with_wings: '),
            'weekly_payers': _('Top Funders :moneybag: '),
            'weekly_orgs': _('Top Orgs :office: '),
            'weekly_tokens': _('Top Tokens :bank: '),
        }
        msg = "_Gitcoin Leaderboard for the Past Week_\n"
        for key, title in titles.items():
            msg += f"\n*{title}*\n"
            leadeboardranks = LeaderboardRank.objects.active().filter(leaderboard=key).order_by('-amount')[0:num_items]
            counter = 1
            for lr in leadeboardranks:
                emoji = num_to_emoji.get(counter, '')
                emoji = f":{emoji}:" if emoji else "      "
                url = f"https://gitocoin.co/{lr.github_username}"
                user_link = f"[{lr.github_username}]({url})"
                user_link = f"{lr.at_ify_username}"
                amount = '{:8}'.format(f"_{round(lr.amount)}_")
                msg += f"{counter}.   {emoji}   ${amount}   {user_link}\n"
                counter += 1
        msg += "\n :chart_with_upwards_trend:  View Leaderboard: https://gitcoin.co/leaderboard "
        msg += "\n=========================================\n If you are in the top 3 in any category, DM @owocki for some Gitcoin schwag !! "
        msg += "\n=========================================\n\n :four_leaf_clover: Good luck and see you next week! \n\n:love_gitcoin: ~gitcoinbot "
        print(msg)
        success = post_to_slack(channel, msg)
        print(success)
