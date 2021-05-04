# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

Copyright (C) 2020 Gitcoin Core

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
from datetime import date, datetime, timedelta

from dashboard.models import Bounty, BountyFulfillment, Profile, Tip, UserAction
from marketing.management.commands import assemble_leaderboards
from marketing.management.commands.assemble_leaderboards import BREAKDOWNS, Command, do_leaderboard, should_suppress_leaderboard
from marketing.models import LeaderboardRank
from pytz import UTC
from test_plus.test import TestCase


class TestAssembleLeaderboards(TestCase):
    """Define tests for assemble leaderboards."""

    def setUp(self):
        """Perform setup for the testcase."""
        """
        self.bounty_value = 3
        self.bounty_payer_handle = 'flintstone'
        self.bounty_earner_handle = 'freddy'

        self.bounty_payer_profile = Profile.objects.create(
            data={},
            handle=self.bounty_payer_handle,
            hide_profile=False,
        )
        UserAction.objects.create(
            profile=self.bounty_payer_profile,
            action='Login',
            ip_address='24.210.224.38',
        )
        UserAction.objects.create(
            profile=self.bounty_payer_profile,
            action='Login',
            ip_address='185.86.151.11',
        )
        self.bounty_earner_profile = Profile.objects.create(
            data={},
            handle=self.bounty_earner_handle,
            hide_profile=False,
        )
        UserAction.objects.create(
            profile=self.bounty_earner_profile,
            action='Login',
            ip_address='110.174.165.78',
        )
        self.bounty = Bounty.objects.create(
            title='foo',
            value_in_token=self.bounty_value,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username=self.bounty_payer_handle,
            bounty_owner_profile=self.bounty_payer_profile,
            is_open=False,
            accepted=True,
            expires_date=datetime.now(UTC) + timedelta(days=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            current_bounty=True,
            network='rinkeby',
            metadata={"issueKeywords": "Python, Shell"},
        )

        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            bounty=self.bounty,
            accepted=True,
            profile=self.bounty_earner_profile,
            token_name='USDT',
            payout_amount=3,
        )

        self.tip_value = 7
        self.tip_payer_handle = 'johnny'
        self.tip_earner_handle = 'john'

        self.tip_username_profile = Profile.objects.create(
            data={},
            handle=self.tip_earner_handle,
            hide_profile=False,
        )
        self.tip_from_username_profile = Profile.objects.create(
            data={},
            handle=self.tip_payer_handle,
            hide_profile=False,
        )
        UserAction.objects.create(
            profile=self.tip_username_profile,
            action='Login',
            ip_address='24.210.224.38',
        )
        UserAction.objects.create(
            profile=self.tip_from_username_profile,
            action='Login',
            ip_address='185.86.151.11',
        )
        self.tip = Tip.objects.create(
            emails=['john@bar.com'],
            tokenName='USDT',
            amount=self.tip_value,
            username=self.tip_earner_handle,
            from_username=self.tip_payer_handle,
            github_url='https://github.com/gitcoinco/web',
            network='rinkeby',
            expires_date=datetime.now(UTC) + timedelta(days=1),
            tokenAddress='0x0000000000000000000000000000000000000000',
            txid='123',
        )
        """

    def tearDown(self):
        """
        self.bounty_payer_profile.delete()
        self.bounty_earner_profile.delete()
        self.tip_username_profile.delete()
        self.tip_from_username_profile.delete()
        """

    def suppress_leaderboard_when_missing_user_handle(self):
        assert should_suppress_leaderboard() == True

    def suppress_leaderboard_when_options_set(self):
        hidden_profile = Profile.objects.create(
            data={},
            handle="hidden_user",
            hide_profile=True,
        )
        assert should_suppress_leaderboard("hidden_user") == True
        hidden_profile.delete()

        suppressed_profile = Profile.objects.create(
            data={},
            handle="suppressed_user",
            suppress_leaderboard=True,
            hide_profile=False
        )
        assert should_suppress_leaderboard("suppressed_user") == True
        suppressed_profile.delete()

    def show_leaderboard_when_profile_does_not_exist(self):
        assert should_suppress_leaderboard("random_user_name_9876") == False

    def show_leaderboard_when_user_exists_and_not_hiding(self):
        public_profile = Profile.objects.create(
            data={},
            handle="public_user",
            hide_profile=False,
            suppress_leaderboard=False,
        )
        assert should_suppress_leaderboard("public_user") == False
        public_profile.delete()
