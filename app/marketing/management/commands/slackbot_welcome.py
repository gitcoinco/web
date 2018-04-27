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
from django.conf import settings
from django.core.management.base import BaseCommand
from slackclient import SlackClient
import os
import time

MESSAGE="""
Welcome to Gitcoin! :gitcoin:

Gitcoin's mission is to *Grow Open Source*.

A few quick facts:
- We aren't an ICO.  There is no Gitcoin token.
- We are a community of blockchain developers.
- We are mission driven.  Check out our mission: https://gitcoin.co/mission

Here's how to get started in the community
- Say hey :wave: in #community-intros
- Join the community livestream every Friday at 5pm EST: https://gitcoin.co/livestream

We believe that a great way to build new skills is to learn by doing, and Gitcoin's core product (Bounties) supports that.

Here's how to get started with bounties:
- Check out the open bounties at https://gitcoin.co/explorer
- Post a bounty of your own at https://gitcoin.co/new
- Send a tip to any github username at https://gitcoin.co/tip

If you have any feedback for the team, or just want to say hi, this is them:
- @owocki, @vivek, @Pixelant, @mbeacom, @coderberry, @justin-bean

See you around! :spock-hand: 
Welcome_bot (and the Gitcoin Team)

"""

class Command(BaseCommand):

    help = 'pulls mailchimp emails'

    def handle(self, *args, **options):
        sc = SlackClient(settings.SLACK_WELCOMEBOT_TOKEN)
        if sc.rtm_connect():
            while True:
                new_evts = sc.rtm_read()
                for evt in new_evts:
                    if "type" in evt:
                        print("-" + evt['type'])
                        if evt['type'] == 'team_join':
                            user_info=sc.api_call("users.info", user=evt['user'])
                            channel = sc.api_call("im.open", user=evt['user']['id'])
                            channel_id = channel['channel']['id']
                            sc.api_call("chat.postMessage", channel=channel_id, unfurl_links=False, text=MESSAGE, as_user=True)
        else:
            print("Connection Failed, invalid token?")