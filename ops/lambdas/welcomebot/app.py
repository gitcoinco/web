# -*- coding: utf-8 -*-
"""Define the Gitcoin Slack Welcome Bot flask app.

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

"""
import os

from flask import Flask, abort, jsonify, redirect, request
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter

SLACK_VERIFICATION_TOKEN = os.environ.get('SLACK_VERIFICATION_TOKEN', '')
SLACK_WELCOMEBOT_TOKEN = os.environ.get('SLACK_WELCOMEBOT_TOKEN', '')
SLACK_TEAM_ID = os.environ.get('SLACK_TEAM_ID', '')
INDEX_REDIRECT_URL = os.environ.get('INDEX_REDIRECT_URL', 'https://gitcoin.co/slack')

app = Flask(__name__)


def get_default_message():
    """Return the Gitcoin Welcomebot message."""
    return """
Welcome to Gitcoin! :gitcoin:

Gitcoin's mission is to *Grow Open Source*.

A few quick facts:
- We are mission driven.  Check out our mission: https://gitcoin.co/mission
- We aren't an ICO.  There is no Gitcoin token.
- We are a community of blockchain developers.

Here's how to get started in the community
- Say hey :wave: in #community-intros
- Join the community livestream every Friday at 5pm EST: https://gitcoin.co/livestream

We believe that a great way to build new skills is to learn by doing, and Gitcoin's core product (Bounties) supports that.

Here's how to get started with bounties:
- Developer? Start by completing the contributor onboarding at https://gitcoin.co/onboard/contributor and check out the open bounties at https://gitcoin.co/explorer
- Repo Owner? Accelerate your dev progress by posting a bounty of your own at https://gitcoin.co/new
- Send a tip to any github username with https://gitcoin.co/tip

We have more details in our onboarding guide at https://gitcoin.co/docs/onboard . We also have a FAQ and tutorials available at https://gitcoin.co/help

If you have any feedback for the team, or just want to say hi, this is them:
- <@U55F2LT5L>, <@U88M8173P>, <@U8J2TK1L6>, <@U87BL3KS6>, <@U7Z23ATPB>, <@U9UKDGS01>, <@U88BVQAJD>, <@U9PL1BSAC>, <@U7J5ZPCPQ>, <@U85EFS1MM>

See you around! :spock-hand:
Welcome_bot (and the Gitcoin Team)

"""


MESSAGE = get_default_message()


def is_request_valid(request, team_id=''):
    token_valid = request.form['token'] == SLACK_VERIFICATION_TOKEN
    team_id_valid = True

    if team_id:
        team_id_valid = request.form['team_id'] == team_id

    return token_valid and team_id_valid


@app.route('/')
def index():
    """Handle the index route."""
    return redirect(INDEX_REDIRECT_URL, code=302)


@app.route('/welcomebot', methods=['POST'])
def welcomebot():
    if not is_request_valid(request):
        abort(400)
    return jsonify(response_type='ephemeral', text=MESSAGE)


slack_events_adapter = SlackEventAdapter(
    SLACK_VERIFICATION_TOKEN, '/slack/events', app)


@slack_events_adapter.on('team_join')
def new_user_welcome(event):
    """Handle team_join slack events by sending the user our welcome message."""
    sc = SlackClient(SLACK_WELCOMEBOT_TOKEN)
    user = event.get('event', {}).get('user', {}).get('id', '')
    if user:
        channel = sc.api_call('im.open', user=user)
        channel_id = channel['channel']['id']
        sc.api_call(
            'chat.postMessage', channel=channel_id, unfurl_links=False, text=MESSAGE, as_user=True
        )


# Serve the slack welcomebot flask app.
if __name__ == '__main__':
    app.run()
