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

from django.test import TestCase

from dashboard.models import Bounty, BountyFulfillment, Profile, Tip
from marketing.management.commands import assemble_leaderboards
from marketing.management.commands.assemble_leaderboards import Command, default_ranks, sum_bounties, sum_tips
from marketing.models import LeaderboardRank


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
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web',
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
        sum_tips(self.tip, ['john'])
        print(assemble_leaderboards.ranks)
        assert assemble_leaderboards.ranks['all_fulfilled']['john'] == 7
        assert assemble_leaderboards.ranks['all_earners']['john'] == 7

        assert assemble_leaderboards.ranks['weekly_fulfilled']['john'] == 7
        assert assemble_leaderboards.ranks['weekly_earners']['john'] == 7
        assert assemble_leaderboards.ranks['weekly_all']['john'] == 7

        assert assemble_leaderboards.ranks['monthly_fulfilled']['john'] == 7
        assert assemble_leaderboards.ranks['monthly_earners']['john'] == 7
        assert assemble_leaderboards.ranks['monthly_all']['john'] == 7

        assert assemble_leaderboards.ranks['yearly_fulfilled']['john'] == 7
        assert assemble_leaderboards.ranks['yearly_earners']['john'] == 7
        assert assemble_leaderboards.ranks['yearly_all']['john'] == 7

    def test_sum_bounties(self):
        """Test sum tips of bounties leaderboards."""
        sum_bounties(self.bounty, ['fred'])

        print(assemble_leaderboards.ranks)

        assert assemble_leaderboards.ranks['all_all']['fred'] == 3
        assert assemble_leaderboards.ranks['weekly_all']['fred'] == 3
        assert assemble_leaderboards.ranks['monthly_all']['fred'] == 3
        assert assemble_leaderboards.ranks['yearly_all']['fred'] == 3

        assert not dict(assemble_leaderboards.ranks['weekly_fulfilled'])
        assert not dict(assemble_leaderboards.ranks['weekly_payers'])
        assert not dict(assemble_leaderboards.ranks['weekly_earners'])
        assert not dict(assemble_leaderboards.ranks['monthly_fulfilled'])
        assert not dict(assemble_leaderboards.ranks['monthly_payers'])
        assert not dict(assemble_leaderboards.ranks['monthly_earners'])
        assert not dict(assemble_leaderboards.ranks['yearly_fulfilled'])
        assert not dict(assemble_leaderboards.ranks['yearly_payers'])
        assert not dict(assemble_leaderboards.ranks['yearly_earners'])
        assert not dict(assemble_leaderboards.ranks['all_fulfilled'])
        assert not dict(assemble_leaderboards.ranks['all_payers'])
        assert not dict(assemble_leaderboards.ranks['all_earners'])

    def test_handle_command(self):
        """Test command assemble leaderboards."""
        Command().handle()

        assert LeaderboardRank.objects.filter().count() == 8
