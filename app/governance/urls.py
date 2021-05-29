# -*- coding: utf-8 -*-
"""Handle grant URLs.

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
from django.urls import path, re_path

import governance.views
from governance.games.diplomacy import index as diplomacy, diplomacy_idx

app_name = 'governance'
urlpatterns = [
    path('', governance.views.index, name='governance'),
    path('diplomacy/<str:slug>', diplomacy, name='governance_game_diplomacy'),
    re_path(r'diplomacy/?', diplomacy_idx, name='governance_game_diplomacy_idx'),


]
