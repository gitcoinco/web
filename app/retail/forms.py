# -*- coding: utf-8 -*-
"""Define retail related forms.

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
from django.utils.html import escape, strip_tags
from django.utils.translation import gettext_lazy as _


class FundingLimitIncreaseRequestForm(forms.Form):
    """Define the FundingLimitIncreaseRequestForm handling."""

    usdt_per_tx = forms.DecimalField(label=_('New Limit in USD per Transaction'), initial=500, max_digits=50)
    usdt_per_week = forms.DecimalField(label=_('New Limit in USD per Week'), initial=1500, max_digits=50)
    comment = forms.CharField(max_length=500, widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(FundingLimitIncreaseRequestForm, self).__init__(*args, **kwargs)

        self.fields['comment'].widget.attrs['placeholder'] = _('Please tell us why you need a limit increase.')
        self.fields['comment'].widget.attrs['rows'] = '4'
        self.fields['comment'].widget.attrs['cols'] = '50'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form__input'

    def clean_comment(self):
        comment = self.cleaned_data['comment'] or ''
        return escape(strip_tags(comment))
