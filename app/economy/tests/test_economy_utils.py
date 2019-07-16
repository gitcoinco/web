# -*- coding: utf-8 -*-
"""Handle economy util related tests.

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
from datetime import datetime
from unittest import mock

from django.test.client import RequestFactory

from economy.models import ConversionRate
from economy.utils import ConversionRateNotFoundError, convert_amount, convert_token_to_usdt, etherscan_link
from test_plus.test import TestCase


def mocked_convert_amount_side_effect(from_amount, from_currency, to_currency, timestamp=None):
    if from_currency == 'foo' and to_currency == 'USDT':
        raise ConversionRateNotFoundError()
    return 123


class EconomyUtilsTest(TestCase):
    """Define tests for economy utils."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.factory = RequestFactory()
        ConversionRate.objects.create(
            from_amount=1,
            to_amount=5,
            source='etherdelta',
            from_currency='ETH',
            to_currency='USDT',
            timestamp=datetime(2018, 1, 1)  # Arbitrary timestamp in the past
        )
        ConversionRate.objects.create(
            from_amount=1,
            to_amount=2,
            source='etherdelta',
            from_currency='ETH',
            to_currency='USDT',
        )
        ConversionRate.objects.create(
            from_amount=1,
            to_amount=3,
            source='etherdelta',
            from_currency='ETH',
            to_currency='USDT',
        )

    def test_convert_amount(self):
        """Test the economy util convert_amount method."""
        result = convert_amount(2, 'ETH', 'USDT')
        assert round(result, 1) == 6

    def test_convert_amount_time_travel(self):
        """Test the economy util convert_amount method for historic ConversionRates."""
        result = convert_amount(2, 'ETH', 'USDT', datetime(2018, 1, 1))
        assert round(result, 1) == 10

    def test_convert_amount_raises(self):
        """Test the economy util convert_amount method for raising ConversionRateNotFoundError."""
        from_currency = 'foo'
        to_currency = 'bar'
        exc_msg = f"ConversionRate {from_currency}/{to_currency} @ None not found"
        with self.assertRaisesMessage(ConversionRateNotFoundError, exc_msg):
            convert_amount(101, from_currency, to_currency)

    @mock.patch('economy.utils.convert_amount', return_value=321)
    def test_convert_token_to_usdt(self, mocked_convert_amount):
        """Test the economy util convert_token_to_usdt method."""
        rv = convert_token_to_usdt('ETH')
        assert rv == 321
        mocked_convert_amount.assert_called_with(1, 'ETH', 'USDT', None)

    @mock.patch('economy.utils.convert_amount', side_effect=mocked_convert_amount_side_effect)
    def test_convert_token_to_usdt_conversion_rate_not_found(self, mocked_convert_amount):
        """Test the economy util convert_token_to_usdt for handling ConversionRateNotFoundError."""
        from_token = 'foo'
        rv = convert_token_to_usdt(from_token)
        assert rv == 123
        calls = [
            mock.call(1, from_token, 'USDT', None),
            mock.call(1, from_token, 'ETH', None),
            mock.call(123, 'ETH', 'USDT', None)
        ]
        mocked_convert_amount.assert_has_calls(calls)

    def test_etherscan_link(self):
        """Test the economy util etherscan_link method."""
        txid = '0xcb39900d98fa00de2936d2770ef3bfef2cc289328b068e580dc68b7ac1e2055b'
        assert etherscan_link(txid) == 'https://etherscan.io/tx/0xcb39900d98fa00de2936d2770ef3bfef2cc289328b068e580dc68b7ac1e2055b'
