# -*- coding: utf-8 -*-
"""Define data visualization related models.

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
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class DataPayload(SuperModel):
    """Define the structure of an ExternalBounty."""

    key = models.CharField(db_index=True, max_length=255, help_text=_("key for this data report"))
    report = models.CharField(max_length=255, blank=True, help_text=_("The report associated with this project"))
    payload = JSONField(default=dict, blank=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        """Return the string representation of an ExternalBounty."""
        return f'{self.key} {self.report} - {self.comments}'

    def get_payload_with_mutations(self):
        payload = self.payload
        if self.key == 'graph':
            if self.report == 'corporate america':
                for x in range(1, len(self.payload['nodes'])):
                    payload['links'].append({"source": 0, "target": x, "weight": 10})

        return payload
