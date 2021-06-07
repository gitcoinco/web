# -*- coding: utf-8 -*-
"""Handle binance sync related tests.

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
import os
from datetime import timedelta
from unittest import mock

from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment, Profile
from dashboard.sync.binance import get_binance_txn_status, sync_binance_payout
from test_plus.test import TestCase


class BinanceSyncTest(TestCase):
    """Define tests for binance sync."""

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
        self.bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='BNB',
            network='mainnet',
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
            bounty=bounty,
            payout_tx_id='0xc32f5ad8a1dec9e0ae67f0f55f772ea752e7e032b62b1cdaf8d392e12c66e919'
        )

    # def test_get_binance_txn_status(self, mocked_requests):
    #     pass

    # def test_sync_binance_payout(self):
    #     pass
