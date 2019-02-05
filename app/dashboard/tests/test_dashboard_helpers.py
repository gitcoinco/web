# -*- coding: utf-8 -*-
"""Handle dashboard helper related tests.

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
import json
from datetime import date, datetime, timedelta
from unittest.mock import patch

from django.test.client import RequestFactory

import pytz
import requests_mock
from dashboard.helpers import amount, issue_details, normalize_url
from dashboard.models import Bounty
from economy.models import ConversionRate
from marketing.mails import featured_funded_bounty
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
        assert amount(request).content == b'{"eth": 5.0, "usdt": 10.0}'

    def test_normalize_url(self):
        """Test the dashboard helper normalize_url method."""
        assert normalize_url('https://gitcoin.co/') == 'https://gitcoin.co'
    
    @patch('marketing.mails.featured_funded_bounty')
    def test_featured_funded_mail(self, mock_featured_funded_bounty):
        """Test sending featured funded bounty mail."""
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/305#issuecomment-999999999',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='iamonuwa',
            bounty_owner_email='matrix4u2002@gmail.com',
            is_open=False,
            accepted=False,
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            is_featured=True
        )
        assert mock_featured_funded_bounty().call_count == 0
