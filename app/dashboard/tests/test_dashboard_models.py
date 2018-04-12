# -*- coding: utf-8 -*-
"""Handle dashboard model related tests.

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

import pytz
from dashboard.models import Bounty, BountyFulfillment, Interest, Profile, Tip
from economy.models import ConversionRate
from test_plus.test import TestCase


class DashboardModelsTest(TestCase):
    """Define tests for dashboard models."""

    def setUp(self):
        """Perform setup for the testcase."""
        ConversionRate.objects.create(
            from_amount=1,
            to_amount=2,
            source='etherdelta',
            from_currency='ETH',
            to_currency='USDT',
        )

    @staticmethod
    def test_bounty():
        """Test the dashboard Bounty model."""
        fulfiller_profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@localhost'
        )
        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/11',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=True,
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        bounty_fulfillment = BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            fulfiller_email='',
            fulfiller_github_username='fred',
            fulfiller_name='Fred',
            bounty=bounty,
            profile=fulfiller_profile,
        )
        assert str(bounty) == 'foo 3 ETH 2008-10-31 00:00:00+00:00'
        assert bounty.url == '/issue/gitcoinco/web/11'
        assert bounty.title_or_desc == 'foo'
        assert bounty.issue_description_text == 'hello world'
        assert bounty.org_name == 'gitcoinco'
        assert bounty.is_hunter('fred') is True
        assert bounty.is_hunter('flintstone') is False
        assert bounty.is_funder('fred') is False
        assert bounty.is_funder('flintstone') is True
        assert bounty.get_avatar_url
        assert bounty.status == 'expired'
        assert bounty.value_true == 3e-18
        assert bounty.value_in_eth == 3
        assert bounty.value_in_usdt_now == 0
        assert 'ago 5 Feature Intermediate' in bounty.desc
        assert bounty.is_legacy is False
        assert bounty.get_github_api_url() == 'https://api.github.com/repos/gitcoinco/web/issues/11'
        assert bounty_fulfillment.profile.handle == 'fred'
        assert bounty_fulfillment.bounty.title == 'foo'

    @staticmethod
    def test_exclude_bounty_by_status():
        Bounty.objects.create(
          title='First',
          idx_status=0,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          raw_data={}
        )
        Bounty.objects.create(
          title='Second',
          idx_status=1,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          raw_data={}
        )
        Bounty.objects.create(
          title='Third',
          idx_status=2,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2222, 11, 30, tzinfo=pytz.UTC),
          raw_data={},
        )
        Bounty.objects.create(
          title='Fourth',
          idx_status=3,
          is_open=True,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2222, 11, 30, tzinfo=pytz.UTC),
          raw_data={}
        )
        bounty_stats = Bounty.objects.exclude_by_status()
        assert len(bounty_stats) == 4
        bounty_stats = Bounty.objects.exclude_by_status(['open'])
        assert len(bounty_stats) == 3
        bounty_stats = Bounty.objects.exclude_by_status(['cancelled', 'done'])
        assert len(bounty_stats) == 3
        bounty_stats = Bounty.objects.exclude_by_status(['open', 'expired', 'cancelled'])
        assert len(bounty_stats) == 0

    @staticmethod
    def test_relative_bounty_url_with_malformed_issue_number():
        bounty = Bounty.objects.create(
          title='First',
          idx_status=0,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          github_url='https://github.com/gitcoinco/web/issues/0xDEADBEEF',
          raw_data={}
        )
        expected_url = '/funding/details?url=https://github.com/gitcoinco/web/issues/0xDEADBEEF'
        assert bounty.get_relative_url() == expected_url

    @staticmethod
    def test_get_natural_value_if_bad_token_address_provided():
        bounty = Bounty.objects.create(
          title='BadTokenBounty',
          idx_status=0,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          token_address='0xDEADDEADDEADDEAD',
          raw_data={}
        )
        assert bounty.get_natural_value() == 0

    @staticmethod
    def test_can_submit_legacy_bounty_after_expiration_date():
        bounty = Bounty.objects.create(
          title='ExpiredBounty',
          web3_type='legacy_gitcoin',
          idx_status=0,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          raw_data={}
        )
        assert bounty.is_legacy is True
        assert bounty.can_submit_after_expiration_date is True

    @staticmethod
    def test_cannot_submit_standard_bounty_after_expiration_date():
        bounty = Bounty.objects.create(
          title='ExpiredBounty',
          idx_status=0,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          raw_data={}
        )
        assert bounty.can_submit_after_expiration_date is False

    @staticmethod
    def test_can_submit_standard_bounty_after_expiration_date_if_deadline_extended():
        bounty = Bounty.objects.create(
          title='ExpiredBounty',
          idx_status=0,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          raw_data={'contract_deadline': 1001, 'ipfs_deadline': 1000}
        )
        assert bounty.can_submit_after_expiration_date is True

    @staticmethod
    def test_title_or_desc():
        bounty = Bounty.objects.create(
          title='TitleTest',
          idx_status=0,
          is_open=False,
          web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
          expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
          github_url='https://github.com/gitcoinco/web/issues/0xDEADBEEF',
          raw_data={}
        )
        assert bounty.title_or_desc == "TitleTest"
        bounty.title = None
        assert bounty.title_or_desc == "https://github.com/gitcoinco/web/issues/0xDEADBEEF"

    @staticmethod
    def test_tip():
        """Test the dashboard Tip model."""
        tip = Tip(
            emails=['foo@bar.com'],
            tokenName='ETH',
            amount=7,
            username='fred',
            network='net',
            expires_date=date.today() + timedelta(days=1),
            created_on=date.today(),
            tokenAddress='0x0000000000000000000000000000000000000000',
        )
        assert str(tip) == '(net) - PENDING 7 ETH to fred, created: today, expires: tomorrow'
        assert tip.get_natural_value() == 7e-18
        assert tip.value_in_eth == 7
        assert tip.value_in_usdt == 14
        assert tip.status == 'PENDING'

    @staticmethod
    def test_interest():
        """Test the dashboard Interest model."""
        profile = Profile(
            handle='foo',
        )
        interest = Interest(
            profile=profile,
        )
        assert str(interest) == 'foo'

    @staticmethod
    def test_profile():
        """Test the dashboard Profile model."""
        bounty = Bounty.objects.create(
            github_url='https://github.com/gitcoinco/web',
            web3_created=datetime.now(tz=pytz.UTC),
            expires_date=datetime.now(tz=pytz.UTC) + timedelta(days=1),
            is_open=True,
            raw_data={},
            current_bounty=True,
            bounty_owner_github_username='gitcoinco',
        )
        tip = Tip.objects.create(
            emails=['foo@bar.com'],
            github_url='https://github.com/gitcoinco/web',
            expires_date=datetime.now(tz=pytz.UTC) + timedelta(days=1),
        )
        profile = Profile(
            handle='gitcoinco',
            data={'type': 'Organization'},
            repos_data=[{'contributors': [{'contributions': 50, 'login': 'foo'}]}],
        )
        assert str(profile) == 'gitcoinco'
        assert profile.is_org is True
        assert profile.bounties.first() == bounty
        assert profile.tips.first() == tip
        assert profile.authors == ['foo', 'gitcoinco']
        assert profile.desc == '@gitcoinco is a newbie who has participated in 1 funded issue on Gitcoin'
        assert profile.stats == [
            ('newbie', 'Status'),
            (1, 'Total Funded Issues'),
            (1, 'Open Funded Issues'),
            ('0x', 'Loyalty Rate'),
        ]
        assert profile.github_url == 'https://github.com/gitcoinco'
        assert profile.get_relative_url() == '/profile/gitcoinco'
