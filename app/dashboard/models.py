# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Gitcoin Core

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

import base64
import collections
import logging
from datetime import datetime, timedelta
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection, models
from django.db.models import Q, Sum
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.templatetags.static import static
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import pytz
import requests
from app.utils import get_upload_filename
from dashboard.sql.persona import PERSONA_SQL
from dashboard.tokens import addr_to_token
from economy.models import ConversionRate, SuperModel
from economy.utils import ConversionRateNotFoundError, convert_amount, convert_token_to_usdt
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from git.utils import (
    _AUTH, HEADERS, TOKEN_URL, build_auth_dict, get_gh_issue_details, get_issue_comments, issue_number, org_name,
    repo_name,
)
from marketing.mails import featured_funded_bounty, start_work_approved
from marketing.models import LeaderboardRank
from rest_framework import serializers
from web3 import Web3

from .notifications import (
    maybe_market_to_github, maybe_market_to_slack, maybe_market_to_twitter, maybe_market_to_user_slack,
)
from .signals import m2m_changed_interested

logger = logging.getLogger(__name__)


class BountyQuerySet(models.QuerySet):
    """Handle the manager queryset for Bounties."""

    def current(self):
        """Filter results down to current bounties only."""
        return self.filter(current_bounty=True, admin_override_and_hide=False)

    def stats_eligible(self):
        """Exclude results that we don't want to track in statistics."""
        return self.current().exclude(idx_status__in=['unknown', 'cancelled'])

    def exclude_by_status(self, excluded_statuses=None):
        """Exclude results with a status matching the provided list."""
        if excluded_statuses is None:
            excluded_statuses = []

        return self.exclude(idx_status__in=excluded_statuses)

    def filter_by_status(self, filtered_status=None):
        """Filter results with a status matching the provided list."""
        if filtered_status is None:
            filtered_status = list()
        elif isinstance(filtered_status, list):
            return self.filter(idx_status__in=filtered_status)
        else:
            return

    def keyword(self, keyword):
        """Filter results to all Bounty objects containing the keywords.

        Args:
            keyword (str): The keyword to search title, issue description, and issue keywords by.

        Returns:
            dashboard.models.BountyQuerySet: The QuerySet of bounties filtered by keyword.

        """
        return self.filter(
            Q(metadata__issueKeywords__icontains=keyword) | \
            Q(title__icontains=keyword) | \
            Q(issue_description__icontains=keyword)
        )

    def hidden(self):
        """Filter results to only bounties that have been manually hidden by moderators."""
        return self.filter(admin_override_and_hide=True)

    def visible(self):
        """Filter results to only bounties not marked as hidden."""
        return self.filter(admin_override_and_hide=False)

    def needs_review(self):
        """Filter results by bounties that need reviewed."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type__in=['bounty_abandonment_escalation_to_mods', 'bounty_abandonment_warning'],
                activities__needs_review=True,
            )

    def reviewed(self):
        """Filter results by bounties that have been reviewed."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type__in=['bounty_abandonment_escalation_to_mods', 'bounty_abandonment_warning'],
                activities__needs_review=False,
            )

    def warned(self):
        """Filter results by bounties that have been warned for inactivity."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type='bounty_abandonment_warning',
                activities__needs_review=True,
            )

    def escalated(self):
        """Filter results by bounties that have been escalated for review."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type='bounty_abandonment_escalation_to_mods',
                activities__needs_review=True,
            )

    def closed(self):
        """Filter results by bounties that have been closed on Github."""
        return self.filter(github_issue_details__state='closed')

    def not_started(self):
        """Filter results by bounties that have not been picked up in 3+ days."""
        dt = timezone.now() - timedelta(days=3)
        return self.prefetch_related('interested').filter(interested__isnull=True, created_on__gt=dt)

    def has_funds(self):
        """Filter results by bounties that are actively funded or funds have been dispersed."""
        return self.filter(idx_status__in=Bounty.FUNDED_STATUSES)


"""Fields that bonties table should index together."""
def get_bounty_index_together():
    import copy
    index_together = [
            ["network", "idx_status"],
            ["current_bounty", "network"],
            ["current_bounty", "network", "idx_status"],
            ["current_bounty", "network", "web3_created"],
            ["current_bounty", "network", "idx_status", "web3_created"],
        ]
    additions = ['admin_override_and_hide', 'experience_level', 'is_featured', 'project_length', 'bounty_owner_github_username', 'event']
    for addition in additions:
        for ele in copy.copy(index_together):
            index_together.append([addition] + ele)
    return index_together


