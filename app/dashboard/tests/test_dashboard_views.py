# -*- coding: utf-8 -*-
"""Handle dashboard views related tests.

Copyright (C) 2020 Gitcoin Core

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

from datetime import date, datetime, timedelta
from unittest import TestCase
from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone

import requests
from dashboard.models import Profile
from dashboard.views import verify_user_duniter


class VerifyUserDuniterTests(TestCase):
    def test_get_search_user_duniter(self):
        gitcoin_handle = "developerfred"
        url = 'https://g1.data.duniter.fr/user/profile/_search?q=' + gitcoin_handle

        response = requests.get(url)
        self.assertEqual(response.ok, 200)

    def test_get_public_key_duniter(self):
        gitcoin_handle = "developerfred"
        url = "https://g1.duniter.org/user/profile/_search?q=" + gitcoin_handle
        pub_res = "9PDu1zkECAKZd5uULKZz6ecAeHuv5FtnzCruhBM4a5cr"

        response = requests.get(url)
        duniter_user_response = response.json()
        position = duniter_user_response.get('hits', {}).get('hits', {})
        public_key_duniter = next(iter(position)).get('_id', {})

        self.assertEqual(public_key_duniter, pub_res)

    def test_same_uid_duniter(self):
        gitcoin_handle = "leomatteudi"
        public_key_duniter = "13XfrqY92tTCDbtu2jFAHsgNbZ9Ne2r5Ts1VGhSCrvUb"
        url = "https://g1.duniter.org/wot/lookup/" + public_key_duniter

        response = requests.get(url)
        duniter_lockup_response = response.json().get('results', {})[0].get('uids', '')[0].get('uid', '')

        self.assertEqual(duniter_lockup_response, gitcoin_handle)

    def test_is_duniter_member(self):
        public_key_duniter = "13XfrqY92tTCDbtu2jFAHsgNbZ9Ne2r5Ts1VGhSCrvUb"
        url = 'https://g1.duniter.org/wot/certified-by/' + public_key_duniter

        response = requests.get(url)
        member_data = response.json()
        is_verified = member_data.get('isMember', {})

        self.assertEqual(is_verified, True)
