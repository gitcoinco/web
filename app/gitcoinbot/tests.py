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
from django.test import TestCase

from gitcoinbot.actions import (
    claim_bounty_text, confused_text, help_text, new_bounty_text, new_tip_text, parse_comment_amount,
    parse_tippee_username,
)


class gitcoinbotActions(TestCase):
    """Define the Gitcoin Bot actions TestCase."""

    def test_help_text(self):
        """Test that help_text function returns the correct text."""
        text = help_text()
        target_text = f"I am @{settings.GITHUB_API_USER}, a bot that facilitates gitcoin bounties.\n\n<hr>" \
            "Here are the commands I understand:\n\n " \
            "* `bounty <amount> ETH` -- receive link to gitcoin.co form to create bounty.\n " \
            "* `claim` -- receive link to gitcoin.co to start work on a bounty.\n " \
            "* `tip <user> <amount> ETH` -- receive link to complete tippping another github user *<amount>* ETH.\n " \
            "* `help` -- displays a help menu\n\n<br>Learn more at: [https://gitcoin.co](https://gitcoin.co)\n" \
            f":zap::heart:, @{settings.GITHUB_API_USER}\n"
        self.assertEqual(text, target_text)

    def test_new_bounty_text(self):
        """Test that new_bounty_text returns the correct text."""
        issue_link = "https://github.com/test_owner/gitcoin/issues/1234"
        bounty_link = f"{settings.BASE_URL}funding/new?source={issue_link}&amount=3.3"
        target_text = "To create the bounty please [visit this link]" +\
        f"({bounty_link}).\n\n PS Make sure you're logged into Metamask!"
        text = new_bounty_text("test_owner", "gitcoin", "1234", "3.3 ETH")
        self.assertEqual(text, target_text)

    def test_parse_comment_amount(self):
        """Test parse_comment_amount can retrieve amount when they're whole numbers."""
        amount = parse_comment_amount("@gitcoinbot bounty 234 ETH")
        self.assertEqual(amount, "234")
        amount2 = parse_comment_amount("@gitcoinbot bounty 1 ETH")
        self.assertEqual(amount2, "1")
        amount3 = parse_comment_amount("@gitcoinbot bounty 1741852963 ETH")
        self.assertEqual(amount3, "1741852963")

    def test_parse_comment_amount_decimal(self):
        """Test parse_comment_amount can retrieve amount when it includes decimals."""
        amount = parse_comment_amount("@gitcoinbot bounty 2.34 ETH")
        self.assertEqual(amount, "2.34")
        amount = parse_comment_amount("@gitcoinbot bounty .23 ETH")
        self.assertEqual(amount, ".23")
        amount = parse_comment_amount("@gitcoinbot bounty 1.333334 ETH")
        self.assertEqual(amount, "1.333334")

    def test_parse_comment_amount_spaces(self):
        """Test parse_comment_amount returns first instance of amount."""
        amount = parse_comment_amount("@gitcoinbot bounty 2.2 34 ETH")
        self.assertEqual(amount, "2.2")

    def test_parse_tipee_username(self):
        """Test parse_tippe_username out from gitcoinbot command text."""
        username = parse_tippee_username("@gitcoinbot tip @user123 20 ETH")
        self.assertEqual(username, "@user123")

    def test_new_tip_text(self):
        """Test Gitcoinbot can respond with link to complete a tip."""
        issue_url = "https://github.com/test_owner/gitcoin/issues/1234"
        tip_link = f"{settings.BASE_URL}tip/?amount=3.3&username=@user&source={issue_url}"
        target_text = f"To complete the tip, please [visit this link]({tip_link}).\n " \
            "PS Make sure you're logged into Metamask!"
        text = new_tip_text("test_owner", "gitcoin", "1234", "@user 3.3 ETH")
        self.assertEqual(text, target_text)

    def test_claim_bounty_text(self):
        """Test Gitcoinbot can respond with link to claim bounty."""
        issue_url = "https://github.com/test_owner/gitcoin/issues/1234"
        claim_link = f"{settings.BASE_URL}funding/details/?url={issue_url}"
        target_text = f"To finish claiming this bounty please [visit this link]({claim_link})"
        text = claim_bounty_text("test_owner", "gitcoin", "1234")
        self.assertEqual(text, target_text)

    def test_confused_text(self):
        """Test Gitcoinbot can respond that it's confused."""
        self.assertEqual(confused_text(),
            'Sorry I did not understand that request. Please try again or use `@gitcoinbot help` to see supported commands.')
