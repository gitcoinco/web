# -*- coding: utf-8 -*-
"""Handle marketing commands related tests.

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
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

import requests_mock
from dashboard.models import Bounty, Subscription
from marketing.management.commands.send_subscription_mails import Command


class TestSendSubsciptionMails(TestCase):
    """Define tests for roundup send subscription mails."""

    def setUp(self):
        """Perform setup for the testcase."""

        Subscription.objects.create(
            email='john@gitcoin.co',
            raw_data='raw',
            ip='127.0.0.1'
        )

    @patch('marketing.management.commands.send_subscription_mails.new_bounty')
    def test_handle_old_bounties(self, mock_new_bounty):
        """Test command send subscription mails with old bounties."""

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
            expires_date=timezone.now(),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='open',
            bounty_owner_email='john@bar.com',
            current_bounty=True
        )

        with requests_mock.Mocker() as m:
            m.get('https://gitcoin.co/raw', json=[{'pk': bounty.pk}])
            Command().handle()

        assert mock_new_bounty.call_count == 0

    @patch('marketing.management.commands.send_subscription_mails.new_bounty')
    def test_handle_new_bounties(self, mock_new_bounty):
        """Test command send subscription mails with new bounties."""

        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=timezone.now(),
            github_url='https://github.com/gitcoinco/web',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=True,
            accepted=True,
            expires_date=timezone.now(),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='open',
            bounty_owner_email='john@bar.com',
            current_bounty=True
        )

        with requests_mock.Mocker() as m:
            m.get('https://gitcoin.co/raw', json=[{'pk': bounty.pk}])
            Command().handle()

        assert mock_new_bounty.call_count == 1
