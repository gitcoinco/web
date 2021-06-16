# -*- coding: utf-8 -*-
"""Handle dashboard embed related tests.

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
import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.test.client import RequestFactory
from django.utils import timezone

from dashboard.models import Bounty, BountyFulfillment, Profile
from dashboard.views import users_fetch
from test_plus.test import TestCase

CURRENT_USERNAME = "asdfasdf"

def setup_bounties():
    owners = [CURRENT_USERNAME, 'user2']
    for owner in owners:
        Bounty.objects.create(
            title='foo',
            value_in_token=3,
            token_name='USDT',
            network='rinkeby',
            web3_created=timezone.now() - timedelta(days=7),
            github_url='https://github.com/oogetyboogety/gitcointestproject/issues/28',
            token_address='0x0',
            issue_description='hello world',
            bounty_owner_github_username=owner,
            is_open=True,
            accepted=True,
            expires_date=timezone.now() + timedelta(days=1, hours=1),
            idx_project_length=5,
            project_length='Months',
            bounty_type='Feature',
            experience_level='Intermediate',
            raw_data={},
            idx_status='submitted',
            bounty_owner_email='asdfasdf@bar.com',
            current_bounty=True
        )

    BountyFulfillment.objects.create(
        fulfiller_address='0x0000000000000000000000000000000000000000',
        accepted=True,
        bounty=Bounty.objects.first(),
        token_name='USDT',
        payout_amount=1.5,
        profile=User.objects.filter(username='user1').first().profile
    )

    BountyFulfillment.objects.create(
        fulfiller_address='0x0000000000000000000000000000000000000000',
        accepted=True,
        bounty=Bounty.objects.last(),
        token_name='USDT',
        payout_amount=1.5,
        profile=User.objects.last().profile
    )


class UsersListTest(TestCase):
    """Define tests for the user list."""

    fixtures = ['tokens.json']

    def setUp(self):
        self.request = RequestFactory()
        self.current_user = User.objects.create(
            password="asdfasdf", username=CURRENT_USERNAME)
        current_user_profile = Profile.objects.create(
            user=self.current_user, data={}, hide_profile=False, handle=CURRENT_USERNAME)

        for i in range(20):
            user = User.objects.create(password="{}".format(i),
                                       username="user{}".format(i))
            profile = Profile.objects.create(
                user=user, data={}, hide_profile=False, handle="{}".format(i))

    def test_user_list(self):
        request = self.request
        request.user = self.current_user
        assert json.loads(users_fetch(request.get('/api/v0.1/users_fetch?user={}'.format(self.current_user.id))).content)['count'] == 21

    def test_default_users_ordering_with_previous_workers_at_the_top(self):
        setup_bounties()

        all_profiles = Profile.objects.annotate(
            worked_with=Count(
                'fulfilled', filter=Q(
                    fulfilled__accepted=True,
                    fulfilled__bounty__bounty_owner_github_username__iexact=CURRENT_USERNAME
                )
            )
        ).order_by('-worked_with')

        #assert all_profiles.values('user__username', 'worked_with')[0] == {'user__username': 'user1', 'worked_with': 1}
