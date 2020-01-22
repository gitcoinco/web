# -*- coding: utf-8 -*-
"""Define the Grant forms.

Copyright (C) 2020 Gitcoin Core

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
from django.utils.translation import gettext_lazy as _

from gitmentor.models import SessionScheduling


class SessionSchedulingForm(forms.ModelForm):
    """Define the Session scheduling form logic."""

    class Meta:
        """Define the metadata for the SessionScheduling model form."""

        model = SessionScheduling
        fields = ('mentor', 'session_type', 'session_date', 'session_time',
                  'notes',)
        widgets = {
            'mentor': forms.MultipleChoiceField(attrs={
                'class': 'form__input form__input-lg username-search',
                'placeholder': _('Mentor')
            }),
            'session_date':
                forms.TextInput(
                    attrs={
                        'type': 'text',
                        'class': 'form__input form__input-lg',
                        'placeholder': _('Due Date for completion')
                    }
                )
        }
