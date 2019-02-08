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
from dashboard.helpers import amount, issue_details, normalize_url, process_bounty_details
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
    
    @patch('marketing.mails.send_mail')
    def test_featured_funded_mail(self, mock_send_mail):
        """Test sending featured funded bounty mail."""
        bounty_payload = {
            "id": 1,
            "url": "https://gitcoin.co/issue/danlipert/gitcoin-test/5/1725",
            "created_on": "2019-02-07T15:18:36.941414Z",
            "modified_on": "2019-02-08T10:17:30.891073Z",
            "title": "The real issue that will be closed",
            "web3_created": "2019-02-07T14:38:22Z",
            "value_in_token": "1000000000000000.00",
            "token_name": "ETH",
            "token_address": "0x0000000000000000000000000000000000000000",
            "bounty_type": "",
            "project_length": "Unknown",
            "experience_level": "",
            "github_url": "https://github.com/danlipert/gitcoin-test/issues/5",
            "github_comments": 0,
            "bounty_owner_address": "0xe317c793ebc9d4a3732ca66e5a8fc4ffc213b989",
            "bounty_owner_email": "danlipert@gmail.com",
            "bounty_owner_github_username": "dan",
            "bounty_owner_name": "Anonymous",
            "fulfillments": [
                {
                    "fulfiller_address": "0xAeF6300Bc0E4227c08ab62a2489B2BFF3511e5aF",
                    "fulfiller_email": "danlipert@gmail.com",
                    "fulfiller_github_username": "danlipert",
                    "fulfiller_name": "",
                    "fulfillment_id": 0,
                    "accepted":True,
                    "profile": 7766,
                    "created_on": "2019-02-07T15:18:38.678328Z",
                    "accepted_on": "2019-02-07T15:18:38.678320Z",
                    "fulfiller_github_url": ""
                }
            ],
            "interested": [],
            "is_open":True,
            "expires_date": "2020-02-07T14:38:22Z",
            "activities": [],
            "keywords": "",
            "current_bounty":True,
            "value_in_eth": "1000000000000000.00",
            "token_value_in_usdt": "104.60",
            "value_in_usdt_now": "0.00",
            "value_in_usdt": "0.00",
            "status": "done",
            "now": "2019-02-08T12:38:36.208491Z",
            "avatar_url": "https://gitcoin.co/dynamic/avatar/danlipert",
            "value_true": "0.00",
            "issue_description": "adsgadfh",
            "network": "rinkeby",
            "org_name": "danlipert",
            "pk": 8564,
            "issue_description_text": "adsgadfh",
            "standard_bounties_id": 1725,
            "web3_type": "bounties_network",
            "can_submit_after_expiration_date":True,
            "github_issue_number": 5,
            "github_org_name": "danlipert",
            "github_repo_name": "gitcoin-test",
            "idx_status": "done",
            "token_value_time_peg": "2019-02-07T14:38:22Z",
            "fulfillment_accepted_on": "2019-02-07T15:18:38.678320Z",
            "fulfillment_submitted_on": "2019-02-07T15:18:38.678328Z",
            "fulfillment_started_on": 'null',
            "canceled_on": 'null',
            "canceled_bounty_reason": "",
            "issuer": "null",
            "action_urls": {
                "fulfill": "/issue/fulfill?pk=8564&network=rinkeby",
                "increase": "/issue/increase?pk=8564&network=rinkeby",
                "accept": "/issue/accept?pk=8564&network=rinkeby",
                "cancel": "/issue/cancel?pk=8564&network=rinkeby",
                "payout": "/issue/payout?pk=8564&network=rinkeby",
                "contribute": "/issue/contribute?pk=8564&network=rinkeby",
                "advanced_payout": "/issue/advanced_payout?pk=8564&network=rinkeby",
                "social_contribution": "/issue/social_contribution?pk=8564&network=rinkeby",
                "invoice": "/issue/invoice?pk=8564&network=rinkeby"
            },
            "project_type": "traditional",
            "permission_type": "approval",
            "attached_job_description": "",
            "needs_review":False,
            "github_issue_state": "closed",
            "is_issue_closed":True,
            "additional_funding_summary": {},
            "funding_organisation": "",
            "paid": [
                "danlipert"
            ],
            "admin_override_suspend_auto_approval":True,
            "reserved_for_user_handle": "",
            "is_featured":True
        },
        process_bounty_details(bounty_payload)
        if (bounty_payload['is_featured']):
            assert mock_send_mail.call_count == 1
