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
# shamelessly stolen from:
# https://stackoverflow.com/questions/10361240/template-filter-to-trim-any-leading-or-trailing-whitespace
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def trim(value):
    """Trim/Strip string

    Args:
        value (str): string

    Usage:
        {% filter trim %}{% someothertag %}{% endfilter %}

    Returns:
        str: trimmed string

    """
    return value.strip()