class Bounty(SuperModel):
    """Define the structure of a Bounty.

    Attributes:
        BOUNTY_TYPES (list of tuples): The valid bounty types.
        EXPERIENCE_LEVELS (list of tuples): The valid experience levels.
        PROJECT_LENGTHS (list of tuples): The possible project lengths.
        STATUS_CHOICES (list of tuples): The valid status stages.
        FUNDED_STATUSES (list of str): The list of status types considered to have retained value.
        OPEN_STATUSES (list of str): The list of status types considered open.
        CLOSED_STATUSES (list of str): The list of status types considered closed.
        TERMINAL_STATUSES (list of str): The list of status types considered terminal states.

    """

    PERMISSION_TYPES = [
        ('permissionless', 'permissionless'),
        ('approval', 'approval'),
    ]
    REPO_TYPES = [
        ('public', 'public'),
        ('private', 'private'),
    ]
    PROJECT_TYPES = [
        ('traditional', 'traditional'),
        ('contest', 'contest'),
        ('cooperative', 'cooperative'),
    ]
    BOUNTY_CATEGORIES = [
        ('frontend', 'frontend'),
        ('backend', 'backend'),
        ('design', 'design'),
        ('documentation', 'documentation'),
        ('other', 'other'),
    ]
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
    FUNDED_STATUSES = ['open', 'started', 'submitted', 'done']
    OPEN_STATUSES = ['open', 'started', 'submitted']
    CLOSED_STATUSES = ['expired', 'unknown', 'cancelled', 'done']
    WORK_IN_PROGRESS_STATUSES = ['open', 'started', 'submitted']
    TERMINAL_STATUSES = ['done', 'expired', 'cancelled']

    web3_type = models.CharField(max_length=50, default='bounties_network')
    title = models.CharField(max_length=255)
    web3_created = models.DateTimeField(db_index=True)
    value_in_token = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    bounty_type = models.CharField(max_length=50, choices=BOUNTY_TYPES, blank=True, db_index=True)
    project_length = models.CharField(max_length=50, choices=PROJECT_LENGTHS, blank=True)
    estimated_hours = models.PositiveIntegerField(blank=True, null=True)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS, blank=True, db_index=True)
    github_url = models.URLField(db_index=True)
    github_issue_details = JSONField(default=dict, blank=True, null=True)
    github_comments = models.IntegerField(default=0)
    bounty_owner_address = models.CharField(max_length=50)
    bounty_owner_email = models.CharField(max_length=255, blank=True)
    bounty_owner_github_username = models.CharField(max_length=255, blank=True, db_index=True)
    bounty_owner_name = models.CharField(max_length=255, blank=True)
    bounty_owner_profile = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.SET_NULL, related_name='bounties_funded', blank=True
    )
    bounty_reserved_for_user = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.SET_NULL, related_name='reserved_bounties', blank=True
    )
    is_open = models.BooleanField(help_text=_('Whether the bounty is still open for fulfillments.'))
    expires_date = models.DateTimeField()
    raw_data = JSONField()
    metadata = JSONField(default=dict, blank=True)
    current_bounty = models.BooleanField(
        default=False, help_text=_('Whether this bounty is the most current revision one or not'), db_index=True)
    _val_usd_db = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    contract_address = models.CharField(max_length=50, default='')
    network = models.CharField(max_length=255, blank=True, db_index=True)
    idx_experience_level = models.IntegerField(default=0, db_index=True)
    idx_project_length = models.IntegerField(default=0, db_index=True)
    idx_status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='open', db_index=True)
    issue_description = models.TextField(default='', blank=True)
    funding_organisation = models.CharField(max_length=255, default='', blank=True)
    standard_bounties_id = models.IntegerField(default=0)
    num_fulfillments = models.IntegerField(default=0)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    accepted = models.BooleanField(default=False, help_text=_('Whether the bounty has been done'))
    interested = models.ManyToManyField('dashboard.Interest', blank=True)
    interested_comment = models.IntegerField(null=True, blank=True)
    submissions_comment = models.IntegerField(null=True, blank=True)
    override_status = models.CharField(max_length=255, blank=True)
    last_comment_date = models.DateTimeField(null=True, blank=True)
    funder_last_messaged_on = models.DateTimeField(null=True, blank=True)
    fulfillment_accepted_on = models.DateTimeField(null=True, blank=True)
    fulfillment_submitted_on = models.DateTimeField(null=True, blank=True)
    fulfillment_started_on = models.DateTimeField(null=True, blank=True)
    canceled_on = models.DateTimeField(null=True, blank=True)
    canceled_bounty_reason = models.TextField(default='', blank=True, verbose_name=_('Cancelation reason'))
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPES, default='traditional', db_index=True)
    permission_type = models.CharField(max_length=50, choices=PERMISSION_TYPES, default='permissionless', db_index=True)
    bounty_categories = ArrayField(models.CharField(max_length=50, choices=BOUNTY_CATEGORIES), default=list)
    repo_type = models.CharField(max_length=50, choices=REPO_TYPES, default='public')
    snooze_warnings_for_days = models.IntegerField(default=0)
    is_featured = models.BooleanField(
        default=False, help_text=_('Whether this bounty is featured'))
    featuring_date = models.DateTimeField(blank=True, null=True, db_index=True)
    fee_amount = models.DecimalField(default=0, decimal_places=18, max_digits=50)
    fee_tx_id = models.CharField(default="0x0", max_length=255, blank=True)
    coupon_code = models.ForeignKey('dashboard.Coupon', blank=True, null=True, related_name='coupon', on_delete=models.SET_NULL)
    unsigned_nda = models.ForeignKey('dashboard.BountyDocuments', blank=True, null=True, related_name='bounty', on_delete=models.SET_NULL)

    token_value_time_peg = models.DateTimeField(blank=True, null=True)
    token_value_in_usdt = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_in_usdt_now = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_in_usdt = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_in_eth = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    value_true = models.DecimalField(default=0, decimal_places=2, max_digits=50, blank=True, null=True)
    privacy_preferences = JSONField(default=dict, blank=True)
    admin_override_and_hide = models.BooleanField(
        default=False, help_text=_('Admin override to hide the bounty from the system')
    )
    admin_override_suspend_auto_approval = models.BooleanField(
        default=False, help_text=_('Admin override to suspend work auto approvals')
    )
    admin_mark_as_remarket_ready = models.BooleanField(
        default=False, help_text=_('Admin override to mark as remarketing ready')
    )
    admin_override_org_name = models.CharField(max_length=255, blank=True) # TODO: Remove POST ORGS
    admin_override_org_logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('Organization Logo - Override'),
    ) # TODO: Remove POST ORGS
    attached_job_description = models.URLField(blank=True, null=True, db_index=True)
    event = models.ForeignKey('dashboard.HackathonEvent', related_name='bounties', null=True, on_delete=models.SET_NULL, blank=True)

    # Bounty QuerySet Manager
    objects = BountyQuerySet.as_manager()

    class Meta:
        """Define metadata associated with Bounty."""

        verbose_name_plural = 'Bounties'
        index_together = [
            ["network", "idx_status"],
        ] + get_bounty_index_together()

    def __str__(self):
        """Return the string representation of a Bounty."""
        return f"{'(C) ' if self.current_bounty else ''}{self.pk}: {self.title}, {self.value_true} " \
               f"{self.token_name} @ {naturaltime(self.web3_created)}"

    def save(self, *args, **kwargs):
        """Define custom handling for saving bounties."""
        from .utils import clean_bounty_url
        if self.bounty_owner_github_username:
            self.bounty_owner_github_username = self.bounty_owner_github_username.lstrip('@')
        if self.github_url:
            self.github_url = clean_bounty_url(self.github_url)
        super().save(*args, **kwargs)

    @property
    def latest_activity(self):
        activity = Activity.objects.filter(bounty=self.pk).order_by('-pk')
        if activity.exists():
            from dashboard.router import ActivitySerializer
            return ActivitySerializer(activity.first()).data
        return None

    @property
    def profile_pairs(self):
        profile_handles = []

        for profile in self.interested.select_related('profile').all().order_by('pk'):
            profile_handles.append((profile.profile.handle, profile.profile.absolute_url))

        return profile_handles

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

    def get_canonical_url(self):
        """Get the canonical URL of the Bounty for SEO purposes.

        Returns:
            str: The canonical URL of the Bounty.

        """
        _org_name = org_name(self.github_url)
        _repo_name = repo_name(self.github_url)
        _issue_num = int(issue_number(self.github_url))
        return settings.BASE_URL.rstrip('/') + reverse('issue_details_new2', kwargs={'ghuser': _org_name, 'ghrepo': _repo_name, 'ghissue': _issue_num})

    def get_natural_value(self):
        token = addr_to_token(self.token_address)
        if not token:
            return 0
        decimals = token.get('decimals', 0)
        return float(self.value_in_token) / 10**decimals

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def canonical_url(self):
        return self.get_canonical_url()

    def snooze_url(self, num_days):
        """Get the bounty snooze URL.

        Args:
            num_days (int): The number of days to snooze the Bounty.

        Returns:
            str: The snooze URL based on the provided number of days.

        """
        return f'{self.get_absolute_url()}?snooze={num_days}'

    def approve_worker_url(self, worker):
        """Get the bounty work approval URL.

        Args:
            worker (string): The handle to approve

        Returns:
            str: The work approve URL based on the worker name

        """
        return f'{self.get_absolute_url()}?mutate_worker_action=approve&worker={worker}'

    def reject_worker_url(self, worker):
        """Get the bounty work rejection URL.

        Args:
            worker (string): The handle to reject

        Returns:
            str: The work reject URL based on the worker name

        """
        return f'{self.get_absolute_url()}?mutate_worker_action=reject&worker={worker}'

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
    def org_display_name(self): # TODO: Remove POST ORGS
        if self.admin_override_org_name:
            return self.admin_override_org_name
        return org_name(self.github_url)

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

    def is_fulfiller(self, handle):
        """Determine whether or not the profile is the bounty is_fulfiller.

        Args:
            handle (str): The profile handle to be compared.

        Returns:
            bool: Whether or not the user is the bounty is_fulfiller.

        """
        return any(profile.fulfiller_github_username == handle for profile in self.fulfillments.filter(accepted=True).all())

    def is_funder(self, handle):
        """Determine whether or not the profile is the bounty funder.

        Args:
            handle (str): The profile handle to be compared.

        Returns:
            bool: Whether or not the user is the bounty funder.

        """
        return handle.lower().lstrip('@') == self.bounty_owner_github_username.lower().lstrip('@')

    def has_started_work(self, handle, pending=False):
        """Determine whether or not the profile has started work

        Args:
            handle (str): The profile handle to be compared.

        Returns:
            bool: Whether or not the user has started work.

        """
        return self.interested.filter(pending=pending, profile__handle__iexact=handle).exists()

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

        if self.admin_override_org_logo:
            return self.admin_override_org_logo.url

        org_name = self.github_org_name
        gitcoin_logo_flag = "/1" if gitcoin_logo_flag else ""
        if org_name:
            return f"{settings.BASE_URL}dynamic/avatar/{org_name}{gitcoin_logo_flag}"
        return f"{settings.BASE_URL}funding/avatar?repo={self.github_url}&v=3"

    @property
    def keywords(self):
        try:
            return self.metadata.get('issueKeywords', False)
        except Exception:
            return False

    @property
    def keywords_list(self):
        keywords = self.keywords
        if not keywords:
            return []
        else:
            try:
                return [keyword.strip() for keyword in keywords.split(",")]
            except AttributeError:
                return []

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
            return self.idx_status

        # standard bounties
        is_traditional_bounty_type = self.project_type == 'traditional'
        try:
            has_tips = self.tips.filter(is_for_bounty_fulfiller=False).send_happy_path().exists()
            if has_tips and is_traditional_bounty_type:
                return 'done'
            if not self.is_open:
                if self.accepted:
                    return 'done'
                elif self.past_hard_expiration_date:
                    return 'expired'
                elif has_tips:
                    return 'done'
                # If its not expired or done, and no tips, it must be cancelled.
                return 'cancelled'
            # per https://github.com/gitcoinco/web/pull/1098 ,
            # cooperative/contest are open no matter how much started/submitted work they have
            if self.pk and self.project_type in ['contest', 'cooperative']:
                return 'open'
            if self.num_fulfillments == 0:
                if self.pk and self.interested.filter(pending=False).exists():
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
            return convert_amount(self.value_true, self.token_name, 'ETH')
        except Exception:
            return None

    @property
    def get_value_in_usdt_now(self):
        return self.value_in_usdt_at_time(None)

    @property
    def get_value_in_usdt(self):
        if self.status in self.OPEN_STATUSES:
            return self.value_in_usdt_now
        return self.value_in_usdt_then

    @property
    def value_in_usdt_then(self):
        return self.value_in_usdt_at_time(self.web3_created)

    def value_in_usdt_at_time(self, at_time):
        decimals = 10 ** 18
        if self.token_name == 'USDT':
            return float(self.value_in_token)
        if self.token_name in settings.STABLE_COINS:
            return float(self.value_in_token / 10 ** 18)
        try:
            return round(float(convert_amount(self.value_true, self.token_name, 'USDT', at_time)), 2)
        except ConversionRateNotFoundError:
            try:
                in_eth = round(float(convert_amount(self.value_true, self.token_name, 'ETH', at_time)), 2)
                return round(float(convert_amount(in_eth, 'USDT', 'USDT', at_time)), 2)
            except ConversionRateNotFoundError:
                return None

    @property
    def token_value_in_usdt_now(self):
        if self.token_name in settings.STABLE_COINS:
            return 1
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
        params = f'pk={self.pk}&network={self.network}'
        urls = {}
        for item in ['fulfill', 'increase', 'accept', 'cancel', 'payout', 'contribute',
                     'advanced_payout', 'social_contribution', 'invoice', ]:
            urls.update({item: f'/issue/{item}?{params}'})
        return urls

    def is_notification_eligible(self, var_to_check=True):
        """Determine whether or not a notification is eligible for transmission outside of production.

        Returns:
            bool: Whether or not the Bounty is eligible for outbound notifications.

        """
        if not var_to_check or self.get_natural_value() < 0.0001 or (
           self.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK):
            return False
        if self.network == 'mainnet' and (settings.DEBUG or settings.ENV != 'prod'):
            return False
        if (settings.DEBUG or settings.ENV != 'prod') and settings.GITHUB_API_USER != self.github_org_name:
            return False

        return True

    @property
    def is_project_type_fulfilled(self):
        """Determine whether or not the Project Type is currently fulfilled.

        Todo:
            * Add remaining Project Type fulfillment handling.

        Returns:
            bool: Whether or not the Bounty Project Type is fully staffed.

        """
        fulfilled = False
        if self.project_type == 'traditional':
            fulfilled = self.interested.filter(pending=False).exists()
        return fulfilled

    @property
    def needs_review(self):
        if self.activities.filter(needs_review=True).exists():
            return True
        return False

    @property
    def github_issue_state(self):
        current_github_state = self.github_issue_details.get('state') if self.github_issue_details else None
        if not current_github_state:
            try:
                _org_name = org_name(self.github_url)
                _repo_name = repo_name(self.github_url)
                _issue_num = issue_number(self.github_url)
                gh_issue_details = get_gh_issue_details(_org_name, _repo_name, int(_issue_num))
                if gh_issue_details:
                    self.github_issue_details = gh_issue_details
                    self.save()
                    current_github_state = self.github_issue_details.get('state', 'open')
            except Exception as e:
                logger.info(e)
                return 'open'
        return current_github_state

    @property
    def is_issue_closed(self):
        if self.github_issue_state == 'closed':
            return True
        return False

    @property
    def tips(self):
        """Return the tips associated with this bounty."""
        try:
            return Tip.objects.filter(github_url__iexact=self.github_url, network=self.network).order_by('-created_on')
        except:
            return Tip.objects.none()

    @property
    def bulk_payout_tips(self):
        """Return the Bulk payout tips associated with this bounty."""
        queryset = self.tips.filter(is_for_bounty_fulfiller=False, metadata__is_clone__isnull=True)
        return (queryset.filter(from_address=self.bounty_owner_address) |
                queryset.filter(from_name=self.bounty_owner_github_username))

    @property
    def paid(self):
        """Return list of users paid for this bounty."""
        if self.status != 'done':
            return []  # to save the db hits

        return_list = []
        for fulfillment in self.fulfillments.filter(accepted=True):
            if fulfillment.fulfiller_github_username:
                return_list.append(fulfillment.fulfiller_github_username)
        for tip in self.tips.send_happy_path():
            if tip.username:
                return_list.append(tip.username)
        return list(set(return_list))

    @property
    def additional_funding_summary(self):
        """Return a dict describing the additional funding from crowdfunding that this object has"""
        ret = {}
        for tip in self.tips.filter(is_for_bounty_fulfiller=True).send_happy_path():
            token = tip.tokenName
            obj = ret.get(token, {})

            if not obj:
                obj['amount'] = 0.0

                conversion_rate = ConversionRate.objects.filter(
                    from_currency=token,
                    to_currency='USDT',
                ).order_by('-timestamp').first()

                if conversion_rate:
                    obj['ratio'] = (float(conversion_rate.to_amount) / float(conversion_rate.from_amount))
                    obj['timestamp'] = conversion_rate.timestamp
                else:
                    obj['ratio'] = 0.0
                    obj['timestamp'] = datetime.now()

                ret[token] = obj

            obj['amount'] += tip.amount_in_whole_units
        return ret

    @property
    def additional_funding_summary_sentence(self):
        afs = self.additional_funding_summary
        tokens = afs.keys()

        if not tokens:
            return ''

        items = []
        usd_value = 0.0

        for token_name in tokens:
            obj = afs[token_name]
            ratio = obj['ratio']
            amount = obj['amount']
            usd_value += amount * ratio
            items.append(f"{amount} {token_name}")

        sentence = ", ".join(items)

        if usd_value:
            sentence += f" worth {usd_value} USD"

        return sentence

    @property
    def reserved_for_user_handle(self):
        if self.bounty_reserved_for_user:
            return self.bounty_reserved_for_user.handle
        return ''

    @reserved_for_user_handle.setter
    def reserved_for_user_handle(self, handle):
        profile = None

        if handle:
            try:
                profile = Profile.objects.filter(handle__iexact=handle).first()
            except:
                logger.warning(f'reserved_for_user_handle: Unknown handle: ${handle}')

        self.bounty_reserved_for_user = profile


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
    fulfiller_metadata = JSONField(default=dict, blank=True)
    fulfillment_id = models.IntegerField(null=True, blank=True)
    fulfiller_hours_worked = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=50)
    fulfiller_github_url = models.CharField(max_length=255, blank=True, null=True)
    funder_last_notified_on = models.DateTimeField(null=True, blank=True)
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
    def should_hide(self):
        return self.fulfiller_github_username in settings.BLOCKED_USERS

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


