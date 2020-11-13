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
import requests
from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone

from dashboard.models import Profile
from dashboard.views import verify_user_duniter

from unittest import TestCase


class VerifyUserDuniterTests(TestCase):
    def test_get_search_user_duniter(self):
        gitcoin_handle = "developerfred"
        url =  "https://g1.data.duniter.fr/user/profile/_search?q=" + "'gitcoin.co/" + gitcoin_handle + "'"

        response = response.get(url)
        assert_true(response.ok)

    def test_get_public_key_duniter(self):
             gitcoin_handle = "developerfred"
             url =  "https://g1.data.duniter.fr/user/profile/_search?q=" + "'gitcoin.co/" + gitcoin_handle + "'""

             response = response.get(url)
             duniter_user_response = response.json()
             position = duniter_user_json.get('hits', {}).get('hits', {})
             public_key_duniter = next(iter(position)).get('_id', {})

        assert_true(public_key_duniter == "9PDu1zkECAKZd5uULKZz6ecAeHuv5FtnzCruhBM4a5cr")


    def test_same_uid_duniter(self):
             gitcoin_handle = "leomatteudi"
             public_key_duniter = "13XfrqY92tTCDbtu2jFAHsgNbZ9Ne2r5Ts1VGhSCrvUb"
             url =  "https://g1.duniter.org/wot/lookup/" + public_key_duniter

             response = response.get(url)
             duniter_lockup_response = response.json().get('results', {})[0].get('uids', '')[0].get('uid', '')


       assert_true(response.ok)
       assert_true(duniter_lockup_response == gitcoin_handle)

    def test_is_duniter_member(self):
             gitcoin_handle = "leomatteudi"
             public_key_duniter = "13XfrqY92tTCDbtu2jFAHsgNbZ9Ne2r5Ts1VGhSCrvUb"
             url =  'https://g1.duniter.org/wot/certified-by/' + public_key_duniter

             response = response.get(url)
             member_data = response.json()
             isVerified = member_data.get('isMember', {})


       assert_true(isVerified)
