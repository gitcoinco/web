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
import re

from django import template

register = template.Library()


@register.filter
def add_url_schema(url):
    """Clean the provided URL to include the scheme (http) if no scheme is present.

    Args:
        url (str): The URL to be cleaned.

    Usage:
        {{ url|clean_url }}

    Returns:
        str: The URL with the scheme attached.

    """
    pattern = re.compile(r'https?://')
    return url if pattern.match(url) else f'http://{url}'
