# -*- coding: utf-8 -*-
"""Define models.

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
import logging
from datetime import datetime, timedelta

from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


def default_job_expiry():
    return datetime.today() + timedelta(days=30)


class Job(SuperModel):
    """Model representing a single Job posted on the job board

    Attributes
        title (str): Title
        job_type (str): part-time/full-time/contract etc.
        location (str): SanFranciso/Remote etc.
        descritpion (markdown formatted): detailed job description,
        posted_by (str): linked to a gitcoin profile
        active (bool - yes/n)
        skills (list of strings)
        company (str)
        github profile (str)
        expiry_date (date, default = 30 days in future)
        apply_location (url or mailto:)
        amount
        txid(str): paid TXid
    """

    JOB_TYPE_CHOICES = (
        ('part-time', 'part-time'),
        ('full-time', 'full-time'),
        ('intern', 'intern'),
        ('contractor', 'contractor'),
    )

    title = models.CharField(default='', max_length=255, help_text=_('The Job title'))
    job_type = models.CharField(default='full-time', choices=JOB_TYPE_CHOICES, max_length=255, help_text=_('The Job type'))
    job_location = models.CharField(default='', max_length=255, help_text=_('city where the job is or remote'))
    description = models.TextField(default='', blank=True, help_text=_('The description of the Job'))
    posted_by = models.ForeignKey('dashboard.Profile', null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=False, help_text=_('Whether or not the Job is active'))
    skills = JSONField(default=list, blank=True, help_text=_('The list of Skills'))
    company = models.CharField(default='', max_length=255, help_text=_('The Company hiring'))
    github_profile = models.CharField(default='', max_length=255, help_text=_('user or company profile on github'))
    expiry_date = models.DateField(default=default_job_expiry)
    apply_location = models.CharField(max_length=255, help_text=_('link to apply to, url or mailto:'))


    txid = models.CharField(max_length=255)
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address paid with.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='ETH',
        help_text=_('The token symbol paid with.'),
    )
    amount = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The amount expected to be paid.'),
    )

    @property
    def url(self):
        return reverse('job_show', args=[self.pk])
