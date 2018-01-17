# -*- coding: utf-8 -*-
"""Handle github URLs.

Copyright (C) 2017 Gitcoin Core

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

from django.conf.urls import url

from .views import github_authentication, github_callback

app_name = 'github'
urlpatterns = [
    url(r'^callback/$', github_callback, name='github_callback'),
    url(r'^auth/$', github_authentication, name='github_auth'),
]
