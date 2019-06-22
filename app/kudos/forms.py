# -*- coding: utf-8 -*-
"""Define Forms.

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
from django import forms
from django.utils.translation import gettext as _


class KudosSearchForm(forms.Form):
    """Form template for kudos search.

    Attributes:
        kudos_search (form): Use for kudos search GET request.
    """
    kudos_search = forms.CharField(label=_('Kudos Search'), max_length=100)
