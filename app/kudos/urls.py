# -*- coding: utf-8 -*-
"""Handle kudos URLs.

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

from .views import (
    about, details, details_by_address_and_token_id, kudos_preferred_wallet, lazy_load, marketplace, mint, receive,
    receive_bulk, search, send_2, send_3, send_4,
)

app_name = 'kudos'
urlpatterns = [
    path('', about, name='main'),
    path('about/', about, name='about'),
    path('marketplace/', marketplace, name='marketplace'),
    path('mint/', mint, name='mint'),
    path('send/', send_2, name='send'),
    path('send/3/', send_3, name='send_3'),
    path('send/4/', send_4, name='send_4'),
    re_path(r'^receive/v3/(?P<key>.*)/(?P<txid>.*)/(?P<network>.*)?', receive, name='receive'),
    re_path(r'^redeem/(?P<secret>.*)/?$', receive_bulk, name='receive_bulk'),
    re_path(r'^search/$', search, name='search'),
    re_path(
        r'^(?P<address>\w*)/(?P<token_id>\d+)/(?P<name>\w*)',
        details_by_address_and_token_id,
        name='details_by_address_and_token_id'
    ),
    re_path(r'^(?P<kudos_id>\d+)/(?P<name>\w*)', details, name='details'),
    re_path(r'^address/(?P<handle>.*)', kudos_preferred_wallet, name='preferred_wallet'),
    re_path(r'^lazy_load/$', lazy_load, name='lazy_load'),
]
