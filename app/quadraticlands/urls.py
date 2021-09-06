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
from django.conf import settings
from django.conf.urls import include, url
from django.urls import path, re_path

from quadraticlands.helpers import vote
from quadraticlands.router import router
from quadraticlands.views import (
    base, base_auth, dashboard_index, handler400, handler403, handler404, handler500, index, mission_diplomacy,
    mission_diplomacy_room, mission_index, mission_lore, mission_postcard, mission_postcard_svg, mission_schwag,
    workstream_base, workstream_index, get_steward_all_data, get_stewards, get_stewards_data
)

app_name = 'quadraticlands'

urlpatterns = [
    path('', index, name='quadraticlands'),
    re_path(r'^dashboard/?$', dashboard_index, name='dashboard'),
    re_path(r'^vote/?$', vote, name='vote_json'),
    re_path(r'^(?P<base>about|faq)/?$', base, name='quadraticlands_base'),
    re_path(r'^(?P<base>|dashboard|stewards)/?$', base_auth, name='quadraticlands_auth_base'),

    # workstreams
    re_path(r'^workstream/(?P<stream_name>publicgoods|sybil|decentralization|labs)/?$', workstream_base, name='workstream_base'),
    re_path(r'^workstream/?$', workstream_index, name='workstream'),

    # misc
    re_path(r'^mission/?$', mission_index, name='mission'),
    re_path(r'^mission/postcard$', mission_postcard, name='mission_postcard'),
    re_path(r'^mission/postcard/svg$', mission_postcard_svg, name='mission_postcard_svg'),
    re_path(r'^mission/ql-lore$', mission_lore, name='mission_lore'),
    re_path(r'^mission/schwag$', mission_schwag, name='mission_schwag'),

    #richard test to build new interface stuff
    path('mission/diplomacy/<str:uuid>/<str:name>/', mission_diplomacy_room, name='mission_diplomacy_room'),
    path('mission/diplomacy/<str:uuid>/<str:name>', mission_diplomacy_room, name='mission_diplomacy_room'),
    re_path(r'^mission/diplomacy/?', mission_diplomacy, name='mission_diplomacy'),

    url(r'^api/v1/', include(router.urls)),

    # Stwards endpoints
    path('/steward/<steward-id>', get_stewards_data, name='get_stewards_data'),
    path('/steward/', get_steward_all_data , name='get_all_steward_data'),
]


# if settings.DEBUG:
urlpatterns += [
    re_path(r'^400/?$', handler400, name='400'),
    re_path(r'^403/?$', handler403, name='403'),
    re_path(r'^404/?$', handler404, name='404'),
    re_path(r'^500/?$', handler500, name='500'),
]

handler403 = 'quadraticlands.views.handler403'
handler404 = 'quadraticlands.views.handler404'
handler500 = 'quadraticlands.views.handler500'
handler400 = 'quadraticlands.views.handler400'