class RefundFeeRequest(SuperModel):
    """Define the Refund Fee Request model."""
    profile = models.ForeignKey(
        'dashboard.Profile',
        null=True,
        on_delete=models.SET_NULL,
        related_name='refund_requests',
    )
    bounty = models.ForeignKey(
        'dashboard.Bounty',
        on_delete=models.CASCADE
    )
    fulfilled = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    comment = models.TextField(max_length=500, blank=True)
    comment_admin = models.TextField(max_length=500, blank=True)
    fee_amount = models.FloatField()
    token = models.CharField(max_length=10)
    address = models.CharField(max_length=255)
    txnId = models.CharField(max_length=255, blank=True)

    def __str__(self):
        """Return the string representation of RefundFeeRequest."""
        return f"bounty: {self.bounty}, fee: {self.fee_amount}, token: {self.token}. Time: {self.created_on}"


class Subscription(SuperModel):

    email = models.EmailField(max_length=255)
    raw_data = models.TextField()
    ip = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.email} {self.created_on}"


class BountyDocuments(SuperModel):

    doc = models.FileField(upload_to=get_upload_filename, null=True, blank=True, help_text=_('Bounty documents.'))
    doc_type = models.CharField(max_length=50)


class SendCryptoAssetQuerySet(models.QuerySet):
    """Handle the manager queryset for SendCryptoAsset."""

    def send_success(self):
        """Filter results down to successful sends only."""
        return self.filter(tx_status='success').exclude(txid='')

    def send_pending(self):
        """Filter results down to pending sends only."""
        return self.filter(tx_status='pending').exclude(txid='')

    def send_happy_path(self):
        """Filter results down to pending/success sends only."""
        return self.filter(tx_status__in=['pending', 'success']).exclude(txid='')

    def send_fail(self):
        """Filter results down to failed sends only."""
        return self.filter(Q(txid='') | Q(tx_status__in=['dropped', 'unknown', 'na', 'error']))

    def receive_success(self):
        """Filter results down to successful receives only."""
        return self.filter(receive_tx_status='success').exclude(receive_txid='')

    def receive_pending(self):
        """Filter results down to pending receives only."""
        return self.filter(receive_tx_status='pending').exclude(receive_txid='')

    def receive_happy_path(self):
        """Filter results down to pending receives only."""
        return self.filter(receive_tx_status__in=['pending', 'success']).exclude(receive_txid='')

    def receive_fail(self):
        """Filter results down to failed receives only."""
        return self.filter(Q(receive_txid='') | Q(receive_tx_status__in=['dropped', 'unknown', 'na', 'error']))


class SendCryptoAsset(SuperModel):
    """Abstract Base Class to handle the model for both Tips and Kudos."""

    TX_STATUS_CHOICES = (
        ('na', 'na'),  # not applicable
        ('pending', 'pending'),
        ('success', 'success'),
        ('error', 'error'),
        ('unknown', 'unknown'),
        ('dropped', 'dropped'),
    )

    web3_type = models.CharField(max_length=50, default='v3')
    emails = JSONField(blank=True)
    url = models.CharField(max_length=255, default='', blank=True)
    primary_email = models.CharField(max_length=255, default='', blank=True)
    tokenName = models.CharField(max_length=255, default='ETH')
    tokenAddress = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    comments_public = models.TextField(default='', blank=True)
    ip = models.CharField(max_length=50)
    github_url = models.URLField(null=True, blank=True)
    from_name = models.CharField(max_length=255, default='', blank=True)
    from_email = models.CharField(max_length=255, default='', blank=True)
    from_username = models.CharField(max_length=255, default='', blank=True)
    username = models.CharField(max_length=255, default='', blank=True)  # to username
    network = models.CharField(max_length=255, default='')
    txid = models.CharField(max_length=255, default='')
    receive_txid = models.CharField(max_length=255, default='', blank=True)
    received_on = models.DateTimeField(null=True, blank=True)
    from_address = models.CharField(max_length=255, default='', blank=True)
    receive_address = models.CharField(max_length=255, default='', blank=True)
    metadata = JSONField(default=dict, blank=True)
    is_for_bounty_fulfiller = models.BooleanField(
        default=False,
        help_text='If this option is chosen, this tip will be automatically paid to the bounty'
                  ' fulfiller, not self.usernameusername.',
    )

    tx_status = models.CharField(max_length=9, choices=TX_STATUS_CHOICES, default='na', db_index=True)
    receive_tx_status = models.CharField(max_length=9, choices=TX_STATUS_CHOICES, default='na', db_index=True)
    tx_time = models.DateTimeField(null=True, blank=True)
    receive_tx_time = models.DateTimeField(null=True, blank=True)

    # QuerySet Manager
    objects = SendCryptoAssetQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self):
        """Return the string representation for a tip."""
        if self.web3_type == 'yge':
            return f"({self.network}) - {self.status}{' ORPHAN' if not self.emails else ''} " \
               f"{self.amount} {self.tokenName} to {self.username} from {self.from_name or 'NA'}, " \
               f"created: {naturalday(self.created_on)}, expires: {naturalday(self.expires_date)}"
        status = 'funded' if self.txid else 'not funded'
        status = status if not self.receive_txid else 'received'
        return f"({self.web3_type}) {status} {self.amount} {self.tokenName} to {self.username} from {self.from_name or 'NA'}"

    # TODO: DRY
    def get_natural_value(self):
        token = addr_to_token(self.tokenAddress)
        decimals = token['decimals']
        return float(self.amount) / 10**decimals

    @property
    def value_true(self):
        return self.get_natural_value()

    @property
    def amount_in_wei(self):
        token = addr_to_token(self.tokenAddress)
        decimals = token['decimals'] if token else 18
        return float(self.amount) * 10**decimals

    @property
    def amount_in_whole_units(self):
        return float(self.amount)

    @property
    def org_name(self):
        try:
            return org_name(self.github_url)
        except Exception:
            return None

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
        return self.value_in_usdt_at_time(None)

    @property
    def value_in_usdt(self):
        return self.value_in_usdt_then

    @property
    def value_in_usdt_then(self):
        return self.value_in_usdt_at_time(self.created_on)

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

    def value_in_usdt_at_time(self, at_time):
        decimals = 1
        if self.tokenName in settings.STABLE_COINS:
            return float(self.amount)
        try:
            return round(float(convert_amount(self.amount, self.tokenName, 'USDT', at_time)) / decimals, 2)
        except ConversionRateNotFoundError:
            try:
                in_eth = convert_amount(self.amount, self.tokenName, 'ETH', at_time)
                return round(float(convert_amount(in_eth, 'ETH', 'USDT', at_time)) / decimals, 2)
            except ConversionRateNotFoundError:
                return None

    @property
    def status(self):
        if self.receive_txid:
            return "RECEIVED"
        return "PENDING"

    @property
    def github_org_name(self):
        try:
            return org_name(self.github_url)
        except Exception:
            return None

    def is_notification_eligible(self, var_to_check=True):
        """Determine whether or not a notification is eligible for transmission outside of production.

        Returns:
            bool: Whether or not the Tip is eligible for outbound notifications.

        """
        if not var_to_check or self.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
            return False
        if self.network == 'mainnet' and (settings.DEBUG or settings.ENV != 'prod'):
            return False
        if (settings.DEBUG or settings.ENV != 'prod') and settings.GITHUB_API_USER != self.github_org_name:
            return False
        return True

    def update_tx_status(self):
        """ Updates the tx status according to what infura says about the tx

        """
        from dashboard.utils import get_tx_status
        self.tx_status, self.tx_time = get_tx_status(self.txid, self.network, self.created_on)
        return bool(self.tx_status)

    def update_receive_tx_status(self):
        """ Updates the receive tx status according to what infura says about the receive tx

        """
        from dashboard.utils import get_tx_status
        self.receive_tx_status, self.receive_tx_time = get_tx_status(self.receive_txid, self.network, self.created_on)
        return bool(self.receive_tx_status)

    @property
    def bounty(self):
        try:
            return Bounty.objects.current().filter(
                github_url__iexact=self.github_url,
                network=self.network).order_by('-web3_created').first()
        except Bounty.DoesNotExist:
            return None


