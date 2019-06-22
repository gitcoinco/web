# -*- coding: utf-8 -*-
"""Define bounty request related forms.

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

from .models import BountyRequest


class BountyRequestForm(forms.ModelForm):
    """Define the BountyRequestForm handling."""
    github_url = forms.URLField(label=_('The Github Issue Link'))

    class Meta:
        model = BountyRequest
        fields = ['github_url', 'eth_address', 'amount', 'comment']
        labels = {
            'eth_address': _('Your ETH Address (Optional)'),
            'amount': _('Proposed Funding Amount (USD)'),
            'comment': _('Comment')
        }

    def __init__(self, *args, **kwargs):
        super(BountyRequestForm, self).__init__(*args, **kwargs)

        self.fields['eth_address'].widget.attrs['placeholder'] = '0x0'
        self.fields['github_url'].widget.attrs['placeholder'] = 'https://github.com/gitcoinco/web/issues/2036'
        self.fields['amount'].widget.attrs['placeholder'] = '1'
        self.fields['amount'].widget.attrs['min'] = '1'
        self.fields['comment'].widget.attrs['placeholder'] = _('Anything you want to tell us.')
        self.fields['comment'].widget.attrs['rows'] = '4'
        self.fields['comment'].widget.attrs['cols'] = '50'

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form__input'

    def clean_comment(self):
        comment = self.cleaned_data['comment'] or ''
        return escape(strip_tags(comment))
