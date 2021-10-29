# -*- coding: utf-8 -*-
"""Define the add_url_schema template tag to allow cleaning up url in templates.

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
from django import template

from grants.utils import is_grant_team_member

register = template.Library()


@register.filter
def addstr(value, arg):
    """Concats argument to string.

    Args:
        value (str): Original string
        arg (str): String to be concated

    Usage:
        {{ value|addstr(arg) }}

    Returns:
        str: The concatenated string.

    """
    return str(value) + str(arg)


@register.filter
def modulo(num, val):
    """Get the modulo of the provided number and value.

    Args:
        num (int): Something describing the number.
        val (int): Something describing the value.

    Usage:
        {{ num|modulo(val) }}

    Returns:
        int: The modulo of number and value.

    """
    if num and val:
        return num % val
    return 0

@register.simple_tag
def is_team_member(grant, profile):
    return is_grant_team_member(grant, profile)

@register.simple_tag
def is_grants_path(path):
    return path.lower().startswith('/grants')

@register.simple_tag
def is_favorite(grant, profile):
    if profile:
        return grant.favorite(profile)

    return False


@register.filter
def humanize_short(number):
    try:
        number = float(number)
        if number > 1000000:
            number = str(round(number / 100000)) + 'M'
        elif number > 1000:
            number = str(round(number / 1000)) + 'K'
    except:
        pass

    return number
