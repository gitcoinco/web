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
import csv
import io
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

# The following CSV contains the expected behavior, when we are sneding notifications:
# Columns:
#   user_handle_prefix - just some prefix to which we add the row number (starting with 1) and create a test profile
#   interest_days_back - number of days back, when the interest of the user in a bounty was registered
#   accepted_days_back - number of days back, when the interest of the user was accepted
#   snooze_days - the number of days to snooze notifications for the bounty
#   last_action_days_back - number of days back since the last action was performed
#   expect_expire_warning - do we expect warning ?
#   expect_expired_notification - do we expect expired notification ?
#   comment - just some comment for the line, this is not used in the TC
#
#   Boolean values: True for true / any other value means false
#   Where numeric value is expected: if None, the setting will be ignored

CSV_NOTIFICATION_EXPECTATIONS = """\
user_handle_prefix,interest_days_back,accepted_days_back,snooze_days,last_action_days_back,expect_expire_warning,expect_expired_notification, comment
fred_        , 2                  , 1                     , None        , None                        , False                       , False
fred_        , 3                  , 2                     , None        , None                        , False                       , False
fred_        , 4                  , 3                     , None        , None                        , True                        , False
fred_        , 4                  , 3                     , 10          , None                        , False                       , False
fred_        , 5                  , 4                     , None        , None                        , False                       , False
fred_        , 6                  , 5                     , None        , None                        , True                        , False , I would not expect notification here - I would expect on day 6 since acceptance
fred_        , 6                  , 5                     , 10          , None                        , False                       , False
fred_        , 7                  , 6                     , None        , None                        , False                       , True
fred_        , 7                  , 6                     , 10          , None                        , False                       , False
fred_        , 8                  , 7                     , None        , None                        , False                       , False
fred_        , 9                  , 8                     , None        , None                        , False                       , True
fred_        , 9                  , 8                     , 10          , None                        , False                       , False
fred_        , 10                 , 9                     , None        , None                        , False                       , False
fred_        , 11                 , 10                    , None        , None                        , False                       , False
fred_        , 12                 , 11                    , None        , None                        , False                       , False
fred_        , 13                 , 12                    , None        , 1                           , False                       , False
fred_        , 13                 , 12                    , None        , 2                           , False                       , False
fred_        , 13                 , 12                    , None        , 3                           , True                        , False
fred_        , 13                 , 12                    , 10          , 3                           , False                       , False
fred_        , 13                 , 12                    , None        , 4                           , True                        , False
fred_        , 13                 , 12                    , 10          , 4                           , False                       , False
fred_        , 13                 , 12                    , None        , 5                           , True                        , False
fred_        , 13                 , 12                    , 10          , 5                           , False                       , False
fred_        , 13                 , 12                    , None        , 6                           , False                       , True
fred_        , 13                 , 12                    , None        , 7                           , False                       , True
fred_        , 13                 , 12                    , None        , 8                           , False                       , True
fred_        , 13                 , 12                    , None        , 9                           , False                       , False
fred_        , 12                 , 12                    , None        , None                        , False                       , False
fred_        , 9                  , 9                     , None        , None                        , False                       , False
fred_        , 6                  , 6                     , None        , None                        , False                       , True
fred_        , 30                 , 30                    , 50          , None                        , False                       , False
fred_        , 30                 , 30                    , None        , 3                           , True                        , False
fred_        , 30                 , 30                    , None        , 6                           , False                       , True
fred_        , 30                 , 30                    , 50          , 6                           , False                       , False
fred_        , 30                 , 30                    , 50          , 51                          , False                       , False
"""




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

    def test_notifications(self):
        print(CSV_NOTIFICATION_EXPECTATIONS)
        dict_reader = csv.DictReader(io.StringIO(CSV_NOTIFICATION_EXPECTATIONS), delimiter=",")
        idx = 0
        for csv_dict in dict_reader:
            idx += 1
            d = {k: v.strip() if v else v for k, v in csv_dict.items()}
            d["user_handle"] = d["user_handle_prefix"] + str(idx)
            print(d)
            user_handle = d["user_handle"]
            interest_days_back = int(d["interest_days_back"]) if d["interest_days_back"] != "None" else None
            accepted_days_back = int(d["accepted_days_back"]) if d["accepted_days_back"] != "None" else None
            snooze_days = int(d["snooze_days"]) if d["snooze_days"] != "None" else None
            last_action_days_back = int(d["last_action_days_back"]) if d["last_action_days_back"] != "None" else None
            expected_warning_call_count = 1 if d["expect_expire_warning"] == "True" else 0
            expected_expired_call_count = 1 if d["expect_expired_notification"] == "True" else 0
            profile = Profile.objects.create(
                data={},
                handle=user_handle,
                email=f'{user_handle}@bar.com'
            )

            interest = Interest.objects.create(
                profile=profile
            )
            interest.created = timezone.now() - timedelta(days=interest_days_back)
            if accepted_days_back:
                interest.acceptance_date = timezone.now() - timedelta(days=accepted_days_back)
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
                permission_type='approval',
            )

            if snooze_days:
                bounty.snooze_warnings_for_days = snooze_days

            bounty.interested.add(interest)
            bounty.save()

            actions_expired = []

            if last_action_days_back:
                actions_expired = [{
                    'user': {
                        'login': user_handle
                    },
                    'created_at': (timezone.now() - timedelta(days=last_action_days_back)).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'event': 'commented',
                }]

            with patch.object(marketing.management.commands.expiration_start_work, 'get_interested_actions', return_value=actions_expired) as mock_get_interested_actions:
                with patch.object(marketing.management.commands.expiration_start_work, 'bounty_startwork_expire_warning', return_value=actions_expired) as mock_bounty_startwork_expire_warning:
                    with patch.object(marketing.management.commands.expiration_start_work, 'bounty_startwork_expired', return_value=actions_expired) as mock_bounty_startwork_expired:
                        
                        Command().handle()

                        print("GERI mock_get_interested_actions.call_count", mock_get_interested_actions.call_count)
                        print("GERI mock_bounty_startwork_expire_warning.call_count", mock_bounty_startwork_expire_warning.call_count)
                        print("GERI mock_bounty_startwork_expired.call_count", mock_bounty_startwork_expired.call_count)

                        assert mock_bounty_startwork_expired.call_count == expected_expired_call_count
                        assert mock_bounty_startwork_expire_warning.call_count == expected_warning_call_count

            interest.delete()
