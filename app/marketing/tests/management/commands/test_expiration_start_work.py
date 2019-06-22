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
from datetime import datetime, timedelta
from unittest.mock import patch

from django.utils import timezone

from dashboard.models import Bounty, Interest, Profile
from marketing.management.commands.expiration_start_work import Command
from test_plus.test import TestCase

actions_expired = [
    {
        'user': {
            'login': 'fred'
        },
        'created_at': (timezone.now() - timedelta(days=13)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'event': 'commented',
    },
    {
        'user': {
            'login': 'paul'
        },
        'created_at': (timezone.now() - timedelta(days=13)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'event': 'commented',
    }
]

actions_warning = [
    {
        'user': {
            'login': 'fred'
        },
        'created_at': (timezone.now() - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'event': 'commented',
    }
]


class TestExpirationStartWork(TestCase):
    """Define tests for expiration start work."""

    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expire_warning')
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expired')
    def test_handle_no_interest(self, mock_bounty_startwork_expired, mock_bounty_startwork_expire_warning):
        """Test command expiration start work with not interests."""
        Command().handle()

        assert mock_bounty_startwork_expired.call_count == 0
        assert mock_bounty_startwork_expire_warning.call_count == 0

    @patch('marketing.management.commands.expiration_start_work.get_interested_actions', return_value=actions_expired)
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expire_warning')
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expired')
    def test_handle_expired(self, mock_bounty_startwork_expired, mock_bounty_startwork_expire_warning, *args):
        """Test command expiration start work for expired."""
        profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )
        interest = Interest.objects.create(
            profile=profile
        )
        interest.created = timezone.now() - timedelta(days=12)
        interest.save()

        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web/issues/1/',
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
            network='mainnet',
            idx_status='open',
            bounty_owner_email='john@bar.com',
            current_bounty=True,
            permission_type='approval'
        )

        bounty.interested.add(interest)
        bounty.save()

        Command().handle()

        assert mock_bounty_startwork_expire_warning.call_count == 0
        assert mock_bounty_startwork_expired.call_count == 0

    @patch('marketing.management.commands.expiration_start_work.get_interested_actions', return_value=actions_warning)
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expire_warning')
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expired')
    def test_handle_expire_warning_unaccepted(self, mock_bounty_startwork_expired,
                                              mock_bounty_startwork_expire_warning,
                                              *args):
        """Test command expiration start work for expire warning."""
        profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )
        interest = Interest.objects.create(
            profile=profile
        )
        interest.created = timezone.now() - timedelta(days=9)
        interest.save()

        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web/issues/1/',
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
            idx_status='open',
            bounty_owner_email='john@bar.com',
            current_bounty=True,
            network='mainnet',
            permission_type='approval'
        )

        bounty.interested.add(interest)
        bounty.save()

        Command().handle()

        assert mock_bounty_startwork_expire_warning.call_count == 0
        assert mock_bounty_startwork_expired.call_count == 0

    @patch('marketing.management.commands.expiration_start_work.get_interested_actions', return_value=actions_warning)
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expire_warning')
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expired')
    def test_handle_expire_warning_permissionless(self, mock_bounty_startwork_expired,
                                                  mock_bounty_startwork_expire_warning,
                                                  *args):
        """Test command expiration start work for expire warning."""
        profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )
        interest = Interest.objects.create(
            profile=profile
        )
        interest.created = timezone.now() - timedelta(days=9)
        interest.save()

        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web/issues/1/',
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
            idx_status='open',
            bounty_owner_email='john@bar.com',
            current_bounty=True,
            network='mainnet',
            permission_type='permissionless'
        )

        bounty.interested.add(interest)
        bounty.save()

        Command().handle()

        assert mock_bounty_startwork_expire_warning.call_count == 1
        assert mock_bounty_startwork_expired.call_count == 0

    @patch('marketing.management.commands.expiration_start_work.get_interested_actions', return_value=actions_warning)
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expire_warning')
    @patch('marketing.management.commands.expiration_start_work.bounty_startwork_expired')
    def test_handle_expire_warning_accepted(self, mock_bounty_startwork_expired,
                                            mock_bounty_startwork_expire_warning,
                                            *args):
        """Test command expiration start work for expire warning."""
        profile = Profile.objects.create(
            data={},
            handle='fred',
            email='fred@bar.com'
        )
        interest = Interest.objects.create(
            profile=profile
        )
        interest.created = timezone.now() - timedelta(days=9)
        interest.acceptance_date = timezone.now() - timedelta(days=9)
        interest.save()

        bounty = Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            web3_created=datetime(2008, 10, 31),
            github_url='https://github.com/gitcoinco/web/issues/1/',
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
            idx_status='open',
            bounty_owner_email='john@bar.com',
            current_bounty=True,
            network='mainnet',
            permission_type='approval'
        )

        bounty.interested.add(interest)
        bounty.save()

        Command().handle()

        assert mock_bounty_startwork_expire_warning.call_count == 1
        assert mock_bounty_startwork_expired.call_count == 0
