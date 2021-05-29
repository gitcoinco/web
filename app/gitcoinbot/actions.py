# -*- coding: utf-8 -*-
"""Define the Gitcoin Bot action methods for interacting with the Github API as a Github App.

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
import datetime
import json
import re
from functools import wraps

from django.conf import settings

import jwt
import requests
from dashboard.models import Bounty
from dashboard.tokens import get_tokens
from git.utils import post_issue_comment_reaction
from gitcoinbot.models import GitcoinBotResponses

MIN_AMOUNT = 0
FALLBACK_CURRENCY = 'ETH'


class Bound:
    """Validate every bound before call the annotated function."""

    def __init__(self, *args):
        self.bounds = args

    def __call__(self, f):
        wraps(f)

        def wrapped_f(*args, **kwargs):
            for bound in self.bounds:  # Check if every bound is complained
                (valid, msg) = bound(*args, **kwargs)
                if not valid:
                    return msg  # specify what bound failed and why

            return f(*args, **kwargs)

        return wrapped_f


def amount_greater_than_zero(*args, **kwargs):
    """Validate if the specified amount is not negative and greater than zero."""
    comment_text = args[-1]
    amount = parse_comment_amount(comment_text)
    tip_currency = parse_comment_currency(comment_text)
    response = f'The amount should be greater than {MIN_AMOUNT} {tip_currency}'

    try:
        f_amount = float(amount)
        if f_amount > MIN_AMOUNT:
            return True, ''
    except ValueError:
        pass

    return False, response


def help_text():
    github_bot_user = f'@{settings.GITHUB_API_USER}'

    currencies = ', '.join(['ETH', 'GIT',
                           'TIME & [more](https://github.com/gitcoinco/web/blob/master/app/dashboard/tokens.py)'])
    help_text_response = f'I am {github_bot_user}, a bot that facilitates gitcoin bounties.\n' \
        '\n<hr>Here are the commands I understand:\n\n ' \
        '* `bounty <amount> <currency>` -- receive link to gitcoin.co form to create bounty.\n ' \
        '* `submit work` -- receive link to gitcoin.co to submit work on a bounty.\n ' \
        '* `start work` -- receive link to gitcoin.co to start work on a bounty.\n ' \
        '* `tip <user> <amount> <currency>` -- receive link to complete tippping another ' \
                         'github user *<amount>* <currency>.\n ' \
        '* `help` -- displays a help menu\n\n<br>' \
        f'Some currencies I support: \n{currencies}\n\n<br>' \
        'Learn more at: [https://gitcoin.co](https://gitcoin.co)\n' \
        f':zap::heart:, {github_bot_user}\n'
    return help_text_response


@Bound(amount_greater_than_zero)
def new_bounty_text(owner, repo, issue_id, comment_text):
    """Based on comment_text generate instructions to create a bounty with the specified amount and token."""
    issue_link = f'https://github.com/{owner}/{repo}/issues/{issue_id}'
    bounty_amount = parse_comment_amount(comment_text)
    token_name = parse_comment_currency(comment_text)
    bounty_link = f'{settings.BASE_URL}funding/new?source={issue_link}&amount={bounty_amount}&tokenName={token_name}'
    new_bounty_response = f'To create the bounty please [visit this link]({bounty_link}).\n\n ' \
                          'PS Make sure you\'re logged into Metamask!'
    return new_bounty_response


def no_active_bounty(owner, repo, issue_id):
    """Instructions to create a bounty."""
    issue_link = f'https://github.com/{owner}/{repo}/issues/{issue_id}'
    bounty_link = f'{settings.BASE_URL}funding/new?source={issue_link}'
    no_active_bounty_response = 'No active bounty for this issue, consider create the bounty please ' \
                                f'[visit this link]({bounty_link}).\n\n ' \
                                'PS Make sure you\'re logged into Metamask!'

    return no_active_bounty_response


def parse_comment_amount(comment_text):
    re_amount = r'\d*\.?\d+'
    result = re.findall(re_amount, comment_text)
    return result[0]


def parse_comment_currency(comment_text, fallback_currency=FALLBACK_CURRENCY):
    """Get the first token defined in comment_text."""
    CURRENCIES = set(map(lambda currency: currency['name'], get_tokens()))
    or_currencies = '|'.join(CURRENCIES)
    re_currencies = fr'({or_currencies})'
    result = re.findall(re_currencies, comment_text)
    return result[0] if result else fallback_currency


def parse_tippee_username(comment_text):
    re_username = r'[@][a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}'
    username = re.findall(re_username, comment_text)
    return username[-1]


@Bound(amount_greater_than_zero)
def new_tip_text(owner, repo, issue_id, comment_text):
    tip_amount = parse_comment_amount(comment_text)
    tip_currency = parse_comment_currency(comment_text)
    username = parse_tippee_username(comment_text)
    issue_url = f'https://github.com/{owner}/{repo}/issues/{issue_id}'
    tip_link = f'{settings.BASE_URL}tip/?'\
               f'amount={tip_amount}&tokenName={tip_currency}&username={username}&source={issue_url}'
    tip_response = f'To complete the tip, please [visit this link]({tip_link}).\n ' \
        'PS Make sure you\'re logged into Metamask!'
    return tip_response


def start_work_text(owner, repo, issue_id):
    """Instructions to start work on current bounty."""
    start_work_link = f'{settings.BASE_URL}issue/{owner}/{repo}/{issue_id}'
    start_work_response = f'To show this bounty as started please [visit this link]({start_work_link})'
    return start_work_response


def submit_work_text(owner, repo, issue_id):
    """Return the instruction to submit the work associated to the bounty."""
    submit_link = f'{settings.BASE_URL}issue/{owner}/{repo}/{issue_id}'
    submit_response = f'To finish claiming this bounty please [visit this link]({submit_link})'
    return submit_response


def submit_work_or_new_bounty_text(owner, repo, issue_id):
    """Submit work if the bounty exists else show instructions to create one."""
    bounties = Bounty.objects.filter(github_url=f'https://github.com/{owner}/{repo}/issues/{issue_id}').exists()

    if bounties:
        response_text = submit_work_text(owner, repo, issue_id)
    else:
        response_text = no_active_bounty(owner, repo, issue_id)

    return response_text


def confused_text():
    return 'Sorry I did not understand that request. Please try again or use `@gitcoinbot help` ' \
           'to see supported commands.'


def post_gitcoin_app_comment(owner, repo, issue_id, content, install_id):
    token = create_token(install_id)
    if not token:
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


def get_text_from_query_responses(comment_text, sender):
    """Based on comment_text an assigned response is returned."""
    comment_text_low = comment_text.casefold()
    result_text = GitcoinBotResponses.objects.filter(request=comment_text_low)
    if result_text.exists():
        return f'@{sender} {result_text.first().response}'
    return ''


def determine_response(owner, repo, comment_id, comment_text, issue_id, install_id, sender):
    help_regex = r'@?[Gg]itcoinbot\s[Hh]elp'
    bounty_regex = r'@?[Gg]itcoinbot\s[Bb]ounty\s\d*\.?(\d+\s?)'
    submit_work_regex = r'@?[Gg]itcoinbot\s[Ss]ubmit(\s[Ww]ork)?'
    tip_regex = r'@?[Gg]itcoinbot\s[Tt]ip\s@\w*\s\d*\.?(\d+\s?)'
    start_work_regex = r'@?[Gg]itcoinbot\s[Ss]tart(\s[Ww]ork)?'

    if re.match(help_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        post_gitcoin_app_comment(owner, repo, issue_id, help_text(), install_id)
    elif re.match(bounty_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        bounty_text = new_bounty_text(owner, repo, issue_id, comment_text)
        post_gitcoin_app_comment(owner, repo, issue_id, bounty_text, install_id)
    elif re.match(submit_work_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, '+1')
        result_text = submit_work_or_new_bounty_text(owner, repo, issue_id)
        post_gitcoin_app_comment(owner, repo, issue_id, result_text, install_id)
    elif re.match(tip_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, 'heart')
        tip_text = new_tip_text(owner, repo, issue_id, comment_text)
        post_gitcoin_app_comment(owner, repo, issue_id, tip_text, install_id)
    elif re.match(start_work_regex, comment_text) is not None:
        post_issue_comment_reaction(owner, repo, comment_id, 'heart')
        start_text = start_work_text(owner, repo, issue_id)
        post_gitcoin_app_comment(owner, repo, issue_id, start_text, install_id)
    else:
        only_message = re.sub(r'@?[Gg]itcoinbot\s', '', comment_text)
        text_response = get_text_from_query_responses(re.sub(r'</?\[\d+>', '', only_message), sender)

        if text_response:
            post_issue_comment_reaction(owner, repo, comment_id, 'hooray')
            post_gitcoin_app_comment(owner, repo, issue_id, text_response, install_id)
        else:
            post_issue_comment_reaction(owner, repo, comment_id, 'confused')
            # post_gitcoin_app_comment(owner, repo, issue_id, confused_text(), install_id)
