# -*- coding: utf-8 -*-
"""Define the add_url_schema template tag to allow cleaning up url in templates.

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

from django import template

from kudos.utils import humanize_name as humanize_method

register = template.Library()


@register.filter
def humanize_name(name):
    """Convert the lowercase and underscores to uppercase and spaces.

    Args:
        name (str): The name to convert.

    Usage:
        {{ name|humanize_name }}

    Returns:
        str: The new name.

    """
    return humanize_method(name)


@register.filter
def humanize_address(address):
    """Shorten the Ethereum address to be more readable.

    Args:
        address (str): The address to shorten.

    Usage:
        {{ address|humanize_address }}

    Returns:
        str: The new address.

    """
    return address[:6] + '...' + address[-4:]


@register.filter
def replace_commas(string):
    return ' '.join([x.capitalize() for x in string.split(',')])
