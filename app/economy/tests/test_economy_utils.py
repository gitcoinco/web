# -*- coding: utf-8 -*-
"""Handle economy util related tests.

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

from django.test.client import RequestFactory

from economy.models import ConversionRate
from economy.utils import convert_amount, etherscan_link
from test_plus.test import TestCase


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

    def test_etherscan_link(self):
        """Test the economy util etherscan_link method."""
        txid = '0xcb39900d98fa00de2936d2770ef3bfef2cc289328b068e580dc68b7ac1e2055b'
        assert etherscan_link(txid) == 'https://etherscan.io/tx/0xcb39900d98fa00de2936d2770ef3bfef2cc289328b068e580dc68b7ac1e2055b'
