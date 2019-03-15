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
from unittest.mock import patch

from marketing.management.commands.roundup import Command
from marketing.models import EmailSubscriber
from test_plus.test import TestCase


class TestRoundup(TestCase):
    """Define tests for roundup."""

    def setUp(self):
        """Perform setup for the testcase."""
        EmailSubscriber.objects.create(
            email='john@bar.com',
            source='mysource',
            newsletter=True
        )
        EmailSubscriber.objects.create(
            email='jackson@bar.com',
            source='mysource',
            newsletter=True
        )
        EmailSubscriber.objects.create(
            email='fred@bar.com',
            source='mysource',
            newsletter=True
        )
        EmailSubscriber.objects.create(
            email='paul@bar.com',
            source='mysource'
        )

    @patch('time.sleep')
    @patch('marketing.management.commands.roundup.weekly_roundup')
    def test_handle_no_options(self, mock_weekly_roundup, *args):
        """Test command roundup when live option is False."""
        Command().handle(exclude_startswith=None, filter_startswith=None, start_counter=0, live=False)

        assert mock_weekly_roundup.call_count == 0

    @patch('time.sleep')
    @patch('marketing.management.commands.roundup.weekly_roundup')
    def test_handle_with_options(self, mock_weekly_roundup, *args):
        """Test command roundup which various options."""
        Command().handle(exclude_startswith='f', filter_startswith='jack', start_counter=0, live=True)

        assert mock_weekly_roundup.call_count == 1

        mock_weekly_roundup.assert_called_once_with(['jackson@bar.com'])
