# -*- coding: utf-8 -*-
"""Handle avatar URLs.

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

from django.urls import re_path, path

from .views import grant_show, grants, new_grant

app_name = 'grants'
urlpatterns = [
    path('', grants, name='grants'),
    path('<int:grant_id>', grant_show, name='grant'),
    re_path(r'^new', new_grant, name='new_grant')
]
