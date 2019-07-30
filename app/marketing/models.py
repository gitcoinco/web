# -*- coding: utf-8 -*-
"""Define the marketing models and related logic.

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

from secrets import token_hex

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

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
    preferences = JSONField(default=dict)
    metadata = JSONField(default=dict, blank=True)
    priv = models.CharField(max_length=30, default='')
    github = models.CharField(max_length=255, default='', blank=True)
    keywords = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='email_subscriptions',
        null=True, blank=True)
    form_submission_records = JSONField(default=list, blank=True)

    def __str__(self):
        return self.email

    def set_priv(self):
        self.priv = token_hex(16)[:29]

    def should_send_email_type_to(self, email_type):
        is_on_global_suppression_list = EmailSupressionList.objects.filter(email__iexact=self.email).exists()
        if is_on_global_suppression_list:
            return False

        should_suppress = self.preferences.get('suppression_preferences', {}).get(email_type, False)
        return not should_suppress

    def build_email_preferences(self, form=None):
        from retail.emails import ALL_EMAILS, TRANSACTIONAL_EMAILS, MARKETING_EMAILS
        if form is None:
            form = {}

        suppression_preferences = self.preferences.get('suppression_preferences', {})

        # update from legacy email preferences
        level = self.preferences.pop('level', None)
        if level:
            if level == 'lite1':
                for email_tuple in MARKETING_EMAILS:
                    key, __, __ = email_tuple
                    suppression_preferences[key] = True
                for email_tuple in TRANSACTIONAL_EMAILS:
                    key, __, __ = email_tuple
                    suppression_preferences[key] = False
            elif level == 'lite':
                for email_tuple in MARKETING_EMAILS:
                    key, __, __ = email_tuple
                    suppression_preferences[key] = False
                for email_tuple in TRANSACTIONAL_EMAILS:
                    key, __, __ = email_tuple
                    suppression_preferences[key] = True
            else:
                for email_tuple in ALL_EMAILS:
                    key, __, __ = email_tuple
                    suppression_preferences[key] = False

        # update from form
        for email_tuple in ALL_EMAILS:
            key, __, __ = email_tuple
            if key in form.keys():
                suppression_preferences[key] = bool(form[key])

        # save and return
        self.preferences['suppression_preferences'] = suppression_preferences
        return suppression_preferences

    @property
    def is_eu(self):
        from app.utils import get_country_from_ip
        try:
            ip_addresses = self.metadata.get('ip')
            if ip_addresses:
                for ip_address in ip_addresses:
                    country = get_country_from_ip(ip_address)
                    if country.continent.code == 'EU':
                        return True
        except Exception:
            # Cowardly pass on everything for the moment.
            pass
        return False


# method for updating
@receiver(pre_save, sender=EmailSubscriber, dispatch_uid="psave_es")
def psave_es(sender, instance, **kwargs):
    instance.build_email_preferences()


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
            return self.val - Stat.objects.filter(
                key=self.key, created_on__lt=self.created_on, created_on__hour=self.created_on.hour
            ).order_by('-created_on').first().val
        except Exception:
            return 0

    @property
    def val_since_hour(self):
        try:
            return self.val - Stat.objects.filter(
                key=self.key, created_on__lt=self.created_on
            ).order_by('-created_on').first().val
        except Exception:
            return 0


class LeaderboardRankQuerySet(models.QuerySet):
    """Handle the manager queryset for Leaderboard Ranks."""

    def active(self):
        """Filter results to only active LeaderboardRank objects."""
        return self.select_related('profile').filter(active=True)


class LeaderboardRank(SuperModel):
    """Define the Leaderboard Rank model."""

    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.SET_NULL,
        null=True,
        related_name='leaderboard_ranks',
    )
    github_username = models.CharField(max_length=255)
    leaderboard = models.CharField(max_length=255, db_index=True)
    amount = models.FloatField(db_index=True)
    active = models.BooleanField(db_index=True)
    count = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)
    tech_keywords = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    objects = LeaderboardRankQuerySet.as_manager()

    class Meta:

        index_together = [
            ["leaderboard", "active"],
        ]


    def __str__(self):
        return f"{self.leaderboard}, {self.github_username}: {self.amount}"

    @property
    def github_url(self):
        return f"https://github.com/{self.github_username}"

    @property
    def is_not_user_based(self):
        profile_keys = ['_tokens', '_keywords', '_cities', '_countries', '_continents', '_kudos']
        return any(sub in self.leaderboard for sub in profile_keys)

    @property
    def is_a_kudos(self):
        return 'https://gitcoin.co/kudos/' == self.github_username[0:25]

    @property
    def at_ify_username(self):
        if not self.is_not_user_based:
            return f"@{self.github_username}"
        if self.is_a_kudos:
            pk = self.github_username.split('/')[4]
            from kudos.models import Token
            return Token.objects.get(pk=pk).humanized_name
        return self.github_username

    @property
    def avatar_url(self):
        if self.is_a_kudos:
            pk = self.github_username.split('/')[4]
            from kudos.models import Token
            return Token.objects.get(pk=pk).img_url
        key = self.github_username

        # these two types won't have images
        if self.is_not_user_based:
            key = 'None'

        return f"/dynamic/avatar/{key}"

    @property
    def url(self):
        if self.is_a_kudos:
            pk = self.github_username.split('/')[4]
            from kudos.models import Token
            return Token.objects.get(pk=pk).url
        ret_url = f"/profile/{self.github_username}"
        return ret_url


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

    def __str__(self):
        return f"{self.keyword}; created => {self.created_on}"


class SlackUser(SuperModel):

    username = models.CharField(max_length=500)
    email = models.EmailField(max_length=255)
    last_seen = models.DateTimeField(null=True)
    last_unseen = models.DateTimeField(null=True)
    profile = JSONField(default=dict)
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
    payload = JSONField(default=dict)

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
    category = models.CharField(max_length=255, db_index=True, blank=True, default='')
    ip_address = models.GenericIPAddressField(default=None, null=True)

    def __str__(self):
        return f"{self.email} - {self.event} - {self.created_on}"


class AccountDeletionRequest(SuperModel):

    handle = models.CharField(max_length=255, db_index=True)
    profile = JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.handle} - {self.created_on}"


class EmailSupressionList(SuperModel):

    email = models.EmailField(max_length=255)
    metadata = JSONField(default=dict, blank=True)
    comments = models.TextField(max_length=5000, blank=True)

    def __str__(self):
        return f"{self.email}"
