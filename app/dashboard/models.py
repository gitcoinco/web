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

import logging
from datetime import datetime
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import pytz
import requests
from dashboard.tokens import addr_to_token
from economy.models import SuperModel
from economy.utils import ConversionRateNotFoundError, convert_amount, convert_token_to_usdt
from github.utils import (
    _AUTH, HEADERS, TOKEN_URL, build_auth_dict, get_issue_comments, get_user, issue_number, org_name, repo_name,
)
from rest_framework import serializers
from web3 import Web3

from .signals import m2m_changed_interested

logger = logging.getLogger(__name__)


class BountyQuerySet(models.QuerySet):
    """Handle the manager queryset for Bounties."""

    def current(self):
        """Filter results down to current bounties only."""
        return self.filter(current_bounty=True)

    def stats_eligible(self):
        """Exclude results that we don't want to track in statistics."""
        return self.exclude(idx_status__in=['unknown', 'cancelled'])

    def exclude_by_status(self, excluded_statuses=None):
        """Exclude results with a status matching the provided list."""
        if excluded_statuses is None:
            excluded_statuses = []

        return self.exclude(idx_status__in=excluded_statuses)


class Bounty(SuperModel):
    """Define the structure of a Bounty.

    Attributes:
        BOUNTY_TYPES (list of tuples): The valid bounty types.
        EXPERIENCE_LEVELS (list of tuples): The valid experience levels.
        PROJECT_LENGTHS (list of tuples): The possible project lengths.
        STATUS_CHOICES (list of tuples): The valid status stages.
        OPEN_STATUSES (list of str): The list of status types considered open.
        CLOSED_STATUSES (list of str): The list of status types considered closed.

    """

    BOUNTY_TYPES = [
        ('Bug', 'Bug'),
        ('Security', 'Security'),
        ('Feature', 'Feature'),
        ('Unknown', 'Unknown'),
    ]
    EXPERIENCE_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Unknown', 'Unknown'),
    ]
    PROJECT_LENGTHS = [
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('Months', 'Months'),
        ('Unknown', 'Unknown'),
    ]

    STATUS_CHOICES = (
        ('cancelled', 'cancelled'),
        ('done', 'done'),
        ('expired', 'expired'),
        ('open', 'open'),
        ('started', 'started'),
        ('submitted', 'submitted'),
        ('unknown', 'unknown'),
    )
    OPEN_STATUSES = ['open', 'started', 'submitted']
    CLOSED_STATUSES = ['expired', 'unknown', 'cancelled', 'done']

    web3_type = models.CharField(max_length=50, default='bounties_network')
    title = models.CharField(max_length=255)
    web3_created = models.DateTimeField(db_index=True)
    value_in_token = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    bounty_type = models.CharField(max_length=50, choices=BOUNTY_TYPES, blank=True)
    project_length = models.CharField(max_length=50, choices=PROJECT_LENGTHS, blank=True)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS, blank=True)
    github_url = models.URLField(db_index=True)
    github_comments = models.IntegerField(default=0)
    bounty_owner_address = models.CharField(max_length=50)
    bounty_owner_email = models.CharField(max_length=255, blank=True)
    bounty_owner_github_username = models.CharField(max_length=255, blank=True)
    bounty_owner_name = models.CharField(max_length=255, blank=True)
    is_open = models.BooleanField(help_text=_('Whether the bounty is still open for fulfillments.'))
    expires_date = models.DateTimeField()
    raw_data = JSONField()
    metadata = JSONField(default={}, blank=True)
    current_bounty = models.BooleanField(
        default=False, help_text=_('Whether this bounty is the most current revision one or not'))
    _val_usd_db = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    contract_address = models.CharField(max_length=50, default='')
    network = models.CharField(max_length=255, blank=True, db_index=True)
    idx_experience_level = models.IntegerField(default=0, db_index=True)
    idx_project_length = models.IntegerField(default=0, db_index=True)
    idx_status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='open', db_index=True)
    issue_description = models.TextField(default='', blank=True)
    standard_bounties_id = models.IntegerField(default=0)
    num_fulfillments = models.IntegerField(default=0)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    accepted = models.BooleanField(default=False, help_text=_('Whether the bounty has been done'))
    interested = models.ManyToManyField('dashboard.Interest', blank=True)
    interested_comment = models.IntegerField(null=True, blank=True)
    submissions_comment = models.IntegerField(null=True, blank=True)
    override_status = models.CharField(max_length=255, blank=True)
    last_comment_date = models.DateTimeField(null=True, blank=True)
    fulfillment_accepted_on = models.DateTimeField(null=True, blank=True)
    fulfillment_submitted_on = models.DateTimeField(null=True, blank=True)
    fulfillment_started_on = models.DateTimeField(null=True, blank=True)
    canceled_on = models.DateTimeField(null=True, blank=True)
    snooze_warnings_for_days = models.IntegerField(default=0)

    token_value_time_peg = models.DateTimeField(blank=True, null=True)
    token_value_in_usdt = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_in_usdt_now = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_in_usdt = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_in_eth = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_true = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    privacy_preferences = JSONField(default={}, blank=True)

    # Bounty QuerySet Manager
    objects = BountyQuerySet.as_manager()

    class Meta:
        """Define metadata associated with Bounty."""

        verbose_name_plural = 'Bounties'
        index_together = [
            ["network", "idx_status"],
        ]

    def __str__(self):
        """Return the string representation of a Bounty."""
        return f"{'(CURRENT) ' if self.current_bounty else ''}{self.title} {self.value_in_token} " \
               f"{self.token_name} {self.web3_created}"

    def save(self, *args, **kwargs):
        """Define custom handling for saving bounties."""
        if self.bounty_owner_github_username:
            self.bounty_owner_github_username = self.bounty_owner_github_username.lstrip('@')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get the absolute URL for the Bounty.

        Returns:
            str: The absolute URL for the Bounty.

        """
        return settings.BASE_URL + self.get_relative_url(preceding_slash=False)

    def get_relative_url(self, preceding_slash=True):
        """Get the relative URL for the Bounty.

        Attributes:
            preceding_slash (bool): Whether or not to include a preceding slash.

        Returns:
            str: The relative URL for the Bounty.

        """
        try:
            _org_name = org_name(self.github_url)
            _issue_num = int(issue_number(self.github_url))
            _repo_name = repo_name(self.github_url)
            return f"{'/' if preceding_slash else ''}issue/{_org_name}/{_repo_name}/{_issue_num}/{self.standard_bounties_id}"
        except Exception:
            return f"{'/' if preceding_slash else ''}funding/details?url={self.github_url}"

    def get_natural_value(self):
        token = addr_to_token(self.token_address)
        if not token:
            return 0
        decimals = token.get('decimals', 0)
        return float(self.value_in_token) / 10**decimals

    @property
    def url(self):
        return self.get_absolute_url()

    def snooze_url(self, num_days):
        """Get the bounty snooze URL.

        Args:
            num_days (int): The number of days to snooze the Bounty.

        Returns:
            str: The snooze URL based on the provided number of days.

        """
        return f'{self.get_absolute_url()}?snooze={num_days}'

    @property
    def can_submit_after_expiration_date(self):
        if self.is_legacy:
            # legacy bounties could submit after expiration date
            return True

        # standardbounties
        contract_deadline = self.raw_data.get('contract_deadline')
        ipfs_deadline = self.raw_data.get('ipfs_deadline')
        if not ipfs_deadline:
            # if theres no expiry date in the payload, then expiration date is not mocked, and one cannot submit after expiration date
            return False

        # if contract_deadline > ipfs_deadline, then by definition, can be submitted after expiry date
        return contract_deadline > ipfs_deadline

    @property
    def title_or_desc(self):
        """Return the title of the issue."""
        if not self.title:
            title = self.fetch_issue_item('title') or self.github_url
            return title
        return self.title

    @property
    def issue_description_text(self):
        import re
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        return tag_re.sub('', self.issue_description).strip()

    @property
    def github_issue_number(self):
        try:
            return int(issue_number(self.github_url))
        except Exception:
            return None

    @property
    def org_name(self):
        return self.github_org_name

    @property
    def github_org_name(self):
        try:
            return org_name(self.github_url)
        except Exception:
            return None

    @property
    def github_repo_name(self):
        try:
            return repo_name(self.github_url)
        except Exception:
            return None

    def is_hunter(self, handle):
        """Determine whether or not the profile is the bounty hunter.

        Args:
            handle (str): The profile handle to be compared.

        Returns:
            bool: Whether or not the user is the bounty hunter.

        """
        return any(profile.fulfiller_github_username == handle for profile in self.fulfillments.all())

    def is_funder(self, handle):
        """Determine whether or not the profile is the bounty funder.

        Args:
            handle (str): The profile handle to be compared.

        Returns:
            bool: Whether or not the user is the bounty funder.

        """
        return handle.lower().lstrip('@') == self.bounty_owner_github_username.lower().lstrip('@')

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    @property
    def avatar_url(self):
        return self.get_avatar_url(False)

    @property
    def avatar_url_w_gitcoin_logo(self):
        return self.get_avatar_url(True)

    def get_avatar_url(self, gitcoin_logo_flag=False):
        """Return the local avatar URL."""
        org_name = self.github_org_name
        gitcoin_logo_flag = "/1" if gitcoin_logo_flag else ""
        if org_name:
            return f"{settings.BASE_URL}static/avatar/{org_name}{gitcoin_logo_flag}"
        else:
            return f"{settings.BASE_URL}funding/avatar?repo={self.github_url}&v=3"

    @property
    def keywords(self):
        try:
            return self.metadata.get('issueKeywords', False)
        except Exception:
            return False

    @property
    def now(self):
        """Return the time now in the current timezone."""
        return timezone.now()

    @property
    def past_expiration_date(self):
        """Return true IFF issue is past expiration date"""
        return timezone.localtime().replace(tzinfo=None) > self.expires_date.replace(tzinfo=None)

    @property
    def past_hard_expiration_date(self):
        """Return true IFF issue is past smart contract expiration date
        and therefore cannot ever be claimed again"""
        return self.past_expiration_date and not self.can_submit_after_expiration_date

    @property
    def status(self):
        """Determine the status of the Bounty.

        Raises:
            Exception: Catch whether or not any exception is encountered and
                return unknown for status.

        Returns:
            str: The status of the Bounty.

        """
        if self.override_status:
            return self.override_status
        if self.is_legacy:
            # TODO: Remove following full deprecation of legacy bounties
            try:
                fulfillments = self.fulfillments \
                    .exclude(fulfiller_address='0x0000000000000000000000000000000000000000') \
                    .exists()
                if not self.is_open:
                    if timezone.now() > self.expires_date and fulfillments:
                        return 'expired'
                    return 'done'
                elif not fulfillments:
                    if self.pk and self.interested.exists():
                        return 'started'
                    return 'open'
                return 'submitted'
            except Exception as e:
                logger.warning(e)
                return 'unknown'
        else:
            try:
                if not self.is_open:
                    if self.accepted:
                        return 'done'
                    elif self.past_hard_expiration_date:
                        return 'expired'
                    # If its not expired or done, it must be cancelled.
                    return 'cancelled'
                if self.num_fulfillments == 0:
                    if self.pk and self.interested.exists():
                        return 'started'
                    return 'open'
                return 'submitted'
            except Exception as e:
                logger.warning(e)
                return 'unknown'

    @property
    def get_value_true(self):
        return self.get_natural_value()

    @property
    def get_value_in_eth(self):
        if self.token_name == 'ETH':
            return self.value_in_token
        try:
            return convert_amount(self.value_in_token, self.token_name, 'ETH')
        except Exception:
            return None

    @property
    def get_value_in_usdt_now(self):
        decimals = 10**18
        if self.token_name == 'USDT':
            return float(self.value_in_token)
        if self.token_name == 'DAI':
            return float(self.value_in_token / 10**18)
        try:
            return round(float(convert_amount(self.value_in_token, self.token_name, 'USDT')) / decimals, 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def get_value_in_usdt(self):
        if self.status in self.OPEN_STATUSES:
            return self.value_in_usdt_now
        return self.value_in_usdt_then

    @property
    def value_in_usdt_then(self):
        decimals = 10 ** 18
        if self.token_name == 'USDT':
            return float(self.value_in_token)
        if self.token_name == 'DAI':
            return float(self.value_in_token / 10 ** 18)
        try:
            return round(float(convert_amount(self.value_in_token, self.token_name, 'USDT', self.web3_created)) / decimals, 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def token_value_in_usdt_now(self):
        try:
            return round(convert_token_to_usdt(self.token_name), 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def token_value_in_usdt_then(self):
        try:
            return round(convert_token_to_usdt(self.token_name, self.web3_created), 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def get_token_value_in_usdt(self):
        if self.status in self.OPEN_STATUSES:
            return self.token_value_in_usdt_now
        return self.token_value_in_usdt_then

    @property
    def get_token_value_time_peg(self):
        if self.status in self.OPEN_STATUSES:
            return timezone.now()
        return self.web3_created

    @property
    def desc(self):
        return f"{naturaltime(self.web3_created)} {self.idx_project_length} {self.bounty_type} {self.experience_level}"

    @property
    def turnaround_time_accepted(self):
        try:
            return (self.get_fulfillment_accepted_on - self.web3_created).total_seconds()
        except Exception:
            return None

    @property
    def turnaround_time_started(self):
        try:
            return (self.get_fulfillment_started_on - self.web3_created).total_seconds()
        except Exception:
            return None

    @property
    def turnaround_time_submitted(self):
        try:
            return (self.get_fulfillment_submitted_on - self.web3_created).total_seconds()
        except Exception:
            return None

    @property
    def get_fulfillment_accepted_on(self):
        try:
            return self.fulfillments.filter(accepted=True).first().accepted_on
        except Exception:
            return None

    @property
    def get_fulfillment_submitted_on(self):
        try:
            return self.fulfillments.first().created_on
        except Exception:
            return None

    @property
    def get_fulfillment_started_on(self):
        try:
            return self.interested.first().created
        except Exception:
            return None

    @property
    def hourly_rate(self):
        try:
            hours_worked = self.fulfillments.filter(accepted=True).first().fulfiller_hours_worked
            return float(self.value_in_usdt) / float(hours_worked)
        except Exception:
            return None

    @property
    def is_legacy(self):
        """Determine if the Bounty is legacy based on sunset date.

        Todo:
            * Remove this method following legacy bounty sunsetting.

        Returns:
            bool: Whether or not the Bounty is using the legacy contract.

        """
        return (self.web3_type == 'legacy_gitcoin')

    def get_github_api_url(self):
        """Get the Github API URL associated with the bounty.

        Returns:
            str: The Github API URL associated with the issue.

        """
        from urllib.parse import urlparse
        if self.github_url.lower()[:19] != 'https://github.com/':
            return ''
        url_path = urlparse(self.github_url).path
        return 'https://api.github.com/repos' + url_path

    def fetch_issue_item(self, item_type='body'):
        """Fetch the item type of an issue.

        Args:
            type (str): The github API response body item to be fetched.

        Returns:
            str: The item content.

        """
        github_url = self.get_github_api_url()
        if github_url:
            issue_description = requests.get(github_url, auth=_AUTH)
            if issue_description.status_code == 200:
                item = issue_description.json().get(item_type, '')
                if item_type == 'body' and item:
                    self.issue_description = item
                elif item_type == 'title' and item:
                    self.title = item
                self.save()
                return item
        return ''

    def fetch_issue_comments(self, save=True):
        """Fetch issue comments for the associated Github issue.

        Args:
            save (bool): Whether or not to save the Bounty after fetching.

        Returns:
            dict: The comments data dictionary provided by Github.

        """
        if self.github_url.lower()[:19] != 'https://github.com/':
            return []

        parsed_url = urlsplit(self.github_url)
        try:
            github_user, github_repo, _, github_issue = parsed_url.path.split('/')[1:5]
        except ValueError:
            logger.info(f'Invalid github url for Bounty: {self.pk} -- {self.github_url}')
            return []
        comments = get_issue_comments(github_user, github_repo, github_issue)
        if isinstance(comments, dict) and comments.get('message', '') == 'Not Found':
            logger.info(f'Bounty {self.pk} contains an invalid github url {self.github_url}')
            return []
        comment_count = 0
        for comment in comments:
            if (isinstance(comment, dict) and comment.get('user', {}).get('login', '') not in settings.IGNORE_COMMENTS_FROM):
                comment_count += 1
        self.github_comments = comment_count
        if comment_count:
            comment_times = [datetime.strptime(comment['created_at'], '%Y-%m-%dT%H:%M:%SZ') for comment in comments]
            max_comment_time = max(comment_times)
            max_comment_time = max_comment_time.replace(tzinfo=pytz.utc)
            self.last_comment_date = max_comment_time
        if save:
            self.save()
        return comments

    @property
    def next_bounty(self):
        if self.current_bounty:
            return None
        try:
            return Bounty.objects.filter(standard_bounties_id=self.standard_bounties_id, created_on__gt=self.created_on).order_by('created_on').first()
        except Exception:
            return None

    @property
    def prev_bounty(self):
        try:
            return Bounty.objects.filter(standard_bounties_id=self.standard_bounties_id, created_on__lt=self.created_on).order_by('-created_on').first()
        except Exception:
            return None

    # returns true if this bounty was active at _time
    def was_active_at(self, _time):
        if _time < self.web3_created:
            return False
        if _time < self.created_on:
            return False
        next_bounty = self.next_bounty
        if next_bounty is None:
            return True
        if next_bounty.created_on > _time:
            return True
        return False

    def action_urls(self):
        """Provide URLs for bounty related actions.

        Returns:
            dict: A dictionary of action URLS for this bounty.

        """
        return {
            'fulfill': f"/issue/fulfill/{self.pk}",
            'increase': f"/issue/increase/{self.pk}",
            'accept': f"/issue/accept/{self.pk}",
            'cancel': f"/issue/cancel/{self.pk}",
        }


class BountyFulfillmentQuerySet(models.QuerySet):
    """Handle the manager queryset for BountyFulfillments."""

    def accepted(self):
        """Filter results to accepted bounty fulfillments."""
        return self.filter(accepted=True)

    def submitted(self):
        """Exclude results that have not been submitted."""
        return self.exclude(fulfiller_address='0x0000000000000000000000000000000000000000')


class BountyFulfillment(SuperModel):
    """The structure of a fulfillment on a Bounty."""

    fulfiller_address = models.CharField(max_length=50)
    fulfiller_email = models.CharField(max_length=255, blank=True)
    fulfiller_github_username = models.CharField(max_length=255, blank=True)
    fulfiller_name = models.CharField(max_length=255, blank=True)
    fulfiller_metadata = JSONField(default={}, blank=True)
    fulfillment_id = models.IntegerField(null=True, blank=True)
    fulfiller_hours_worked = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=50)
    fulfiller_github_url = models.CharField(max_length=255, blank=True, null=True)
    accepted = models.BooleanField(default=False)
    accepted_on = models.DateTimeField(null=True, blank=True)

    bounty = models.ForeignKey(Bounty, related_name='fulfillments', on_delete=models.CASCADE)
    profile = models.ForeignKey('dashboard.Profile', related_name='fulfilled', on_delete=models.CASCADE, null=True)

    def __str__(self):
        """Define the string representation of BountyFulfillment.

        Returns:
            str: The string representation of the object.

        """
        return f'BountyFulfillment ID: ({self.pk}) - Bounty ID: ({self.bounty.pk})'

    def save(self, *args, **kwargs):
        """Define custom handling for saving bounty fulfillments."""
        if self.fulfiller_github_username:
            self.fulfiller_github_username = self.fulfiller_github_username.lstrip('@')
        super().save(*args, **kwargs)

    @property
    def to_json(self):
        """Define the JSON representation of BountyFulfillment.

        Returns:
            dict: A JSON representation of BountyFulfillment.

        """
        return {
            'address': self.fulfiller_address,
            'bounty_id': self.bounty.pk,
            'email': self.fulfiller_email,
            'githubUsername': self.fulfiller_github_username,
            'name': self.fulfiller_name,
        }


class BountySyncRequest(SuperModel):
    """Define the structure for bounty syncing."""

    github_url = models.URLField()
    processed = models.BooleanField()


class Subscription(SuperModel):

    email = models.EmailField(max_length=255)
    raw_data = models.TextField()
    ip = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.email} {self.created_on}"


class Tip(SuperModel):

    emails = JSONField()
    url = models.CharField(max_length=255, default='')
    tokenName = models.CharField(max_length=255)
    tokenAddress = models.CharField(max_length=255)
    amount = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    comments_priv = models.TextField(default='', blank=True)
    comments_public = models.TextField(default='', blank=True)
    ip = models.CharField(max_length=50)
    expires_date = models.DateTimeField()
    github_url = models.URLField(null=True, blank=True)
    from_name = models.CharField(max_length=255, default='', blank=True)
    from_email = models.CharField(max_length=255, default='', blank=True)
    from_username = models.CharField(max_length=255, default='', blank=True)
    username = models.CharField(max_length=255, default='')  # to username
    network = models.CharField(max_length=255, default='')
    txid = models.CharField(max_length=255, default='')
    receive_txid = models.CharField(max_length=255, default='', blank=True)
    received_on = models.DateTimeField(null=True, blank=True)
    from_address = models.CharField(max_length=255, default='', blank=True)
    receive_address = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        """Return the string representation for a tip."""
        return f"({self.network}) - {self.status}{' ORPHAN' if not self.emails else ''} {self.amount} " \
               f"{self.tokenName} to {self.username}, created: {naturalday(self.created_on)}, " \
               f"expires: {naturalday(self.expires_date)}"

    # TODO: DRY
    def get_natural_value(self):
        token = addr_to_token(self.tokenAddress)
        decimals = token['decimals']
        return float(self.amount) / 10**decimals

    @property
    def value_true(self):
        return self.get_natural_value()

    # TODO: DRY
    @property
    def value_in_eth(self):
        if self.tokenName == 'ETH':
            return self.amount
        try:
            return convert_amount(self.amount, self.tokenName, 'ETH')
        except Exception:
            return None

    @property
    def value_in_usdt_now(self):
        decimals = 1
        if self.tokenName == 'USDT':
            return float(self.amount)
        if self.tokenName == 'DAI':
            return float(self.amount / 10**18)
        try:
            return round(float(convert_amount(self.amount, self.tokenName, 'USDT')) / decimals, 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def value_in_usdt(self):
        return self.value_in_usdt_then

    @property
    def value_in_usdt_then(self):
        decimals = 1
        if self.tokenName == 'USDT':
            return float(self.amount)
        if self.tokenName == 'DAI':
            return float(self.amount / 10 ** 18)
        try:
            return round(float(convert_amount(self.amount, self.tokenName, 'USDT', self.created_on)) / decimals, 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def token_value_in_usdt_now(self):
        try:
            return round(convert_token_to_usdt(self.tokenName), 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def token_value_in_usdt_then(self):
        try:
            return round(convert_token_to_usdt(self.tokenName, self.created_on), 2)
        except ConversionRateNotFoundError:
            return None

    @property
    def status(self):
        if self.receive_txid:
            return "RECEIVED"
        return "PENDING"


# @receiver(pre_save, sender=Bounty, dispatch_uid="normalize_usernames")
# def normalize_usernames(sender, instance, **kwargs):
#     if instance.bounty_owner_github_username:
#         instance.bounty_owner_github_username = instance.bounty_owner_github_username.lstrip('@')


# method for updating
@receiver(pre_save, sender=Bounty, dispatch_uid="psave_bounty")
def psave_bounty(sender, instance, **kwargs):
    idx_experience_level = {
        'Unknown': 1,
        'Beginner': 2,
        'Intermediate': 3,
        'Advanced': 4,
    }

    idx_project_length = {
        'Unknown': 1,
        'Hours': 2,
        'Days': 3,
        'Weeks': 4,
        'Months': 5,
    }

    instance.idx_status = instance.status
    instance.fulfillment_accepted_on = instance.get_fulfillment_accepted_on
    instance.fulfillment_submitted_on = instance.get_fulfillment_submitted_on
    instance.fulfillment_started_on = instance.get_fulfillment_started_on
    instance._val_usd_db = instance.get_value_in_usdt if instance.get_value_in_usdt else 0
    instance._val_usd_db_now = instance.get_value_in_usdt_now if instance.get_value_in_usdt_now else 0
    instance.idx_experience_level = idx_experience_level.get(instance.experience_level, 0)
    instance.idx_project_length = idx_project_length.get(instance.project_length, 0)
    instance.token_value_time_peg = instance.get_token_value_time_peg
    instance.token_value_in_usdt = instance.get_token_value_in_usdt
    instance.value_in_usdt_now = instance.get_value_in_usdt_now
    instance.value_in_usdt = instance.get_value_in_usdt
    instance.value_in_eth = instance.get_value_in_eth
    instance.value_true = instance.get_value_true


class Interest(models.Model):
    """Define relationship for profiles expressing interest on a bounty."""

    profile = models.ForeignKey('dashboard.Profile', related_name='interested', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    issue_message = models.TextField(default='', blank=True)

    def __str__(self):
        """Define the string representation of an interested profile."""
        return self.profile.handle


@receiver(post_save, sender=Interest, dispatch_uid="psave_interest")
@receiver(post_delete, sender=Interest, dispatch_uid="pdel_interest")
def psave_interest(sender, instance, **kwargs):
    # when a new interest is saved, update the status on frontend
    print("signal: updating bounties psave_interest")
    for bounty in Bounty.objects.filter(interested=instance):
        bounty.save()


class Profile(SuperModel):
    """Define the structure of the user profile.

    TODO:
        * Remove all duplicate identity related information already stored on User.

    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    data = JSONField()
    handle = models.CharField(max_length=255, db_index=True)
    last_sync_date = models.DateTimeField(null=True)
    email = models.CharField(max_length=255, blank=True, db_index=True)
    github_access_token = models.CharField(max_length=255, blank=True, db_index=True)
    pref_lang_code = models.CharField(max_length=2, choices=settings.LANGUAGES)
    slack_repos = ArrayField(models.CharField(max_length=200), blank=True, default=[])
    slack_token = models.CharField(max_length=255, default='', blank=True)
    slack_channel = models.CharField(max_length=255, default='', blank=True)
    suppress_leaderboard = models.BooleanField(
        default=False,
        help_text='If this option is chosen, we will remove your profile information from the leaderboard',
    )
    hide_profile = models.BooleanField(
        default=True,
        help_text='If this option is chosen, we will remove your profile information all_together',
    )
    # Sample data: https://gist.github.com/mbeacom/ee91c8b0d7083fa40d9fa065125a8d48
    # Sample repos_data: https://gist.github.com/mbeacom/c9e4fda491987cb9728ee65b114d42c7
    repos_data = JSONField(default={})
    max_num_issues_start_work = models.IntegerField(default=3)

    @property
    def is_org(self):
        return self.data['type'] == 'Organization'

    @property
    def bounties(self):
        fulfilled_bounty_ids = self.fulfilled.all().values_list('bounty_id')
        bounties = Bounty.objects.filter(github_url__istartswith=self.github_url, current_bounty=True)
        for interested in self.interested.all():
            bounties = bounties | Bounty.objects.filter(interested=interested, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(pk__in=fulfilled_bounty_ids, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(bounty_owner_github_username__iexact=self.handle, current_bounty=True) | Bounty.objects.filter(bounty_owner_github_username__iexact="@" + self.handle, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(github_url__in=[url for url in self.tips.values_list('github_url', flat=True)], current_bounty=True)
        bounties = bounties.distinct()
        return bounties.order_by('-web3_created')

    @property
    def tips(self):
        on_repo = Tip.objects.filter(github_url__startswith=self.github_url).order_by('-id')
        tipped_for = Tip.objects.filter(username__iexact=self.handle).order_by('-id')
        return on_repo | tipped_for

    def has_been_removed_by_staff(self):
        user_actions = UserAction.objects.filter(
            profile=self,
            action='bounty_removed_by_staff',
            )
        return user_actions.exists()

    @property
    def authors(self):
        auto_include_contributors_with_count_gt = 40
        limit_to_num = 10

        _return = []

        for repo in sorted(self.repos_data, key=lambda repo: repo.get('contributions', -1), reverse=True):
            for c in repo.get('contributors', []):
                if isinstance(c, dict) and c.get('contributions', 0) > auto_include_contributors_with_count_gt:
                    _return.append(c['login'])

        include_gitcoin_users = len(_return) < limit_to_num
        if include_gitcoin_users:
            for b in self.bounties:
                vals = [b.bounty_owner_github_username]
                for val in vals:
                    if val:
                        _return.append(val.lstrip('@'))
            for t in self.tips:
                vals = [t.username]
                for val in vals:
                    if val:
                        _return.append(val.lstrip('@'))
        _return = list(set(_return))
        _return.sort()
        return _return[:limit_to_num]

    @property
    def desc(self):
        stats = self.stats
        role = stats[0][0]
        total_funded_participated = stats[1][0]
        plural = 's' if total_funded_participated != 1 else ''
        return f"@{self.handle} is a {role} who has participated in {total_funded_participated} " \
               f"funded issue{plural} on Gitcoin"

    @property
    def is_moderator(self):
        """Determine whether or not the user is a moderator.

        Returns:
            bool: Whether or not the user is a moderator.

        """
        return self.user.groups.filter(name='Moderators').exists() if self.user else False

    @property
    def is_staff(self):
        """Determine whether or not the user is a staff member.

        Returns:
            bool: Whether or not the user is a member of the staff.

        """
        return self.user.is_staff if self.user else False

    @property
    def stats(self):
        bounties = self.bounties.stats_eligible()
        loyalty_rate = 0
        total_funded = sum([bounty.value_in_usdt if bounty.value_in_usdt else 0 for bounty in bounties if bounty.is_funder(self.handle)])
        total_fulfilled = sum([bounty.value_in_usdt if bounty.value_in_usdt else 0 for bounty in bounties if bounty.is_hunter(self.handle)])
        print(total_funded, total_fulfilled)
        role = 'newbie'
        if total_funded > total_fulfilled:
            role = 'funder'
        elif total_funded < total_fulfilled:
            role = 'coder'

        loyalty_rate = self.fulfilled.filter(accepted=True).count()
        success_rate = 0
        if bounties.exists():
            numer = bounties.filter(idx_status__in=['submitted', 'started', 'done']).count()
            denom = bounties.exclude(idx_status__in=['open']).count()
            success_rate = int(round(numer * 1.0 / denom, 2) * 100) if denom != 0 else 'N/A'
        if success_rate == 0:
            success_rate = 'N/A'
            loyalty_rate = 'N/A'
        else:
            success_rate = f"{success_rate}%"
            loyalty_rate = f"{loyalty_rate}x"
        if role == 'newbie':
            return [
                (role, 'Status'),
                (bounties.count(), 'Total Funded Issues'),
                (bounties.filter(idx_status='open').count(), 'Open Funded Issues'),
                (loyalty_rate, 'Loyalty Rate'),
            ]
        elif role == 'coder':
            return [
                (role, 'Primary Role'),
                (bounties.count(), 'Total Funded Issues'),
                (success_rate, 'Success Rate'),
                (loyalty_rate, 'Loyalty Rate'),
            ]
        # funder
        return [
            (role, 'Primary Role'),
            (bounties.count(), 'Total Funded Issues'),
            (bounties.filter(idx_status='open').count(), 'Open Funded Issues'),
            (success_rate, 'Success Rate'),
        ]

    @property
    def github_url(self):
        return f"https://github.com/{self.handle}"

    @property
    def avatar_url(self):
        return f"{settings.BASE_URL}static/avatar/{self.handle}"

    @property
    def avatar_url_with_gitcoin_logo(self):
        return f"{self.avatar_url}/1"

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    @property
    def username(self):
        handle = ''
        if getattr(self, 'user', None) and self.user.username:
            handle = self.user.username
        # TODO: (mbeacom) Remove this check once we get rid of all the lingering identity shenanigans.
        elif self.handle:
            handle = self.handle
        return handle

    def has_repo(self, full_name):
        """Check if user has access to repo.

        Args:
            full_name (str): Repository name, like gitcoin/web.

        Returns:
            bool: Whether or not user has access to repository.

        """
        for repo in self.repos_data:
            if repo['full_name'] == full_name:
                return True
        return False

    def is_github_token_valid(self):
        """Check whether or not a Github OAuth token is valid.

        Args:
            access_token (str): The Github OAuth token.

        Returns:
            bool: Whether or not the provided OAuth token is valid.

        """
        if not self.github_access_token:
            return False

        _params = build_auth_dict(self.github_access_token)
        url = TOKEN_URL.format(**_params)
        response = requests.get(
            url,
            auth=(_params['client_id'], _params['client_secret']),
            headers=HEADERS)

        if response.status_code == 200:
            return True
        return False

    def __str__(self):
        return self.handle

    def get_relative_url(self, preceding_slash=True):
        return f"{'/' if preceding_slash else ''}profile/{self.handle}"

    def get_absolute_url(self):
        return settings.BASE_URL + self.get_relative_url(preceding_slash=False)

    def get_access_token(self, save=True):
        """Get the Github access token from User.

        Args:
            save (bool): Whether or not to save the User access token to the profile.

        Raises:
            Exception: The exception is raised in the event of any error and returns an empty string.

        Returns:
            str: The Github access token.

        """
        try:
            access_token = self.user.social_auth.filter(provider='github').latest('pk').access_token
            if save:
                self.github_access_token = access_token
                self.save()
        except Exception:
            return ''
        return access_token

    def get_profile_preferred_language(self):
        return settings.LANGUAGE_CODE if not self.pref_lang_code else self.pref_lang_code

    def get_slack_repos(self, join=False):
        """Get the profile's slack tracked repositories.

        Args:
            join (bool): Whether or not to return a joined string representation.
                Defaults to: False.

        Returns:
            list of str: If joined is False, a list of slack repositories.
            str: If joined is True, a combined string of slack repositories.

        """
        if join:
            repos = ','.join(self.slack_repos)
            return repos
        return self.slack_repos

    def update_slack_integration(self, token, channel, repos):
        """Update the profile's slack integration settings.

        Args:
            token (str): The profile's slack token.
            channel (str): The profile's slack channel.
            repos (list of str): The profile's github repositories to track.

        """
        repos = repos.split()
        self.slack_token = token
        self.slack_repos = [repo.strip() for repo in repos]
        self.slack_channel = channel
        self.save()


@receiver(user_logged_in)
def post_login(sender, request, user, **kwargs):
    """Handle actions to take on user login."""
    from dashboard.utils import create_user_action
    create_user_action(user, 'Login', request)


@receiver(user_logged_out)
def post_logout(sender, request, user, **kwargs):
    """Handle actions to take on user logout."""
    from dashboard.utils import create_user_action
    create_user_action(user, 'Logout', request)


class ProfileSerializer(serializers.BaseSerializer):
    """Handle serializing the Profile object."""

    class Meta:
        """Define the profile serializer metadata."""

        model = Profile
        fields = ('handle', 'github_access_token')
        extra_kwargs = {'github_access_token': {'write_only': True}}

    def to_representation(self, instance):
        """Provide the serialized representation of the Profile.

        Args:
            instance (Profile): The Profile object to be serialized.

        Returns:
            dict: The serialized Profile.

        """
        return {
            'id': instance.id,
            'handle': instance.handle,
            'github_url': instance.github_url,
            'avatar_url': instance.avatar_url,
            'url': instance.get_relative_url()
        }


@receiver(pre_save, sender=Tip, dispatch_uid="normalize_tip_usernames")
def normalize_tip_usernames(sender, instance, **kwargs):
    """Handle pre-save signals from Tips to normalize Github usernames."""
    if instance.username:
        instance.username = instance.username.replace("@", '')


m2m_changed.connect(m2m_changed_interested, sender=Bounty.interested.through)
# m2m_changed.connect(changed_fulfillments, sender=Bounty.fulfillments)


class UserAction(SuperModel):
    """Records Actions that a user has taken ."""

    ACTION_TYPES = [
        ('Login', 'Login'),
        ('Logout', 'Logout'),
        ('added_slack_integration', 'Added Slack Integration'),
        ('removed_slack_integration', 'Removed Slack Integration'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    user = models.ForeignKey(User, related_name='actions', on_delete=models.CASCADE, null=True)
    profile = models.ForeignKey('dashboard.Profile', related_name='actions', on_delete=models.CASCADE, null=True)
    ip_address = models.GenericIPAddressField(null=True)
    location_data = JSONField(default={})
    metadata = JSONField(default={})

    def __str__(self):
        return f"{self.action} by {self.profile} at {self.created_on}"


class CoinRedemption(SuperModel):
    """Define the coin redemption schema."""

    class Meta:
        """Define metadata associated with CoinRedemption."""

        verbose_name_plural = 'Coin Redemptions'

    shortcode = models.CharField(max_length=255, default='')
    url = models.URLField(null=True)
    network = models.CharField(max_length=255, default='')
    token_name = models.CharField(max_length=255)
    contract_address = models.CharField(max_length=255)
    amount = models.IntegerField(default=1)
    expires_date = models.DateTimeField()


@receiver(pre_save, sender=CoinRedemption, dispatch_uid="to_checksum_address")
def to_checksum_address(sender, instance, **kwargs):
    """Handle pre-save signals from CoinRemptions to normalize the contract address."""
    if instance.contract_address:
        instance.contract_address = Web3.toChecksumAddress(instance.contract_address)
        print(instance.contract_address)


class CoinRedemptionRequest(SuperModel):
    """Define the coin redemption request schema."""

    class Meta:
        """Define metadata associated with CoinRedemptionRequest."""

        verbose_name_plural = 'Coin Redemption Requests'

    coin_redemption = models.OneToOneField(CoinRedemption, blank=False, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(protocol='IPv4')
    txid = models.CharField(max_length=255, default='')
    txaddress = models.CharField(max_length=255)
    sent_on = models.DateTimeField(null=True)


class Tool(SuperModel):
    """Define the Tool schema."""

    CAT_ADVANCED = 'AD'
    CAT_ALPHA = 'AL'
    CAT_BASIC = 'BA'
    CAT_BUILD = 'BU'
    CAT_COMING_SOON = 'CS'
    CAT_COMMUNITY = 'CO'
    CAT_FOR_FUN = 'FF'

    TOOL_CATEGORIES = (
        (CAT_ADVANCED, 'advanced'),
        (CAT_ALPHA, 'alpha'),
        (CAT_BASIC, 'basic'),
        (CAT_BUILD, 'tools to build'),
        (CAT_COMING_SOON, 'coming soon'),
        (CAT_COMMUNITY, 'community'),
        (CAT_FOR_FUN, 'just for fun'),
    )

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=2, choices=TOOL_CATEGORIES)
    img = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    url_name = models.CharField(max_length=40, blank=True)
    link = models.CharField(max_length=255, blank=True)
    link_copy = models.CharField(max_length=255, blank=True)
    active = models.BooleanField(default=False)
    new = models.BooleanField(default=False)
    stat_graph = models.CharField(max_length=255)
    votes = models.ManyToManyField('dashboard.ToolVote', blank=True)

    def __str__(self):
        return self.name

    @property
    def img_url(self):
        return static(self.img)

    @property
    def link_url(self):
        if self.link and not self.url_name:
            return self.link

        try:
            return reverse(self.url_name)
        except NoReverseMatch:
            pass

        return reverse('tools')

    def starting_score(self):
        if self.category == self.CAT_BASIC:
            return 10
        elif self.category == self.CAT_ADVANCED:
            return 5
        elif self.category in [self.CAT_BUILD, self.CAT_COMMUNITY]:
            return 3
        elif self.category == self.CAT_ALPHA:
            return 2
        elif self.category == self.CAT_COMING_SOON:
            return 1
        elif self.category == self.CAT_FOR_FUN:
            return 1
        return 0

    def vote_score(self):
        score = self.starting_score()
        for vote in self.votes.all():
            score += vote.value
        return score

    def i18n_name(self):
        return _(self.name)

    def i18n_description(self):
        return _(self.description)

    def i18n_link_copy(self):
        return _(self.link_copy)

    def __str__(self):
        return self.name


class ToolVote(models.Model):
    """Define the vote placed on a tool."""

    profile = models.ForeignKey('dashboard.Profile', related_name='votes', on_delete=models.CASCADE)
    value = models.IntegerField(default=0)

    @property
    def tool(self):
        try:
            return Tool.objects.filter(votes__in=[self.pk]).first()
        except Exception:
            return None

    def __str__(self):
        return f"{self.profile} | {self.value} | {self.tool}"
