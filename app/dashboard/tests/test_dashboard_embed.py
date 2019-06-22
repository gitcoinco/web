# -*- coding: utf-8 -*-
"""Handle dashboard embed related tests.

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
from decimal import Decimal

from django.test.client import RequestFactory

import pytz
from dashboard.embed import embed, summarize_bounties, wrap_text
from dashboard.models import Bounty
from test_plus.test import TestCase


class DashboardEmbedTest(TestCase):
    """Define tests for embed."""

    def setUp(self):
        self.factory = RequestFactory()

    @staticmethod
    def test_wrap_text():
        text = " u la la. " * 60
        assert len(wrap_text(text).splitlines()) == 19

    @staticmethod
    def test_summarize_bounties():
        Bounty.objects.create(
            title='First',
            idx_status=0,
            value_in_token=1,
            token_name='USDT',
            is_open=False,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            raw_data={}
        )
        Bounty.objects.create(
            title='Second',
            idx_status=1,
            value_in_token=2,
            token_name='USDT',
            is_open=False,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            raw_data={}
        )
        assert summarize_bounties(Bounty.objects.filter()) == (True, 'Total: 2 issues, 3.00 USD, 0.0 USDT')
        Bounty.objects.create(
            title='Third',
            idx_status=1,
            value_in_token=3,
            token_name='USDT',
            is_open=False,
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
            raw_data={}
        )
        val_usdt = sum(Bounty.objects.filter().values_list('_val_usd_db', flat=True))
        assert val_usdt == Decimal("6.00")

    def test_embed(self):
        assert embed(self.factory.get('/explorer')).status_code == 200
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
            github_url='https://github.com/gitcoinco/web/issues/11',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=True,
            accepted=False,
            network='mainnet',
            expires_date=datetime(2222, 11, 30, tzinfo=pytz.UTC),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
        )
        assert embed(self.factory.get(
            'https://github.com/gitcoinco/web/issues/11?repo=https://github.com/gitcoinco/web'
        )).status_code in [200, 422]
