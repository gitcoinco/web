# -*- coding: utf-8 -*-
"""Define authentication pipeline functions and logic.

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
from django.core.exceptions import SuspiciousOperation

from app.utils import setup_lang, sync_profile
from dashboard.utils import is_blocked


def save_profile(backend, user, response, request, *args, **kwargs):
    """Associate a Profile with a User."""
    if backend.name == 'github':
        handle = user.username
        if is_blocked(handle):
            raise SuspiciousOperation('You cannot login')

        if not user.is_active:
            raise SuspiciousOperation('You cannot login')

        sync_profile(handle, user, hide_profile=False)
        setup_lang(request, user)
