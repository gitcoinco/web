# -*- coding: utf-8 -*-
"""Handle dashboard embed related tests.

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

import json

from django.contrib.auth.models import User
from django.test.client import RequestFactory

from dashboard.models import Profile
from dashboard.views import users_fetch
from test_plus.test import TestCase


class UsersListTest(TestCase):
    """Define tests for the user list."""

    def setUp(self):
        self.request = RequestFactory()
        self.current_user = User.objects.create(
            password="asdfasdf", username="asdfasdf")
        current_user_profile = Profile.objects.create(
            user=self.current_user, data={}, hide_profile=False, handle="asdfasdf")

        for i in range(20):
            user = User.objects.create(password="{}".format(i),
                                       username="user{}".format(i))
            profile = Profile.objects.create(
                user=user, data={}, hide_profile=False, handle="{}".format(i))

    def test_user_list(self):
        request = self.request
        request.user = self.current_user
        assert json.loads(users_fetch(request.get('/api/v0.1/users_fetch?user={}'.format(self.current_user.id))).content)['count'] == 21
