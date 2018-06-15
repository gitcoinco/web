# -*- coding: utf-8 -*-
"""Define the retail models.

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
from django.db import models
from django.utils import timezone

from economy.models import SuperModel


class LivestreamSession(SuperModel):
    """Define the live stream session schema.

    TODO:
        * Add thumbnail field
        * Add boto3 based elastic transcoder queuing against the VOD.

    """

    class Meta:
        """Define the live stream session metadata."""

        verbose_name_plural = 'Livestream Sessions'

    attendees = models.ManyToManyField('dashboard.Profile', blank=True)
    description = models.TextField(blank=True)
    vod = models.FileField(upload_to='livestream/vods/', blank=True, null=True)
    zoom_id = models.CharField(blank=True, max_length=50)
    zoom_password = models.CharField(blank=True, max_length=50)

    def __str__(self):
        """Define the string representation of the livestream session."""
        return f'{self.pk} - {self.created_on}'

    @property
    def zoom_url(self):
        """Return the zoom URL."""
        return f"https://consensys.zoom.us/j/{self.zoom_id}?pwd={self.zoom_password if self.zoom_password else ''}"

    @property
    def attendee_count(self):
        """Return the total number of attendees."""
        return self.attendees.count()
