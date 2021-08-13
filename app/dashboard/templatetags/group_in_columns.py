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
import itertools

from django import template

register = template.Library()

@register.filter
def group_in_columns(list_input, number_of_columns):
    """Groups list_input into columns based on the number_of_columns required (to be used in a loop)"""
    columns = int(number_of_columns)
    items = iter(list_input)
    while True:
        column = list(itertools.islice(items, columns))
        if column:
            yield column
        else:
            break
