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
from django.test import TestCase
from django.test.client import RequestFactory

import requests_mock
from dashboard.helpers import amount, description, keywords, normalize_url, title
from economy.models import ConversionRate


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

    def test_title(self):
        """Test the dashboard helper title method."""
        sample_url = 'https://github.com/gitcoinco/web/issues/353'
        params = {'url': sample_url, 'denomination': 'ETH'}
        with requests_mock.Mocker() as m:
            m.get(sample_url, text='<span class="js-issue-title refined-linkified-title">Increase Code Coverage by 4%</span>')
            request = self.factory.get('/sync/get_issue_title', params)
            assert title(request).content == b'{"title": "Increase Code Coverage by 4%"}'

    def test_description(self):
        """Test the dashboard helper description method."""
        sample_url = 'https://github.com/gitcoinco/web/issues/353'
        params = {'url': sample_url}
        with requests_mock.Mocker() as m:
            m.get('https://api.github.com/repos/gitcoinco/web/issues/353', text='{"body": "This bounty will be paid out to anyone who meaningfully increases the code coverage of the repository by 4%."}')
            request = self.factory.get('/sync/get_issue_description', params)
            assert description(request).content == b'{"description": "This bounty will be paid out to anyone who meaningfully increases the code coverage of the repository by 4%."}'

    def test_keywords(self):
        """Test the dashboard helper keywords method."""
        sample_url = 'https://github.com/gitcoinco/web/issues/353'
        params = {'url': sample_url}
        with requests_mock.Mocker() as m:
            m.get('https://github.com/gitcoinco/web', text='<span class="lang">hello</span><span class="lang">world</span>')
            request = self.factory.get('/sync/get_issue_keywords', params)
            assert keywords(request).content == b'{"keywords": ["web", "gitcoinco", "hello", "world"]}'

    def test_normalize_url(self):
        """Test the dashboard helper normalize_url method."""
        assert normalize_url('https://gitcoin.co/') == 'https://gitcoin.co'
