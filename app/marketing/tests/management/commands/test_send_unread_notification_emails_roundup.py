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

from marketing.mails import setup_lang, unread_notification_email_weekly_roundup
from test_plus.test import TestCase


class TestSendUnreadNotificationEmailsRoundup(TestCase):
    """Define tests for roundup."""

    def setUp(self):
        """Perform setup for the testcase."""
        self.email = 'matrix4u2002@gmail.com'

    @patch('marketing.mails.send_mail')
    def test_send_unread_notification_emails(self, mock_send_mail, *args):
        """Test command send unread notification"""

        setup_lang(self.email)
        unread_notification_email_weekly_roundup(to_emails=[self.email])
        assert mock_send_mail.call_count == 1