class Tip(SendCryptoAsset):
    """ Inherit from SendCryptoAsset base class, and extra fields that are needed for Tips. """
    expires_date = models.DateTimeField(null=True, blank=True)
    comments_priv = models.TextField(default='', blank=True)
    recipient_profile = models.ForeignKey(
        'dashboard.Profile', related_name='received_tips', on_delete=models.SET_NULL, null=True, blank=True
    )
    sender_profile = models.ForeignKey(
        'dashboard.Profile', related_name='sent_tips', on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def receive_url(self):
        if self.web3_type == 'yge':
            return self.url
        elif self.web3_type == 'v3':
            return self.receive_url_for_recipient
        elif self.web3_type != 'v2':
            raise Exception

        return self.receive_url_for_recipient

    @property
    def receive_url_for_recipient(self):
        if self.web3_type != 'v3':
            logger.error('Web3 type is not "v3"')
            return ''

        try:
            key = self.metadata['reference_hash_for_receipient']
            return f"{settings.BASE_URL}tip/receive/v3/{key}/{self.txid}/{self.network}"
        except Exception as e:
            logger.warning('Receive url for Tip recipient not found')
            return ''


class TipPayoutException(Exception):
    pass

@receiver(pre_save, sender=Tip, dispatch_uid="psave_tip")
def psave_tip(sender, instance, **kwargs):
    # when a new tip is saved, make sure it doesnt have whitespace in it
    instance.username = instance.username.replace(' ', '')


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


class InterestQuerySet(models.QuerySet):
    """Handle the manager queryset for Interests."""

    def needs_review(self):
        """Filter results to Interest objects requiring review by moderators."""
        return self.filter(status=Interest.STATUS_REVIEW)

    def warned(self):
        """Filter results to Interest objects that are currently in warning."""
        return self.filter(status=Interest.STATUS_WARNED)


class Interest(SuperModel):
    """Define relationship for profiles expressing interest on a bounty."""

    STATUS_REVIEW = 'review'
    STATUS_WARNED = 'warned'
    STATUS_OKAY = 'okay'
    STATUS_SNOOZED = 'snoozed'
    STATUS_PENDING = 'pending'

    WORK_STATUSES = (
        (STATUS_REVIEW, 'Needs Review'),
        (STATUS_WARNED, 'Hunter Warned'),
        (STATUS_OKAY, 'Okay'),
        (STATUS_SNOOZED, 'Snoozed'),
        (STATUS_PENDING, 'Pending'),
    )

    profile = models.ForeignKey('dashboard.Profile', related_name='interested', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_('Date Created'))
    issue_message = models.TextField(default='', blank=True, verbose_name=_('Issue Comment'))
    pending = models.BooleanField(
        default=False,
        help_text=_('If this option is chosen, this interest is pending and not yet active'),
        verbose_name=_('Pending'),
    )
    acceptance_date = models.DateTimeField(blank=True, null=True, verbose_name=_('Date Accepted'))
    status = models.CharField(
        choices=WORK_STATUSES,
        default=STATUS_OKAY,
        max_length=7,
        help_text=_('Whether or not the interest requires review'),
        verbose_name=_('Needs Review'))
    signed_nda = models.ForeignKey('dashboard.BountyDocuments', blank=True, null=True, related_name='interest', on_delete=models.SET_NULL)

    # Interest QuerySet Manager
    objects = InterestQuerySet.as_manager()

    def __str__(self):
        """Define the string representation of an interested profile."""
        return f"{self.profile.handle} / pending: {self.pending} / status: {self.status}"

    @property
    def bounties(self):
        return Bounty.objects.filter(interested=self)

    def change_status(self, status=None):
        if status is None or status not in self.WORK_STATUSES:
            return self
        self.status = status
        self.save()
        return self

    def mark_for_review(self):
        """Flag the Interest for review by the moderation team."""
        self.status = self.STATUS_REVIEW
        self.save()
        return self

def auto_user_approve(interest, bounty):
    interest.pending = False
    interest.acceptance_date = timezone.now()
    start_work_approved(interest, bounty)
    maybe_market_to_github(bounty, 'work_started', profile_pairs=bounty.profile_pairs)
    maybe_market_to_slack(bounty, 'worker_approved')
    maybe_market_to_user_slack(bounty, 'worker_approved')
    maybe_market_to_twitter(bounty, 'worker_approved')


@receiver(post_save, sender=Interest, dispatch_uid="psave_interest")
@receiver(post_delete, sender=Interest, dispatch_uid="pdel_interest")
def psave_interest(sender, instance, **kwargs):
    # when a new interest is saved, update the status on frontend
    print("signal: updating bounties psave_interest")
    for bounty in Bounty.objects.filter(interested=instance):

        if bounty.bounty_reserved_for_user == instance.profile:
            auto_user_approve(instance, bounty)
        bounty.save()


class ActivityQuerySet(models.QuerySet):
    """Handle the manager queryset for Activities."""

    def needs_review(self):
        """Filter results to Activity objects to be reviewed by moderators."""
        return self.select_related('bounty', 'profile').filter(needs_review=True)

    def reviewed(self):
        """Filter results to Activity objects to be reviewed by moderators."""
        return self.select_related('bounty', 'profile').filter(
            needs_review=False,
            activity_type__in=['bounty_abandonment_escalation_to_mods', 'bounty_abandonment_warning'],
        )

    def warned(self):
        """Filter results to Activity objects to be reviewed by moderators."""
        return self.select_related('bounty', 'profile').filter(
            activity_type='bounty_abandonment_warning',
        )

    def escalated_for_removal(self):
        """Filter results to Activity objects to be reviewed by moderators."""
        return self.select_related('bounty', 'profile').filter(
            activity_type='bounty_abandonment_escalation_to_mods',
        )


class Activity(SuperModel):
    """Represent Start work/Stop work event.

    Attributes:
        ACTIVITY_TYPES (list of tuples): The valid activity types.

    """

    ACTIVITY_TYPES = [
        ('new_bounty', 'New Bounty'),
        ('start_work', 'Work Started'),
        ('stop_work', 'Work Stopped'),
        ('work_submitted', 'Work Submitted'),
        ('work_done', 'Work Done'),
        ('worker_approved', 'Worker Approved'),
        ('worker_rejected', 'Worker Rejected'),
        ('worker_applied', 'Worker Applied'),
        ('increased_bounty', 'Increased Funding'),
        ('killed_bounty', 'Canceled Bounty'),
        ('new_tip', 'New Tip'),
        ('receive_tip', 'Tip Received'),
        ('bounty_abandonment_escalation_to_mods', 'Escalated for Abandonment of Bounty'),
        ('bounty_abandonment_warning', 'Warning for Abandonment of Bounty'),
        ('bounty_removed_slashed_by_staff', 'Dinged and Removed from Bounty by Staff'),
        ('bounty_removed_by_staff', 'Removed from Bounty by Staff'),
        ('bounty_removed_by_funder', 'Removed from Bounty by Funder'),
        ('new_crowdfund', 'New Crowdfund Contribution'),
        # Grants
        ('new_grant', 'New Grant'),
        ('update_grant', 'Updated Grant'),
        ('killed_grant', 'Cancelled Grant'),
        ('new_grant_contribution', 'Contributed to Grant'),
        ('new_grant_subscription', 'Subscribed to Grant'),
        ('killed_grant_contribution', 'Cancelled Grant Contribution'),
        ('new_milestone', 'New Milestone'),
        ('update_milestone', 'Updated Milestone'),
        ('new_kudos', 'New Kudos'),
        ('joined', 'Joined Gitcoin'),
        ('updated_avatar', 'Updated Avatar'),
    ]

    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='activities',
        on_delete=models.CASCADE
    )
    bounty = models.ForeignKey(
        'dashboard.Bounty',
        related_name='activities',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    tip = models.ForeignKey(
        'dashboard.Tip',
        related_name='activities',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    kudos = models.ForeignKey(
        'kudos.KudosTransfer',
        related_name='activities',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='activities',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    subscription = models.ForeignKey(
        'grants.Subscription',
        related_name='activities',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_index=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, blank=True, db_index=True)
    metadata = JSONField(default=dict)
    needs_review = models.BooleanField(default=False)

    # Activity QuerySet Manager
    objects = ActivityQuerySet.as_manager()

    def __str__(self):
        """Define the string representation of an interested profile."""
        return f"{self.profile.handle} type: {self.activity_type} created: {naturalday(self.created)} " \
               f"needs review: {self.needs_review}"


    @property
    def humanized_activity_type(self):
        """Turn snake_case into Snake Case.

        Returns:
            str: The humanized nameactivity_type
        """
        for activity_type in self.ACTIVITY_TYPES:
            if activity_type[0] == self.activity_type:
                return activity_type[1]
        return ' '.join([x.capitalize() for x in self.activity_type.split('_')])


    def i18n_name(self):
        return _(next((x[1] for x in self.ACTIVITY_TYPES if x[0] == self.activity_type), 'Unknown type'))

    @property
    def view_props(self):
        from dashboard.tokens import token_by_name
        from kudos.models import Token
        icons = {
            'new_tip': 'fa-thumbs-up',
            'start_work': 'fa-lightbulb',
            'new_bounty': 'fa-money-bill-alt',
            'work_done': 'fa-check-circle',
            'new_kudos': 'fa-thumbs-up',
            'new_grant': 'fa-envelope',
            'update_grant': 'fa-edit',
            'killed_grant': 'fa-trash',
            'new_grant_contribution': 'fa-coins',
            'new_grant_subscription': 'fa-calendar-check',
            'killed_grant_contribution': 'fa-calendar-times',
        }

        # load up this data package with all of the information in the already existing objects
        properties = [
            'i18n_name'
            'title',
            'token_name',
            'created_human_time',
            'humanized_name',
            'url',
        ]
        activity = self.to_standard_dict(properties=properties)
        for key, value in model_to_dict(self).items():
            activity[key] = value
        for fk in ['bounty', 'tip', 'kudos', 'profile']:
            if getattr(self, fk):
                activity[fk] = getattr(self, fk).to_standard_dict(properties=properties)
        print(activity['kudos'])
        # KO notes 2019/01/30
        # this is a bunch of bespoke information that is computed for the views
        # in a later release, it couild be refactored such that its just contained in the above code block ^^.
        activity['icon'] = icons.get(self.activity_type, 'fa-check-circle')
        if activity.get('kudos'):
            activity['kudos_data'] = Token.objects.get(pk=self.kudos.kudos_token_cloned_from_id)
        obj = self.metadata
        if 'new_bounty' in self.metadata:
            obj = self.metadata['new_bounty']
        activity['title'] = obj.get('title', '')
        if 'id' in obj:
            if 'category' not in obj or obj['category'] == 'bounty': # backwards-compatible for category-lacking metadata
                activity['bounty_url'] = Bounty.objects.get(pk=obj['id']).get_relative_url()
                if activity.get('title'):
                    activity['urled_title'] = f'<a href="{activity["bounty_url"]}">{activity["title"]}</a>'
                else:
                    activity['urled_title'] = activity.get('title')
            activity['humanized_activity_type'] = self.humanized_activity_type
        if 'value_in_usdt_now' in obj:
            activity['value_in_usdt_now'] = obj['value_in_usdt_now']
        if 'token_name' in obj:
            activity['token'] = token_by_name(obj['token_name'])
            if 'value_in_token' in obj and activity['token']:
                activity['value_in_token_disp'] = round((float(obj['value_in_token']) /
                                                      10 ** activity['token']['decimals']) * 1000) / 1000

        # finally done!

        return activity

    @property
    def token_name(self):
        if self.bounty:
            return self.bounty.token_name
        if 'token_name' in self.metadata.keys():
            return self.metadata['token_name']
        return None

    def to_dict(self, fields=None, exclude=None):
        """Define the standard to dict representation of the object.

        Args:
            fields (list): The list of fields to include. If not provided,
                include all fields. If not provided, all fields are included.
                Defaults to: None.
            exclude (list): The list of fields to exclude. If not provided,
                no fields are excluded. Default to: None.

        Returns:
            dict: The dictionary representation of the object.

        """
        kwargs = {}
        if fields:
            kwargs['fields'] = fields
        if exclude:
            kwargs['exclude'] = exclude
        return model_to_dict(self, **kwargs)


class LabsResearch(SuperModel):
    """Define the structure of Labs Research object."""

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    link = models.URLField(null=True)
    image = models.ImageField(upload_to='labs', blank=True, null=True)
    upcoming = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class UserVerificationModel(SuperModel):
    """Define the checkboxes for user verification."""

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    verified = models.BooleanField(
        default=False,
        help_text='Select to display the Verified checkmark on the user\'s profile',
    )
    speedy_and_responsive = models.BooleanField(
        default=False,
    )
    great_communication = models.BooleanField(
        default=False,
    )
    bug_free_code = models.BooleanField(
        default=False,
    )
    completed_x_bounties = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f"User: {self.user}; Verified: {self.verified}"


class BountyInvites(SuperModel):
    """Define the structure of bounty invites."""

    INVITE_STATUS = [
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('completed', 'completed'),
    ]

    bounty = models.ManyToManyField('dashboard.Bounty', related_name='bountyinvites', blank=True)
    inviter = models.ManyToManyField(User, related_name='inviter', blank=True)
    invitee = models.ManyToManyField(User, related_name='invitee', blank=True)
    status = models.CharField(max_length=20, choices=INVITE_STATUS, blank=True)

    def __str__(self):
        return f"Inviter: {self.inviter}; Invitee: {self.invitee}; Bounty: {self.bounty}"

    @property
    def get_bounty_invite_url(self):
        """Returns a unique url for each bounty and one who is inviting

        Returns:
            A unique string for each bounty
        """
        salt = "X96gRAVvwx52uS6w4QYCUHRfR3OaoB"
        string = self.inviter.username + salt + self.bounty
        return base64.urlsafe_b64encode(string.encode()).decode()


class ProfileQuerySet(models.QuerySet):
    """Define the Profile QuerySet to be used as the objects manager."""

    def visible(self):
        """Filter results to only visible profiles."""
        return self.filter(hide_profile=False)

    def hidden(self):
        """Filter results to only hidden profiles."""
        return self.filter(hide_profile=True)


class Profile(SuperModel):
    """Define the structure of the user profile.

    TODO:
        * Remove all duplicate identity related information already stored on User.

    """

    JOB_SEARCH_STATUS = [
        ('AL', 'Actively looking for work'),
        ('PL', 'Passively looking and open to hearing new opportunities'),
        ('N', 'Not open to hearing new opportunities'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = JSONField()
    handle = models.CharField(max_length=255, db_index=True, unique=True)
    last_sync_date = models.DateTimeField(null=True)
    email = models.CharField(max_length=255, blank=True, db_index=True)
    github_access_token = models.CharField(max_length=255, blank=True, db_index=True)
    pref_lang_code = models.CharField(max_length=2, choices=settings.LANGUAGES, blank=True)
    slack_repos = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    slack_token = models.CharField(max_length=255, default='', blank=True)
    custom_tagline = models.CharField(max_length=255, default='', blank=True)
    slack_channel = models.CharField(max_length=255, default='', blank=True)
    discord_repos = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    discord_webhook_url = models.CharField(max_length=400, default='', blank=True)
    suppress_leaderboard = models.BooleanField(
        default=False,
        help_text='If this option is chosen, we will remove your profile information from the leaderboard',
    )
    hide_profile = models.BooleanField(
        default=True,
        help_text='If this option is chosen, we will remove your profile information all_together',
    )
    trust_profile = models.BooleanField(
        default=False,
        help_text='If this option is chosen, the user is able to submit a faucet/ens domain registration even if they are new to github',
    )
    keywords = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    organizations = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    form_submission_records = JSONField(default=list, blank=True)
    max_num_issues_start_work = models.IntegerField(default=3)
    preferred_payout_address = models.CharField(max_length=255, default='', blank=True)
    preferred_kudos_wallet = models.OneToOneField('kudos.Wallet', related_name='preferred_kudos_wallet', on_delete=models.SET_NULL, null=True, blank=True)
    max_tip_amount_usdt_per_tx = models.DecimalField(default=2500, decimal_places=2, max_digits=50)
    max_tip_amount_usdt_per_week = models.DecimalField(default=20000, decimal_places=2, max_digits=50)
    last_visit = models.DateTimeField(null=True, blank=True)
    job_search_status = models.CharField(max_length=2, choices=JOB_SEARCH_STATUS, blank=True)
    show_job_status = models.BooleanField(
        default=False,
        help_text='If this option is chosen, we will not show job search status',
    )
    job_type = models.CharField(max_length=255, default='', blank=True)
    remote = models.BooleanField(
        default=False,
        help_text='If this option is chosen, profile is okay with remote job',
    )
    job_salary = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    job_location = JSONField(default=dict, blank=True)
    linkedin_url = models.CharField(max_length=255, default='', blank=True, null=True)
    resume = models.FileField(upload_to=get_upload_filename, null=True, blank=True, help_text=_('The profile resume.'))
    profile_wallpaper = models.CharField(max_length=255, default='', blank=True, null=True)
    actions_count = models.IntegerField(default=3)
    fee_percentage = models.IntegerField(default=10)
    persona_is_funder = models.BooleanField(default=False)
    persona_is_hunter = models.BooleanField(default=False)
    admin_override_name = models.CharField(max_length=255, blank=True, help_text=_('override profile name.'))
    admin_override_avatar = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('override profile avatar'),
    )

    objects = ProfileQuerySet.as_manager()

    @property
    def get_my_tips(self):
        return Tip.objects.filter(username__iexact=self.handle)

    @property
    def get_sent_tips(self):
        return Tip.objects.filter(from_username__iexact=self.handle)

    @property
    def get_my_bounties(self):
        return self.bounties

    @property
    def get_sent_bounties(self):
        return Bounty.objects.current().filter(bounty_owner_github_username__iexact=self.handle)

    @property
    def get_my_grants(self):
        from grants.models import Grant
        return Grant.objects.filter(Q(admin_profile=self) | Q(team_members__in=[self]) | Q(subscriptions__contributor_profile=self))

    @property
    def get_my_kudos(self):
        from kudos.models import KudosTransfer
        kt_owner_address = KudosTransfer.objects.filter(
            receive_address__iexact=self.preferred_payout_address
        )
        if not self.preferred_payout_address:
            kt_owner_address = KudosTransfer.objects.none()

        kt_profile = KudosTransfer.objects.filter(recipient_profile=self)

        kudos_transfers = kt_profile | kt_owner_address
        kudos_transfers = kudos_transfers.filter(
            kudos_token_cloned_from__contract__network=settings.KUDOS_NETWORK
        )
        kudos_transfers = kudos_transfers.send_success() | kudos_transfers.send_pending()

        # remove this line IFF we ever move to showing multiple kudos transfers on a profile
        kudos_transfers = kudos_transfers.distinct('id')

        return kudos_transfers

    @property
    def get_sent_kudos(self):
        from kudos.models import KudosTransfer
        kt_address = KudosTransfer.objects.filter(
            from_address__iexact=self.preferred_payout_address
        )
        kt_sender_profile = KudosTransfer.objects.filter(sender_profile=self)

        kudos_transfers = kt_address | kt_sender_profile
        kudos_transfers = kudos_transfers.send_success() | kudos_transfers.send_pending()
        kudos_transfers = kudos_transfers.filter(
            kudos_token_cloned_from__contract__network=settings.KUDOS_NETWORK
        )

        # remove this line IFF we ever move to showing multiple kudos transfers on a profile
        kudos_transfers = kudos_transfers.distinct('id')

        return kudos_transfers

    @property
    def get_num_actions(self):
        num = 0
        num += self.get_sent_kudos.count()
        num += self.get_my_kudos.count()
        num += self.get_my_tips.count()
        num += self.get_sent_tips.count()
        num += self.get_my_grants.count()
        return num

    @property
    def get_average_star_rating(self):
        """Returns the average star ratings (overall and individual topic)
        for a particular user"""

        feedbacks = FeedbackEntry.objects.filter(receiver_profile=self).all()
        average_rating = {}
        average_rating['overall'] = sum([feedback.rating for feedback in feedbacks]) \
            / feedbacks.count() if feedbacks.count() != 0 else 0
        average_rating['code_quality_rating'] = sum([feedback.code_quality_rating for feedback in feedbacks]) \
            / feedbacks.count() if feedbacks.count() != 0 else 0
        average_rating['communication_rating'] = sum([feedback.communication_rating for feedback in feedbacks]) \
            / feedbacks.count() if feedbacks.count() != 0 else 0
        average_rating['recommendation_rating'] = sum([feedback.recommendation_rating for feedback in feedbacks]) \
            / feedbacks.count() if feedbacks.count() != 0 else 0
        average_rating['satisfaction_rating'] = sum([feedback.satisfaction_rating for feedback in feedbacks]) \
            / feedbacks.count() if feedbacks.count() != 0 else 0
        average_rating['speed_rating'] = sum([feedback.speed_rating for feedback in feedbacks]) \
            / feedbacks.count() if feedbacks.count() != 0 else 0
        average_rating['total_rating'] = feedbacks.count()
        return average_rating


    @property
    def get_my_verified_check(self):
        verification = UserVerificationModel.objects.filter(user=self.user).first()
        return verification

    @property
    def get_profile_referral_code(self):
        return base64.urlsafe_b64encode(self.handle.encode()).decode()

    @property
    def job_status_verbose(self):
        return dict(Profile.JOB_SEARCH_STATUS)[self.job_search_status]

    @property
    def active_bounties(self):
        active_bounties = Bounty.objects.current().filter(idx_status__in=['open', 'started'])
        return Interest.objects.filter(profile_id=self.pk, bounty__in=active_bounties)

    @property
    def is_org(self):
        try:
            return self.data['type'] == 'Organization'
        except KeyError:
            return False

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

    def calculate_and_save_persona(self):
        network = settings.ENABLE_NOTIFICATIONS_ON_NETWORK
        designation = None
        with connection.cursor() as cursor:
            try:
                cursor.execute(PERSONA_SQL, [network, self.id, network])
                result = cursor.fetchone()
                _, _, designation, _, _ = result
            except Exception as e:
                logger.info(
                    'Exception calculating persona for user %s: %s' % (self.id,
                                                                       e))

        if designation and designation == "bounty_hunter":
            self.persona_is_hunter = True

        if designation and designation == "funder":
            self.persona_is_funder = True

        self.save()

    def has_custom_avatar(self):
        from avatar.models import CustomAvatar
        return CustomAvatar.objects.filter(active=True, profile=self).exists()

    def build_random_avatar(self):
        from avatar.utils import build_random_avatar
        from avatar.models import CustomAvatar
        purple = '8A2BE2'
        payload = build_random_avatar(purple, '000000', False)
        try:
            custom_avatar = CustomAvatar.create(self, payload)
            custom_avatar.autogenerated = True
            custom_avatar.save()
            self.activate_avatar(custom_avatar.pk)
            self.save()
            return custom_avatar
        except Exception as e:
            logger.warning('Save Random Avatar - Error: (%s) - Handle: (%s)', e, self.handle)

    def no_times_slashed_by_staff(self):
        user_actions = UserAction.objects.filter(
            profile=self,
            action='bounty_removed_slashed_by_staff',
            )
        return user_actions.count()

    def no_times_been_removed_by_funder(self):
        user_actions = UserAction.objects.filter(
            profile=self,
            action='bounty_removed_by_funder',
            )
        return user_actions.count()

    def no_times_been_removed_by_staff(self):
        user_actions = UserAction.objects.filter(
            profile=self,
            action='bounty_removed_by_staff',
            )
        return user_actions.count()

    def get_desc(self, funded_bounties, fulfilled_bounties):
        total_funded = funded_bounties.aggregate(Sum('value_in_usdt'))['value_in_usdt__sum'] or 0
        total_fulfilled = fulfilled_bounties.aggregate(Sum('value_in_usdt'))['value_in_usdt__sum'] or 0

        role = 'newbie'
        if total_funded > total_fulfilled:
            role = 'funder'
        elif total_funded < total_fulfilled:
            role = 'coder'

        total_funded_participated = funded_bounties.count() + fulfilled_bounties.count()
        plural = 's' if total_funded_participated != 1 else ''

        return f"@{self.handle} is a {role} who has participated in {total_funded_participated} " \
               f"funded issue{plural} on Gitcoin"

    @property
    def desc(self):
        return self.get_desc(self.get_funded_bounties(), self.get_fulfilled_bounties())

    @property
    def github_created_on(self):
        created_at = self.data.get('created_at', '')

        if not created_at:
            return ''

        created_on = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
        return created_on.replace(tzinfo=pytz.UTC)

    @property
    def repos_data_lite(self):
        from git.utils import get_user
        # TODO: maybe rewrite this so it doesnt have to go to the internet to get the info
        # but in a way that is respectful of db size too
        return get_user(self.handle, '/repos')

    @property
    def repos_data(self):
        from app.utils import add_contributors
        repos_data = self.repos_data_lite
        repos_data = sorted(repos_data, key=lambda repo: repo['stargazers_count'], reverse=True)
        repos_data = [add_contributors(repo_data) for repo_data in repos_data]
        return repos_data

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
    def get_quarterly_stats(self):
        """Generate last 90 days stats for this user.

        Returns:
            dict : containing the following information
            'user_total_earned_eth': Total earnings of user in ETH.
            'user_total_earned_usd': Total earnings of user in USD.
            'user_total_funded_usd': Total value of bounties funded by the user on bounties in done status in USD
            'user_total_funded_hours': Total hours input by the developers on the fulfillment of bounties created by the user in USD
            'user_fulfilled_bounties_count': Total bounties fulfilled by user
            'user_fufilled_bounties': bool, if the user fulfilled bounties
            'user_funded_bounties_count': Total bounties funded by the user
            'user_funded_bounties': bool, if the user funded bounties in the last quarter
            'user_funded_bounty_developers': Unique set of users that fulfilled bounties funded by the user
            'user_avg_hours_per_funded_bounty': Average hours input by developer on fulfillment per bounty
            'user_avg_hourly_rate_per_funded_bounty': Average hourly rate in dollars per bounty funded by user
            'user_avg_eth_earned_per_bounty': Average earning in ETH earned by user per bounty
            'user_avg_usd_earned_per_bounty': Average earning in USD earned by user per bounty
            'user_num_completed_bounties': Total no. of bounties completed.
            'user_num_funded_fulfilled_bounties': Total bounites that were funded by the user and fulfilled
            'user_bounty_completion_percentage': Percentage of bounties successfully completed by the user
            'user_funded_fulfilled_percentage': Percentage of bounties funded by the user that were fulfilled
            'user_active_in_last_quarter': bool, if the user was active in last quarter
            'user_no_of_languages': No of languages user used while working on bounties.
            'user_languages': Languages that were used in bounties that were worked on.
            'relevant_bounties': a list of Bounty(s) that would match the skillset input by the user into the Match tab of their settings
        """
        user_active_in_last_quarter = False
        user_fulfilled_bounties = False
        user_funded_bounties = False
        last_quarter = datetime.now() - timedelta(days=90)
        bounties = self.bounties.filter(created_on__gte=last_quarter, network='mainnet')
        fulfilled_bounties = [
            bounty for bounty in bounties if bounty.is_fulfiller(self.handle) and bounty.status == 'done'
        ]
        fulfilled_bounties_count = len(fulfilled_bounties)
        funded_bounties = self.get_funded_bounties()
        funded_bounties_count = funded_bounties.count()

        if funded_bounties_count:
            total_funded_usd = funded_bounties.has_funds().aggregate(Sum('value_in_usdt'))['value_in_usdt__sum']
            total_funded_hourly_rate = float(0)
            hourly_rate_bounties_counted = float(0)
            for bounty in funded_bounties:
                hourly_rate = bounty.hourly_rate
                if hourly_rate:
                    total_funded_hourly_rate += bounty.hourly_rate
                    hourly_rate_bounties_counted += 1
            funded_bounty_fulfillments = []
            for bounty in funded_bounties:
                fulfillments = bounty.fulfillments.filter(accepted=True)
                for fulfillment in fulfillments:
                    if isinstance(fulfillment, BountyFulfillment):
                        funded_bounty_fulfillments.append(fulfillment)
            funded_bounty_fulfillments_count = len(funded_bounty_fulfillments)

            total_funded_hours = 0
            funded_fulfillments_with_hours_counted = 0
            if funded_bounty_fulfillments_count:
                from decimal import Decimal
                for fulfillment in funded_bounty_fulfillments:
                    if isinstance(fulfillment.fulfiller_hours_worked, Decimal):
                        total_funded_hours += fulfillment.fulfiller_hours_worked
                        funded_fulfillments_with_hours_counted += 1

            user_funded_bounty_developers = []
            for fulfillment in funded_bounty_fulfillments:
                user_funded_bounty_developers.append(fulfillment.fulfiller_github_username.lstrip('@'))
            user_funded_bounty_developers = [*{*user_funded_bounty_developers}]
            if funded_fulfillments_with_hours_counted:
                avg_hourly_rate_per_funded_bounty = \
                    float(total_funded_hourly_rate) / float(funded_fulfillments_with_hours_counted)
                avg_hours_per_funded_bounty = \
                    float(total_funded_hours) / float(funded_fulfillments_with_hours_counted)
            else:
                avg_hourly_rate_per_funded_bounty = 0
                avg_hours_per_funded_bounty = 0
            funded_fulfilled_bounties = [
                bounty for bounty in funded_bounties if bounty.status == 'done'
            ]
            num_funded_fulfilled_bounties = len(funded_fulfilled_bounties)
            funded_fulfilled_percent = float(
                # Round to 0 places of decimals to be displayed in template
                round(num_funded_fulfilled_bounties * 1.0 / funded_bounties_count, 2) * 100
            )
            user_funded_bounties = True
        else:
            num_funded_fulfilled_bounties = 0
            funded_fulfilled_percent = 0
            user_funded_bounties = False
            avg_hourly_rate_per_funded_bounty = 0
            avg_hours_per_funded_bounty = 0
            total_funded_usd = 0
            total_funded_hours = 0
            user_funded_bounty_developers = []

        total_earned_eth = sum([
            bounty.value_in_eth if bounty.value_in_eth else 0
            for bounty in fulfilled_bounties
        ])
        total_earned_eth /= 10**18
        total_earned_usd = sum([
            bounty.value_in_usdt if bounty.value_in_usdt else 0
            for bounty in fulfilled_bounties
        ])

        num_completed_bounties = bounties.filter(idx_status__in=['done']).count()
        terminal_state_bounties = bounties.filter(idx_status__in=Bounty.TERMINAL_STATUSES).count()
        completetion_percent = int(
            round(num_completed_bounties * 1.0 / terminal_state_bounties, 2) * 100
        ) if terminal_state_bounties != 0 else 0

        avg_eth_earned_per_bounty = 0
        avg_usd_earned_per_bounty = 0

        if fulfilled_bounties_count:
            avg_eth_earned_per_bounty = total_earned_eth / fulfilled_bounties_count
            avg_usd_earned_per_bounty = total_earned_usd / fulfilled_bounties_count
            user_fulfilled_bounties = True

        user_languages = []
        for bounty in fulfilled_bounties:
            user_languages += bounty.keywords.split(',')
        user_languages = set(user_languages)
        user_no_of_languages = len(user_languages)

        if num_completed_bounties or fulfilled_bounties_count:
            user_active_in_last_quarter = True
            relevant_bounties = []
        else:
            from marketing.utils import get_or_save_email_subscriber
            user_coding_languages = get_or_save_email_subscriber(self.email, 'internal').keywords
            if user_coding_languages is not None:
                potential_bounties = Bounty.objects.all()
                relevant_bounties = Bounty.objects.none()
                for keyword in user_coding_languages:
                    relevant_bounties = relevant_bounties.union(potential_bounties.current().filter(
                            network=Profile.get_network(),
                            metadata__icontains=keyword,
                            idx_status__in=['open'],
                            ).order_by('?')
                    )
                relevant_bounties = relevant_bounties[:3]
                relevant_bounties = list(relevant_bounties)
        # Round to 2 places of decimals to be diplayed in templates
        completetion_percent = float('%.2f' % completetion_percent)
        funded_fulfilled_percent = float('%.2f' % funded_fulfilled_percent)
        avg_eth_earned_per_bounty = float('%.2f' % avg_eth_earned_per_bounty)
        avg_usd_earned_per_bounty = float('%.2f' % avg_usd_earned_per_bounty)
        avg_hourly_rate_per_funded_bounty = float('%.2f' % avg_hourly_rate_per_funded_bounty)
        avg_hours_per_funded_bounty = float('%.2f' % avg_hours_per_funded_bounty)
        total_earned_eth = float('%.2f' % total_earned_eth)
        total_earned_usd = float('%.2f' % total_earned_usd)

        user_languages = []
        for bounty in fulfilled_bounties:
            user_languages += bounty.keywords.split(',')
        user_languages = set(user_languages)
        user_no_of_languages = len(user_languages)

        return {
            'user_total_earned_eth': total_earned_eth,
            'user_total_earned_usd': total_earned_usd,
            'user_total_funded_usd': total_funded_usd,
            'user_total_funded_hours': total_funded_hours,
            'user_fulfilled_bounties_count': fulfilled_bounties_count,
            'user_fulfilled_bounties': user_fulfilled_bounties,
            'user_funded_bounties_count': funded_bounties_count,
            'user_funded_bounties': user_funded_bounties,
            'user_funded_bounty_developers': user_funded_bounty_developers,
            'user_avg_hours_per_funded_bounty': avg_hours_per_funded_bounty,
            'user_avg_hourly_rate_per_funded_bounty': avg_hourly_rate_per_funded_bounty,
            'user_avg_eth_earned_per_bounty': avg_eth_earned_per_bounty,
            'user_avg_usd_earned_per_bounty': avg_usd_earned_per_bounty,
            'user_num_completed_bounties': num_completed_bounties,
            'user_num_funded_fulfilled_bounties': num_funded_fulfilled_bounties,
            'user_bounty_completion_percentage': completetion_percent,
            'user_funded_fulfilled_percentage': funded_fulfilled_percent,
            'user_active_in_last_quarter': user_active_in_last_quarter,
            'user_no_of_languages': user_no_of_languages,
            'user_languages': user_languages,
            'relevant_bounties': relevant_bounties
        }

    @property
    def active_avatar(self):
        return self.avatar_baseavatar_related.filter(active=True).first()

    @property
    def github_url(self):
        return f"https://github.com/{self.handle}"

    @property
    def avatar_url(self):
        if self.admin_override_avatar:
            return self.admin_override_avatar.url
        if self.active_avatar:
            return self.active_avatar.avatar_url
        return f"{settings.BASE_URL}dynamic/avatar/{self.handle}"

    @property
    def avatar_url_with_gitcoin_logo(self):
        return f"{settings.BASE_URL}dynamic/avatar/{self.handle}/1"

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    @property
    def username(self):
        if getattr(self, 'user', None) and self.user.username:
            return self.user.username

        if self.handle:
            return self.handle

        return None

    @property
    def name(self):
        if self.admin_override_name:
            return self.admin_override_name

        if self.data and self.data["name"]:
            return self.data["name"]

        return self.username


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

    @property
    def url(self):
        return self.get_absolute_url()

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

    @property
    def access_token(self):
        """The Github access token associated with this Profile.

        Returns:
            str: The associated Github access token.

        """
        return self.github_access_token or self.get_access_token(save=False)

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
            repos = ', '.join(self.slack_repos)
            return repos
        return self.slack_repos

    def update_slack_integration(self, token, channel, repos):
        """Update the profile's slack integration settings.

        Args:
            token (str): The profile's slack token.
            channel (str): The profile's slack channel.
            repos (list of str): The profile's github repositories to track.

        """
        repos = repos.split(',')
        self.slack_token = token
        self.slack_repos = [repo.strip() for repo in repos]
        self.slack_channel = channel
        self.save()

    def get_discord_repos(self, join=False):
        """Get the profile's Discord tracked repositories.

        Args:
            join (bool): Whether or not to return a joined string representation.
                Defaults to: False.

        Returns:
            list of str: If joined is False, a list of discord repositories.
            str: If joined is True, a combined string of discord repositories.

        """
        if join:
            repos = ', '.join(self.discord_repos)
            return repos
        return self.discord_repos

    def update_discord_integration(self, webhook_url, repos):
        """Update the profile's Discord integration settings.

        Args:
            webhook_url (str): The profile's Discord webhook url.
            repos (list of str): The profile's github repositories to track.

        """
        repos = repos.split(',')
        self.discord_webhook_url = webhook_url
        self.discord_repos = [repo.strip() for repo in repos]
        self.save()

    @staticmethod
    def get_network():
        return 'mainnet' if not settings.DEBUG else 'rinkeby'

    def get_fulfilled_bounties(self, network=None):
        network = network or self.get_network()
        fulfilled_bounty_ids = self.fulfilled.all().values_list('bounty_id', flat=True)
        bounties = Bounty.objects.current().filter(pk__in=fulfilled_bounty_ids, accepted=True, network=network)
        return bounties

    def get_orgs_bounties(self, network=None):
        network = network or self.get_network()
        url = f"https://github.com/{self.handle}"
        bounties = Bounty.objects.current().filter(network=network, github_url__icontains=url)
        return bounties

    def get_leaderboard_index(self, key='quarterly_earners'):
        try:
            rank = self.leaderboard_ranks.active().filter(leaderboard=key).latest('id')
            return rank.rank
        except LeaderboardRank.DoesNotExist:
            score = 0
        return score

    def get_contributor_leaderboard_index(self):
        return self.get_leaderboard_index()

    def get_funder_leaderboard_index(self):
        return self.get_leaderboard_index('quarterly_payers')

    def get_org_leaderboard_index(self):
        return self.get_leaderboard_index('quarterly_orgs')

    def get_eth_sum(self, sum_type='collected', network='mainnet', bounties=None):
        """Get the sum of collected or funded ETH based on the provided type.

        Args:
            sum_type (str): The sum to lookup.  Defaults to: collected.
            network (str): The network to query results for.
                Defaults to: mainnet.
            bounties (dashboard.models.BountyQuerySet): Override the BountyQuerySet this function processes.
                Defaults to: None.

        Returns:
            float: The total sum of all ETH of the provided type.

        """
        eth_sum = 0
        if bounties is None:
            if sum_type == 'funded':
                bounties = self.get_funded_bounties(network=network)
            elif sum_type == 'collected':
                bounties = self.get_fulfilled_bounties(network=network)
            elif sum_type == 'org':
                bounties = self.get_orgs_bounties(network=network)

        if sum_type == 'funded':
            bounties = bounties.has_funds()

        try:
            if bounties.exists():
                eth_sum = sum([amount for amount in bounties.values_list("value_true", flat=True)])
        except Exception:
            pass

        return eth_sum

    def get_all_tokens_sum(self, sum_type='collected', network='mainnet', bounties=None):
        """Get the sum of collected or funded tokens based on the provided type.

        Args:
            sum_type (str): The sum to lookup.  Defaults to: collected.
            network (str): The network to query results for.
                Defaults to: mainnet.
            bounties (dashboard.models.BountyQuerySet): Override the BountyQuerySet this function processes.
                Defaults to: None.

        Returns:
            query: Grouped query by token_name and sum all token value
        """
        all_tokens_sum = None
        if bounties is None:
            if sum_type == 'funded':
                bounties = self.get_funded_bounties(network=network)
            elif sum_type == 'collected':
                bounties = self.get_fulfilled_bounties(network=network)
            elif sum_type == 'org':
                bounties = self.get_orgs_bounties(network=network)

        if bounties and sum_type == 'funded':
            bounties = bounties.has_funds()

        try:
            if bounties.exists():
                tokens_and_values = bounties.values_list('token_name', 'value_in_token')
                all_tokens_sum_tmp = {token: 0 for token in set([ele[0] for ele in tokens_and_values])}
                for ele in tokens_and_values:
                    all_tokens_sum_tmp[ele[0]] += ele[1] / 10**18
                all_tokens_sum = [{'token_name': token_name, 'value_in_token': value_in_token} for token_name, value_in_token in all_tokens_sum_tmp.items()]

        except Exception:
            pass

        return all_tokens_sum

    def get_who_works_with(self, work_type='collected', network='mainnet', bounties=None):
        """Get an array of profiles that this user works with.

        Args:
            work_type (str): The work type to lookup.  Defaults to: collected.
            network (str): The network to query results for.
                Defaults to: mainnet.
            bounties (dashboard.models.BountyQuerySet): Override the BountyQuerySet this function processes.
                Defaults to: None.

        Returns:
            dict: list of the profiles that were worked with (key) and the number of times they occured

        """
        if bounties is None:
            if work_type == 'funded':
                bounties = self.bounties_funded.filter(network=network)
            elif work_type == 'collected':
                bounties = self.get_fulfilled_bounties(network=network)
            elif work_type == 'org':
                bounties = self.get_orgs_bounties(network=network)

        if work_type != 'org':
            github_urls = bounties.values_list('github_url', flat=True)
            profiles = [org_name(url) for url in github_urls]
            profiles = [ele for ele in profiles if ele]
        else:
            profiles = []
            for bounty in bounties:
                for bf in bounty.fulfillments.filter(accepted=True):
                    if bf.fulfiller_github_username:
                        profiles.append(bf.fulfiller_github_username)

        profiles_dict = {profile: 0 for profile in profiles}
        for profile in profiles:
            profiles_dict[profile] += 1

        ordered_profiles_dict = collections.OrderedDict()
        for ele in sorted(profiles_dict.items(), key=lambda x: x[1], reverse=True):
            ordered_profiles_dict[ele[0]] = ele[1]
        return ordered_profiles_dict

    def get_funded_bounties(self, network='mainnet'):
        """Get the bounties that this user has funded

        Args:
            network (string): the network to look at.
                Defaults to: mainnet.


        Returns:
            queryset: list of bounties

        """

        funded_bounties = Bounty.objects.current().filter(
            Q(bounty_owner_github_username__iexact=self.handle) |
            Q(bounty_owner_github_username__iexact=f'@{self.handle}'),
            network=network,
        )
        return funded_bounties

    def get_various_activities(self):
        """Get bounty, tip and grant related activities for this profile.

        Args:
            network (str): The network to query results for.
                Defaults to: mainnet.

        Returns:
            (dashboard.models.ActivityQuerySet): The query results.

        """

        if not self.is_org:
            all_activities = self.activities
        else:
            # orgs
            url = self.github_url
            all_activities = Activity.objects.filter(
                Q(bounty__github_url__istartswith=url) |
                Q(tip__github_url__istartswith=url)
            )

        return all_activities.all().order_by('-created')

    def activate_avatar(self, avatar_pk):
        self.avatar_baseavatar_related.update(active=False)
        self.avatar_baseavatar_related.filter(pk=avatar_pk).update(active=True)

    def to_dict(self, activities=True, leaderboards=True, network=None, tips=True):
        """Get the dictionary representation with additional data.

        Args:
            activities (bool): Whether or not to include activity queryset data.
                Defaults to: True.
            leaderboards (bool): Whether or not to include leaderboard position data.
                Defaults to: True.
            network (str): The Ethereum network to use for relevant queries.
                Defaults to: None (Environment specific).
            tips (bool): Whether or not to include tip data.
                Defaults to: True.

        Attributes:
            params (dict): The context dictionary to be returned.
            network (str): The bounty network to operate on.
            query_kwargs (dict): The kwargs to be passed to all queries
                throughout the method.
            bounties (dashboard.models.BountyQuerySet): All bounties referencing this profile.
            fulfilled_bounties (dashboard.models.BountyQuerySet): All fulfilled bounties for this profile.
            funded_bounties (dashboard.models.BountyQuerySet): All funded bounties for this profile.
            orgs_bounties (dashboard.models.BountyQuerySet or None):
                All bounties belonging to this organization, if applicable.
            sum_eth_funded (float): The total amount of ETH funded.
            sum_eth_collected (float): The total amount of ETH collected.

        Returns:
            dict: The profile card context.

        """
        params = {}
        network = network or self.get_network()
        query_kwargs = {'network': network}
        bounties = self.bounties
        fulfilled_bounties = self.get_fulfilled_bounties(network=network)
        funded_bounties = self.get_funded_bounties(network=network)
        orgs_bounties = None

        if self.is_org:
            orgs_bounties = self.get_orgs_bounties(network=network)
        sum_eth_funded = self.get_eth_sum(sum_type='funded', bounties=funded_bounties)
        sum_eth_collected = self.get_eth_sum(bounties=fulfilled_bounties)
        works_with_funded = self.get_who_works_with(work_type='funded', bounties=funded_bounties)
        works_with_collected = self.get_who_works_with(work_type='collected', bounties=fulfilled_bounties)

        sum_all_funded_tokens = self.get_all_tokens_sum(sum_type='funded', bounties=funded_bounties, network=network)
        sum_all_collected_tokens = self.get_all_tokens_sum(
            sum_type='collected', bounties=fulfilled_bounties, network=network
        )
        # org only
        count_bounties_on_repo = 0
        sum_eth_on_repos = 0
        works_with_org = []
        if orgs_bounties:
            count_bounties_on_repo = orgs_bounties.count()
            sum_eth_on_repos = self.get_eth_sum(bounties=orgs_bounties)
            works_with_org = self.get_who_works_with(work_type='org', bounties=orgs_bounties)

        total_funded = funded_bounties.count()
        total_fulfilled = fulfilled_bounties.count()
        desc = self.get_desc(funded_bounties, fulfilled_bounties)
        no_times_been_removed = self.no_times_been_removed_by_funder() + self.no_times_been_removed_by_staff() + self.no_times_slashed_by_staff()
        params = {
            'title': f"@{self.handle}",
            'active': 'profile_details',
            'newsletter_headline': _('Be the first to know about new funded issues.'),
            'card_title': f'@{self.handle} | Gitcoin',
            'card_desc': desc,
            'avatar_url': self.avatar_url_with_gitcoin_logo,
            'profile': self,
            'bounties': bounties,
            'count_bounties_completed': total_fulfilled,
            'sum_eth_collected': sum_eth_collected,
            'sum_eth_funded': sum_eth_funded,
            'works_with_collected': works_with_collected,
            'works_with_funded': works_with_funded,
            'funded_bounties_count': total_funded,
            'no_times_been_removed': no_times_been_removed,
            'sum_eth_on_repos': sum_eth_on_repos,
            'works_with_org': works_with_org,
            'count_bounties_on_repo': count_bounties_on_repo,
            'sum_all_funded_tokens': sum_all_funded_tokens,
            'sum_all_collected_tokens': sum_all_collected_tokens
        }

        if activities:
            params['activities'] = self.get_various_activities()

        if tips:
            params['tips'] = self.tips.filter(**query_kwargs).send_happy_path()

        if leaderboards:
            params['scoreboard_position_contributor'] = self.get_contributor_leaderboard_index()
            params['scoreboard_position_funder'] = self.get_funder_leaderboard_index()
            if self.is_org:
                params['scoreboard_position_org'] = self.get_org_leaderboard_index()

        return params

    @property
    def locations(self):
        from app.utils import get_location_from_ip
        locations = []
        for login in self.actions.filter(action='Login'):
            if login.location_data:
                locations.append(login.location_data)
            else:
                location_data = get_location_from_ip(login.ip_address)
                login.location_data = location_data
                login.save()
                locations.append(location_data)
        return locations

    @property
    def is_eu(self):
        from app.utils import get_country_from_ip
        try:
            ip_addresses = list(set(self.actions.filter(action='Login').values_list('ip_address', flat=True)))
            for ip_address in ip_addresses:
                country = get_country_from_ip(ip_address)
                if country.continent.code == 'EU':
                    return True
        except Exception:
            pass
        return False


# enforce casing / formatting rules for profiles
@receiver(pre_save, sender=Profile, dispatch_uid="psave_profile")
def psave_profile(sender, instance, **kwargs):
    instance.handle = instance.handle.replace(' ', '')
    instance.handle = instance.handle.replace('@', '')
    instance.handle = instance.handle.lower()
    instance.actions_count = instance.get_num_actions


@receiver(user_logged_in)
def post_login(sender, request, user, **kwargs):
    """Handle actions to take on user login."""
    from dashboard.utils import create_user_action
    profile = getattr(user, 'profile', None)
    if profile and not profile.github_access_token:
        profile.github_access_token = profile.get_access_token()
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
            'keywords': instance.keywords,
            'url': instance.get_relative_url(),
            'position': instance.get_contributor_leaderboard_index(),
            'organizations': instance.get_who_works_with(network=None),
            'total_earned': instance.get_eth_sum(network=None)
        }


@receiver(pre_save, sender=Tip, dispatch_uid="normalize_tip_usernames")
def normalize_tip_usernames(sender, instance, **kwargs):
    """Handle pre-save signals from Tips to normalize Github usernames."""
    if instance.username:
        instance.username = instance.username.replace("@", '')


m2m_changed.connect(m2m_changed_interested, sender=Bounty.interested.through)


class UserAction(SuperModel):
    """Records Actions that a user has taken ."""

    ACTION_TYPES = [
        ('Login', 'Login'),
        ('Logout', 'Logout'),
        ('Visit', 'Visit'),
        ('added_slack_integration', 'Added Slack Integration'),
        ('removed_slack_integration', 'Removed Slack Integration'),
        ('updated_avatar', 'Updated Avatar'),
        ('account_disconnected', 'Account Disconnected'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    user = models.ForeignKey(User, related_name='actions', on_delete=models.SET_NULL, null=True, db_index=True)
    profile = models.ForeignKey('dashboard.Profile', related_name='actions', on_delete=models.CASCADE, null=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True)
    location_data = JSONField(default=dict)
    metadata = JSONField(default=dict)
    utm = JSONField(default=dict, null=True)

    class Meta:
        """Define metadata associated with UserAction."""

        index_together = [
            ["profile", "action"],
        ]

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
    GAS_TOOLS = "TO"
    CAT_RETIRED = "CR"

    TOOL_CATEGORIES = (
        (CAT_ADVANCED, 'advanced'),
        (GAS_TOOLS, 'gas'),
        (CAT_ALPHA, 'alpha'),
        (CAT_BASIC, 'basic'),
        (CAT_BUILD, 'tools to build'),
        (CAT_COMING_SOON, 'coming soon'),
        (CAT_COMMUNITY, 'community'),
        (CAT_FOR_FUN, 'just for fun'),
        (CAT_RETIRED, 'retired'),
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


class ToolVote(SuperModel):
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


class TokenApproval(SuperModel):
    """A token approval."""

    profile = models.ForeignKey('dashboard.Profile', related_name='token_approvals', on_delete=models.CASCADE)
    coinbase = models.CharField(max_length=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    approved_address = models.CharField(max_length=50)
    approved_name = models.CharField(max_length=50)
    tx = models.CharField(max_length=255, default='')
    network = models.CharField(max_length=255, default='')

    def __str__(self):
        return f"{self.coinbase} | {self.token_name} | {self.profile}"

    @property
    def coinbase_short(self):
        coinbase_short = f"{self.coinbase[0:5]}...{self.coinbase[-4:]}"
        return coinbase_short


class SearchHistory(SuperModel):
    """Define the structure of a Search History object."""

    class Meta:
        """Define metadata associated with SearchHistory."""

        verbose_name_plural = 'Search History'

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = JSONField(default=dict)
    ip_address = models.GenericIPAddressField(blank=True, null=True)


class BlockedUser(SuperModel):
    """Define the structure of the BlockedUser."""

    handle = models.CharField(max_length=255, db_index=True, unique=True)
    comments = models.TextField(default='', blank=True)
    active = models.BooleanField(help_text=_('Is the block active?'))
    user = models.OneToOneField(User, related_name='blocked', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        """Return the string representation of a Bounty."""
        return f'<BlockedUser: {self.handle}>'


class Sponsor(SuperModel):
    """Defines the Hackthon Sponsor"""

    name = models.CharField(max_length=255, help_text='sponsor Name')
    logo = models.ImageField(help_text='sponsor logo', blank=True)
    logo_svg = models.FileField(help_text='sponsor logo svg', blank=True)

    def __str__(self):
        return self.name


class HackathonEvent(SuperModel):
    """Defines the HackathonEvent model."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    logo = models.ImageField(blank=True)
    logo_svg = models.FileField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    background_color = models.CharField(max_length=255, null=True, blank=True, help_text='hexcode for the banner')
    identifier = models.CharField(max_length=255, default='', help_text='used for custom styling for the banner')
    sponsors = models.ManyToManyField(Sponsor, through='HackathonSponsor')

    def __str__(self):
        """String representation for HackathonEvent.

        Returns:
            str: The string representation of a HackathonEvent.
        """
        return f'{self.name} - {self.start_date}'

    def save(self, *args, **kwargs):
        """Define custom handling for saving HackathonEvent."""
        from django.utils.text import slugify
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class HackathonSponsor(SuperModel):
    SPONSOR_TYPES = [
        ('G', 'Gold'),
        ('S', 'Silver'),
    ]
    hackathon = models.ForeignKey('HackathonEvent', default=1, on_delete=models.CASCADE)
    sponsor = models.ForeignKey('Sponsor', default=1, on_delete=models.CASCADE)
    sponsor_type = models.CharField(
        max_length=1,
        choices=SPONSOR_TYPES,
        default='G',
    )

class FeedbackEntry(SuperModel):
    bounty = models.ForeignKey(
        'dashboard.Bounty',
        related_name='feedbacks',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    sender_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='feedbacks_sent',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    receiver_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='feedbacks_got',
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    rating = models.SmallIntegerField(blank=True, default=0)
    satisfaction_rating = models.SmallIntegerField(blank=True, default=0)
    communication_rating = models.SmallIntegerField(blank=True, default=0)
    speed_rating = models.SmallIntegerField(blank=True, default=0)
    code_quality_rating = models.SmallIntegerField(blank=True, default=0)
    recommendation_rating = models.SmallIntegerField(blank=True, default=0)
    comment = models.TextField(default='', blank=True)
    feedbackType = models.TextField(default='', blank=True, max_length=20)

    def __str__(self):
        """Return the string representation of a Bounty."""
        return f'<Feedback Bounty #{self.bounty} - from: {self.sender_profile} to: {self.receiver_profile}>'


class Coupon(SuperModel):
    code = models.CharField(unique=True, max_length=10)
    fee_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    expiry_date = models.DateField()

    def __str__(self):
        """Return the string representation of Coupon."""
        return f'code: {self.code} | fee: {self.fee_percentage} %'
