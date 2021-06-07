# -*- coding: utf-8 -*-
"""Test BountyState and BountyEvent interactions and FSM

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

from datetime import timedelta

from django.utils import timezone

from dashboard.models import Bounty, BountyEvent
from test_plus.test import TestCase


class BountyStateTest(TestCase):
    """Define tests for bounty states and events."""

    def setUp(self):
        self.bounty = Bounty.objects.create(
            title='foo',
            project_type='traditional',
            value_in_token=3,
            token_name='USDT',
            web3_created=timezone.now() - timedelta(days=7),
            github_url='https://github.com/danlipert/gitcoin-test/issues/1',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username='example',
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='open',
            bounty_owner_email='asdfasdf@bar.com',
            current_bounty=True,
            bounty_state='open'
        )

    def test_handle_event(self):
        event = BountyEvent.objects.create(
            bounty=self.bounty,
            event_type='express_interest'
        )
        self.bounty.handle_event(event)
        assert self.bounty.bounty_state == 'open'
        event_accept = BountyEvent.objects.create(
            bounty=self.bounty,
            event_type='accept_worker'
        )
        self.bounty.handle_event(event_accept)
        assert self.bounty.bounty_state == 'work_started'
