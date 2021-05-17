# -*- coding: utf-8 -*-
"""Define authentication pipeline functions and logic.

Copyright (C) 2021 Gitcoin Core

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

        # BLOCKEDUSER BASED BLOCKING
        # COUNTRY-BASED BASED BLOCKING
        if is_blocked(handle):
            raise SuspiciousOperation('You cannot login')

        # INACTIVE USERS
        if not user.is_active:
            raise SuspiciousOperation('You cannot login')

        ## IP BASED BLOCKING
        from retail.helpers import get_ip
        ip_addr = get_ip(request)
        from dashboard.models import BlockedIP
        _is_blocked = BlockedIP.objects.filter(addr=ip_addr).exists()
        if _is_blocked:
            raise SuspiciousOperation('You cannot login')

        # SUCCESS, LET USER LOGIN
        sync_profile(handle, user, hide_profile=False, delay_okay=True)
        setup_lang(request, user)
