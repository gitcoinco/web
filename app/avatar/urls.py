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

from django.urls import re_path

from .views import activate_avatar, avatar, save_custom_avatar, save_github_avatar, select_preset_avatar

app_name = 'avatar'
urlpatterns = [
    re_path(r'^view', avatar, name='view_avatar'),
    re_path(r'^github/save', save_github_avatar, name='save_github_avatar'),
    re_path(r'^custom/save', save_custom_avatar, name='save_avatar_custom'),
    re_path(r'^activate', activate_avatar, name='activate_avatar'),
    re_path(r'^select-preset', select_preset_avatar, name='select_preset_avatar'),
]
