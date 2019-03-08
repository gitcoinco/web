# -*- coding: utf-8 -*-
"""Handle marketing mail related tests.

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
import os
from datetime import timedelta
from unittest import mock

from django.conf import settings
from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment, Profile
from marketing.mails import funder_payout_reminder
from test_plus.test import TestCase


class MarketingMailTest(TestCase):
    """Define tests for each individual marketing mail."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.email = 'user1@gitcoin.co'
        self.user = self.make_user('user1')
        self.user.email = self.email
        self.user.profile = Profile.objects.create(
            user=self.user,
            handle='user1',
            last_sync_date=timezone.now(),
            data={},
        )
        self.user.save()
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

    @mock.patch("premailer.premailer.requests") 
    def test_funder_payout_reminder(self, mocked_requests):
        with open(settings.BASE_DIR + '/assets/v2/css/lib/typography.css') as f:
            mocked_requests.get.return_value.ok = True
            mocked_requests.get.return_value.body = f.read()
            mocked_requests.get.return_value.text = f.read()
            html = funder_payout_reminder("user1@gitcoin.co", bounty=Bounty.objects.last(), github_username="samplegitcoindeveloper1", live=False)
            assert 'There is a currently pending claim against this funded issue.' in html
            assert "Please make sure you process them!" in html
            assert 'foo' in html
