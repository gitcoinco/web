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

register = template.Library()

@register.simple_tag
def group_by_field(list_input, fields, field):
    """Groups list_input into columns by pivotting on the given field (for each of the given fields)"""
    output = []
    for fields_val in fields:
        # collect columns details into a dict ({field:fields_val, 'list':[...]})
        group = {}
        # eg group.type = "current"
        group[field] = fields_val
        # collate the list by pivotting only the matching elements
        group['list'] = [ele for ele in list_input if ele[field] == fields_val]
        # appending each dict to the output
        output.append(group)

    return output
