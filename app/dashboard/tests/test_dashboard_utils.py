# -*- coding: utf-8 -*-
"""Handle dashboard utility related tests.

Copyright (C) 2021 Gitcoin Core

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
from datetime import datetime
from unittest.mock import patch

from django.conf import settings
from django.test.client import RequestFactory
from django.utils import timezone

from dashboard.models import Bounty, Profile
from dashboard.utils import (
    apply_new_bounty_deadline, clean_bounty_url, create_user_action, get_bounty, get_ordinal_repr,
    get_token_recipient_senders, get_web3, getBountyContract, humanize_event_name, re_market_bounty,
    release_bounty_to_the_public,
)
from eth_utils import is_address
from pytz import UTC
from test_plus.test import TestCase
from web3.main import Web3
from web3.providers.rpc import HTTPProvider


class DashboardUtilsTest(TestCase):
    """Define tests for dashboard utils."""

    @staticmethod
    def test_get_web3():
        """Test the dashboard utility get_web3."""
        networks = ['mainnet', 'rinkeby', 'ropsten']
        for network in networks:
            web3_provider = get_web3(network)
            assert isinstance(web3_provider, Web3)
            assert len(web3_provider.providers) == 1
            assert isinstance(web3_provider.providers[0], HTTPProvider)
            if settings.INFURA_USE_V3:
                assert web3_provider.providers[0].endpoint_uri == f'https://{network}.infura.io/v3/{settings.INFURA_V3_PROJECT_ID}'
            else:
                assert web3_provider.providers[0].endpoint_uri == f'https://{network}.infura.io'

    @staticmethod
    def test_get_bounty_contract():
        assert getBountyContract('mainnet').address == "0x2af47a65da8CD66729b4209C22017d6A5C2d2400"

    @staticmethod
    def test_get_bounty():
        assert get_bounty(100, 'rinkeby')['contract_deadline'] == 1515699751

    @staticmethod
    def test_get_ordinal_repr():
        """Test the dashboard utility get_ordinal_repr."""
        assert get_ordinal_repr(1) == '1st'
        assert get_ordinal_repr(2) == '2nd'
        assert get_ordinal_repr(3) == '3rd'
        assert get_ordinal_repr(4) == '4th'
        assert get_ordinal_repr(10) == '10th'
        assert get_ordinal_repr(11) == '11th'
        assert get_ordinal_repr(21) == '21st'
        assert get_ordinal_repr(22) == '22nd'
        assert get_ordinal_repr(23) == '23rd'
        assert get_ordinal_repr(24) == '24th'

    @staticmethod
    def test_clean_bounty_url():
        """Test the cleaning of a bounty-esque URL of # sections."""
        assert clean_bounty_url(
            'https://github.com/gitcoinco/web/issues/9999#issuecomment-999999999'
        ) == 'https://github.com/gitcoinco/web/issues/9999'

    @staticmethod
    def test_humanize_event_name():
        """Test the humanized representation of an event name."""
        assert humanize_event_name('start_work') == 'WORK STARTED'
        assert humanize_event_name('remarket_funded_issue') == 'REMARKET_FUNDED_ISSUE'
        assert humanize_event_name('issue_remarketed') == 'ISSUE RE-MARKETED'

    @staticmethod
    @patch('dashboard.utils.UserAction.objects')
    def test_create_user_action_with_cookie(mockUserAction):
        """Test the giving utm* in cookie should store in DB."""
        request = RequestFactory().get('/login')
        request.COOKIES['utm_source'] = 'test source'
        request.COOKIES['utm_medium'] = 'test medium'
        request.COOKIES['utm_campaign'] = 'test campaign'
        create_user_action(None, 'Login', request)
        mockUserAction.create.assert_called_once_with(action='Login', metadata={}, user=None,
                                                      utm={'utm_source': 'test source',
                                                           'utm_medium': 'test medium',
                                                           'utm_campaign': 'test campaign'})

    @staticmethod
    @patch('dashboard.utils.UserAction.objects')
    def test_create_user_action_without_cookie(mockUserAction):
        """Test the giving utm* in cookie should store in DB as empty dict."""
        request = RequestFactory().get('/login')
        create_user_action(None, 'Login', request)
        mockUserAction.create.assert_called_once_with(action='Login', metadata={}, user=None)

    @staticmethod
    @patch('dashboard.utils.UserAction.objects')
    def test_create_user_action_with_partial_cookie(mockUserAction):
        """Test the giving utm* in cookie should store partial utm in DB."""
        request = RequestFactory().get('/login')
        request.COOKIES['utm_campaign'] = 'test campaign'
        create_user_action(None, 'Login', request)
        mockUserAction.create.assert_called_once_with(action='Login', metadata={}, user=None,
                                                      utm={'utm_campaign': 'test campaign'})


    @staticmethod
    def test_can_successfully_re_market_a_bounty():
        bounty = Bounty.objects.create(
            title='CanRemarketTrueTest',
            idx_status=0,
            is_open=True,
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )

        assert bounty.remarketed_count == 0

        result = re_market_bounty(bounty, False)

        assert result['success'] is True
        assert result['msg'] == f"The issue will appear at the top of the issue explorer. You will be able to remarket this bounty {settings.RE_MARKET_LIMIT - 1} more time if a contributor does not pick this up."
        assert bounty.remarketed_count == 1
        assert bounty.last_remarketed > (timezone.now() - timezone.timedelta(minutes=1))

    @staticmethod
    def test_can_successfully_re_market_a_bounty_twice():
        if settings.RE_MARKET_LIMIT == 2:
            bounty = Bounty.objects.create(
                title='CanRemarketTrueTest',
                idx_status=0,
                is_open=True,
                web3_created=datetime(2008, 10, 31, tzinfo=UTC),
                expires_date=datetime(2008, 11, 30, tzinfo=UTC),
                last_remarketed=datetime(2008, 10, 31, tzinfo=UTC),
                github_url='https://github.com/gitcoinco/web/issues/12345678',
                raw_data={}
            )

            result = re_market_bounty(bounty, False)
            assert result['success'] is True
            assert result['msg'] == "The issue will appear at the top of the issue explorer. You will be able to remarket this bounty 1 more time if a contributor does not pick this up."
            assert bounty.remarketed_count == 1

            bounty.last_remarketed = timezone.now() - timezone.timedelta(hours=2)

            result = re_market_bounty(bounty, False)
            assert result['success'] is True
            assert result['msg'] == "The issue will appear at the top of the issue explorer. Please note this is the last time the issue is able to be remarketed."
            assert bounty.remarketed_count == 2

    @staticmethod
    def test_re_market_fails_after_reaching_re_market_limit():
        if settings.RE_MARKET_LIMIT == 2:
            bounty = Bounty.objects.create(
                title='CanRemarketFalseTest',
                idx_status=0,
                is_open=True,
                web3_created=datetime(2008, 10, 31, tzinfo=UTC),
                expires_date=datetime(2008, 11, 30, tzinfo=UTC),
                last_remarketed=datetime(2008, 10, 31, tzinfo=UTC),
                github_url='https://github.com/gitcoinco/web/issues/12345678',
                raw_data={}
            )

            assert bounty.remarketed_count == 0
            result = re_market_bounty(bounty, False)
            assert result['success'] is True
            assert bounty.remarketed_count == 1

            bounty.last_remarketed = timezone.now() - timezone.timedelta(hours=2)

            result = re_market_bounty(bounty, False)
            assert result['success'] is True
            assert bounty.remarketed_count == 2

            result = re_market_bounty(bounty, False)
            assert result['success'] is False
            assert result['msg'] == "The issue was not remarketed due to reaching the remarket limit (2)."

    @staticmethod
    def test_re_market_fails_after_re_marketing_in_quick_succession():
        bounty = Bounty.objects.create(
            title='CanRemarketFalseTest',
            idx_status=0,
            is_open=True,
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )

        assert bounty.remarketed_count == 0
        result = re_market_bounty(bounty, False)
        assert result['success'] is True
        assert bounty.remarketed_count == 1

        result = re_market_bounty(bounty, False)
        assert result['success'] is False

        assert result['msg'] == f'As you recently remarketed this issue, you need to wait {settings.MINUTES_BETWEEN_RE_MARKETING} minutes before remarketing this issue again.'

    @staticmethod
    def test_apply_new_bounty_deadline_is_successful_with_re_market():
        bounty = Bounty.objects.create(
            title='CanRemarketFalseTest',
            idx_status=0,
            is_open=True,
            web3_created=datetime(2008, 10, 31, tzinfo=UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=UTC),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )

        assert bounty.remarketed_count == 0

        import time
        deadline = time.time()
        re_market_result = apply_new_bounty_deadline(bounty, deadline, False)
        assert bounty.remarketed_count == 1
        assert re_market_result['success'] is True
        assert re_market_result['msg'] == "You've extended expiration of this issue. The issue will appear at the top of the issue explorer. You will be able to remarket this bounty 1 more time if a contributor does not pick this up."

        deadline_as_date_time = timezone.make_aware(
            timezone.datetime.fromtimestamp(deadline),
            timezone=UTC
        )
        assert bounty.expires_date == deadline_as_date_time

    @staticmethod
    def test_release_bounty_to_public_fails_when_bounty_is_none():
        assert release_bounty_to_the_public(None) is False

    @staticmethod
    def test_release_bounty_to_public_is_successful():
        now = timezone.now()
        profile = Profile(
            handle='foo',
        )
        bounty = Bounty(
            title='ReleaseToPublicTrueTest',
            idx_status='reserved',
            is_open=True,
            web3_created=now,
            expires_date=now + timezone.timedelta(minutes=2),
            bounty_reserved_for_user=profile,
            reserved_for_user_from=now,
            reserved_for_user_expiration=now + timezone.timedelta(minutes=2),
            github_url='https://github.com/gitcoinco/web/issues/12345678',
            raw_data={}
        )

        assert bounty.bounty_reserved_for_user is not None
        assert bounty.reserved_for_user_from is not None
        assert bounty.reserved_for_user_expiration is not None

        assert release_bounty_to_the_public(bounty, False) is True

        assert bounty.bounty_reserved_for_user is None
        assert bounty.reserved_for_user_from is None
        assert bounty.reserved_for_user_expiration is None

    @staticmethod
    def test_get_token_recipient_senders():
        addresses = get_token_recipient_senders(
            'rinkeby',
            token_address="0x8ad3aA5d5ff084307d28C8f514D7a193B2Bfe725",
            recipient_address="0x03bCeC53fD1a2617a3B064eE8fE4f4c4aacc765B")

        def validate(address):
            return is_address(address) or address == "0x0"

        assert all(validate(address) for address in addresses)

        empty_addresses = get_token_recipient_senders(
            'rinkeby',
            token_address="0x8ad3aA5d5ff084307d28C8f514D7a193B2Bfe725",
            recipient_address="0x57b4Af69127C69ec3248886bBa6deBAB7994695a")

        assert len(empty_addresses) == 0
