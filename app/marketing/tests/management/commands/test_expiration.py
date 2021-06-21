# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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
from datetime import datetime, timedelta
from unittest.mock import patch

from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment, Profile
from marketing.management.commands.expiration import Command
from test_plus.test import TestCase


class TestExpiration(TestCase):
    """Define tests for expiration bounty."""

    @patch('marketing.management.commands.expiration.bounty_expire_warning')
    def test_handle(self, mock_func):
        """Test command expiration bounty with expired bounties."""
        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
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
            current_bounty=True,
            network='mainnet'
        )
        fulfiller_profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )
        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            bounty=bounty,
            profile=fulfiller_profile,
        )

        Command().handle()

        mock_func.assert_called_once_with(bounty, ['john@bar.com', 'fred@bar.com'])

    @patch('marketing.management.commands.expiration.bounty_expire_warning')
    def test_handle_no_users(self, mock_func):
        """Test command expiration bounty without users for expired bounties."""
        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            current_bounty=True,
            network='mainnet'
        )
        fulfiller_profile = Profile.objects.create(
            data={},
            handle='fred'
        )
        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            bounty=bounty,
            profile=fulfiller_profile,
        )

        Command().handle()

        mock_func.assert_called_once_with(bounty, [])
