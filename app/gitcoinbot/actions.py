# -*- coding: utf-8 -*-
"""Define the Gitcoin Bot action methods for interacting with the Github API as a Github App.

Copyright (C) 2018 Gitcoin Core

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
import datetime
import json
import re

from django.conf import settings

import jwt
import requests
import rollbar
from github.utils import post_issue_comment_reaction


def help_text():
    github_bot_user = f"@{settings.GITHUB_API_USER}"
    help_text_response = f"I am {github_bot_user}, a bot that facilitates gitcoin bounties.\n" \
        "\n<hr>Here are the commands I understand:\n\n " \
        "* `bounty <amount> ETH` -- receive link to gitcoin.co form to create bounty.\n " \
        "* `claim` -- receive link to gitcoin.co to start work on a bounty.\n " \
        "* `tip <user> <amount> ETH` -- receive link to complete tippping another github user *<amount>* ETH.\n " \
        "* `help` -- displays a help menu\n\n<br>" \
        "Learn more at: [https://gitcoin.co](https://gitcoin.co)\n" \
        f":zap::heart:, {github_bot_user}\n"
    return help_text_response


def new_bounty_text(owner, repo, issue_id, comment_text):
    issue_link = f"https://github.com/{owner}/{repo}/issues/{issue_id}"
    bounty_amount = parse_comment_amount(comment_text)
    bounty_link = f"{settings.BASE_URL}funding/new?source={issue_link}&amount={bounty_amount}"
    new_bounty_response = f"To create the bounty please [visit this link]({bounty_link}).\n\n " \
        "PS Make sure you're logged into Metamask!"
    return new_bounty_response


def parse_comment_amount(comment_text):
    re_amount = r'\d*\.?\d+'
    result = re.findall(re_amount, comment_text)
    return result[0]


def parse_tippee_username(comment_text):
    re_username = r'[@][a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}'
    username = re.findall(re_username, comment_text)
    return username[-1]


def new_tip_text(owner, repo, issue_id, comment_text):
    tip_amount = parse_comment_amount(comment_text)
    username = parse_tippee_username(comment_text)
    issue_url = f'https://github.com/{owner}/{repo}/issues/{issue_id}'
    tip_link = f'{settings.BASE_URL}tip/?amount={tip_amount}&username={username}&source={issue_url}'
    tip_response = f'To complete the tip, please [visit this link]({tip_link}).\n ' \
        'PS Make sure you\'re logged into Metamask!'
    return tip_response


def claim_bounty_text(owner, repo, issue_id):
    issue_url = f'https://github.com/{owner}/{repo}/issues/{issue_id}'
    claim_link = f'{settings.BASE_URL}funding/details/?url={issue_url}'
    claim_response = f'To finish claiming this bounty please [visit this link]({claim_link})'
    return claim_response


def confused_text():
    return 'Sorry I did not understand that request. Please try again or use `@gitcoinbot help` ' \
        'to see supported commands.'


def post_gitcoin_app_comment(owner, repo, issue_id, content, install_id):
    token = create_token(install_id)
    if not token:
        rollbar.report_message('Failed to create Github Bot token', 'warning')
        return {}
    url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_id}/comments'
    github_app_headers = {
        'Authorization': 'token ' + token,
        'Accept': 'application/vnd.github.machine-man-preview+json'
    }
    body = {'body': content}
    response = requests.post(url, data=json.dumps(body), headers=github_app_headers)
    return response.json


def create_token(install_id):
    # Token expires after 10 minutes
    payload = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=500),
        'iss': settings.GITCOINBOT_APP_ID,
    }
    jwt_token = jwt.encode(payload, settings.SECRET_KEYSTRING, algorithm='RS256')
    jwt_token_string = jwt_token.decode('utf-8')
    url = f'https://api.github.com/installations/{install_id}/access_tokens'
    github_app_headers = {
        'Authorization': f'Bearer {jwt_token_string}',
        'Accept': 'application/vnd.github.machine-man-preview+json'}
    response = requests.post(url, headers=github_app_headers)
    token = json.loads(response.content).get('token', '')
    return token


def determine_response(owner, repo, comment_id, comment_text, issue_id, install_id):
    help_regex = r'@?[Gg]itcoinbot\s[Hh]elp'
    bounty_regex = r'@?[Gg]itcoinbot\s[Bb]ounty\s\d*\.?(\d+\s?)'
    claim_regex = r'@?[Gg]itcoinbot\s[Cc]laim'
    tip_regex = r'@?[Gg]itcoinbot\s[Tt]ip\s@\w*\s\d*\.?(\d+\s?)'

    if re.match(help_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        post_gitcoin_app_comment(owner, repo, issue_id, help_text(), install_id)
    elif re.match(bounty_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        bounty_text = new_bounty_text(owner, repo, issue_id, comment_text)
        post_gitcoin_app_comment(owner, repo, issue_id, bounty_text, install_id)
    elif re.match(claim_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        claim_text = claim_bounty_text(owner, repo, issue_id)
        post_gitcoin_app_comment(owner, repo, issue_id, claim_text, install_id)
    elif re.match(tip_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, 'heart')
        tip_text = new_tip_text(owner, repo, issue_id, comment_text)
        post_gitcoin_app_comment(owner, repo, issue_id, tip_text, install_id)
    else:
        post_issue_comment_reaction(owner, repo, comment_id, 'confused')
        post_gitcoin_app_comment(owner, repo, issue_id, confused_text(), install_id)
