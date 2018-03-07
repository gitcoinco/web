# -*- coding: utf-8 -*-
from django.conf import settings
from django.test import TestCase

from gitcoinbot.actions import *


class gitcoinbotActions(TestCase):

    def test_help_text(self):
        """help text function returns the correct text"""
        text = help_text()
        target_text =  "I am @{}, a bot that facilitates gitcoin bounties.\n".format(settings.GITHUB_API_USER) + \
        "\n" +\
        "<hr>" +\
        "Here are the commands I understand:\n" +\
        "\n" +\
        " * `bounty <amount> ETH` -- receive link to gitcoin.co form to create bounty.\n" +\
        " * `claim` -- receive link to gitcoin.co to start work on a bounty.\n" +\
        " * `tip <user> <amount> ETH` -- receive link to complete tippping another github user *<amount>* ETH.\n" +\
        " * `help` -- displays a help menu\n" +\
        "\n" +\
        "<br>" +\
        "Learn more at: [https://gitcoin.co](https://gitcoin.co)\n" +\
        ":zap::heart:, @{}\n".format(settings.GITHUB_API_USER)
        self.assertEqual(text, target_text)

    def test_new_bounty_text(self):
        """New bounty text returns the correct text"""
        issue_link = "https://github.com/test_owner/gitcoin/issues/1234"
        bounty_link = "{}funding/new?source={}&amount=3.3".format(
            settings.BASE_URL, issue_link)
        target_text = "To create the bounty please [visit this link]" +\
        "({}).\n\n PS Make sure you're logged into Metamask!".format(bounty_link)
        text = new_bounty_text("test_owner", "gitcoin", "1234", "3.3 ETH")
        self.assertEqual(text, target_text)

    def test_parse_comment_amount(self):
        """Parse comment amount can retrieve amount when they're whole numbers
        """
        amount = parse_comment_amount("@gitcoinbot bounty 234 ETH")
        self.assertEqual(amount, "234")
        amount2 = parse_comment_amount("@gitcoinbot bounty 1 ETH")
        self.assertEqual(amount2, "1")
        amount3 = parse_comment_amount("@gitcoinbot bounty 1741852963 ETH")
        self.assertEqual(amount3, "1741852963")

    def test_parse_comment_amount_decimal(self):
        """Parse comment amount can retrieve amount when it includes decimals
        """
        amount = parse_comment_amount("@gitcoinbot bounty 2.34 ETH")
        self.assertEqual(amount, "2.34")
        amount = parse_comment_amount("@gitcoinbot bounty .23 ETH")
        self.assertEqual(amount, ".23")
        amount = parse_comment_amount("@gitcoinbot bounty 1.333334 ETH")
        self.assertEqual(amount, "1.333334")

    def test_parse_comment_amount_spaces(self):
        """Parse comment amount returns first instance of amount"""
        amount = parse_comment_amount("@gitcoinbot bounty 2.2 34 ETH")
        self.assertEqual(amount, "2.2")

    def test_parse_tipee_username(self):
        """Parse tippe username out from gitcoinbot command text"""
        username = parse_tippee_username("@gitcoinbot tip @user123 20 ETH")
        self.assertEqual(username, "@user123")

    def test_new_tip_text(self):
        """Gitcoinbot can respond with link to complete a tip"""
        issue_url = "https://github.com/test_owner/gitcoin/issues/1234"
        tip_link = "{}tip/?amount=3.3&username=@user&source={}".format(
        settings.BASE_URL, issue_url)
        target_text = "To complete the tip, please [visit this link]({}).".format(
            tip_link) + "\n PS Make sure you're logged into Metamask!"
        text = new_tip_text("test_owner", "gitcoin", "1234", "@user 3.3 ETH")
        self.assertEqual(text, target_text)

    def test_claim_bounty_text(self):
        """Gitcoinbot can respond with link to claim bounty"""
        issue_url = "https://github.com/test_owner/gitcoin/issues/1234"
        claim_link = "{}funding/details/?url={}".format(
            settings.BASE_URL, issue_url)
        target_text = "To finish claiming this bounty please [visit this link]({})".format(claim_link)
        text = claim_bounty_text("test_owner", "gitcoin", "1234")
        self.assertEqual(text, target_text)

    def test_confused_text(self):
        """Gitcoinbot can respond that it's confused"""
        self.assertEqual(confused_text(),
            'Sorry I did not understand that request. Please try again')
