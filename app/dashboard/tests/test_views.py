# -*- coding: utf-8 -*-
"""Handle github dashboard view related tests.

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

from django.conf import settings
from django.test import Client
from django.utils import timezone

from dashboard.views import bounty_details
from test_plus.test import TestCase


class DashboardViewsTest(TestCase):
    """Define tests for Dashboard views module."""

    def test_bounty_details_issueURL_context_set_to_github_url_when_github_bounty(self):
        """Test the issueURL param value is set as expected when a ghissue argument is provided"""
        from dashboard.models import Bounty
        from datetime import datetime
        owner = 'github_owner'
        repo = 'github_repo'
        issue_id = 999
        expected_url = f'https://github.com/{owner}/{repo}/issues/{issue_id}'
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=timezone.make_aware(datetime.now()),
            github_url=expected_url,
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=True,
            accepted=True,
            expires_date=timezone.make_aware(datetime.now()) + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            network='mainnet',
            current_bounty=True
        )
        response = Client().get(f'/bounty/details/{owner}/{repo}/{issue_id}')
        actual_url = response.context['issueURL']
        self.assertEqual(actual_url, expected_url)

    def test_bounty_details_issueURL_set_to_url_query_param_when_non_github_bounty(self):
        """Test the issueURL param value is set as expected when no ghissue argument is provided"""
        from dashboard.models import Bounty
        from datetime import datetime
        expected_url = f'https://foo.com?bar=1&baz=2&faz=3'
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='ETH',
            web3_created=timezone.make_aware(datetime.now()),
            github_url=expected_url,
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='flintstone',
            is_open=True,
            accepted=True,
            expires_date=timezone.make_aware(datetime.now()) + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            network='mainnet',
            current_bounty=True
        )
        response = Client().get(f'/bounty/details/?url={expected_url}')
        actual_url = response.context['issueURL']
        self.assertEqual(actual_url, expected_url)
