# -*- coding: utf-8 -*-
"""Handle gas util related tests.

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
from marketing.models import EmailSubscriber, Stat
from marketing.utils import func_name, get_or_save_email_subscriber, get_stat, should_suppress_notification_email
from test_plus.test import TestCase


class MarketingUtilsTestCase(TestCase):
    """Define tests for general marketing utils."""

    @staticmethod
    def test_func_name():
        """Test the func_name method and ensure parent method matches."""
        function_name = func_name()
        assert function_name == 'test_func_name'


class MarketingStatUtilsTest(TestCase):
    """Define tests for marketing utils."""

    def setUp(self):
        """Perform setup for the testcase."""
        Stat.objects.create(key='mykey', val=1)
        Stat.objects.create(key='mykey', val=2)

    def test_get_stat(self):
        """Test the marketing util get_stat method."""
        assert get_stat('mykey') == 2


class MarketingEmailUtilsTest(TestCase):
    """Define tests for marketing email utils."""

    def setUp(self):
        """Perform setup for the testcase."""
        test_es = EmailSubscriber.objects.all().delete()

        EmailSubscriber.objects.create(
            email='emailSubscriber1@gitcoin.co',
            source='mysource',
            priv='priv1',
            preferences={'suppression_preferences': {
                'foo': False
            }}
        )
        EmailSubscriber.objects.create(
            email='emailSubscriber2@gitcoin.co',
            source='mysource',
            preferences={'suppression_preferences': {
                'foo': False
            }}
        )
        EmailSubscriber.objects.create(
            email='emailSubscriber3@gitcoin.co',
            source='mysource',
            preferences={'suppression_preferences': {
                'foo': True
            }}
        )

    def test_should_suppress_notification_email(self):
        """Test the marketing util test_should_suppress_notification_email method."""
        assert not should_suppress_notification_email('emailSubscriber1@gitcoin.co', 'foo')
        assert not should_suppress_notification_email('emailSubscriber2@gitcoin.co', 'foo')
        assert should_suppress_notification_email('emailSubscriber3@gitcoin.co', 'foo')

    def test_get_of_get_or_save_email_subscriber(self):
        """Test the marketing util get_or_save_email_subscriber method."""
        es = get_or_save_email_subscriber('emailSubscriber1@gitcoin.co', 'mysource')
        assert es.priv == 'priv1'

        es2 = get_or_save_email_subscriber('emailSubscriber1@gitcoin.co', 'secondsource')

        assert es2.priv == 'priv1'

    def test_save_get_or_save_email_subscriber_get(self):
        """Test the marketing util get_or_save_email_subscriber method."""
        self.assertIsNotNone(get_or_save_email_subscriber('newemail@gitcoin.co', 'mysource', send_slack_invite=False))

        assert EmailSubscriber.objects.filter().count() == 4
