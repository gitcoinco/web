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

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone

import pytz
from avatar.models import CustomAvatar, SocialAvatar
from dashboard.models import Bounty, BountyFulfillment, Interest, Profile, Tip, Tool, ToolVote
from economy.models import ConversionRate, Token
from test_plus.test import TestCase


class DashboardModelsTest(TestCase):
    """Define tests for dashboard models."""

    fixtures = ['tokens.json']

    def setUp(self):
        """Perform setup for the testcase."""
        Token.objects.create(priority=999, symbol='ETH', address='0x0000000000000000000000000000000000000000')
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
            estimated_hours=7,
        )
        bounty_fulfillment = BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            fulfiller_email='',
            fulfiller_github_username='fred',
            fulfiller_name='Fred',
            bounty=bounty,
            profile=fulfiller_profile,
        )
        assert str(bounty) == f'{bounty.pk}: foo, 0 ETH @ {naturaltime(bounty.web3_created)}'
        assert bounty.url == f'{settings.BASE_URL}issue/gitcoinco/web/11/{bounty.standard_bounties_id}'
        assert bounty.title_or_desc == 'foo'
        assert bounty.issue_description_text == 'hello world'
        assert bounty.org_name == 'gitcoinco'
        assert bounty.is_hunter('fred') is True
        assert bounty.is_hunter('flintstone') is False
        assert bounty.is_funder('fred') is False
        assert bounty.is_funder('flintstone') is True
        assert bounty.status == 'done'
        assert bounty.value_true == 0
        assert bounty.value_in_eth == 3
        assert bounty.value_in_usdt_now == 0
        assert 'ago 5 Feature Intermediate' in bounty.desc
        assert bounty.is_legacy is False
        assert bounty.get_github_api_url() == 'https://api.github.com/repos/gitcoinco/web/issues/11'
        assert bounty.estimated_hours == 7
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
        assert not bounty_stats

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
    def test_github_issue_number():
        bounty = Bounty.objects.create(
            title='TitleTest',
            idx_status=0,
            is_open=False,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )
        assert bounty.github_issue_number == 12345678
        bounty.github_url = 'https://github.com/gitcoinco/web/issues/THIS_SHALL_RETURN_NONE'
        assert not bounty.github_issue_number

    @staticmethod
    def test_github_org_name():
        bounty = Bounty.objects.create(
            title='TitleTest',
            idx_status=0,
            is_open=False,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )
        assert bounty.github_org_name == "gitcoinco"
        bounty.github_url = None
        assert not bounty.github_org_name

    @staticmethod
    def test_github_repo_name():
        bounty = Bounty.objects.create(
            title='TitleTest',
            idx_status=0,
            is_open=False,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )
        assert bounty.github_repo_name == "web"
        bounty.github_url = None
        assert not bounty.github_repo_name

    @staticmethod
    def test_bounty_status():
        bounty = Bounty.objects.create(
            title='TitleTest',
            idx_status=0,
            is_open=True,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )
        assert bounty.status == "open"
        bounty.web3_type = "legacy_gitcoin"
        assert bounty.is_legacy
        bounty.pk = 12345
        assert bounty.status == "open"
        bounty.web3_type = None
        bounty.is_open = False
        bounty.accepted = False
        assert bounty.status == "expired"
        bounty.accepted = True
        assert bounty.status == "done"
        bounty.expires_date = datetime(2222, 11, 11, tzinfo=pytz.UTC)
        assert bounty.status == "done"
        bounty.accepted = False
        assert bounty.status == "cancelled"
        bounty.is_open = True
        bounty.num_fulfillments = 1
        assert bounty.status == "submitted"
        bounty.is_open = False
        bounty.num_fulfillments = 0
        bounty.expires_date = None
        assert bounty.status == "unknown"
        bounty.override_status = "overridden"
        assert bounty.status == "overridden"

    @staticmethod
    def test_fetch_issue_comments():
        bounty = Bounty.objects.create(
            title='TitleTest',
            idx_status=0,
            is_open=False,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )
        assert bounty.github_repo_name == "web"
        bounty.github_url = None
        assert not bounty.github_repo_name

    @staticmethod
    def test_bounty_expired():
        """Test the status and details of an expired bounty."""
        bounty = Bounty(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=False,
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        assert bounty.status == 'expired'

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
            web3_type='yge',
        )
        assert str(tip) == '(net) - PENDING 7 ETH to fred from NA, created: today, expires: tomorrow'
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
        assert str(interest) == 'foo / pending: False / status: okay'

    @staticmethod
    def test_profile():
        """Test the dashboard Profile model."""
        bounty = Bounty.objects.create(
            github_url='https://github.com/gitcoinco/web/issues/305',
            web3_created=datetime.now(tz=pytz.UTC),
            expires_date=datetime.now(tz=pytz.UTC) + timedelta(days=1),
            is_open=True,
            raw_data={},
            current_bounty=True,
            bounty_owner_github_username='gitcoinco',
            network='mainnet',
        )
        tip = Tip.objects.create(
            emails=['foo@bar.com'],
            github_url='https://github.com/gitcoinco/web/issues/305',
            expires_date=datetime.now(tz=pytz.UTC) + timedelta(days=1),
        )
        profile = Profile(
            handle='gitcoinco',
            data={'type': 'Organization'},
        )
        assert str(profile) == 'gitcoinco'
        assert profile.is_org is True
        assert profile.bounties.first() == bounty
        assert profile.tips.first() == tip
        assert profile.desc == '@gitcoinco is a newbie who has participated in 1 funded issue on Gitcoin'
        assert profile.github_url == 'https://github.com/gitcoinco'
        assert profile.get_relative_url() == '/profile/gitcoinco'

    def test_tool(self):
        """Test the dashboard Tool model."""
        tool = Tool.objects.create(
            name='Issue Explorer',
            category=Tool.CAT_BASIC,
            img='v2/images/why-different/code_great.png',
            description='A searchable index of all of the funded work available in the system.',
            link='http://gitcoin.co/explorer',
            link_copy='Try It',
            active=True,
            stat_graph='bounties_fulfilled')
        profile = Profile.objects.create(
            handle='gitcoinco',
            data={'type': 'Organization'},
        )
        vote = ToolVote.objects.create(profile_id=profile.id, value=1)
        tool.votes.add(vote)
        assert tool.vote_score() == 11
        assert tool.link_url == 'http://gitcoin.co/explorer'

    @staticmethod
    def test_profile_activate_avatar():
        """Test the dashboard Profile model activate_avatar method."""
        profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@localhost'
        )
        CustomAvatar.objects.create(profile=profile, config="{}")
        social_avatar = SocialAvatar.objects.create(profile=profile)
        profile.activate_avatar(social_avatar.pk)
        assert profile.avatar_baseavatar_related.get(pk=1).active is False
        assert profile.avatar_baseavatar_related.get(pk=2).active is True

    @staticmethod
    def test_bounty_snooze_url():
        """Test the dashboard Bounty model snooze_url method."""
        bounty = Bounty(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=False,
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        assert bounty.snooze_url(1) == f'{bounty.get_absolute_url()}?snooze=1'

    @staticmethod
    def test_bounty_canonical_url():
        """Test the dashboard Bounty model canonical url property."""
        bounty = Bounty(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/12',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=False,
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        assert bounty.canonical_url == settings.BASE_URL + 'issue/gitcoinco/web/12'

    @staticmethod
    def test_bounty_clean_gh_url_on_save():
        """Test the dashboard Bounty model with clean_github_url in save method."""
        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/305#issuecomment-999999999',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=False,
            accepted=False,
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        assert bounty.github_url == 'https://github.com/gitcoinco/web/issues/305'
        bounty.delete()

    @staticmethod
    def test_auto_user_auto_approve():

        profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )
        interest = Interest.objects.create(
            profile=profile, pending=True
        )
        interest.created = timezone.now()
        interest.save()

        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web/issues/1/',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            network='mainnet',
            idx_status='open',
            bounty_owner_email='john@bar.com',
            current_bounty=True,
            permission_type='approval',
            bounty_reserved_for_user=profile
        )

        bounty.interested.add(interest)
        bounty.save()
        interest.save()

        assert not interest.pending

    @staticmethod
    def get_all_tokens_sum():
        """Test all users funded tokens."""
        token_names = ['ETH', 'ETH', 'DAI']
        for name in token_names:
            Bounty.objects.create(
                title='foo',
                value_in_token=3,
                token_name=name,
                web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
                github_url='https://github.com/gitcoinco/web/issues/305#issuecomment-999999999',
                token_address='0x0',
                issue_description='hello world',
                bounty_owner_github_username='gitcoinco',
                is_open=True,
                expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
                idx_project_length=5,
                project_length='Months',
                bounty_type='Feature',
                experience_level='Intermediate',
                raw_data={},
                current_bounty=True,
                network='mainnet',
            )

        profile = Profile(
            handle='gitcoinco',
            data={'type': 'Organization'},
        )
        query = profile.to_dict()['sum_all_funded_tokens']
        assert query[0]['token_name'] == 'DAI'
        assert query[0]['value_in_token'] == 3

        assert query[1]['token_name'] == 'ETH'
        assert query[1]['value_in_token'] == 6
