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

from grants.views import (
    grant_details, grant_fund, grant_new, grant_new_v0, grants, leaderboard, milestones, new_matching_partner, profile,
    quickstart, subscription_cancel,
)

app_name = 'grants'
urlpatterns = [
    path('', grants, name='grants'),
    path('<int:grant_id>/<slug:grant_slug>', grant_details, name='details'),
    path('<int:grant_id>/<slug:grant_slug>/', grant_details, name='details2'),
    re_path(r'^new', grant_new, name='new'),
    re_path(r'^old', grant_new_v0, name='old'),
    path('<int:grant_id>/<slug:grant_slug>/milestones', milestones, name='milestones'),
    path('<int:grant_id>/<slug:grant_slug>/fund', grant_fund, name='fund'),
    path(
        '<int:grant_id>/<slug:grant_slug>/subscription/<int:subscription_id>/cancel',
        subscription_cancel,
        name='subscription_cancel'
    ),
    re_path(r'^profile', profile, name='profile'),
    re_path(r'^quickstart', quickstart, name='quickstart'),
    re_path(r'^leaderboard', leaderboard, name='leaderboard'),
    re_path(r'^matching-partners/new', new_matching_partner, name='new_matching_partner'),
]
