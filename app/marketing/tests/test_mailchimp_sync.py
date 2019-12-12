# -*- coding: utf-8 -*-
"""Handle mailchimp sync related tests.

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
from unittest.mock import patch

from django.conf import settings
from django.utils import timezone

from dashboard.models import Profile
from marketing.management.commands.sync_mail import push_to_mailchimp
from marketing.models import EmailSubscriber
from retail.emails import render_nth_day_email_campaign
from test_plus.test import TestCase


class MailchimpSyncTest(TestCase):
    """Define tests for mailchimp sync."""

    def setUp(self):
        for i in range(10):
            user = self.make_user('user{}'.format(i))
            user.email = 'user{}@gitcoin.co'.format(i)
            user.profile = Profile.objects.create(
                user=user,
                handle='user{}'.format(i),
                last_sync_date=timezone.now(),
                data={},
                persona_is_funder=(i % 2 == 0),
                persona_is_hunter=(i % 3 == 0)
            )
            user.save()
            EmailSubscriber.objects.create(profile=user.profile,
                                           email=user.email)
        settings.MAILCHIMP_LIST_ID_HUNTERS = 'hunters'
        settings.MAILCHIMP_LIST_ID_FUNDERS = 'funders'
        settings.MAILCHIMP_LIST_ID = 'all'


    @patch('marketing.management.commands.sync_mail.sync_mailchimp_list')
    @patch('marketing.management.commands.sync_mail.MailChimp')
    def test_mailchimp_sync(self, mock_mc, mock_sync):
        """Test the marketing mails setup_lang method."""
        push_to_mailchimp()
        assert mock_sync.call_count == 3

        call_dict = {args[0][1]: [es.pk for es in args[0][0]]
                     for args
                     in mock_sync.call_args_list}

        eses_funder = EmailSubscriber.objects.filter(
            active=True, profile__persona_is_funder=True).order_by('-pk')
        assert [es.pk for es in eses_funder] == call_dict['funders']

        eses_hunter = EmailSubscriber.objects.filter(
            active=True, profile__persona_is_hunter=True).order_by('-pk')
        assert [es.pk for es in eses_hunter] == call_dict['hunters']

        eses_all = EmailSubscriber.objects.filter(active=True).order_by('-pk')
        assert [es.pk for es in eses_all] == call_dict['all']
