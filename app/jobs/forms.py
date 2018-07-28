# -*- coding: utf-8 -*-
"""Define external bounty related forms.

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

from dashboard.views import profile_keywords_helper

from .models import Job
from .services import clean_html_data


class JobForm(forms.ModelForm):
    """Define the Job form handling."""
    skills = forms.ChoiceField(choices=(), required=True)

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['skills'].choices = [(x, x) for x in profile_keywords_helper(user.profile.handle)]

    def clean_description(self):
        description = self.cleaned_data['description']
        # Allow `strong`, `em` & `p` tags.
        description = clean_html_data(description, ['strong', 'em', 'p'])
        return description

    def clean_title(self):
        title = self.cleaned_data['title']
        # Allow `strong`, `em` & `p` tags.
        title = clean_html_data(title, ['strong', 'em'])
        return title

    class Meta:
        """Define the JOB form metadata."""

        model = Job
        fields = [
            'title', 'job_type', 'location', 'skills', 'company', 'description'
        ]
