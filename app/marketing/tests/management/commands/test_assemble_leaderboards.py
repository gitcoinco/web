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
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

import pytest
from dashboard.models import Activity, Bounty, BountyFulfillment, Earning, Profile, Tip, UserAction
from marketing.management.commands import assemble_leaderboards
from marketing.management.commands.assemble_leaderboards import (
    BREAKDOWNS, do_leaderboard, run_monthly, run_quarterly, run_weekly, run_yearly, should_suppress_leaderboard,
)
from marketing.models import LeaderboardRank
from pytz import UTC
from test_plus.test import TestCase


class TestAssembleLeaderboards(TestCase):
    """Define tests for assemble leaderboards."""

    def setUp(self):
        """Perform setup for the testcase."""
        patch('marketing.management.commands.assemble_leaderboards.DAILY_CUTOFF', datetime(2021, 4, 27, 10, 00, tzinfo=UTC)).start()

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
            expires_date=datetime(2021, 4, 27, 11, 00, tzinfo=UTC) + timedelta(days=1),
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
        Earning.objects.create(
            from_profile_id=self.bounty_payer_profile.id,
            to_profile_id=self.bounty_earner_profile.id,
            token_name='USDT',
            value_usd=3,
            source_id=self.bounty.id,
            created_on=datetime(2021, 4, 27, 11, 00, tzinfo=UTC),
            network='mainnet',
            success=True,
            source_type=ContentType.objects.get(app_label='dashboard', model='bountyfulfillment')
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
            expires_date=datetime(2021, 4, 27, 11, 00, tzinfo=UTC) + timedelta(days=1),
            tokenAddress='0x0000000000000000000000000000000000000000',
            txid='123',
        )
        Earning.objects.create(
            from_profile_id=self.tip_from_username_profile.id,
            to_profile_id=self.tip_username_profile.id,
            token_name='USDT',
            value_usd=self.tip_value,
            created_on=datetime(2021, 4, 27, 11, 00, tzinfo=UTC),
            network='mainnet',
            source_id=self.tip.id,
            success=True,
            source_type=ContentType.objects.get(app_label='dashboard', model='tip')
        )

    def tearDown(self):
        patch.stopall()
        self.bounty_payer_profile.delete()
        self.bounty_earner_profile.delete()
        self.tip_username_profile.delete()
        self.tip_from_username_profile.delete()

    def mock_run_cadence_datetimes(self, func, passing, failing):
        with patch.object(timezone, 'now', return_value=passing) as mock_now:
            is_valid = func()
            assert is_valid == True
        with patch.object(timezone, 'now', return_value=failing) as mock_now:
            is_valid = func()
            assert is_valid == False


    def test_run_weekly(self):
        self.mock_run_cadence_datetimes(run_weekly, datetime(2021, 4, 23, 11, 00), datetime(2021, 4, 27, 11, 00))


    def test_run_monthly(self):
        self.mock_run_cadence_datetimes(run_monthly, datetime(2021, 4, 1, 11, 00), datetime(2021, 4, 27, 11, 00))


    def test_run_quarterly(self):
        self.mock_run_cadence_datetimes(run_quarterly, datetime(2021, 4, 1, 11, 00), datetime(2021, 4, 27, 11, 00))


    def test_run_yearly(self):
        self.mock_run_cadence_datetimes(run_yearly, datetime(2021, 1, 1, 11, 00), datetime(2021, 4, 27, 11, 00))


    def test_do_leaderboard(self):
        """Test assemble leaderboards function."""

        with patch.object(timezone, 'now', return_value=datetime(2021, 4, 28, 11, 00, tzinfo=UTC)) as mock_now:

            do_leaderboard()

            assert LeaderboardRank.objects.filter(product='all', active=True).all().count() == 5

            assert LeaderboardRank.objects.filter(product='bounties', active=True, leaderboard="daily_earners").count() == 1
            assert LeaderboardRank.objects.filter(product='bounties', active=True, leaderboard="daily_payers").count() == 1

            assert LeaderboardRank.objects.filter(product='tips', active=True, leaderboard="daily_earners").count() == 1
            assert LeaderboardRank.objects.filter(product='tips', active=True, leaderboard="daily_payers").count() == 1

            assert LeaderboardRank.objects.filter(product='all', active=True, leaderboard="daily_earners").count() == 2
            assert LeaderboardRank.objects.filter(product='all', active=True, leaderboard="daily_payers").count() == 2

            assert LeaderboardRank.objects.filter(product='all', active=True, leaderboard="daily_tokens").count() == 1

    def test_suppress_leaderboard_when_missing_user_handle(self):
        assert should_suppress_leaderboard(None) == True

    def test_suppress_leaderboard_when_options_set(self):
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

    def test_show_leaderboard_when_profile_does_not_exist(self):
        assert should_suppress_leaderboard("random_user_name_9876") == False

    def test_show_leaderboard_when_user_exists_and_not_hiding(self):
        public_profile = Profile.objects.create(
            data={},
            handle="public_user",
            hide_profile=False,
            suppress_leaderboard=False,
        )
        assert should_suppress_leaderboard("public_user") == False
        public_profile.delete()
