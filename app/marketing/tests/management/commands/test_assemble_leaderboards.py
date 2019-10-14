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

from dashboard.models import Bounty, BountyFulfillment, Profile, Tip, UserAction
from marketing.management.commands import assemble_leaderboards
from marketing.management.commands.assemble_leaderboards import (
    BREAKDOWNS, TIMES, Command, bounty_index_terms, default_ranks, sum_bounties, sum_tips, tip_index_terms,
)
from marketing.models import LeaderboardRank
from pytz import UTC
from test_plus.test import TestCase


class TestAssembleLeaderboards(TestCase):
    """Define tests for assemble leaderboards."""

    def setUp(self):
        """Perform setup for the testcase."""
        assemble_leaderboards.ranks = default_ranks()

        self.bounty_value = 3
        self.bounty_payer_handle = 'flintstone'
        self.bounty_earner_handle = 'freddy'
        self.fulfiller_handle = 'bambam'

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
            network='mainnet',
            metadata={"issueKeywords": "Python, Shell"},
        )
        self.fulfiller_profile = Profile.objects.create(
            data={},
            handle=self.fulfiller_handle,
            hide_profile=False,
        )
        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            fulfiller_github_username=self.bounty_earner_handle,
            bounty=self.bounty,
            accepted=True,
            profile=self.fulfiller_profile,
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
            network='mainnet',
            expires_date=datetime.now(UTC) + timedelta(days=1),
            tokenAddress='0x0000000000000000000000000000000000000000',
            txid='123',
        )

    def tearDown(self):
        self.bounty_payer_profile.delete()
        self.bounty_earner_profile.delete()
        self.fulfiller_profile.delete()
        self.tip_username_profile.delete()
        self.tip_from_username_profile.delete()

    def test_default_ranks(self):
        """Test default ranks dictionary."""
        ranks = default_ranks()

        assert len(ranks) == len(TIMES) * len(BREAKDOWNS)

    def test_bounty_index_terms(self):
        """Test bounty index terms list."""
        index_terms = bounty_index_terms(self.bounty)
        assert len(index_terms) == 15
        assert 'USDT' in index_terms
        assert {self.bounty_payer_handle, self.bounty_earner_handle, 'gitcoinco'}.issubset(set(index_terms))
        '''
        these asserts are not worth testing as they break every time the
        underlying geoip data gets updated
        assert {'Tallmadge', 'United States', 'North America'}.issubset(set(index_terms))
        assert {'London', 'United Kingdom', 'Europe'}.issubset(set(index_terms))
        assert {'Australia', 'Oceania'}.issubset(set(index_terms))
        '''
        assert {'python', 'shell'}.issubset(set(index_terms))

    def test_tip_index_terms(self):
        """Test tip index terms list."""
        index_terms = tip_index_terms(self.tip)

        assert len(index_terms) == 10
        assert 'USDT' in index_terms
        assert {self.tip_payer_handle, self.tip_earner_handle, 'gitcoinco'}.issubset(set(index_terms))
        '''
        these asserts are not worth testing as they break every time the
        underlying geoip data gets updated
        assert {'Tallmadge', 'United States', 'North America'}.issubset(set(index_terms))
        assert {'London', 'United Kingdom', 'Europe'}.issubset(set(index_terms))
        '''

    def test_sum_bounties_payer(self):
        """Test sum bounties leaderboards."""
        sum_bounties(self.bounty, [self.bounty_payer_handle])

        rank_types_exists = [
            'all_all', 'all_fulfilled', 'all_payers',
            'yearly_all', 'yearly_fulfilled', 'yearly_payers',
            'monthly_all', 'monthly_fulfilled', 'monthly_payers',
            'weekly_all', 'weekly_fulfilled', 'weekly_payers',
        ]
        for rank_type in rank_types_exists:
            assert assemble_leaderboards.ranks[rank_type][self.bounty_payer_handle] == self.bounty_value

        rank_types_not_exists = [
            'all_earners', 'all_orgs', 'all_keywords', 'all_tokens',
            'all_countries', 'all_cities', 'all_continents',
            'yearly_earners', 'yearly_orgs', 'yearly_keywords', 'yearly_tokens',
            'yearly_countries', 'yearly_cities', 'yearly_continents',
            'monthly_earners', 'monthly_orgs', 'monthly_keywords', 'monthly_tokens',
            'monthly_countries', 'monthly_cities', 'monthly_continents',
            'weekly_earners', 'weekly_orgs', 'weekly_keywords', 'weekly_tokens',
            'weekly_countries', 'weekly_cities', 'weekly_continents',
        ]
        for rank_type in rank_types_not_exists:
            assert not dict(assemble_leaderboards.ranks[rank_type])

    def test_sum_bounties_earner(self):
        """Test sum bounties leaderboards."""
        sum_bounties(self.bounty, [self.bounty_earner_handle])

        rank_types_exists = [
            'all_all', 'all_fulfilled', 'all_earners',
            'yearly_all', 'yearly_fulfilled', 'yearly_earners',
            'monthly_all', 'monthly_fulfilled', 'monthly_earners',
            'weekly_all', 'weekly_fulfilled', 'weekly_earners',
        ]
        for rank_type in rank_types_exists:
            assert assemble_leaderboards.ranks[rank_type][self.bounty_earner_handle] == self.bounty_value

        rank_types_not_exists = [
            'all_payers', 'all_orgs', 'all_keywords', 'all_tokens',
            'all_countries', 'all_cities', 'all_continents',
            'yearly_payers', 'yearly_orgs', 'yearly_keywords', 'yearly_tokens',
            'yearly_countries', 'yearly_cities', 'yearly_continents',
            'monthly_payers', 'monthly_orgs', 'monthly_keywords', 'monthly_tokens',
            'monthly_countries', 'monthly_cities', 'monthly_continents',
            'weekly_payers', 'weekly_orgs', 'weekly_keywords', 'weekly_tokens',
            'weekly_countries', 'weekly_cities', 'weekly_continents',
        ]
        for rank_type in rank_types_not_exists:
            assert not dict(assemble_leaderboards.ranks[rank_type])

    def test_sum_tips_payer(self):
        """Test sum tips leaderboards."""
        sum_tips(self.tip, [self.tip_payer_handle])

        rank_types_exists = [
            'all_all', 'all_fulfilled', 'all_payers',
            'yearly_all', 'yearly_fulfilled', 'yearly_payers',
            'monthly_all', 'monthly_fulfilled', 'monthly_payers',
            'weekly_all', 'weekly_fulfilled', 'weekly_payers',
        ]
        for rank_type in rank_types_exists:
            assert assemble_leaderboards.ranks[rank_type][self.tip_payer_handle] == self.tip_value

        rank_types_not_exists = [
            'all_earners', 'all_orgs', 'all_tokens',
            'all_countries', 'all_cities', 'all_continents',
            'yearly_earners', 'yearly_orgs', 'yearly_tokens',
            'yearly_countries', 'yearly_cities', 'yearly_continents',
            'monthly_earners', 'monthly_orgs', 'monthly_tokens',
            'monthly_countries', 'monthly_cities', 'monthly_continents',
            'weekly_earners', 'weekly_orgs', 'weekly_tokens',
            'weekly_countries', 'weekly_cities', 'weekly_continents',
        ]
        for rank_type in rank_types_not_exists:
            assert not dict(assemble_leaderboards.ranks[rank_type])

    def test_sum_tips_earner(self):
        """Test sum tips leaderboards."""
        sum_tips(self.tip, [self.tip_earner_handle])

        rank_types_exists = [
            'all_all', 'all_fulfilled', 'all_earners',
            'yearly_all', 'yearly_fulfilled', 'yearly_earners',
            'monthly_all', 'monthly_fulfilled', 'monthly_earners',
            'weekly_all', 'weekly_fulfilled', 'weekly_earners',
        ]
        for rank_type in rank_types_exists:
            assert assemble_leaderboards.ranks[rank_type][self.tip_earner_handle] == self.tip_value

        rank_types_not_exists = [
            'all_payers', 'all_orgs', 'all_tokens',
            'all_countries', 'all_cities', 'all_continents',
            'yearly_payers', 'yearly_orgs', 'yearly_tokens',
            'yearly_countries', 'yearly_cities', 'yearly_continents',
            'monthly_payers', 'monthly_orgs', 'monthly_tokens',
            'monthly_countries', 'monthly_cities', 'monthly_continents',
            'weekly_payers', 'weekly_orgs', 'weekly_tokens',
            'weekly_countries', 'weekly_cities', 'weekly_continents',
        ]
        for rank_type in rank_types_not_exists:
            assert not dict(assemble_leaderboards.ranks[rank_type])

    def test_command_handle(self):
        """Test command assemble leaderboards."""
        Command().handle()

        assert LeaderboardRank.objects.all().count() == 225
        assert LeaderboardRank.objects.filter(leaderboard="all_all").count() == 15
        assert LeaderboardRank.objects.filter(leaderboard="all_fulfilled").count() == 15
        assert LeaderboardRank.objects.filter(leaderboard="all_earners").count() == 1
        assert LeaderboardRank.objects.filter(leaderboard="all_payers").count() == 1
        assert LeaderboardRank.objects.filter(leaderboard="all_tokens").count() == 1
        assert LeaderboardRank.objects.filter(leaderboard="all_countries").count() == 3
        assert LeaderboardRank.objects.filter(leaderboard="all_keywords").count() == 2
