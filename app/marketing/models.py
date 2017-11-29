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
from dashboard.models import Bounty
from django.contrib.postgres.fields import ArrayField


class EmailSubscriber(SuperModel):
    email = models.EmailField(max_length=255)
    source = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    newsletter = models.BooleanField(default=True)
    preferences = JSONField(default={})
    metadata = JSONField(default={})
    priv = models.CharField(max_length=30, default='')
    github = models.CharField(max_length=255, default='')
    keywords = ArrayField(models.CharField(max_length=200), blank=True, default=[])

    def __str__(self):
        return self.email

    def set_priv(self):
        import hashlib
        from django.utils import timezone

        h = hashlib.new('ripemd160')
        h.update("{}-{}-{}".format(h.hexdigest(), timezone.now(), self.email))
        self.priv = h.hexdigest()[:29]


class Stat(SuperModel):
    key = models.CharField(max_length=50, db_index=True)
    val = models.IntegerField()

    class Meta:
        index_together = [
            ["created_on", "key"],
        ]
    def __str__(self):
        return "{}: {}".format(self.key, self.val)


class LeaderboardRank(SuperModel):
    github_username = models.CharField(max_length=255)
    leaderboard = models.CharField(max_length=255)
    amount = models.FloatField()
    active = models.BooleanField()

    def __str__(self):
        return "{}, {}: {}".format(self.leaderboard, self.github_username, self.amount)

    @property
    def github_url(self):
        return "https://github.com/{}".format(self.github_username)

    @property
    def local_avatar_url(self):
        return "/funding/avatar?repo={}&v=3".format(self.github_url)


class Match(SuperModel):
    email = models.EmailField(max_length=255)
    bounty = models.ForeignKey(Bounty, on_delete=models.CASCADE)
    direction = models.CharField(max_length=50)
    github_username = models.CharField(max_length=255)

    def __str__(self):
        return "{}: {}; {}".format(self.email, self.bounty, self.direction)

