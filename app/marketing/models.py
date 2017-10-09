'''
    Copyright (C) 2017 Gitcoin Core 

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

'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from economy.models import SuperModel
from django.db import models
from django.contrib.postgres.fields import JSONField


class EmailSubscriber(SuperModel):
    email = models.EmailField(max_length=255)
    source = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    preferences = JSONField(default={})
    metadata = JSONField(default={})

    def __str__(self):
        return self.email


class Stat(SuperModel):
    key = models.CharField(max_length=50, db_index=True)
    val = models.IntegerField()

    class Meta:
        index_together = [
            ["created_on", "key"],
        ]
    def __str__(self):
        return "{}: {}".format(self.key, self.val)