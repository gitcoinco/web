# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Gitcoin Core

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

'''


def get_ip(request):
    forward_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forward_for:
        ip_addr = forward_for.split(',')[0]
    else:
        ip_addr = request.META.get('REMOTE_ADDR')
    return ip_addr
