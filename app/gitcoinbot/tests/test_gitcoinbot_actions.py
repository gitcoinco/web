# -*- coding: utf-8 -*-
"""Define Gitcoin Bot related tests.

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
from django.conf import settings

from gitcoinbot.actions import (
    FALLBACK_CURRENCY, confused_text, get_text_from_query_responses, help_text, new_bounty_text, new_tip_text,
    parse_comment_amount, parse_comment_currency, parse_tippee_username, start_work_text,
    submit_work_or_new_bounty_text, submit_work_text,
)
from gitcoinbot.models import GitcoinBotResponses
from test_plus.test import TestCase


class GitcoinBotActionsTest(TestCase):
    """Define the Gitcoin Bot actions TestCase."""

    fixtures = ['tokens.json']

    def test_help_text(self):
        """Test that help_text function returns the correct text."""
        self.maxDiff = None
        text = help_text()
        currencies = ', '.join(['ETH', 'GIT',
                                'TIME & [more](https://github.com/gitcoinco/web/blob/master/app/dashboard/tokens.py)'])
        target_text = f'I am @{settings.GITHUB_API_USER}, a bot that facilitates gitcoin bounties.\n\n<hr>' \
            'Here are the commands I understand:\n\n ' \
            '* `bounty <amount> <currency>` -- receive link to gitcoin.co form to create bounty.\n ' \
            '* `submit work` -- receive link to gitcoin.co to submit work on a bounty.\n ' \
            '* `start work` -- receive link to gitcoin.co to start work on a bounty.\n ' \
            '* `tip <user> <amount> <currency>` -- receive link to complete tippping another ' \
                      'github user *<amount>* <currency>.\n ' \
            '* `help` -- displays a help menu\n\n<br>' \
            f'Some currencies I support: \n{currencies}\n\n<br>' \
            'Learn more at: [https://gitcoin.co](https://gitcoin.co)\n' \
            f':zap::heart:, @{settings.GITHUB_API_USER}\n'
        self.assertEqual(text, target_text)

    def test_new_bounty_text(self):
        """Test that new_bounty_text returns the correct text."""
        issue_link = 'https://github.com/gitcoinco/web/issues/305'
        bounty_link = f'{settings.BASE_URL}funding/new?source={issue_link}&amount=3.3&tokenName=ETH'
        target_text = 'To create the bounty please [visit this link]' \
                      f'({bounty_link}).\n\n PS Make sure you\'re logged into Metamask!'
        text = new_bounty_text('gitcoinco', 'web', '305', '3.3 ETH')
        self.assertEqual(text, target_text)

    def test_parse_comment_amount(self):
        """Test parse_comment_amount can retrieve amount when they're whole numbers."""
        amount = parse_comment_amount('@gitcoinbot bounty 234 ETH')
        self.assertEqual(amount, '234')
        amount2 = parse_comment_amount('@gitcoinbot bounty 1 ETH')
        self.assertEqual(amount2, '1')
        amount3 = parse_comment_amount('@gitcoinbot bounty 1741852963 ETH')
        self.assertEqual(amount3, '1741852963')

    def test_parse_comment_currency(self):
        """Test parse_comment_amount can retrieve amount when they're whole numbers."""
        currency = parse_comment_currency('@gitcoinbot bounty 234')
        self.assertEqual(currency, FALLBACK_CURRENCY)  # Default behavior should fallback to DEFAULT_CURRENCY
        currency2 = parse_comment_currency('@gitcoinbot bounty 1 TIME')
        self.assertEqual(currency2, 'TIME')  # specified in tokens.py
        currency3 = parse_comment_currency('@gitcoinbot bounty 1741852963 BTW')
        self.assertEqual(currency3, FALLBACK_CURRENCY)  # Unknown currency should fallback to DEFAULT_CURRENCY

    def test_parse_comment_amount_decimal(self):
        """Test parse_comment_amount can retrieve amount when it includes decimals."""
        amount = parse_comment_amount('@gitcoinbot bounty 2.34 ETH')
        self.assertEqual(amount, '2.34')
        amount = parse_comment_amount('@gitcoinbot bounty .23 ETH')
        self.assertEqual(amount, '.23')
        amount = parse_comment_amount('@gitcoinbot bounty 1.333334 ETH')
        self.assertEqual(amount, '1.333334')

    def test_parse_comment_amount_spaces(self):
        """Test parse_comment_amount returns first instance of amount."""
        amount = parse_comment_amount('@gitcoinbot bounty 2.2 34 ETH')
        self.assertEqual(amount, '2.2')

    def test_parse_tipee_username(self):
        """Test parse_tippe_username out from gitcoinbot command text."""
        username = parse_tippee_username('@gitcoinbot tip @user123 20 ETH')
        self.assertEqual(username, '@user123')

    def test_new_tip_text(self):
        """Test Gitcoinbot can respond with link to complete a tip."""
        issue_url = 'https://github.com/gitcoinco/web/issues/305'
        tip_link = f'{settings.BASE_URL}tip/?amount=3.3&tokenName=ETH&username=@user&source={issue_url}'
        target_text = f'To complete the tip, please [visit this link]({tip_link}).\n ' \
                      'PS Make sure you\'re logged into Metamask!'
        text = new_tip_text('gitcoinco', 'web', '305', '@user 3.3 ETH')
        self.assertEqual(text, target_text)

    def test_submit_work_text(self):
        """Test Gitcoinbot can respond with link to submit your work."""
        submit_link = f'{settings.BASE_URL}issue/gitcoinco/web/305'
        target_text = f'To finish claiming this bounty please [visit this link]({submit_link})'
        text = submit_work_text('gitcoinco', 'web', '305')
        self.assertEqual(text, target_text)

    def test_start_work_text(self):
        start_work_link = f'{settings.BASE_URL}issue/gitcoinco/web/305'
        target_text = f'To show this bounty as started please [visit this link]({start_work_link})'
        text = start_work_text('gitcoinco', 'web', '305')
        self.assertEqual(text, target_text)

    def test_confused_text(self):
        """Test Gitcoinbot can respond that it's confused."""
        self.assertEqual(confused_text(),
                         'Sorry I did not understand that request. Please try again or use `@gitcoinbot help` '
                         'to see supported commands.')

    def test_submit_work_or_new_bounty_when_bounty_exists(self):
        """Test submit_work_or_new_bounty_text when bounty is active."""
        from dashboard.models import Bounty
        from datetime import datetime
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web/issues/305',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=True,
            expires_date=datetime(2008, 11, 30),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        submit_link = f'{settings.BASE_URL}issue/gitcoinco/web/305'
        target_text = f'To finish claiming this bounty please [visit this link]({submit_link})'
        text = submit_work_or_new_bounty_text('gitcoinco', 'web', '305')
        self.assertEqual(text, target_text)

    def test_submit_work_or_new_bounty_when_bounty_doesnt_exist(self):
        """Test submit_work_or_new_bounty_text when bounty isn't active."""
        issue_link = f'https://github.com/gitcoinco/web/issues/305'
        bounty_link = f'{settings.BASE_URL}funding/new?source={issue_link}'
        target_text = 'No active bounty for this issue, consider create the bounty please'\
                      f' [visit this link]({bounty_link}).\n\n ' \
                      'PS Make sure you\'re logged into Metamask!'
        text = submit_work_or_new_bounty_text('gitcoinco', 'web', '305')
        self.assertEqual(text, target_text)

    def test_get_text_from_responses_when_doesnt_exist(self):
        """Test get_text_from_query_responses when a response isn't exists."""
        response = get_text_from_query_responses('Party trap', 'sender')
        self.assertEqual(response, '')

    def test_get_text_from_responses_when_exists(self):
        """Test get_text_from_query_responses when a response exists."""
        GitcoinBotResponses.objects.create(request='speedy gonzales', response='The Fastest Mouse in all Mexico')
        response = get_text_from_query_responses('Speedy Gonzales', 'ACME')
        self.assertEqual(response, '@ACME The Fastest Mouse in all Mexico')
