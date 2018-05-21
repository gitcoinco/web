# -*- coding: utf-8 -*-
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
from __future__ import unicode_literals

from secrets import token_hex

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models

from economy.models import SuperModel


class Alumni(SuperModel):

    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='alumni',
        null=True)
    organization = models.CharField(max_length=255, db_index=True, blank=True)
    comments = models.TextField(max_length=5000, blank=True)
    public = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.profile} - {self.organization} - {self.comments}"


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
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='email_subscriptions',
        null=True)

    def __str__(self):
        return self.email

    def set_priv(self):
        self.priv = token_hex(16)[:29]


class Stat(SuperModel):

    key = models.CharField(max_length=50, db_index=True)
    val = models.IntegerField()

    class Meta:

        index_together = [
            ["created_on", "key"],
        ]

    def __str__(self):
        return f"{self.key}: {self.val}"

    @property
    def val_since_yesterday(self):
        try:
            return self.val - Stat.objects.filter(key=self.key, created_on__lt=self.created_on, created_on__hour=self.created_on.hour).order_by('-created_on').first().val
        except Exception:
            return 0

    @property
    def val_since_hour(self):
        try:
            return self.val - Stat.objects.filter(key=self.key, created_on__lt=self.created_on).order_by('-created_on').first().val
        except Exception:
            return 0


class LeaderboardRank(SuperModel):

    github_username = models.CharField(max_length=255)
    leaderboard = models.CharField(max_length=255)
    amount = models.FloatField()
    active = models.BooleanField()

    def __str__(self):
        return f"{self.leaderboard}, {self.github_username}: {self.amount}"

    @property
    def github_url(self):
        return f"https://github.com/{self.github_username}"

    @property
    def avatar_url(self):
        return f"/static/avatar/{self.github_username}"


class Match(SuperModel):

    class Meta:

        verbose_name_plural = 'Matches'

    email = models.EmailField(max_length=255)
    bounty = models.ForeignKey('dashboard.Bounty', on_delete=models.CASCADE)
    direction = models.CharField(max_length=50)
    github_username = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.email}: {self.bounty}; {self.direction}"


class Keyword(SuperModel):

    keyword = models.CharField(max_length=255)


class SlackUser(SuperModel):

    username = models.CharField(max_length=500)
    email = models.EmailField(max_length=255)
    last_seen = models.DateTimeField(null=True)
    last_unseen = models.DateTimeField(null=True)
    profile = JSONField(default={})
    times_seen = models.IntegerField(default=0)
    times_unseen = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username}; lastseen => {self.last_seen}"


class SlackPresence(SuperModel):

    slackuser = models.ForeignKey('marketing.SlackUser', on_delete=models.CASCADE, related_name='presences')
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.slackuser.username} / {self.status} / {self.created_on}"


class GithubEvent(SuperModel):

    profile = models.ForeignKey('dashboard.Profile', on_delete=models.CASCADE, related_name='github_events')
    what = models.CharField(max_length=500, default='', blank=True)
    repo = models.CharField(max_length=500, default='', blank=True)
    payload = JSONField(default={})

    def __str__(self):
        return f"{self.profile.handle} / {self.what} / {self.created_on}"


class GithubOrgToTwitterHandleMapping(SuperModel):

    github_orgname = models.CharField(max_length=500)
    twitter_handle = models.CharField(max_length=500)

    def __str__(self):
        return f"{self.github_orgname} => {self.twitter_handle}"


class EmailEvent(SuperModel):

    email = models.EmailField(max_length=255, db_index=True)
    event = models.CharField(max_length=255, db_index=True)
    payload = JSONField(default={})

    def __str__(self):
        return f"{self.email} - {self.event} - {self.created_on}"
