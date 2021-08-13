# -*- coding: utf-8 -*-
"""Handle dashboard helper related tests.

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
from django.conf import settings
from django.test.client import RequestFactory

from dashboard.helpers import amount, is_lowball_bounty, normalize_url
from economy.models import ConversionRate
from test_plus.test import TestCase


class DashboardHelpersTest(TestCase):
    """Define tests for dashboard helpers."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.factory = RequestFactory()
        ConversionRate.objects.create(
            from_amount=1,
            to_amount=2,
            source='etherdelta',
            from_currency='ETH',
            to_currency='USDT',
        )

    def test_amount(self):
        """Test the dashboard helper amount method."""
        params = {'amount': '5', 'denomination': 'ETH'}
        request = self.factory.get('/sync/get_amount', params)
        assert amount(request).content == b'[{"token": "ETH", "amount": 5.0, "eth": 5.0, "usdt": 10.0}]'

    def test_lowball_bounty(self):
        assert is_lowball_bounty(settings.LOWBALL_BOUNTY_THRESHOLD - 1.0)
        assert not is_lowball_bounty(settings.LOWBALL_BOUNTY_THRESHOLD)

    def test_normalize_url(self):
        """Test the dashboard helper normalize_url method."""
        assert normalize_url('https://gitcoin.co/') == 'https://gitcoin.co'
