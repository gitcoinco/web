# -*- coding: utf-8 -*-
"""Define the job board admin.

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
from __future__ import unicode_literals

from django.contrib import admin, messages

from marketing.mails import new_job_approved

from .models import Job


class JobAdmin(admin.ModelAdmin):
    """Define the admin display of External Bounties."""

    ordering = ['-id']
    list_display = ['pk', 'active', 'title', 'company']
    search_fields = ['title', 'description', 'skills', 'company']

    def save_model(self, request, obj, form, change):
        if 'activate' in form.changed_data and form.changed_data['activate']:
            new_job_approved(obj)
            messages.info(request, "email sent to user about job posting approval")
        super(JobAdmin, self).save_model(request, obj, form, change)



admin.site.register(Job, JobAdmin)
