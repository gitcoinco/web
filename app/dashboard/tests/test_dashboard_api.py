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
import os
import sys
from datetime import date, datetime, timedelta

from django.conf import settings
from django.test.client import RequestFactory

import pytz
import requests_mock
from dashboard.helpers import amount, issue_details, normalize_url
from dashboard.models import Bounty, BountyFulfillment, Interest, Profile, Tip, Tool, ToolVote
from economy.models import ConversionRate
from test_plus.test import APITestCase


def response_to_json(response):
    str_content = response.content.decode("utf-8")
    return json.loads(str_content)

class DashboardAPITest(APITestCase):
    """Define tests for dashboard helpers."""

    def setUp(self):
        """Perform setup for the testcase."""


    def test_bounties(self):
        """Test the dashboard helper amount method."""
        ConversionRate.objects.create(
            from_amount=1,
            to_amount=2,
            source='etherdelta',
            from_currency='ETH',
            to_currency='USDT',
        )
        for i in range(255):
            fulfiller_profile = Profile.objects.create(
                data={},
                handle='fred',
                email='fred@localhost'
            )
            bounty = Bounty.objects.create(
                title='foo'+str(i),
                value_in_token=3,
                token_name='ETH',
                web3_created=datetime(2008, 10, 31, tzinfo=pytz.UTC),
                github_url='https://github.com/gitcoinco/web/issues/11',
                token_address='0x0',
                issue_description='hello world',
                bounty_owner_github_username='flintstone',
                is_open=False,
                accepted=True,
                network="mainnet",
                expires_date=datetime(2008, 11, 30, tzinfo=pytz.UTC),
                idx_project_length=5,
                project_length='Months',
                bounty_type='Feature',
                experience_level='Intermediate',
                raw_data={},
                current_bounty=True,
            )
            bounty_fulfillment = BountyFulfillment.objects.create(
                fulfiller_address='0x0000000000000000000000000000000000000000',
                fulfiller_email='',
                fulfiller_github_username='fred',
                fulfiller_name='Fred',
                bounty=bounty,
                profile=fulfiller_profile,
            )

        self.assertEqual(Bounty.objects.count(), 255)

        response = self.client.get('/api/v0.1/bounties/')
        json_content = response_to_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_content), 100)

        response = self.client.get('/api/v0.1/bounties/?limit=10')
        json_content = response_to_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_content), 10)

        response = self.client.get('/api/v0.1/bounties/?limit=150')
        json_content = response_to_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_content), 100)
        self.assertEqual(Bounty.objects.all()[5].title, json_content[5]['title'],'foo5' )

        response = self.client.get('/api/v0.1/bounties/?limit=150&offset=5')
        json_content = response_to_json(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Bounty.objects.all()[10].title, json_content[5]['title'],'foo10')
