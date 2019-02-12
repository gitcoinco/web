# -*- coding: utf-8 -*-
"""Define the is_in_list template tag to allow if in list checking in templates.

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

register = template.Library()


@register.filter
def is_in_list_type_iexact(value, input_list):
    """Determine whether or not the value is in the provided list.

    Args:
        value: Any value that could be a member of the provided list.
        input_list (list): A list of any primitive types to be checked.

    Usage:
        {% if '<value>'|is_in_list:'about,slack,home,help,mission' %}

    Returns:
        bool: Whether or not the value exists in the input_list. (but the value will be cast to a str)

    """
    value = str(value)
    return value in input_list
