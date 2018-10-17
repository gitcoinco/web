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

from grants.views import grant_details, grant_fund, grant_new, grants, milestones, profile, subscription_cancel

app_name = 'grants'
urlpatterns = [
    path('', grants, name='grants'),
    path('<int:grant_id>', grant_details, name='details'),
    re_path(r'^new', grant_new, name='new'),
    path('<int:grant_id>/milestones', milestones, name='milestones'),
    path('fund/<int:grant_id>', grant_fund, name='fund'),
    path('subscription_cancel/<int:subscription_id>', subscription_cancel, name='subscription_cancel'),
    re_path(r'^profile', profile, name='profile')
]
