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

from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment, Profile
from marketing.management.commands.sync_keywords import Command
from marketing.models import Keyword
from test_plus.test import TestCase


class TestSyncKeywords(TestCase):
    """Define tests for sync keywords."""

    def setUp(self):
        """Perform setup for the testcase."""
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web',
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

        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/ethereum/solidity',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='jack',
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            bounty_owner_email='jack@bar.com',
            current_bounty=True
        )

    def test_handle_simple(self):
        """Test command sync keywords."""
        Command().handle()

        assert Keyword.objects.all().count() == 4

    def test_handle_complex(self):
        """Test command sync keywords with bounties metadata and fulfillments."""
        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/ethereum/solidity',
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
            current_bounty=True,
            metadata={
                'issueKeywords': 'ethereum, blockchain,'
            }
        )

        fulfiller_profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )

        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            bounty=bounty,
            profile=fulfiller_profile
        )

        fulfiller_profile = Profile.objects.create(
            data={},
            handle='',
            email='david@bar.com'
        )

        BountyFulfillment.objects.create(
            fulfiller_address='0x0000000000000000000000000000000000000000',
            bounty=bounty,
            profile=fulfiller_profile
        )
        Command().handle()

        # new two added keywords are blockchain and fred
        assert Keyword.objects.all().count() == 6
