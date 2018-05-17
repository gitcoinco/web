# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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
from datetime import date, datetime, timedelta

from dashboard.models import Bounty, BountyFulfillment, Profile, Tip
from marketing.management.commands import assemble_leaderboards
from marketing.management.commands.assemble_leaderboards import Command, default_ranks, sum_bounties, sum_tips
from marketing.models import LeaderboardRank
from pytz import UTC
from test_plus.test import TestCase


class TestAssembleLeaderboards(TestCase):
    """Define tests for assemble leaderboards."""

    def setUp(self):
        """Perform setup for the testcase."""
        assemble_leaderboards.ranks = default_ranks()
        tip = Tip(
            emails=['john@bar.com'],
            tokenName='USDT',
            amount=7,
            username='john',
            network='net',
            expires_date=date.today() + timedelta(days=1),
            tokenAddress='0x0000000000000000000000000000000000000000'
        )
        fulfiller_profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )
        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=False,
            expires_date=datetime(2008, 11, 30, tzinfo=UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            current_bounty=True
        )
        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=False,
            expires_date=datetime(2008, 11, 30, tzinfo=UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            current_bounty=True
        )
        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            fulfiller_email='',
            fulfiller_github_username='fred',
            fulfiller_name='Fred',
            bounty=bounty,
            profile=fulfiller_profile,
        )

        self.bounty = bounty
        self.tip = tip

    def test_sum_tips(self):
        """Test sum tips of assemble leaderboards."""
        total = 7
        user = 'johnny'
        rank_types = [
            'all_fulfilled', 'all_earners', 'weekly_fulfilled',
            'weekly_earners', 'weekly_all', 'monthly_fulfilled',
            'monthly_earners', 'monthly_all', 'yearly_fulfilled',
            'yearly_earners', 'yearly_all',
        ]

        sum_tips(self.tip, [user])
        for rank_type in rank_types:
            assert assemble_leaderboards.ranks[rank_type][user] == total

    def test_sum_bounties(self):
        """Test sum tips of bounties leaderboards."""
        user = 'freddy'
        total = 3

        sum_bounties(self.bounty, [user])
        print(assemble_leaderboards.ranks)

        rank_types_user = ['all_all', 'weekly_all', 'monthly_all', 'yearly_all']
        for rank_type in rank_types_user:
            assert assemble_leaderboards.ranks[rank_type][user] == total

        rank_types = [
            'weekly_fulfilled', 'weekly_payers', 'weekly_earners',
            'monthly_fulfilled', 'monthly_payers', 'monthly_earners',
            'yearly_fulfilled', 'yearly_payers', 'yearly_earners',
            'all_fulfilled', 'all_payers', 'all_earners',
        ]
        for rank_type in rank_types:
            assert not dict(assemble_leaderboards.ranks[rank_type])

    def test_handle_command(self):
        """Test command assemble leaderboards."""
        Command().handle()

        assert LeaderboardRank.objects.all().count() == 4
