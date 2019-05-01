# -*- coding: utf-8 -*-
"""Handle grant URLs.

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
from django.urls import path, re_path

from experts.views import (  # grant_details, grant_fund, grant_new, experts, leaderboard, milestones, new_matching_partner, profile, quickstart,; subscription_cancel,
    frontend, index, quickstart,
)

app_name = 'experts'
urlpatterns = [
    path('', index, name='index'),
    re_path(r'^quickstart', quickstart, name='quickstart'),
    # Route remaining URLs to React frontend app
    re_path('^new/', frontend, name='new_session'),
    path('sessions/<int:session_id>/', frontend, name='test_frontend'),
]
