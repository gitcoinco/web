# -*- coding: utf-8 -*-
"""Handle gas util related tests.

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
from django.test.client import RequestFactory

from economy.models import ConversionRate
from gas.models import GasProfile
from gas.utils import (
    conf_time_spread, eth_usd_conv_rate, gas_price_to_confirm_time_minutes, recommend_min_gas_price_to_confirm_in_time,
)
from test_plus.test import TestCase


class GasUtilsTest(TestCase):
    """Define tests for gas utils."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.factory = RequestFactory()
        GasProfile.objects.create(
            gas_price=1,
            mean_time_to_confirm_blocks=11,
            mean_time_to_confirm_minutes=10,
            _99confident_confirm_time_blocks=300,
            _99confident_confirm_time_mins=100,
        )
        GasProfile.objects.create(
            gas_price=2,
            mean_time_to_confirm_blocks=5,
            mean_time_to_confirm_minutes=4,
            _99confident_confirm_time_blocks=150,
            _99confident_confirm_time_mins=40,
        )
        GasProfile.objects.create(
            gas_price=3,
            mean_time_to_confirm_blocks=3,
            mean_time_to_confirm_minutes=1,
            _99confident_confirm_time_blocks=100,
            _99confident_confirm_time_mins=10,
        )
        ConversionRate.objects.create(
            from_amount=1,
            to_amount=3,
            source='etherdelta',
            from_currency='ETH',
            to_currency='USDT',
        )

    def test_recommend_min_gas_price_to_confirm_in_time(self):
        """Test the gas util recommend_min_gas_price_to_confirm_in_time method."""
        assert recommend_min_gas_price_to_confirm_in_time(5) == 2

    def test_gas_price_to_confirm_time_minutes(self):
        """Test the gas util gas_price_to_confirm_time_minutes method."""
        assert gas_price_to_confirm_time_minutes(2) == 4

    def test_eth_usd_conv_rate(self):
        """Test the gas util eth_usd_conv_rate method."""
        assert round(eth_usd_conv_rate()) == 3

    def test_conf_time_spread(self):
        """Test the gas util conf_time_spread method."""
        assert conf_time_spread() == '[["1.00", "10.00"], ["2.00", "4.00"], ["3.00", "1.00"]]'
