# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

Copyright (C) 2019 Gitcoin Core

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
from datetime import datetime, timedelta
from unittest import mock

from django.conf import settings
from django.utils import timezone

import marketing
import marketing.management.commands.sync_pull_request_with_bounty_fulfillments
from dashboard.models import Bounty, BountyFulfillment
from test_plus.test import TestCase


class GitHubTestAPI:
    def get_interested_actions(self):
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'github_api_issue_with_pr_call.json')) as f:
            return json.load(f)

class TestSyncPullRequestWithBountyFulfillments(TestCase):
    """Define tests for sync of bounty fulfillments and related issue pull requests."""

    def setUp(self):
        """Perform setup for the testcase."""
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=timezone.now()-timedelta(days=7),
            github_url='https://github.com/oogetyboogety/gitcointestproject/issues/28',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='john',
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            bounty_owner_email='john@bar.com',
            current_bounty=True
        )

        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            fulfiller_email='fred@bar.com',
            fulfiller_github_username='samplegitcoindeveloper1',
            fulfiller_name='Fred',
            accepted=False,
            bounty=Bounty.objects.last()
        )

    @mock.patch('premailer.premailer.requests')
    def test_handle_simple(self, mocked_requests):
        """Test command sync keywords."""
        start_time = timezone.now()
        mock.patch('marketing.management.commands.sync_pull_request_with_bounty_fulfillments.get_gh_issue_state', lambda x, y, z: 'closed').start()
        mock.patch('marketing.management.commands.sync_pull_request_with_bounty_fulfillments.get_interested_actions', lambda x, y: GitHubTestAPI().get_interested_actions()).start()

        with open(settings.BASE_DIR + '/assets/v2/css/lib/typography.css') as f:
            mocked_requests.get.return_value.ok = True
            mocked_requests.get.return_value.text = f.read()
            mocked_requests.get.return_value.body = f.read()

            marketing.management.commands.sync_pull_request_with_bounty_fulfillments.Command().handle(live=False)

            assert BountyFulfillment.objects.last().funder_last_notified_on >= start_time
