# -*- coding: utf-8 -*-
'''
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

'''
from __future__ import unicode_literals

import base64
import collections
import json
import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from functools import reduce
from logging import error
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import connection, models
from django.db.models import Count, F, Q, Subquery, Sum
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.template.defaultfilters import date, floatformat, truncatechars
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

import pytz
import requests
from app.settings import HYPERCHARGE_BOUNTIES_PROFILE_HANDLE
from app.utils import get_upload_filename, timeout
from avatar.models import SocialAvatar
from avatar.utils import get_user_github_avatar_image
from bounty_requests.models import BountyRequest
from bs4 import BeautifulSoup
from dashboard.idena_utils import get_idena_status
from dashboard.tokens import addr_to_token, token_by_name
from economy.models import ConversionRate, SuperModel, get_0_time
from economy.utils import ConversionRateNotFoundError, convert_amount, convert_token_to_usdt
from git.utils import get_issue_comments, get_issue_details, issue_number, org_name, repo_name
from marketing.mails import fund_request_email, start_work_approved
from marketing.models import EmailSupressionList, LeaderboardRank
from rest_framework import serializers
from townsquare.models import PinnedPost
from unidecode import unidecode
from web3 import Web3

from .notifications import maybe_market_to_github, maybe_market_to_slack, maybe_market_to_user_slack
from .signals import m2m_changed_interested

logger = logging.getLogger(__name__)


CROSS_CHAIN_STANDARD_BOUNTIES_OFFSET = 100000000


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

    def has_applicant(self):
        """Filter results by bounties that have applicants."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type='worker_applied',
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
        ('public', 'public')
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
        ('reserved', 'reserved'),
        ('open', 'open'),
        ('started', 'started'),
        ('submitted', 'submitted'),
        ('unknown', 'unknown'),
    )

    BOUNTY_STATES = (
        ('open', 'Open Bounty'),
        ('work_started', 'Work Started'),
        ('work_submitted', 'Work Submitted'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    )

    FUNDED_STATUSES = ['reserved', 'open', 'started', 'submitted', 'done']
    OPEN_STATUSES = ['reserved', 'open', 'started', 'submitted']
    CLOSED_STATUSES = ['expired', 'unknown', 'cancelled', 'done']
    WORK_IN_PROGRESS_STATUSES = ['reserved', 'open', 'started', 'submitted']
    TERMINAL_STATUSES = ['done', 'expired', 'cancelled']

    WEB3_TYPES = (
        ('legacy_gitcoin', 'Legacy Bounty'),
        ('bounties_network', 'Bounties Network'),
        ('qr', 'QR Code'),
        ('web3_modal', 'Web3 Modal'),
        ('polkadot_ext', 'Polkadot Ext'),
        ('binance_ext', 'Binance Ext'),
        ('harmony_ext', 'Harmony Ext'),
        ('rsk_ext', 'RSK Ext'),
        ('xinfin_ext', 'Xinfin Ext'),
        ('nervos_ext', 'Nervos Ext'),
        ('algorand_ext', 'Algorand Ext'),
        ('sia_ext', 'Sia Ext'),
        ('tezos_ext', 'Tezos Ext'),
        ('casper_ext', 'Casper Ext'),
        ('fiat', 'Fiat'),
        ('manual', 'Manual')
    )

    bounty_state = models.CharField(max_length=50, choices=BOUNTY_STATES, default='open', db_index=True)
    web3_type = models.CharField(max_length=50, choices=WEB3_TYPES, default='bounties_network')
    title = models.CharField(max_length=1000)
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
    bounty_owner_address = models.CharField(max_length=100, blank=True, null=True)
    bounty_owner_email = models.CharField(max_length=255, blank=True)
    bounty_owner_github_username = models.CharField(max_length=255, blank=True, db_index=True)
    bounty_owner_name = models.CharField(max_length=255, blank=True)
    bounty_owner_profile = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.SET_NULL, related_name='bounties_funded', blank=True
    )
    bounty_reserved_for_user = models.ForeignKey(
        'dashboard.Profile', null=True, on_delete=models.SET_NULL, related_name='reserved_bounties', blank=True
    )
    reserved_for_user_from = models.DateTimeField(blank=True, null=True)
    reserved_for_user_expiration = models.DateTimeField(blank=True, null=True)
    is_open = models.BooleanField(help_text=_('Whether the bounty is still open for fulfillments.'))
    expires_date = models.DateTimeField()
    raw_data = JSONField(blank=True)
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
    bounty_categories = ArrayField(models.CharField(max_length=50, choices=BOUNTY_CATEGORIES), default=list, blank=True)
    repo_type = models.CharField(max_length=10, choices=REPO_TYPES, default='public')
    snooze_warnings_for_days = models.IntegerField(default=0)
    is_featured = models.BooleanField(
        default=False, help_text=_('Whether this bounty is featured'))
    featuring_date = models.DateTimeField(blank=True, null=True, db_index=True)
    last_remarketed = models.DateTimeField(blank=True, null=True, db_index=True)
    remarketed_count = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    fee_amount = models.DecimalField(default=0, decimal_places=18, max_digits=50)
    fee_tx_id = models.CharField(default="0x0", max_length=255, blank=True)
    coupon_code = models.ForeignKey('dashboard.Coupon', blank=True, null=True, related_name='coupon', on_delete=models.SET_NULL)

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
    chat_channel_id = models.CharField(max_length=255, blank=True, null=True)
    event = models.ForeignKey('dashboard.HackathonEvent', related_name='bounties', null=True, on_delete=models.SET_NULL, blank=True)
    hypercharge_mode = models.BooleanField(
        default=False, help_text=_('This bounty will be part of the hypercharged bounties')
    )
    hyper_next_publication = models.DateTimeField(null=True, blank=True)

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

    EVENT_HANDLERS = {
        'traditional': {
            'open': {
                'accept_worker': 'work_started',
                'cancel_bounty': 'cancelled'},
            'work_started': {
                'submit_work': 'work_submitted',
                'stop_work': 'open_bounty',
                'cancel_bounty': 'cancelled'},
            'work_submitted': {
                'payout_bounty': 'done',
                'cancel_bounty': 'cancelled'},
        },
        'cooperative': {
            'open': {
                'accept_worker': 'work_started',
                'cancel_bounty': 'cancelled'},
            'work_started': {
                'submit_work': 'work_submitted',
                'stop_work': 'open_bounty',
                'cancel_bounty': 'cancelled'},
            'work_submitted': {
                'close_bounty': 'done',
                'cancel_bounty': 'cancelled'},
        },
        'contest': {
            'open': {
                'payout_bounty': 'done',
                'cancel_bounty': 'cancelled'}
        }
    }


    def handle_event(self, event):
        """Handle a new BountyEvent, and potentially change state"""
        next_state = self.EVENT_HANDLERS.get(self.project_type, {}).get(self.bounty_state, {}).get(event.event_type)
        if next_state:
            self.bounty_state = next_state
            self.save()

    @property
    def is_bounties_network(self):
        if self.web3_type == 'bounties_network':
            return True
        return False

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
        if not self.value_in_token:
            return 0
        token = addr_to_token(self.token_address)
        if not token:
            return 0
        decimals = token.get('decimals', 0)
        return float(self.value_in_token) / 10**decimals

    @property
    def no_of_applicants(self):
        return self.interested.count()

    @property
    def has_applicant(self):
        """Filter results by bounties that have applicants."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type='worker_applied',
                activities__needs_review=False,
            )

    @property
    def warned(self):
        """Filter results by bounties that have been warned for inactivity."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type='bounty_abandonment_warning',
                activities__needs_review=True,
            )

    @property
    def escalated(self):
        """Filter results by bounties that have been escalated for review."""
        return self.prefetch_related('activities') \
            .filter(
                activities__activity_type='bounty_abandonment_escalation_to_mods',
                activities__needs_review=True,
            )

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
            title = self.fetch_issue_item('title')
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
    def org_profile(self):
        if not self.org_name:
            return None
        profiles = Profile.objects.filter(handle=self.org_name.lower())
        if profiles.exists():
            return profiles.first()
        return None

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
        return self.interested.filter(pending=pending, profile__handle=handle.lower()).exists()

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
    def fulfillers_handles(self):
        bounty_fulfillers = self.fulfillments.filter(accepted=True).values_list('profile__handle', flat=True)
        tip_fulfillers = self.tips.values_list('username', flat=True)
        return list(bounty_fulfillers) + list(tip_fulfillers)

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
            has_fulfillments = self.fulfillments.filter(payout_status='done').exists()
            has_payments = has_tips or has_fulfillments

            if has_payments and is_traditional_bounty_type and not self.is_open :
                return 'done'
            if not self.is_open:
                if self.accepted:
                    return 'done'
                elif self.past_hard_expiration_date:
                    return 'expired'
                elif has_payments:
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
                elif self.is_reserved:
                    return 'reserved'
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
            return self.value_in_token / 10**18
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
        if self.token_name in ['USDT', 'USDC']:
            return float(self.value_in_token / 10 ** 6)
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
        if self.github_url.lower()[:19] == 'https://github.com/':
            _org_name = org_name(self.github_url)
            _repo_name = repo_name(self.github_url)
            _issue_num = issue_number(self.github_url)
            gh_issue_details = get_issue_details(_org_name, _repo_name, int(_issue_num))

            if gh_issue_details:
                item = gh_issue_details.get(item_type, '')
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
            if comment.user and comment.user.login not in settings.IGNORE_COMMENTS_FROM:
                comment_count += 1
        self.github_comments = comment_count
        if comment_count:
            comment_times = [comment.created_at.strftime('%Y-%m-%dT%H:%M:%SZ') for comment in comments]
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
        for item in ['fulfill', 'increase', 'accept', 'cancel', 'payout', 'advanced_payout', 'invoice', ]:
            urls.update({item: f'/issue/{item}?{params}'})
        return urls

    def is_notification_eligible(self, var_to_check=True):
        """Determine whether or not a notification is eligible for transmission outside of production.

        Returns:
            bool: Whether or not the Bounty is eligible for outbound notifications.

        """

        if self.network != settings.ENABLE_NOTIFICATIONS_ON_NETWORK:
            return False

        if self.network == 'mainnet' and (settings.DEBUG or settings.ENV != 'prod'):
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
                gh_issue_details = get_issue_details(_org_name, _repo_name, int(_issue_num))
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
                profile = Profile.objects.filter(handle=handle.lower()).first()
            except:
                logger.warning(f'reserved_for_user_handle: Unknown handle: ${handle}')

        self.bounty_reserved_for_user = profile

    @property
    def can_remarket(self):
        result = True

        if self.remarketed_count and self.remarketed_count >= 2:
            result = False

        if self.last_remarketed:
            minimum_wait_after_remarketing = self.last_remarketed + timezone.timedelta(minutes=settings.MINUTES_BETWEEN_RE_MARKETING)
            if timezone.now() < minimum_wait_after_remarketing:
                result = False

        if self.interested.count() > 0:
            result = False

        return result

    @property
    def is_reserved(self):
        if self.bounty_reserved_for_user and self.reserved_for_user_from:
            if timezone.now() < self.reserved_for_user_from:
                return False

            if self.reserved_for_user_expiration and timezone.now() > self.reserved_for_user_expiration:
                return False

            return True

    @property
    def total_reserved_length_label(self):
        if self.bounty_reserved_for_user and self.reserved_for_user_from:
            if self.reserved_for_user_expiration is None:
                return 'indefinitely'

            if self.reserved_for_user_from == self.reserved_for_user_expiration:
                return ''

            delta = self.reserved_for_user_expiration - self.reserved_for_user_from
            days = delta.days

            if days > 0:
                if days % 7 == 0:
                    if days == 7:
                        return '1 week'
                    else:
                        weeks = int(days / 7)
                        return f'{weeks} weeks'

                if days == 1:
                    return '1 day'
                else:
                    return f'{days} days'
            else:
                hours = int(int(delta.total_seconds()) / 3600)
                if hours == 1:
                    return '1 hour'
                else:
                    return f'{hours} hours'
        else:
            return ''


@receiver(post_save, sender=Bounty, dispatch_uid="post_bounty")
def post_save_bounty(sender, instance, created, **kwargs):
    final_state = instance.bounty_state in ['done', 'cancelled']
    if not final_state and instance.hypercharge_mode and instance.metadata.get('hyper_tweet_counter', False) is False:
        instance.metadata['hyper_tweet_counter'] = 0

        title = f'Work on "{instance.title}" and receive {floatformat(instance.value_true)} {instance.token_name}'

        # Feature bounty on hackathon/prize explorer
        instance.is_featured = True
        instance.featuring_date = timezone.now()
        instance.hyper_next_publication = timezone.now()

        # Publish and pin on townsquare
        profile = Profile.objects.filter(handle=HYPERCHARGE_BOUNTIES_PROFILE_HANDLE).first()

        utm = f'utm_source=hypercharge-auto-pinned-post&utm_medium=twitter&utm_campaign={instance.title}'
        if profile:
            metadata = {
                    'title': title,
                    'description': truncatechars(instance.issue_description_text, 500),
                    'url': f'{instance.get_absolute_url()}?{utm}',
                    'ask': '#announce'
            }
            activity = Activity.objects.create(profile=profile, activity_type='hypercharge_bounty',
                                               metadata=metadata, bounty=instance)

            PinnedPost.objects.filter(what='everywhere').delete()
            pinned_post = PinnedPost.objects.create(
                what='everywhere', activity=activity, user=profile
            )

        instance.save()

    if not instance.hypercharge_mode and instance.metadata.get('hyper_tweet_counter', False) != False:
        del instance.metadata['hyper_tweet_counter']
        instance.save()


class BountyEvent(SuperModel):
    """An Event taken by a user, which may change the state of a Bounty"""

    EVENT_TYPES = (
        ('accept_worker', 'Accept Worker'),
        ('cancel_bounty', 'Cancel Bounty'),
        ('submit_work', 'Submit Work'),
        ('stop_work', 'Stop Work'),
        ('stop_worker', 'Worker stopped'),
        ('express_interest', 'Express Interest'),
        ('payout_bounty', 'Payout Bounty'),
        ('expire_bounty', 'Expire Bounty'),
        ('extend_expiration', 'Extend Expiration'),
        ('close_bounty', 'Close Bounty'),
        ('worker_paid', 'Worker Paid')
    )

    bounty = models.ForeignKey('dashboard.Bounty', on_delete=models.CASCADE,
        related_name='events')
    created_by = models.ForeignKey('dashboard.Profile',
        on_delete=models.SET_NULL, related_name='events', blank=True, null=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    metadata = JSONField(default=dict, blank=True)


class BountyFulfillment(SuperModel):
    """The structure of a fulfillment on a Bounty."""

    PAYOUT_STATUS = [
        ('expired', 'expired'),
        ('pending', 'pending'),
        ('done', 'done'),
    ]

    PAYOUT_TYPE = [
        ('bounties_network', 'bounties_network'),
        ('qr', 'qr'),
        ('fiat', 'fiat'),
        ('web3_modal', 'web3_modal'),
        ('polkadot_ext', 'polkadot_ext'),
        ('binance_ext', 'binance_ext'),
        ('harmony_ext', 'harmony_ext'),
        ('rsk_ext', 'rsk_ext'),
        ('xinfin_ext', 'xinfin_ext'),
        ('nervos_ext', 'nervos_ext'),
        ('algorand_ext', 'algorand_ext'),
        ('sia_ext', 'sia_ext'),
        ('tezos_ext', 'tezos_ext'),
        ('casper_ext', 'casper_ext'),
        ('manual', 'manual')
    ]

    TENANT = [
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('ETC', 'ETC'),
        ('ZIL', 'ZIL'),
        ('CELO', 'CELO'),
        ('PYPL', 'PYPL'),
        ('POLKADOT', 'POLKADOT'),
        ('BINANCE', 'BINANCE'),
        ('HARMONY', 'HARMONY'),
        ('FILECOIN', 'FILECOIN'),
        ('RSK', 'RSK'),
        ('XINFIN', 'XINFIN'),
        ('NERVOS', 'NERVOS'),
        ('ALGORAND', 'ALGORAND'),
        ('SIA', 'SIA'),
        ('TEZOS', 'TEZOS'),
        ('CASPER', 'CASPER'),
        ('OTHERS', 'OTHERS')
    ]

    bounty = models.ForeignKey(Bounty, related_name='fulfillments', on_delete=models.CASCADE, help_text="the bounty against which the fulfillment is made")

    # TODO: RENAME
    fulfillment_id = models.IntegerField(null=True, blank=True, help_text="bounty's fulfillment number")

    # TODO: RETIRE
    fulfiller_metadata = JSONField(default=dict, blank=True)

    fulfiller_address = models.CharField(max_length=100, null=True, blank=True, help_text="address to which amount is credited")
    funder_address = models.CharField(max_length=100, null=True, blank=True, help_text="address from which amount is deducted")

    # TODO: rename to fulfiller_profile
    profile = models.ForeignKey('dashboard.Profile', related_name='fulfilled', on_delete=models.CASCADE, null=True, help_text="fulfillers's profile")
    funder_profile = models.ForeignKey('dashboard.Profile', null=True, blank=True, on_delete=models.CASCADE, help_text="funder's profile")


    # TODO: rename to hours_worked
    fulfiller_hours_worked = models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=50)
    # TODO: rename to submission_url
    fulfiller_github_url = models.CharField(max_length=255, blank=True, null=True)
    funder_last_notified_on = models.DateTimeField(null=True, blank=True)
    project = models.ForeignKey('dashboard.HackathonProject', blank=True, null=True, on_delete=models.SET_NULL, related_name='submissions')

    accepted = models.BooleanField(default=False, help_text="has the fulfillment been accepted by the funder")
    accepted_on = models.DateTimeField(null=True, blank=True, help_text="date when the fulfillment was accepted by the funder")

    payout_type = models.CharField(max_length=20, null=True, blank=True, choices=PAYOUT_TYPE, help_text="payment type used to make the payment")
    tenant = models.CharField(max_length=10, null=True, blank=True, choices=TENANT, help_text="specific tenant type under the payout_type")

    funder_identifier = models.CharField(max_length=50, null=True, blank=True, help_text="unique funder identifier used by when payout_type is fiat")
    fulfiller_identifier = models.CharField(max_length=50, null=True, blank=True, help_text="unique fulfiller identifier used by when payout_type is fiat")

    token_name = models.CharField(max_length=10, blank=True, help_text="token/currency in which the payout is done")
    payout_tx_id = models.CharField(default="0x0", max_length=255, blank=True, help_text="transaction id")
    payout_status = models.CharField(max_length=10, choices=PAYOUT_STATUS, blank=True, help_text="payment status")
    payout_amount = models.DecimalField(null=True, blank=True, decimal_places=6, max_digits=50, help_text="amount being paid out by funder")

    def __str__(self):
        """Define the string representation of BountyFulfillment.

        Returns:
            str: The string representation of the object.

        """
        return f'BountyFulfillment ID: ({self.pk}) - Bounty ID: ({self.bounty.pk})'

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
        return self.value_in_usdt_at_time(self.created_on)

    # TODO: DRY
    def get_natural_value(self):
        token = token_by_name(self.token_name, self.bounty.network)
        decimals = token['decimals']
        amount = self.payout_amount if self.payout_amount else 0
        return float(amount) / 10**decimals

    @property
    def value_true(self):
        return self.get_natural_value()

    def value_in_usdt_at_time(self, at_time):
        try:
            if self.token_name in ['USDT', 'USDC']:
                return float(self.payout_amount / 10 ** 6)
            if self.token_name in settings.STABLE_COINS:
                return float(self.payout_amount / 10 ** 18)
            if self.token_name in ['ETH']:
                return round(float(convert_amount(self.payout_amount, self.token_name, 'USDT', at_time)), 2)
            try:
                return round(float(convert_amount(self.value_true, self.token_name, 'USDT', at_time)), 2)
            except ConversionRateNotFoundError:
                try:
                    in_eth = round(float(convert_amount(self.value_true, self.token_name, 'ETH', at_time)), 2)
                    return round(float(convert_amount(in_eth, 'USDT', 'USDT', at_time)), 2)
                except ConversionRateNotFoundError:
                    return None
        except:
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
    def fulfiller_email(self):
        if self.profile:
            return self.profile.email
        return None


    @property
    def fulfiller_github_username(self):
        if self.profile:
            return self.profile.handle
        return None


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
            'payout_status': self.payout_status,
            'payout_amount': self.payout_amount,
            'token_name': self.token_name,
            'payout_tx_id': self.payout_tx_id
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


class SendCryptoAssetQuerySet(models.QuerySet):
    """Handle the manager queryset for SendCryptoAsset."""

    def send_success(self):
        """Filter results down to successful sends only."""
        return self.filter(tx_status='success').exclude(txid='')

    def not_submitted(self):
        """Filter results down to not submitted results only."""
        return self.filter(tx_status='not_subed')

    def send_pending(self):
        """Filter results down to pending sends only."""
        return self.filter(Q(tx_status='pending') | Q(txid='pending_celery')).exclude(txid='')

    def send_happy_path(self):
        """Filter results down to pending/success sends only."""
        return self.filter(Q(tx_status__in=['pending', 'success']) | Q(txid='pending_celery')).exclude(txid='')

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
        ('not_subed', 'not_subed'), # not submitted to chain yet
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
        if self.tokenAddress in ['0x0', '0x0000000000000000000000000000000000000000']:
            return self.amount
        token = addr_to_token(self.tokenAddress)
        decimals = token['decimals']
        return float(self.amount) / 10**decimals

    @property
    def value_true(self):
        return self.get_natural_value()

    @property
    def receive_tx_blockexplorer_link(self):
        from dashboard.utils import tx_id_to_block_explorer_url #circular import
        return tx_id_to_block_explorer_url(self.receive_txid, self.network)

    @property
    def send_tx_blockexplorer_link(self):
        from dashboard.utils import tx_id_to_block_explorer_url #circular import
        return tx_id_to_block_explorer_url(self.txid, self.network)

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

    @property
    def org_profile(self):
        if not self.org_name:
            return None
        profiles = Profile.objects.filter(handle=self.org_name.lower())
        if profiles.count():
            return profiles.first()
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
        try:
            from dashboard.utils import get_tx_status
            from economy.tx import getReplacedTX
            self.tx_status, self.tx_time = get_tx_status(self.txid, self.network, self.created_on)

            #handle scenario in which a txn has been replaced
            if self.tx_status in ['pending', 'dropped', 'unknown', '']:
                new_tx = getReplacedTX(self.txid)
                if new_tx:
                    self.txid = new_tx

            return bool(self.tx_status)
        except:
            self.tx_status = 'error'
            return False

    def update_receive_tx_status(self):
        """ Updates the receive tx status according to what infura says about the receive tx

        """
        from dashboard.utils import get_tx_status
        from economy.tx import getReplacedTX
        new_receive_txid = getReplacedTX(self.receive_txid)
        if new_receive_txid:
            self.receive_txid = new_receive_txid
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
    def is_programmatic_comment(self):
        if 'activity:' in self.comments_priv:
            return True
        if 'comment:' in self.comments_priv:
            return True

    @property
    def attached_object(self):
        if not self.comments_priv:
            return None
        if 'activity:' in self.comments_priv:
            pk = self.comments_priv.split(":")[1]
            obj = Activity.objects.get(pk=pk)
            return obj
        if 'comment:' in self.comments_priv:
            pk = self.comments_priv.split(":")[1]
            from townsquare.models import Comment
            obj = Comment.objects.get(pk=pk)
            return obj

    def trigger_townsquare(instance):
        if instance.network == 'mainnet' or settings.DEBUG:
            from townsquare.models import Comment
            network = instance.network if instance.network != 'mainnet' else ''
            if 'activity:' in instance.comments_priv:
                activity=instance.attached_object
                comment = f"Just sent a tip of {instance.amount} {network} ETH to @{instance.username}"
                comment = Comment.objects.create(profile=instance.sender_profile, activity=activity, comment=comment)

            if 'comment:' in instance.comments_priv:
                _comment=instance.attached_object
                _comment.save()
                comment = f"Just sent a tip of {instance.amount} {network} ETH to @{instance.username}"
                comment = Comment.objects.create(profile=instance.sender_profile, activity=_comment.activity, comment=comment)

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


class TipPayout(SuperModel):

    """Model representing redemption of a Kudos
    """
    tip = models.ForeignKey(
        'dashboard.tip', related_name='payouts', on_delete=models.CASCADE
    )
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='tip_payouts', on_delete=models.CASCADE
    )
    txid = models.CharField(max_length=255, default='')

    def __str__(self):
        """Return the string representation of a model."""
        return f"tip: {self.tip.pk} profile: {self.profile.handle}"


class FundRequest(SuperModel):
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='requests_receiver', on_delete=models.CASCADE
    )
    requester = models.ForeignKey(
        'dashboard.Profile', related_name='requests_sender', on_delete=models.CASCADE
    )
    token_name = models.CharField(max_length=255, default='ETH')
    amount = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    comments = models.TextField(default='', blank=True)
    tip = models.OneToOneField(Tip, on_delete=models.CASCADE, null=True, blank=True)
    network = models.CharField(max_length=255, default='')
    address = models.CharField(max_length=255, default='')
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def url(self):
        return settings.BASE_URL + f'tip?request={self.pk}'

    @property
    def other_earnings(self):
        return Earning.objects.filter(Q(from_profile=self.requester, to_profile=self.profile) | Q(from_profile=self.profile, to_profile=self.requester)).filter(network='mainnet').order_by('-created_on')

    def get_absolute_url(self):
        return self.url


@receiver(post_save, sender=FundRequest, dispatch_uid="post_save_fund_request")
def psave_fund_request(sender, instance, created, **kwargs):
    if created:
        fund_request_email(instance, [instance.profile.email])


@receiver(pre_save, sender=Tip, dispatch_uid="psave_tip")
def psave_tip(sender, instance, **kwargs):
    # when a new tip is saved, make sure it doesnt have whitespace in it
    instance.username = instance.username.replace(' ', '')
    # set missing attributes
    if not instance.sender_profile:
        profiles = Profile.objects.filter(handle=instance.from_username.lower())
        if profiles.exists():
            instance.sender_profile = profiles.first()
    if not instance.recipient_profile:
        profiles = Profile.objects.filter(handle=instance.username.lower())
        if profiles.exists():
            instance.recipient_profile = profiles.first()


@receiver(post_save, sender=Tip, dispatch_uid="post_save_tip")
def postsave_tip(sender, instance, created, **kwargs):
    is_valid = instance.sender_profile != instance.recipient_profile and instance.txid
    if instance.pk and is_valid:
        value_true = 0
        value_usd = 0
        try:
            value_usd = instance.value_in_usdt_then
            value_true = instance.value_true
        except:
            pass
        Earning.objects.update_or_create(
            source_type=ContentType.objects.get(app_label='dashboard', model='tip'),
            source_id=instance.pk,
            defaults={
                "created_on":instance.created_on,
                "org_profile":instance.org_profile,
                "from_profile":instance.sender_profile,
                "to_profile":instance.recipient_profile,
                "value_usd":value_usd,
                "url":'https://gitcoin.co/tips',
                "network":instance.network,
                "txid":instance.txid,
                "token_name":instance.tokenName,
                "token_value":value_true,
                "success":instance.tx_status == 'success',
            }
            )

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

    # https://gitcoincore.slack.com/archives/CAXQ7PT60/p1600019142065700
    if not instance.value_true:
        instance.value_true = 0
    if not instance.value_in_token:
        instance.value_in_token = 0
    if not instance.balance:
        instance.balance = 0


    if not instance.bounty_owner_profile:
        if instance.bounty_owner_github_username:
            profiles = Profile.objects.filter(handle=instance.bounty_owner_github_username.lower().replace('@',''))
            if profiles.exists():
                instance.bounty_owner_profile = profiles.first()

    # this is added to allow activities, project submissions, etc. to attach to a specific bounty based on standard_bounties_id - DL
    if instance.pk and not instance.is_bounties_network and instance.standard_bounties_id == 0:
        instance.standard_bounties_id = CROSS_CHAIN_STANDARD_BOUNTIES_OFFSET + instance.pk

    from django.contrib.contenttypes.models import ContentType
    from search.models import SearchResult
    ct = ContentType.objects.get(app_label='dashboard', model='bounty')
    if instance.current_bounty and instance.pk:
        SearchResult.objects.update_or_create(
            source_type=ct,
            source_id=instance.pk,
            defaults={
                "created_on":instance.web3_created,
                "title":instance.title,
                "description":instance.issue_description,
                "url":instance.url,
                "visible_to":None,
                'img_url': instance.get_avatar_url(True),
            }
            )
        # delete any old bounties
        if instance.prev_bounty and instance.prev_bounty.pk:
            for sr in SearchResult.objects.filter(source_type=ct, source_id=instance.prev_bounty.pk):
                sr.delete()


@receiver(post_save, sender=BountyFulfillment, dispatch_uid="psave_bounty_fulfill")
def psave_bounty_fulfilll(sender, instance, **kwargs):
    if instance.pk and instance.accepted:
        Earning.objects.update_or_create(
            source_type=ContentType.objects.get(app_label='dashboard', model='bountyfulfillment'),
            source_id=instance.pk,
            defaults={
                "created_on":instance.created_on,
                "org_profile":instance.bounty.org_profile,
                "from_profile":instance.bounty.bounty_owner_profile,
                "to_profile":instance.profile,
                "value_usd":instance.value_in_usdt_then,
                "url":instance.bounty.url,
                "network":instance.bounty.network,
                "txid": instance.payout_tx_id,
                "token_name":instance.bounty.token_name,
                "token_value":instance.bounty.value_in_token,
                "success":instance.payout_status == 'done',
            }
            )


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

    def related_to(self, profile):
        """Filter results to Activity objects which are related to a particular profile.

        Activities related to a Profile can be defined as:
            - Posts created by that user
            - Posts that the user likes (even a comment)
            - Posts tipped by that user (even a comment)
            - Posts the user commented on
        """
        from townsquare.models import Like, Comment

        # Posts created by that user
        posts = self.filter(profile=profile)

        # Posts that the user likes (even a comment)
        likes = Like.objects.filter(profile=profile).all()
        activity_pks = [_.activity.pk for _ in likes]
        posts.union(self.filter(pk__in=activity_pks))

        comments = Comment.objects.filter(likes__contains=[profile.pk]).all()
        activity_pks = [_.activity.pk for _ in comments]
        posts.union(self.filter(pk__in=activity_pks))

        # Posts tipped by that user (even a comment)
        tips = Tip.objects.filter(sender_profile=profile).all()
        activity_pks = []
        for tip in tips:
            if  tip.comments_priv:
                obj = tip.attached_object()
                if 'activity:' in tip.comments_priv:
                    activity_pks.append(obj.pk)
                if 'comment:' in tip.comments_priv:
                    activity_pks.append(obj.activity.pk)
        posts.union(self.filter(pk__in=activity_pks))


        # Posts the user commented on
        comments = Comment.objects.filter(profile=profile).all()
        activity_pks = [_.activity.pk for _ in comments]
        posts.union(self.filter(pk__in=activity_pks))

        return posts


class ActivityManager(models.Manager):
    """Enables changing the default queryset function for Activities."""

    def get_queryset(self):
        if settings.ENV == 'prod':
            return super().get_queryset().filter(Q(bounty=None) | Q(bounty__network='mainnet'))
        else:
            return super().get_queryset()


class Activity(SuperModel):
    """Represent Start work/Stop work event.

    Attributes:
        ACTIVITY_TYPES (list of tuples): The valid activity types.

    """

    ACTIVITY_TYPES = [
        ('wall_post', 'Wall Post'),
        ('status_update', 'Update status'),
        ('hypercharge_bounty', 'Hypercharged bounty'),
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
        ('bounty_abandonment_escalation_to_mods', 'Escalated checkin from @gitcoinbot about bounty status'),
        ('bounty_abandonment_warning', 'Checkin from @gitcoinbot about bounty status'),
        ('bounty_removed_slashed_by_staff', 'Dinged and Removed from Bounty by Staff'),
        ('bounty_removed_by_staff', 'Removed from Bounty by Staff'),
        ('bounty_removed_by_funder', 'Removed from Bounty by Funder'),
        ('new_crowdfund', 'New Crowdfund Contribution'),
        # Grants
        ('new_grant', 'New Grant'),
        ('update_grant', 'Updated Grant'),
        ('killed_grant', 'Cancelled Grant'),
        ('negative_contribution', 'Negative Grant Contribution'),
        ('new_grant_contribution', 'Contributed to Grant'),
        ('new_grant_subscription', 'Subscribed to Grant'),
        ('killed_grant_contribution', 'Cancelled Grant Contribution'),
        ('new_kudos', 'New Kudos'),
        ('created_kudos', 'Created Kudos'),
        ('receive_kudos', 'Receive Kudos'),
        ('joined', 'Joined Gitcoin'),
        ('played_quest', 'Played Quest'),
        ('beat_quest', 'Beat Quest'),
        ('created_quest', 'Created Quest'),
        ('updated_avatar', 'Updated Avatar'),
        ('mini_clr_payout', 'Mini CLR Payout'),
        ('leaderboard_rank', 'Leaderboard Rank'),
        ('consolidated_leaderboard_rank', 'Consolidated Leaderboard Rank'),
        ('consolidated_mini_clr_payout', 'Consolidated CLR Payout'),
        ('hackathon_registration', 'Hackathon Registration'),
        ('hackathon_new_hacker', 'Hackathon Registration'),
        ('new_hackathon_project', 'New Hackathon Project'),
        ('flagged_grant', 'Flagged Grant'),
        # ptokens (formerly called personal tokens, now called time tokens)
        ('create_ptoken', 'Create time token'),
        ('mint_ptoken', 'Mint time token'),
        ('edit_price_ptoken', 'Edit time token price'),
        ('buy_ptoken', 'Edit time token price'),
        ('accept_redemption_ptoken', 'Accepts a redemption request of ptoken'),
        ('denies_redemption_ptoken', 'Denies a redemption request of ptoken'),
        ('complete_redemption_ptoken', 'Completes an outgoing redemption'),
        ('incoming_redemption_ptoken', 'Has an incoming redemption finalized by the Buyer')
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
    kudos_transfer = models.ForeignKey(
        'kudos.KudosTransfer',
        related_name='activities',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    kudos = models.ForeignKey(
        'kudos.Token',
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
    hackathonevent = models.ForeignKey(
        'dashboard.HackathonEvent',
        related_name='activities',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    project = models.ForeignKey(
        'dashboard.HackathonProject',
        related_name='hackathon_projects',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    ptoken = models.ForeignKey(
        'ptokens.PersonalToken',
        related_name='ptoken_activities',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    redemption = models.ForeignKey(
        'ptokens.RedemptionToken',
        on_delete=models.CASCADE,
        blank=True, null=True
    )


    created = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_index=True)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, blank=True, db_index=True)
    metadata = JSONField(default=dict, blank=True)
    needs_review = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0, db_index=True)
    other_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='other_activities',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    hidden = models.BooleanField(default=False, db_index=True)
    cached_view_props = JSONField(default=dict, blank=True)

    # Activity QuerySet Manager
    objects = ActivityManager.from_queryset(ActivityQuerySet)()

    def __str__(self):
        """Define the string representation of an interested profile."""
        return f"{self.profile.handle} type: {self.activity_type} created: {naturalday(self.created)} " \
               f"needs review: {self.needs_review}"

    def get_absolute_url(self):
        return self.url

    @property
    def show_token_info(self):
        return self.activity_type in 'new_bounty,increased_bounty,killed_bounty,negative_contribution,new_grant_contribution,killed_grant_contribution,new_grant_subscription,new_tip,new_crowdfund,buy_ptoken'.split(',')

    @property
    def video_participants_count(self):
        if not self.metadata.get('video'):
            return 0
        try:
            from app.services import RedisService
            redis = RedisService().redis
            result = redis.get(self.pk)
            if not result:
                return 0
            return int(result.decode('utf-8'))
        except KeyError:
            return 0


    @property
    def action_url(self):
        if self.bounty:
            return self.bounty.url
        if self.grant:
            return self.grant.url
        if self.kudos:
            return self.kudos.url
        if self.profile:
            return self.profile.url
        return ""

    @property
    def what(self):
        # returns what your wall post target is
        if self.grant:
            return 'grant'
        if self.kudos:
            return 'kudos'
        if self.other_profile:
            return 'profile'
        return ""

    @property
    def url(self):
        return f"{settings.BASE_URL}{self.relative_url}"

    @property
    def relative_url(self):
        return f"townsquare?tab=activity:{self.pk}"

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

    def point_value(self):
        """

        Returns:
            int the Point value of this activity
        """
        return point_values.get(self.activity_type, 0)

    def i18n_name(self):
        return _(next((x[1] for x in self.ACTIVITY_TYPES if x[0] == self.activity_type), 'Unknown type'))

    @property
    def text(self):
        params = {
            'row': self,
            'hide_date': True,
            'hide_likes': True,
        }
        html_str = render_to_string('shared/activity.html', params)
        soup = BeautifulSoup(html_str)
        txt = soup.get_text()
        txt = txt.replace("\n","")
        for i in range(0, 100):
            txt = txt.replace("  ",' ')
        return txt


    def has_voted(self, user):
        poll = self.metadata.get('poll_choices')
        if poll:
            if user.is_authenticated:
                for ele in poll:
                    if user.profile.pk in ele['answers']:
                        return ele['i']
        return False

    def view_props_for(self, user):
        # get view props
        vp = self

        if not user.is_authenticated:
            return vp

        vp.metadata['liked'] = False
        if self.likes.exists():
            vp.metadata['liked'] = self.likes.filter(profile=user.profile).exists()
            vp.metadata['likes_title'] = "Liked by " + ",".join(self.likes.values_list('profile__handle', flat=True)) + '. '
        vp.metadata['favorite'] = self.favorites(user)
        vp.metadata['poll_answered'] = self.has_voted(user)

        return vp

    def favorites(self, user):
        self.favorite_set.filter(user=user, grant=None)

    @property
    def tip_count_usd(self):
        network = 'rinkeby' if settings.DEBUG else 'mainnet'
        tips = Tip.objects.filter(comments_priv=f"activity:{self.pk}", network=network)
        return sum([tip.value_in_usdt for tip in tips])

    @property
    def tip_count_eth(self):
        network = 'rinkeby' if settings.DEBUG else 'mainnet'
        tips = Tip.objects.filter(comments_priv=f"activity:{self.pk}", network=network)
        return sum([tip.value_in_eth for tip in tips])

    @property
    def secondary_avatar_url(self):
        if self.metadata.get('to_username'):
            return f"/dynamic/avatar/{self.metadata['to_username']}"
        if self.metadata.get('worker_handle'):
            return f"/dynamic/avatar/{self.metadata['worker_handle']}"
        if self.metadata.get('url'):
            return self.metadata['url']
        if self.bounty:
            return self.bounty.avatar_url
        if self.metadata.get('grant_logo'):
            return self.metadata['grant_logo']
        if self.grant:
            return self.grant.logo.url if self.grant.logo else None
        return None

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

@receiver(pre_save, sender=Activity, dispatch_uid="psave_activity")
def psave_activity(sender, instance, **kwargs):
    if instance.bounty and instance.bounty.event:
        if not instance.hackathonevent:
            instance.hackathonevent = instance.bounty.event

    if hasattr(instance, 'profile') and instance.profile and hasattr(instance.profile, 'user') and instance.profile.user and instance.profile.user.is_staff:
        instance.metadata['staff'] = True


@receiver(post_save, sender=Activity, dispatch_uid="post_add_activity")
def post_add_activity(sender, instance, created, **kwargs):
    if created:

        # make sure duplicate activity feed items are removed
        dupes = Activity.objects.exclude(pk=instance.pk)
        dupes = dupes.filter(created_on__gte=(instance.created_on - timezone.timedelta(minutes=5)))
        dupes = dupes.filter(created_on__lte=(instance.created_on + timezone.timedelta(minutes=5)))
        dupes = dupes.filter(profile=instance.profile)
        dupes = dupes.filter(bounty=instance.bounty)
        dupes = dupes.filter(tip=instance.tip)
        dupes = dupes.filter(kudos=instance.kudos)
        dupes = dupes.filter(grant=instance.grant)
        dupes = dupes.filter(subscription=instance.subscription)
        dupes = dupes.filter(activity_type=instance.activity_type)
        dupes = dupes.filter(metadata=instance.metadata)
        dupes = dupes.filter(needs_review=instance.needs_review)
        for dupe in dupes:
            dupe.delete()


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

    def slim(self):
        """Filter slims down whats returned from the DB to not include large fields."""
        return self.defer('as_dict', 'as_representation', 'job_location')

    def visible(self):
        """Filter results to only visible profiles."""
        return self.filter(hide_profile=False)

    def hidden(self):
        """Filter results to only hidden profiles."""
        return self.filter(hide_profile=True)


class ProfileManager(models.Manager):
    def get_queryset(self):
        return ProfileQuerySet(self.model, using=self._db).slim()



class Repo(SuperModel):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Organization(SuperModel):
    name = models.CharField(max_length=255)
    groups = models.ManyToManyField('auth.Group', blank=True)
    repos = models.ManyToManyField(Repo, blank=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class BlockedURLFilter(SuperModel):
    expression = models.CharField(max_length=255, help_text='the expression to search for in order to block that github url (or website)')
    comment = models.TextField(blank=True)

    def __str__(self):
        return self.expression


class HackathonRegistration(SuperModel):
    """Defines the Hackthon profiles registrations"""
    name = models.CharField(max_length=255, help_text='Hackathon slug')

    hackathon = models.ForeignKey(
        'HackathonEvent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    referer = models.URLField(null=True, blank=True, help_text='Url comes from')
    looking_team_members = models.BooleanField(default=False)
    looking_project = models.BooleanField(default=False)
    registrant = models.ForeignKey(
        'dashboard.Profile',
        related_name='hackathon_registration',
        on_delete=models.CASCADE,
        help_text='User profile'
    )
    def __str__(self):
        return f"Name: {self.name}; Hackathon: {self.hackathon}; Referer: {self.referer}; Registrant: {self.registrant}"


@receiver(post_save, sender=HackathonRegistration, dispatch_uid="post_add_HackathonRegistration")
def post_add_HackathonRegistration(sender, instance, created, **kwargs):
    if created:
        Activity.objects.create(
            profile=instance.registrant,
            hackathonevent=instance.hackathon,
            activity_type='hackathon_registration',

            )


def default_tribes_expiration():
    return timezone.now() + timezone.timedelta(days=365)


class TribesSubscription(SuperModel):

    plans = (
		('LITE', 'Lite'),
		('PRO', 'Pro'),
		('LAUNCH', 'Launch'),
	)

    expires_on = models.DateTimeField(null=True, blank=True, default=default_tribes_expiration)
    tribe = models.ForeignKey('dashboard.Profile', on_delete=models.CASCADE, related_name='subscription')
    plan_type = models.CharField(max_length=10, choices=plans)
    hackathon_tokens = models.IntegerField(default=0)

    def __str__(self):
        return "{} subscription - {}".format(self.tribe.name, self.plan_type)


class Profile(SuperModel):
    """
        Define the structure of the user profile.

        TODO:
            * Remove all duplicate identity related information already stored on User.

    """

    JOB_SEARCH_STATUS = [
        ('AL', 'Actively looking for work'),
        ('PL', 'Passively looking and open to hearing new opportunities'),
        ('N', 'Not open to hearing new opportunities'),
    ]
    PERSONAS = [
        ('hunter', 'Hunter'),
        ('funder', 'Funder'),
        ('', 'Neither'),
    ]

    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    data = JSONField()
    handle = models.CharField(max_length=255, db_index=True, unique=True)
    last_sync_date = models.DateTimeField(null=True)
    last_calc_date = models.DateTimeField(default=get_0_time)
    email = models.CharField(max_length=255, blank=True, db_index=True)
    github_access_token = models.CharField(max_length=255, blank=True, db_index=True)
    # todo remove chat related
    gitcoin_chat_access_token = models.CharField(max_length=255, blank=True, db_index=True)
    chat_id = models.CharField(max_length=255, blank=True, db_index=True)
    pref_lang_code = models.CharField(max_length=2, choices=settings.LANGUAGES, blank=True)
    slack_repos = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    slack_token = models.CharField(max_length=255, default='', blank=True)
    custom_tagline = models.CharField(max_length=255, default='', blank=True)
    slack_channel = models.CharField(max_length=255, default='', blank=True)
    suppress_leaderboard = models.BooleanField(
        default=False,
        help_text='If this option is chosen, we will remove your profile information from the leaderboard',
    )
    anonymize_gitcoin_grants_contributions = models.BooleanField(
        default=False,
        help_text='If this option is chosen, we will anonymize your Gitcoin Grants contributions',
    )
    hide_profile = models.BooleanField(
        default=True,
        help_text='If this option is chosen, we will remove your profile information all_together',
        db_index=True,
    )
    hide_wallet_address = models.BooleanField(
        default=True,
        help_text='If this option is chosen, Gitcoin will hide your wallet address in it\'s UI/APIs wherever it\'s associated with your handle or other PIA (personally identifiable information) wherever possible.',
    )
    hide_wallet_address_anonymized = models.BooleanField(
        default=False,
        help_text='If this option is chosen, Gitcoin will hide your wallet address in it\'s UI/APIs, even in instances in which it\'s anonymized',
    )
    pref_do_not_track = models.BooleanField(
        default=False,
        help_text='If this option is chosen, we will not put GA/FB tracking on pages that you browse',
    )
    trust_profile = models.BooleanField(
        default=False,
        help_text='If this option is chosen, the user is able to submit a ens domain registration even if they are new to github',
    )
    dont_autofollow_earnings = models.BooleanField(
        default=False,
        help_text='If this option is chosen, Gitcoin will not auto-follow users you do business with',
    )

    tokens = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    keywords = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    organizations = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    organizations_fk = models.ManyToManyField('dashboard.Profile', blank=True)
    profile_organizations = models.ManyToManyField(Organization, blank=True)
    repos = models.ManyToManyField(Repo, blank=True)
    form_submission_records = JSONField(default=list, blank=True)
    max_num_issues_start_work = models.IntegerField(default=5)
    etc_address = models.CharField(max_length=255, default='', blank=True)
    preferred_payout_address = models.CharField(max_length=255, default='', blank=True)
    last_observed_payout_address = models.CharField(max_length=255, default='', blank=True)
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
    location = JSONField(default=dict, blank=True)
    address = models.CharField(max_length=255, default='', blank=True, null=True)
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
    dominant_persona = models.CharField(max_length=25, choices=PERSONAS, blank=True)
    selected_persona = models.CharField(max_length=25, choices=PERSONAS, blank=True)
    longest_streak = models.IntegerField(default=0)
    activity_level = models.CharField(max_length=10, blank=True, help_text=_('the users activity level (high, low, new)'))
    num_repeated_relationships = models.IntegerField(default=0)
    avg_hourly_rate = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    success_rate = models.IntegerField(default=0)
    reliability = models.CharField(max_length=10, blank=True, help_text=_('the users reliability level (high, medium, unproven)'))
    as_dict = JSONField(default=dict, blank=True)
    override_dict = JSONField(default=dict, blank=True, help_text="Used to admin override anything in the dic representation of this profile")
    rank_funder = models.IntegerField(default=0)
    rank_org = models.IntegerField(default=0)
    rank_coder = models.IntegerField(default=0)
    referrer = models.ForeignKey('dashboard.Profile', related_name='referred', on_delete=models.CASCADE, null=True, db_index=True, blank=True)
    tribe_description = models.TextField(default='', blank=True, help_text=_('HTML rich description describing tribe.'))
    automatic_backup = models.BooleanField(default=False, help_text=_('automatic backup profile to cloud storage such as 3Box if the flag is true'))
    as_representation = JSONField(default=dict, blank=True)
    tribe_priority = models.TextField(default='', blank=True, help_text=_('HTML rich description for what tribe priorities.'))

    tribes_cover_image = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('The Tribes Cover image.'),
    )

    is_org = models.BooleanField(
        default=True,
        help_text='Is this profile an org?',
        db_index=True,
    )
    is_tribe = models.BooleanField(
        default=False,
        help_text='Is this profile a Tribe (only applies to orgs)?',
    )

    average_rating = models.DecimalField(default=0, decimal_places=2, max_digits=50, help_text='avg feedback from those who theyve done work with')
    follower_count = models.IntegerField(default=0, db_index=True, help_text='how many users follow them')
    following_count = models.IntegerField(default=0, db_index=True, help_text='how many users are they following')
    earnings_count = models.IntegerField(default=0, db_index=True, help_text='How many times has user earned crypto with Gitcoin')
    spent_count = models.IntegerField(default=0, db_index=True, help_text='How many times has user spent crypto with Gitcoin')
    sms_verification = models.BooleanField(default=False, help_text=_('SMS verification process'))
    validation_attempts = models.PositiveSmallIntegerField(default=0, help_text=_('Number of generated SMS codes to validate account'))
    last_validation_request = models.DateTimeField(blank=True, null=True, help_text=_("When the user requested a code for last time "))
    encoded_number = models.CharField(max_length=255, blank=True, help_text=_('Number with the user validate the account'))
    sybil_score = models.IntegerField(default=-1)
    ignore_tribes = models.ManyToManyField('dashboard.Profile', related_name='ignore', blank=True)
    objects = ProfileManager()
    objects_full = ProfileQuerySet.as_manager()
    brightid_uuid=models.UUIDField(default=uuid.uuid4, unique=True)
    is_brightid_verified=models.BooleanField(default=False)
    is_duniter_verified=models.BooleanField(default=False)
    is_twitter_verified=models.BooleanField(default=False)
    poap_owner_account=models.CharField(max_length=255, blank=True, null=True)
    is_poap_verified=models.BooleanField(default=False)
    twitter_handle=models.CharField(blank=True, null=True, max_length=15)
    ens_verification_address = models.CharField(max_length=255, default='', blank=True)
    is_ens_verified = models.BooleanField(default=False)
    is_google_verified=models.BooleanField(default=False)
    identity_data_google = JSONField(blank=True, default=dict, null=True)
    google_user_id = models.CharField(unique=True, blank=True, null=True, max_length=25)
    is_facebook_verified = models.BooleanField(default=False)
    identity_data_facebook = JSONField(blank=True, default=dict, null=True)
    facebook_user_id = models.CharField(unique=True, blank=True, null=True, max_length=25)
    bio = models.TextField(default='', blank=True, help_text=_('User bio.'))
    interests = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    products_choose = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    contact_email = models.EmailField(max_length=255, blank=True)
    is_pro = models.BooleanField(default=False, help_text=_('Is this user upgraded to pro?'))
    mautic_id = models.CharField(max_length=128, null=True, blank=True, db_index=True, help_text=_('Mautic id to be able to do api requests without user being logged'))

    is_poh_verified=models.BooleanField(default=False)
    poh_handle = models.CharField(blank=True, null=True, max_length=64, unique=True)

    # Idena fields
    is_idena_connected = models.BooleanField(default=False)
    is_idena_verified = models.BooleanField(default=False)
    idena_address = models.CharField(max_length=128, null=True, unique=True, blank=True)
    idena_status = models.CharField(max_length=32, null=True, blank=True)

    def update_idena_status(self):
        self.idena_status = get_idena_status(self.idena_address)

        if self.idena_status in ['Newbie', 'Verified', 'Human']:
            self.is_idena_verified = True
        else:
            self.is_idena_verified = False

    @property
    def shadowbanned(self):
        return self.squelches.filter(active=True).exists()

    @property
    def trust_bonus(self):
        # returns a percentage trust bonus, for this curent user.
        # trust bonus starts at 50% and compounds for every new verification added
        # to a max of 150%
        tb = 0.5
        if self.is_poh_verified:
            tb += 0.50
        if self.is_brightid_verified:
            tb += 0.50
        if self.is_idena_verified:
            tb += 0.50
        if self.is_poap_verified:
            tb += 0.25
        if self.is_ens_verified:
            tb += 0.25
        if self.sms_verification:
            tb += 0.15
        if self.is_google_verified:
            tb += 0.15
        if self.is_twitter_verified:
            tb += 0.15
        if self.is_facebook_verified:
            tb += 0.15
        # if self.is_duniter_verified:
        #     tb *= 1.001
        qd_tb = 0
        for player in self.players.all():
            new_score = 0
            if player.tokens_in:
                new_score = min(player.tokens_in / 100, 0.20)
            qd_tb = max(qd_tb, new_score)
        return min(1.5, tb)


    @property
    def is_blocked(self):
        if not self.user:
            return False
        return BlockedUser.objects.filter(user=self.user).exists()

    @property
    def logins(self):
        return self.actions.filter(action='Login')

    @property
    def latest_sybil_investigation(self):
        try:
            return self.investigations.filter(key='sybil').first().description
        except:
            return ''

    @property
    def is_subscription_valid(self):
        return self.tribes_subscription and self.tribes_subscription.expires_on > timezone.now()

    @property
    def active_subscriptions(self):
        if not self.is_org :
            return TribesSubscription.objects.filter(tribe__in=self.organizations_fk.all()).all()
        return TribesSubscription.objects.filter(tribe=self).all()

    @property
    def suggested_bounties(self):
        suggested_bounties = BountyRequest.objects.filter(tribe=self, status='o').order_by('created_on')

    @property
    def sybil_score_str(self):
        _map = {
            0: 'Low',
            1: 'Med-Low',
            2: 'Med',
            3: 'Med-High',
            4: 'High',
            5: 'Very High',
        }
        score = self.sybil_score
        if score < 0:
            return f'VeryX{abs(score)} Low'
        if score > 5:
            return f'VeryX{score} High'
        return _map.get(score, "Unknown")


    @property
    def subscribed_threads(self):
        tips = Tip.objects.filter(Q(pk__in=self.received_tips.all()) | Q(pk__in=self.sent_tips.all())).filter(comments_priv__icontains="activity:").all()
        tips = [tip.comments_priv.split(':')[1] for tip in tips]
        tips = [ele for ele in tips if ele.isnumeric()]
        activities = Activity.objects.filter(
         Q(pk__in=self.likes.values_list('activity__pk', flat=True))
         | Q(pk__in=self.comments.values_list('activity__pk', flat=True))
         | Q(pk__in=tips)
         | Q(profile=self)
         | Q(other_profile=self))
        return activities

    @property
    def quest_level(self):
        return self.quest_attempts.filter(success=True).distinct('quest').count() + 1

    @property
    def match_this_round(self):
        mr = self.matchranking_this_round
        if mr:
            return mr.match_total
        return 0

    @property
    def matchranking_this_round(self):
        if hasattr(self, '_matchranking_this_round'):
            return self._matchranking_this_round
        from townsquare.models import MatchRound
        mr = MatchRound.objects.current().cache(timeout=60).first()
        if mr:
            mr = mr.ranking.filter(profile=self).cache(timeout=60).first()
            self._matchranking_this_round = mr
            if mr:
                return mr
        return None

    @property
    def quest_caste(self):
        castes = [
            'Etherean',
            'Ethereal',
            'BUIDLer',
            'HODLer',
            'Whale',
            'BullBear',
            'MoonKid',
        ]
        i = self.pk % len(castes)
        return castes[i]

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
    def team_or_none_if_timeout(self):
        try:
            return self.team
        except TimeoutError as e:
            logger.error(f'timeout for team of {self.handle}; will be fixed when https://github.com/gitcoinco/web/pull/6218/files is in')
            return []

    @property
    @timeout(1)
    def team(self):
        if not self.is_org:
            return Profile.objects.none()
        return Profile.objects.filter(organizations_fk=self)

    @property
    def tribe_members(self):
        if not self.is_org:
            return TribeMember.objects.filter(profile=self).exclude(status='rejected').exclude(profile__user=None)
        return TribeMember.objects.filter(org=self).exclude(status='rejected').exclude(profile__user=None)

    @property
    def ref_code(self):
        return hex(self.pk).replace("0x",'')

    @property
    def get_org_kudos(self):
        from kudos.models import Token

        if not self.is_org:
            return Token.objects.none()
        return Token.objects.filter(Q(name__icontains=self.name)|Q(name__icontains=self.handle)).filter(cloned_from_id=F('token_id')).visible()

    @property
    def kudos_authored(self):
        from kudos.models import Token
        return Token.objects.filter(artist=self.handle, num_clones_allowed__gt=1, hidden=False)

    @property
    def get_failed_kudos(self):
        from kudos.models import KudosTransfer
        pks = list(self.get_my_kudos.values_list('pk', flat=True)) + list(self.get_sent_kudos.values_list('pk', flat=True))
        qs = KudosTransfer.objects.filter(pk__in=pks)
        return qs.filter(Q(txid='pending_celery') | Q(tx_status__in=['dropped', 'unknown']))

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
            kudos_token_cloned_from__contract__network__in=[settings.KUDOS_NETWORK, 'xdai']
        )
        # Multiple support requests for kudos not showing on profile were caused by this
        # kudos_transfers = kudos_transfers.send_success() | kudos_transfers.send_pending() | kudos_transfers.not_submitted()

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
        # Multiple support requests for kudos not showing on profile were caused by this
        # kudos_transfers = kudos_transfers.send_success() | kudos_transfers.send_pending() | kudos_transfers.not_submitted()
        kudos_transfers = kudos_transfers.filter(
            kudos_token_cloned_from__contract__network__in=[settings.KUDOS_NETWORK, 'xdai']
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

    def get_average_star_rating(self, scale=1):
        """Returns the average star ratings (overall and individual topic)
        for a particular user"""

        feedbacks = FeedbackEntry.objects.filter(receiver_profile=self).all()
        average_rating = {}
        average_rating['overall'] = sum([feedback.rating for feedback in feedbacks]) * scale \
            / feedbacks.count() if feedbacks.count() != 0 else 0
        average_rating['code_quality_rating'] = sum([feedback.code_quality_rating for feedback in feedbacks]) * scale \
            / feedbacks.exclude(code_quality_rating=0).count() if feedbacks.exclude(code_quality_rating=0).count() != 0 else 0
        average_rating['communication_rating'] = sum([feedback.communication_rating for feedback in feedbacks]) * scale \
            / feedbacks.exclude(communication_rating=0).count() if feedbacks.exclude(communication_rating=0).count() != 0 else 0
        average_rating['recommendation_rating'] = sum([feedback.recommendation_rating for feedback in feedbacks]) * scale \
            / feedbacks.exclude(recommendation_rating=0).count() if feedbacks.exclude(recommendation_rating=0).count() != 0 else 0
        average_rating['satisfaction_rating'] = sum([feedback.satisfaction_rating for feedback in feedbacks]) * scale \
            / feedbacks.exclude(satisfaction_rating=0).count() if feedbacks.exclude(satisfaction_rating=0).count() != 0 else 0
        average_rating['speed_rating'] = sum([feedback.speed_rating for feedback in feedbacks]) * scale \
            / feedbacks.exclude(speed_rating=0).count() if feedbacks.exclude(speed_rating=0).count() != 0 else 0
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
        return dict(Profile.JOB_SEARCH_STATUS).get(self.job_search_status, 'Unknown Job Status')

    @property
    def active_bounties(self):
        active_bounties = Bounty.objects.current().filter(bounty_state='work_started')
        return Interest.objects.filter(profile_id=self.pk, bounty__in=active_bounties)

    @property
    def frontend_calc_stale(self):
        return self.last_calc_date < (timezone.now() - timezone.timedelta(hours=72))

    @property
    def org_leaderboard(self):
        return self.leaderboard_helper(self.org_earnings, 'to_profile')

    @property
    def contrib_leaderboard(self):
        return self.leaderboard_helper(self.earnings, 'from_profile')

    @property
    def sent_leaderboard(self):
        return self.leaderboard_helper(self.sent_earnings, 'to_profile')

    def leaderboard_helper(self, earnings, distinct_on):
        order_field = f'{distinct_on}__handle'
        earnings = earnings.filter(network=self.get_network())
        leaderboard = earnings.values(order_field).annotate(sum=Sum('value_usd')).annotate(count=Count('value_usd'))
        kwargs = {order_field:None}
        return [(ele[order_field], ele['count'], ele['sum']) for ele in leaderboard.exclude(**kwargs).order_by('-sum')]

    @property
    def bounties(self):
        fulfilled_bounty_ids = self.fulfilled.all().values_list('bounty_id')
        bounties = Bounty.objects.filter(github_url__istartswith=self.github_url, current_bounty=True)
        for interested in self.interested.all().nocache():
            bounties = bounties | Bounty.objects.filter(interested=interested, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(pk__in=fulfilled_bounty_ids, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(bounty_owner_github_username__iexact=self.handle, current_bounty=True) | Bounty.objects.filter(bounty_owner_github_username__iexact="@" + self.handle, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(github_url__in=[url for url in self.tips.values_list('github_url', flat=True)], current_bounty=True)
        bounties = bounties.distinct()
        return bounties.order_by('-web3_created')

    @property
    def cascaded_persona(self):
        if self.is_org:
            return 'org'
        if self.selected_persona:
            return self.selected_persona
        if self.dominant_persona:
            return self.dominant_persona
        if self.persona_is_funder:
            return 'funder'
        if self.persona_is_hunter:
            return 'hunter'
        return 'hunter'

    @property
    def tips(self):
        on_repo = Tip.objects.filter(github_url__startswith=self.github_url).order_by('-id')
        tipped_for = Tip.objects.filter(username__iexact=self.handle).order_by('-id')
        return on_repo | tipped_for

    def calculate_all(self):
        # calculates all the info needed to make the profile frontend great

        # give the user a profile header if they have not yet selected one
        if not self.profile_wallpaper:
            from dashboard.helpers import load_files_in_directory
            import random
            try:
                wallpapers = load_files_in_directory('wallpapers')
                wallpapers = [image for image in wallpapers if image[0:5] == '2021_']
                self.profile_wallpaper = f"/static/wallpapers/{random.choice(wallpapers)}"
            except Exception as e:
                # fix for travis, which has no static dir
                logger.exception(e)

        self.calculate_and_save_persona()
        self.actions_count = self.get_num_actions
        self.activity_level = self.calc_activity_level()
        self.longest_streak = self.calc_longest_streak()
        self.num_repeated_relationships = self.calc_num_repeated_relationships()
        self.avg_hourly_rate = self.calc_avg_hourly_rate()
        self.success_rate = self.calc_success_rate()
        self.reliability = self.calc_reliability_ranking() # must be calc'd last
        self.as_dict = json.loads(json.dumps(self.to_dict()))
        self.as_representation = json.loads(json.dumps(self.to_representation))
        self.last_calc_date = timezone.now() + timezone.timedelta(seconds=1)

    def get_persona_action_count(self):
        hunter_count = 0
        funder_count = 0

        hunter_count += self.interested.count()
        hunter_count += self.received_tips.count()
        hunter_count += self.grant_admin.count()
        hunter_count += self.fulfilled.count()

        funder_count += self.bounties_funded.count()
        funder_count += self.sent_tips.count()
        funder_count += self.grant_contributor.count()

        return hunter_count, funder_count

    def calculate_and_save_persona(self, respect_defaults=True, decide_only_one=False):
        if respect_defaults and decide_only_one:
            raise Exception('cannot use respect_defaults and decide_only_one')

        # respect to defaults
        is_hunter = False
        is_funder = False
        if respect_defaults:
            is_hunter = self.persona_is_hunter
            is_funder = self.persona_is_funder

        # calculate persona
        hunter_count, funder_count = self.get_persona_action_count()
        if hunter_count > funder_count:
            self.dominant_persona = 'hunter'
        elif hunter_count < funder_count:
            self.dominant_persona = 'funder'

        # update db
        if not decide_only_one:
            if hunter_count > 0:
                self.persona_is_hunter = True
            if funder_count > 0:
                self.persona_is_funder = True
        else:
            if hunter_count > funder_count:
                self.persona_is_hunter = True
                self.persona_is_funder = False
            elif funder_count > hunter_count:
                self.persona_is_funder = True
                self.persona_is_hunter = False

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
        role = 'newbie'
        if self.persona_is_funder and self.persona_is_hunter:
            role = 'funder/coder'
        elif self.persona_is_funder:
            role = 'funder'
        elif self.persona_is_hunter:
            role = 'coder'
        if self.is_org:
            role = 'organization'

        total_funded_participated = funded_bounties.count() + fulfilled_bounties.count()
        plural = 's' if total_funded_participated != 1 else ''

        return f"@{self.handle} is a {role} who has participated in {total_funded_participated} " \
               f"transaction{plural} on Gitcoin"


    @property
    def desc(self):
        bounties1 = self.sent_earnings if not self.is_org else Earning.objects.none()
        bounties2 = self.earnings if not self.is_org else self.org_earnings
        return self.get_desc(bounties1, bounties2)

    @property
    def github_created_on(self):
        created_at = self.data.get('created_at', '')

        if not created_at:
            return ''

        created_on = datetime.strptime(created_at, '%Y-%m-%dT%H:%M:%SZ')
        return created_on.replace(tzinfo=pytz.UTC)

    @property
    def is_moderator(self):
        """Determine whether or not the user is a moderator.

        Returns:
            bool: Whether or not the user is a moderator.

        """
        return self.user.groups.filter(name='Moderators').cache().exists() if self.user else False

    @property
    def is_alpha_tester(self):
        """Determine whether or not the user is an alpha tester.

        Returns:
            bool: Whether or not the user is an alpha tester.

        """
        if self.user.is_staff:
            return True
        return self.user.groups.filter(name='Alpha_Testers').cache().exists() if self.user else False

    @property
    def user_groups(self):
        return self.user.groups.all().cache().values_list('name', flat=True) if self.user else False

    @property
    def is_staff(self):
        """Determine whether or not the user is a staff member.

        Returns:
            bool: Whether or not the user is a member of the staff.

        """
        return self.user.is_staff if self.user else False

    def calc_activity_level(self):
        """Determines the activity level of a user

        Returns:
            str: High, Low, Medium, or New

        """
        high_threshold = 7
        med_threshold = 2
        new_threshold_days = 7

        if self.created_on > (timezone.now() - timezone.timedelta(days=new_threshold_days)):
            return "New"

        visits = self.actions.filter(action='Visit')
        visits_last_month = visits.filter(created_on__gt=timezone.now() - timezone.timedelta(days=30)).count()

        if visits_last_month > high_threshold:
            return "High"
        if visits_last_month > med_threshold:
            return "Med"
        return "Low"


    def calc_longest_streak(self):
        """ Determines the longest streak, in workdays, of this user

        Returns:
            int: a number of weekdays

        """

        # setup
        action_dates = self.actions.all().values_list('created_on', flat=True)
        action_dates = set([ele.replace(tzinfo=pytz.utc).strftime('%m/%d/%Y') for ele in action_dates])
        start_date = timezone.datetime(self.created_on.year, self.created_on.month, self.created_on.day).replace(tzinfo=pytz.utc)
        end_date = timezone.datetime(timezone.now().year, timezone.now().month, timezone.now().day).replace(tzinfo=pytz.utc)

        # loop setup
        iterdate = start_date
        max_streak = 0
        this_streak = 0
        while iterdate < end_date:
            # housekeeping
            last_iterdate = start_date
            iterdate += timezone.timedelta(days=1)

            is_weekday = iterdate.weekday() < 5
            if not is_weekday:
                continue

            has_action_during_window = iterdate.strftime('%m/%d/%Y') in action_dates
            if has_action_during_window:
                this_streak += 1
                max_streak = max(max_streak, this_streak)
            else:
                this_streak = 0

        return max_streak

    def calc_num_repeated_relationships(self):
        """ the number of repeat relationships that this user has created


        Returns:
            int: a number of repeat relationships

        """
        relationships = []
        relationships += list(self.sent_earnings.values_list('to_profile__handle', flat=True))
        relationships += list(self.earnings.values_list('from_profile__handle', flat=True))

        rel_count = { key: 0 for key in relationships }
        for rel in relationships:
            rel_count[rel] += 1

        return len([key for key, val in rel_count.items() if val > 1])

    def calc_avg_hourly_rate(self):
        """

        Returns:
            float: the average hourly rate for this user in dollars

        """
        values_list = self.bounties.values_list('fulfillments__fulfiller_hours_worked', 'value_in_usdt')
        values_list = [ele for ele in values_list if (ele[0] and ele[1])]
        if not len(values_list):
            return 0
        hourly_rates = [(ele[1]/ele[0]) for ele in values_list]
        avg_hourly_rate = sum(hourly_rates)/len(hourly_rates)
        return avg_hourly_rate

    def calc_success_rate(self):
        """

        Returns:
            int; the success percentage for this users bounties as a positive integer.

        """
        bounties = self.bounties.filter(network=self.get_network()) if self.cascaded_persona == 'hunter' else self.get_sent_bounties.current()
        completed_bounties = bounties.filter(idx_status='done').count()
        expired_bounties = bounties.filter(idx_status='expired').count()
        cancelled_bounties = bounties.filter(idx_status='cancelled').count()
        eligible_bounties = cancelled_bounties + expired_bounties + completed_bounties

        if eligible_bounties == 0:
            return -1

        return int(completed_bounties * 100 / eligible_bounties)

    def calc_reliability_ranking(self):
        """

        Returns:
            the reliabiliyt ranking that the user has.

        """

        # thresholds
        high_threshold = 3
        med_threshold = 2
        new_threshold_days = 7
        rating_deduction_threshold = 0.7
        rating_merit_threshold = 0.95
        abandon_deduction_threshold = 0.85
        abandon_merit_threshold = 0.95
        abandon_merit_earnings_threshold = med_threshold
        abandon_slash_multiplier = 2
        success_rate_deduction_threshold = 0.65
        success_ratemerit_threshold = 0.85
        num_repeated_relationships_merit_threshold = 3

        # setup
        base_rating = 0
        deductions = 0


        #calculate base rating
        num_earnings = self.earnings.count() + self.sent_earnings.count()
        if num_earnings < 2:
            return "Unproven"

        if num_earnings > high_threshold:
            base_rating = 3 # high
        elif num_earnings > med_threshold:
            base_rating = 2 # medium
        else:
            base_rating = 1 # low

        # calculate deductions

        ## ratings deduction
        num_5_star_ratings = self.feedbacks_got.filter(rating=5).count()
        num_subpar_star_ratings = self.feedbacks_got.filter(rating__lt=4).count()
        total_rating = num_subpar_star_ratings + num_5_star_ratings
        if total_rating:
            if num_5_star_ratings/total_rating < rating_deduction_threshold:
                deductions -= 1
            if num_5_star_ratings/total_rating > rating_merit_threshold:
                deductions += 1

        ## abandonment deduction
        total_removals = self.no_times_been_removed_by_funder() + self.no_times_been_removed_by_staff()+ (self.no_times_slashed_by_staff() * abandon_slash_multiplier)
        if total_rating:
            if total_removals/num_earnings < abandon_deduction_threshold:
                deductions -= 1
            if num_earnings > abandon_merit_earnings_threshold and total_removals/num_earnings > abandon_merit_threshold:
                deductions += 1

        ## success rate deduction
        if self.success_rate != -1:
            if self.success_rate < success_rate_deduction_threshold:
                deductions -= 1
            if self.success_rate > success_ratemerit_threshold:
                deductions += 1

        ## activity level deduction
        if self.activity_level == "High":
                deductions += 1

        ## activity level deduction
        if self.num_repeated_relationships > num_repeated_relationships_merit_threshold:
                deductions += 1

        # calculate final rating
        final_rating = base_rating + deductions
        if final_rating >= 5:
            return "Very High"
        elif final_rating >= 3:
            return "High"
        elif final_rating >= 2:
            return "Medium"
        elif final_rating >= 1:
            return "Low"
        elif final_rating <= 1:
            return "Very Low"

        return 0

    @property
    def completed_bounties(self):
        """Returns bounties completed by user

        Returns:
            number: number of bounties completed

        """
        network = self.get_network()
        return self.bounties.filter(
            idx_status__in=['done'], network=network).count()


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
        return self.avatar_baseavatar_related.cache(timeout=60).filter(active=True).first()

    @property
    def active_avatar_nocache(self):
        return self.avatar_baseavatar_related.nocache().filter(active=True).first()

    @property
    def github_url(self):
        return f"https://github.com/{self.handle}"

    @property
    def lazy_avatar_url(self):
        return f"{settings.BASE_URL}dynamic/avatar/{self.handle}"

    @property
    def avatar_url(self):
        if self.admin_override_avatar:
            return self.admin_override_avatar.url
        if self.active_avatar:
            return self.active_avatar.avatar_url
        else:
            github_avatar_img = get_user_github_avatar_image(self.handle)
            if github_avatar_img:
                try:
                    github_avatar = SocialAvatar.github_avatar(self, github_avatar_img)
                    github_avatar.save()
                    self.activate_avatar(github_avatar.pk)
                    self.save()
                    return self.active_avatar.avatar_url
                except Exception as e:
                    logger.warning(f'Encountered ({e}) while attempting to save a user\'s github avatar')
        return self.lazy_avatar_url

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

        # TODO: investigate how jsonfield blank keys get set.
        if self.data and self.data["name"] and self.data["name"] != 'null':
            return self.data["name"]
        return self.username

    def __str__(self):
        return self.handle

    def get_relative_url(self, preceding_slash=True):
        from dashboard.utils import get_url_first_indexes # avoid circular import
        prefix = ''
        if self.handle in get_url_first_indexes():
            # handle collision
            prefix = 'profile/'
        return f"{'/' if preceding_slash else ''}{prefix}{self.handle}"

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


    @staticmethod
    def get_network():
        if settings.OVERRIDE_NETWORK:
            return settings.OVERRIDE_NETWORK
        return 'mainnet' if not settings.DEBUG else 'rinkeby'

    def get_fulfilled_bounties(self, network=None):
        network = network or self.get_network()
        fulfilled_bounty_ids = self.fulfilled.all().values_list('bounty_id', flat=True)
        bounties = Bounty.objects.current().filter(pk__in=fulfilled_bounty_ids, accepted=True, network=network)
        return bounties

    def get_orgs_bounties(self, network=None):
        network = network or self.get_network()
        url = f"https://github.com/{self.handle}"
        bounties = Bounty.objects.current().filter(network=network, github_url__istartswith=url)
        return bounties

    def get_leaderboard_index(self, key='weekly_earners'):
        try:
            rank = self.leaderboard_ranks.active().filter(leaderboard=key, product='all').latest('id')
            return rank.rank
        except LeaderboardRank.DoesNotExist:
            score = 0
        return score

    def get_contributor_leaderboard_index(self):
        return self.get_leaderboard_index()

    def get_funder_leaderboard_index(self):
        return self.get_leaderboard_index('weekly_payers')

    def get_org_leaderboard_index(self):
        return self.get_leaderboard_index('weekly_orgs')

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

        eth_sum = 0
        if bounties.exists():
            try:
                for bounty in bounties:
                    eth = bounty.get_value_in_eth
                    if not eth:
                        continue
                    eth_sum += float(eth)
            except Exception as e:
                logger.exception(e)
                pass

        # if sum_type == 'collected' and self.tips:
        #     eth_sum = eth_sum + sum([ float(amount.value_in_eth) for amount in self.tips ])

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
                all_tokens_sum = [{'token_name': token_name, 'value_in_token': float(value_in_token)} for token_name, value_in_token in all_tokens_sum_tmp.items()]

        except Exception as e:
            logger.exception(e)

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
            dict: list of the profiles that were worked with (key) and the number of times they occurred

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
            profiles = self.as_dict.get('orgs_bounties_works_with', [])

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
            all_activities = self.activities.all() | self.other_activities.all()
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

    @property
    def to_representation(instance):
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


    def to_es(self):
        return json.dumps(self.to_dict())

    def to_dict(self):
        """Get the dictionary representation with additional data.

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
        network = self.get_network()
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
        total_fulfilled = fulfilled_bounties.count() + self.tips.count()
        desc = self.desc
        no_times_been_removed = self.no_times_been_removed_by_funder() + self.no_times_been_removed_by_staff() + self.no_times_slashed_by_staff()

        org_works_with = []
        if self.is_org:
            org_bounties = self.get_orgs_bounties(network='mainnet')
            for bounty in org_bounties:
                for bf in bounty.fulfillments.filter(accepted=True):
                    if bf.fulfiller_github_username:
                        org_works_with.append(bf.fulfiller_github_username)
        params = {
            'title': f"@{self.handle}",
            'active': 'profile_details',
            'newsletter_headline': ('Be the first to know about new funded issues.'),
            'card_title': f'@{self.handle} | Gitcoin',
            'org_works_with': org_works_with,
            'card_desc': desc,
            'avatar_url': self.avatar_url_with_gitcoin_logo,
            'count_bounties_completed': total_fulfilled,
            'works_with_collected': works_with_collected,
            'works_with_funded': works_with_funded,
            'works_with_org': works_with_org,
            'sum_eth_collected': sum_eth_collected,
            'sum_eth_funded': sum_eth_funded,
            'funded_bounties_count': total_funded,
            'no_times_been_removed': no_times_been_removed,
            'sum_eth_on_repos': sum_eth_on_repos,
            'count_bounties_on_repo': count_bounties_on_repo,
            'sum_all_funded_tokens': sum_all_funded_tokens,
            'sum_all_collected_tokens': sum_all_collected_tokens,
            'bounties': list(bounties.values_list('pk', flat=True)),
        }

        if self.cascaded_persona == 'org':
            active_bounties = self.bounties.filter(idx_status__in=Bounty.WORK_IN_PROGRESS_STATUSES, network='mainnet')
        elif self.cascaded_persona == 'funder':
            active_bounties = active_bounties = Bounty.objects.filter(bounty_owner_profile=self, idx_status__in=Bounty.WORK_IN_PROGRESS_STATUSES, network='mainnet', current_bounty=True)
        elif self.cascaded_persona == 'hunter':
            active_bounties = Bounty.objects.filter(pk__in=self.active_bounties.filter(pending=False).values_list('bounty', flat=True), network='mainnet')
        else:
            active_bounties = Bounty.objects.none()
        params['active_bounties'] = list(active_bounties.values_list('pk', flat=True))

        all_activities = self.get_various_activities()
        params['activities'] = list(all_activities.values_list('pk', flat=True))
        counts = {}
        if not all_activities or all_activities.count() == 0:
            params['none'] = True
        else:
            counts = all_activities.values('activity_type').order_by('activity_type').annotate(the_count=Count('activity_type'))
            counts = {ele['activity_type']: ele['the_count'] for ele in counts}
        params['activities_counts'] = counts

        params['activities'] = list(self.get_various_activities().values_list('pk', flat=True))
        params['tips'] = list(self.tips.filter(**query_kwargs).send_happy_path().values_list('pk', flat=True))
        params['scoreboard_position_contributor'] = self.get_contributor_leaderboard_index()
        params['scoreboard_position_funder'] = self.get_funder_leaderboard_index()
        if self.is_org:
            params['scoreboard_position_org'] = self.get_org_leaderboard_index()

        context = params
        profile = self

        context['avg_rating'] = profile.get_average_star_rating()
        context['avg_rating_scaled'] = profile.get_average_star_rating(20)
        context['verification'] = bool(profile.get_my_verified_check)
        context['avg_rating'] = profile.get_average_star_rating()
        context['total_kudos_count'] = profile.get_my_kudos.count() + profile.get_sent_kudos.count() + profile.get_org_kudos.count()
        context['total_kudos_sent_count'] = profile.sent_kudos.count()
        context['total_kudos_received_count'] = profile.received_kudos.count()
        context['total_grant_created'] = profile.grant_admin.count()
        context['total_grant_contributions'] = profile.grant_contributor.filter(subscription_contribution__success=True).values_list('subscription_contribution').count() + profile.grant_phantom_funding.count()
        context['total_grant_actions'] = context['total_grant_created'] + context['total_grant_contributions']

        context['total_tips_sent'] = profile.get_sent_tips.count()
        context['total_tips_received'] = profile.get_my_tips.count()

        context['total_quest_attempts'] = profile.quest_attempts.count()
        context['total_quest_success'] = profile.quest_attempts.filter(success=True).count()

        # portfolio
        portfolio_bounties = profile.fulfilled.filter(bounty__network='mainnet', bounty__current_bounty=True)
        portfolio_keywords = {}
        for fulfillment in portfolio_bounties.nocache():
            for keyword in fulfillment.bounty.keywords_list:
                keyword = keyword.lower()
                if keyword not in portfolio_keywords.keys():
                    portfolio_keywords[keyword] = 0
                portfolio_keywords[keyword] += 1
        sorted_portfolio_keywords = [(k, portfolio_keywords[k]) for k in sorted(portfolio_keywords, key=portfolio_keywords.get, reverse=True)]

        context['portfolio'] = list(portfolio_bounties.values_list('pk', flat=True))
        context['portfolio_keywords'] = sorted_portfolio_keywords
        earnings_to = Earning.objects.filter(to_profile=profile, network='mainnet', success=True, value_usd__isnull=False)
        earnings_from = Earning.objects.filter(from_profile=profile, network='mainnet', success=True, value_usd__isnull=False)
        from django.contrib.contenttypes.models import ContentType
        earnings_to = earnings_to.exclude(source_type=ContentType.objects.get(app_label='kudos', model='kudostransfer'))
        context['earnings_total'] = round(sum(earnings_to.values_list('value_usd', flat=True)))
        context['spent_total'] = round(sum(earnings_from.values_list('value_usd', flat=True)))
        context['earnings_count'] = earnings_to.count()
        context['spent_count'] = earnings_from.count()
        context['hackathons_participated_in'] = self.interested.filter(bounty__event__isnull=False).distinct('bounty__event').count()
        context['hackathons_funded'] = funded_bounties.filter(event__isnull=False).distinct('event').count()
        if context['earnings_total'] > 1000:
            context['earnings_total'] = f"{round(context['earnings_total']/1000)}k"
        if context['spent_total'] > 1000:
            context['spent_total'] = f"{round(context['spent_total']/1000)}k"

        for key, val in self.override_dict.items():
            context[key] = val

        return context



    @property
    def reassemble_profile_dict(self):
        params = self.as_dict

        params['active_bounties'] = Bounty.objects.filter(pk__in=params.get('active_bounties', []))
        if params.get('tips'):
            params['tips'] = Tip.objects.filter(pk__in=params['tips'])
        if params.get('activities'):
            params['activities'] = Activity.objects.filter(pk__in=params['activities'])
        params['profile'] = self
        params['portfolio'] = BountyFulfillment.objects.filter(pk__in=params.get('portfolio', []))
        return params

    def get_last_observed_payout_address(self):
        for earning in self.sent_earnings.filter(network='mainnet').order_by('-created_on'):
            for history in earning.history.all().order_by('-created_on'):
                if history.payload.get('from'):
                     return history.payload.get('from')
        return ''


    @property
    def ips(self):
        ips = []
        for login in self.actions.filter(action='Login').order_by('-created_on'):
            if login.ip_address:
                ips.append(login.ip_address)
        return ips

    @property
    def last_known_ip(self):
        ips = self.ips
        if len(ips) > 0:
            return ips[0]
        return ''


    @property
    def locations(self):
        from app.utils import get_location_from_ip
        locations = []
        for login in self.actions.filter(action='Login').order_by('-created_on'):
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

    # sync organizations_fk and organizations
    if hasattr(instance, 'pk') and instance.pk:
        for handle in instance.organizations:
            handle =handle.lower()
            if not instance.organizations_fk.filter(handle=handle).exists():
                obj = Profile.objects.filter(handle=handle).first()
                if obj:
                    instance.organizations_fk.add(obj)
        for profile in instance.organizations_fk.all():
            if profile.handle not in instance.organizations:
                instance.organizations += [profile.handle]

    instance.is_org = instance.data.get('type') == 'Organization'
    instance.average_rating = 0
    if instance.feedbacks_got.count():
        num = instance.feedbacks_got.count()
        val = sum(instance.feedbacks_got.values_list('rating', flat=True))
        instance.average_rating = val/num
    instance.following_count = instance.follower.count()
    instance.follower_count = instance.org.count()
    instance.earnings_count = instance.earnings.count()
    instance.spent_count = instance.sent_earnings.count()

    instance.last_observed_payout_address = instance.get_last_observed_payout_address()

    from django.contrib.contenttypes.models import ContentType
    from search.models import SearchResult
    if instance.pk:
        try:
            SearchResult.objects.update_or_create(
                source_type=ContentType.objects.get(app_label='dashboard', model='profile'),
                source_id=instance.pk,
                defaults={
                    "created_on":instance.created_on,
                    "title":instance.handle,
                    "description":instance.desc,
                    "url":instance.url,
                    "visible_to":None,
                    'img_url': instance.avatar_url,
                }
            )
        except:
            pass

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

class UserDirectoryQuerySet(models.QuerySet):
    """Define the Profile QuerySet to be used as the objects manager."""

class UserDirectoryManager(models.Manager):
    def get_queryset(self):
        return UserDirectoryQuerySet(self.model, using=self._db)

class UserDirectory(models.Model):
    profile_id = models.CharField(max_length=255, primary_key=True)
    join_date = models.CharField(null=True, max_length=255)
    github_created_at = models.CharField(null=True, max_length=255)
    first_name = models.CharField(null=True, max_length=255)
    last_name = models.CharField(null=True, max_length=255)
    email = models.EmailField()
    handle = models.CharField(null=True, max_length=255)
    sms_verification = models.BooleanField()
    persona = models.CharField(null=True, max_length=255)
    rank_coder = models.IntegerField()
    rank_funder = models.IntegerField()
    num_hacks_joined = models.IntegerField()
    which_hacks_joined = ArrayField(base_field=models.IntegerField(), null=True)
    hack_work_starts = models.IntegerField()
    hack_work_submits = models.IntegerField()
    hack_work_start_orgs = ArrayField(base_field=models.CharField(max_length=255), null=True)
    hack_work_submit_orgs = ArrayField(base_field=models.CharField(max_length=255), null=True)
    bounty_work_starts = models.IntegerField()
    bounty_work_submits = models.IntegerField()
    hack_started_feature = models.IntegerField()
    hack_started_code_review = models.IntegerField()
    hack_started_security = models.IntegerField()
    hack_started_design = models.IntegerField()
    hack_started_documentation = models.IntegerField()
    hack_started_bug = models.IntegerField()
    hack_started_other = models.IntegerField()
    hack_started_improvement = models.IntegerField()
    started_feature = models.IntegerField()
    started_code_review = models.IntegerField()
    started_security = models.IntegerField()
    started_design = models.IntegerField()
    started_documentation = models.IntegerField()
    started_bug = models.IntegerField()
    started_other = models.IntegerField()
    started_improvement = models.IntegerField()
    submitted_feature = models.IntegerField()
    submitted_code_review = models.IntegerField()
    submitted_security = models.IntegerField()
    submitted_design = models.IntegerField()
    submitted_documentation = models.IntegerField()
    submitted_bug = models.IntegerField()
    submitted_other = models.IntegerField()
    submitted_improvement = models.IntegerField()
    bounty_earnings  = models.FloatField()
    bounty_work_start_orgs = ArrayField(base_field=models.CharField(max_length=255), null=True)
    bounty_work_submit_orgs = ArrayField(base_field=models.CharField(max_length=255), null=True)
    kudos_sends = models.IntegerField()
    kudos_receives = models.IntegerField()
    hack_winner_kudos_received = models.IntegerField()
    grants_opened = models.IntegerField()
    grant_contributed = models.IntegerField()
    grant_contributions = models.IntegerField()
    grant_contribution_amount = models.FloatField()
    num_actions = models.IntegerField()
    action_points = models.FloatField()
    avg_points_per_action = models.FloatField()
    last_action_on = models.CharField(null=True, max_length=255)
    keywords = ArrayField(base_field=models.CharField(max_length=255), null=True)
    activity_level = models.CharField(null=True, max_length=255)
    reliability = models.CharField(null=True, max_length=255)
    average_rating = models.FloatField()
    longest_streak = models.IntegerField()
    earnings_count = models.FloatField()
    follower_count = models.IntegerField()
    following_count = models.IntegerField()
    num_repeated_relationships  = models.IntegerField()
    verification_status = models.CharField(null=True, max_length=255)


    def email_if_not_supressed(self):
        is_on_global_suppression_list = EmailSupressionList.objects.filter(email__iexact=self.email).exists()
        if is_on_global_suppression_list:
            return ''
        return self.email


    objects = UserDirectoryManager()

    class Meta:
        managed = False

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
        has_representation = instance.as_representation.get('id')
        if not has_representation:
            instance.calculate_all()
            instance.save()
        return instance.as_representation

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
        ('status_update', 'Update Status'),
        ('account_disconnected', 'Account Disconnected'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    user = models.ForeignKey(User, related_name='actions', on_delete=models.SET_NULL, null=True, db_index=True)
    profile = models.ForeignKey('dashboard.Profile', related_name='actions', on_delete=models.CASCADE, null=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, db_index=True)
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

    def point_value(self):
        """

        Returns:
            int the Point value of this user action
        """
        return point_values.get(self.action, 0)


@receiver(post_save, sender=UserAction, dispatch_uid="post_add_ua")
def post_add_ua(sender, instance, created, **kwargs):
    if created:
        pass

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

    search_type = models.CharField(max_length=50, db_index=True)
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
        """Return the string representation of a BlockedUser."""
        return f'<BlockedUser: {self.handle}>'

class BlockedIP(SuperModel):
    """Define the structure of the BlockedIP."""

    addr = models.GenericIPAddressField(null=True, db_index=True)
    comments = models.TextField(default='', blank=True)
    active = models.BooleanField(help_text=_('Is the block active?'))

    def __str__(self):
        """Return the string representation of a BlockedIP."""
        return f'<BlockedIP: {self.addr}>'


class Sponsor(SuperModel):
    """Defines the Hackthon Sponsor"""

    name = models.CharField(max_length=255, help_text='sponsor Name')
    logo = models.ImageField(help_text='sponsor logo', blank=True)
    logo_svg = models.FileField(help_text='sponsor logo svg', blank=True)
    tribe = models.ForeignKey(Profile, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class HackathonEventQuerySet(models.QuerySet):
    """Handle the manager queryset for HackathonEvents."""

    def current(self):
        """Filter results down to current events only."""
        return self.filter(start_date__lt=timezone.now(), end_date__gt=timezone.now())

    def upcoming(self):
        """Filter results down to upcoming events only."""
        return self.filter(start_date__gt=timezone.now())

    def finished(self):
        """Filter results down to upcoming events only."""
        return self.filter(end_date__lt=timezone.now())


class HackathonEvent(SuperModel):
    """Defines the HackathonEvent model."""

    name = models.CharField(max_length=255)
    slug = models.SlugField(blank=True)
    short_code = models.CharField(max_length=5, default='', help_text='used in the chat for better channel grouping')
    logo = models.ImageField(blank=True)
    logo_svg = models.FileField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    banner = models.ImageField(null=True, blank=True)
    background_color = models.CharField(max_length=255, null=True, blank=True, help_text='hexcode for the banner, default to white')
    text_color = models.CharField(max_length=255, null=True, blank=True, help_text='hexcode for the text, default to black')
    border_color = models.CharField(max_length=255, null=True, blank=True, help_text='hexcode for the border, default to none')
    identifier = models.CharField(max_length=255, default='', help_text='used for custom styling for the banner')
    sponsors = models.ManyToManyField(Sponsor, through='HackathonSponsor')
    sponsor_profiles = models.ManyToManyField('dashboard.Profile', blank=True, limit_choices_to={'data__type': 'Organization'})
    show_results = models.BooleanField(help_text=_('Hide/Show the links to access hackathon results'), default=True)
    hackathon_summary = models.CharField(max_length=280, blank=True, help_text=_('280 char summary that shows up on hackathon cards on the hackathon list page'))
    description = models.TextField(default='', blank=True, help_text=_('HTML rich description.'))
    quest_link = models.CharField(max_length=255, blank=True)
    chat_channel_id = models.CharField(max_length=255, blank=True, null=True)
    use_circle = models.BooleanField(help_text=_('Use circle for the Hackathon'), default=False)
    visible = models.BooleanField(help_text=_('Can this HackathonEvent be seeing on /hackathons ?'), default=True)
    total_prize = models.CharField(max_length=255, null=True, blank=True, help_text='extra text to display next the event dates on the hackathon list page')

    default_channels = ArrayField(models.CharField(max_length=255), blank=True, default=list)
    objects = HackathonEventQuerySet.as_manager()
    display_showcase = models.BooleanField(default=False)
    showcase = JSONField(default=dict, blank=True, null=True)
    calendar_id = models.CharField(max_length=255, blank=True)
    metadata = JSONField(default=dict, blank=True)

    def __str__(self):
        """String representation for HackathonEvent.

        Returns:
            str: The string representation of a HackathonEvent.
        """
        return f'{self.name} - {self.start_date}'

    @property
    def relative_url(self):
        return f'hackathon/{self.slug}'

    @property
    def town_square_link(self):
        return f'townsquare/?tab=hackathon:{self.pk}'

    def get_absolute_url(self):
        """Get the absolute URL for the HackathonEvent.

        Returns:
            str: The absolute URL for the HackathonEvent.

        """
        return settings.BASE_URL + self.relative_url

    def get_total_prizes(self, force=False):
        if force or self.showcase.get('prizes_count') is None:
            prizes_count = Bounty.objects.filter(event=self).distinct().count()
            self.showcase['prizes_count'] = prizes_count
            self.save()

        return self.showcase.get('prizes_count', 0)

    def get_total_winners(self, force=False):
        if force or self.showcase.get('winners_count') is None:
            bounties = Bounty.objects.filter(event=self).distinct()
            self.showcase['winners_count'] = reduce(lambda total, prize: total + len(prize.paid), bounties, 0)
            self.save()

        return self.showcase.get('winners_count', 0)

    @property
    def onboard_url(self):
        return self.get_onboard_url()

    def get_onboard_url(self):
        """Get the absolute URL for the HackathonEvent.

        Returns:
            str: The absolute URL for the HackathonEvent.

        """
        return settings.BASE_URL + f'hackathon/onboard/{self.slug}/'

    @property
    def get_current_bounties(self):
        return Bounty.objects.filter(event=self, network='mainnet').current()

    @property
    def url(self):
        return self.get_absolute_url()

    @property
    def stats(self):
        stats = {
            'range': f"{self.start_date.strftime('%m/%d/%Y')} to {self.end_date.strftime('%m/%d/%Y')}",
            'logo': self.logo.url if self.logo else None,
            'num_bounties': self.get_current_bounties.count(),
            'num_bounties_done': self.get_current_bounties.filter(idx_status='done').count(),
            'num_bounties_open': self.get_current_bounties.filter(idx_status='open').count(),
            'total_volume': sum(self.get_current_bounties.values_list('_val_usd_db', flat=True)),
        }
        return stats

    def save(self, *args, **kwargs):
        """Define custom handling for saving HackathonEvent."""
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)


# method for updating
@receiver(pre_save, sender=HackathonEvent, dispatch_uid="psave_hackathonevent")
def psave_hackathonevent(sender, instance, **kwargs):

    hackathon_event = instance
    orgs = []
    try:
        sponsors = hackathon_event.sponsor_profiles.all()
        for sponsor_profile in sponsors:
            org = {
                'handle': sponsor_profile.handle,
                'display_name': sponsor_profile.name,
                'avatar_url': sponsor_profile.avatar_url,
                'org_name': sponsor_profile.handle,
                'follower_count': sponsor_profile.tribe_members.all().count(),
                'bounty_count': sponsor_profile.bounties.count()
            }
            orgs.append(org)
    except:
        pass
    instance.metadata['orgs'] = orgs


    from django.contrib.contenttypes.models import ContentType
    from search.models import SearchResult
    if instance.pk:
        SearchResult.objects.update_or_create(
            source_type=ContentType.objects.get(app_label='dashboard', model='hackathonevent'),
            source_id=instance.pk,
            defaults={
                "created_on":instance.created_on,
                "title":instance.name,
                "description":instance.stats['range'],
                "url":instance.onboard_url,
                "visible_to":None,
                'img_url': instance.logo.url if instance.logo else None,
            }
            )



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
    chat_channel_id = models.CharField(max_length=255, blank=True, null=True)


class HackathonProject(SuperModel):
    PROJECT_STATUS = [
        ('invalid', 'invalid'),
        ('pending', 'pending'),
        ('accepted', 'accepted'),
        ('completed', 'completed'),
    ]
    name = models.CharField(max_length=255)
    hackathon = models.ForeignKey(
        'HackathonEvent',
        related_name='project_event',
        on_delete=models.CASCADE,
        help_text='Hackathon event'
    )
    logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('Project Logo')
    )
    profiles = models.ManyToManyField(
        'dashboard.Profile',
        related_name='project_profiles',
    )
    work_url = models.URLField(help_text='Repo or PR url')
    summary = models.TextField(default='', blank=True)
    bounty = models.ForeignKey(
        'dashboard.Bounty',
        related_name='project_bounty',
        on_delete=models.CASCADE,
        help_text='bounty prize url'
    )
    badge = models.URLField(
        blank=True,
        null=True,
        db_index=True,
        help_text='badge img url'
    )
    status = models.CharField(
        max_length=20,
        choices=PROJECT_STATUS,
        blank=True,
        db_index=True,
    )
    message = models.CharField(
        max_length=150,
        blank=True,
        default=''
    )
    looking_members = models.BooleanField(default=False)
    chat_channel_id = models.CharField(max_length=255, blank=True, null=True)
    winner = models.BooleanField(default=False, db_index=True)
    extra = JSONField(default=dict, blank=True, null=True)
    categories = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    tech_stack = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    grant_obj = models.ForeignKey(
        'grants.Grant',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Link to grant if project is converted to grant')
    )

    class Meta:
        ordering = ['-name']

    def __str__(self):
        return f"{self.name} - {self.bounty} on {self.created_on}"

    def url(self):
        slug = slugify(unidecode(self.name))
        return f'/hackathon/projects/{self.hackathon.slug}/{slug}/'

    def url_project_page(self):
        slug = slugify(unidecode(self.name))
        return f'/hackathon/{self.hackathon.slug}/projects/{self.pk}/{slug}'

    def url_bounty_page(self):
        slug = slugify(unidecode(self.name))
        return f'/hackathon/{self.bounty.org_name}/projects/{self.pk}/{slug}'

    def get_absolute_url(self):
        return self.url()

    def to_json(self):
        profiles = [
            {
                'handle': profile.handle,
                'name': profile.name,
                'email': profile.email,
                'payout_address': profile.preferred_payout_address,
                'url': profile.url,
                'avatar': profile.active_avatar.avatar_url if profile.active_avatar else '',
                'id': profile.pk
            } for profile in self.profiles.all()
        ]
        profile_ids = [profile['id'] for profile in profiles]

        submission = BountyFulfillment.objects.filter(project=self).first()
        # Backward compatibility, for bounty fulfillment without a project assigned
        if not submission:
            submission = BountyFulfillment.objects.filter(profile_id__in=profile_ids, bounty=self.bounty).first()

        paid = False
        if submission:
            paid = submission.payout_status == 'done'

        response = {
            'pk': self.pk,
            'name': self.name,
            'logo': self.logo.url if self.logo else '',
            'badge': self.badge,
            'profiles': profiles,
            'work_url': self.work_url,
            'summary': self.summary,
            'status': self.status,
            'submitted': bool(submission),
            'submition_date': date(submission.created_on, 'Y-m-d H:i') if submission else '',
            'message': self.message,
            'chat_channel_id': self.chat_channel_id,
            'paid': paid,
            'payment_date': date(submission.accepted_on, 'Y-m-d H:i') if paid else '',
            'winner': self.winner,
            'grant_obj': None,
            'extra': self.extra,
            'timestamp': submission.created_on.timestamp() if submission else 0
        }

        if self.grant_obj:
            response['grant_obj'] = {
                'id': self.grant_obj.pk,
                'title': self.grant_obj.title,
                'description': self.grant_obj.description,
                'reference_url': self.grant_obj.reference_url,
                'github_project_url': self.grant_obj.github_project_url,
                'region': self.grant_obj.region,
                'grant_type': self.grant_obj.grant_type.label
            }

        return response


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
    private = models.BooleanField(help_text=_('whether this feedback can be shown publicly'), default=True)

    def __str__(self):
        """Return the string representation of a Bounty."""
        return f'<Feedback Bounty #{self.bounty} - from: {self.sender_profile} to: {self.receiver_profile}>'

    def visible_to(self, user):
        """Whether this user can see the feedback ornot"""
        if not self.private:
            return True
        if user.is_staff:
            return True
        if not user.is_authenticated:
            return False
        if self.sender_profile.handle == user.profile.handle:
            return True
        return False

    @property
    def anonymized_comment(self):
        import re
        replace_str = [
            self.bounty.bounty_owner_github_username,
            ]
        for profile in [self.sender_profile, self.receiver_profile, self.bounty.org_profile]:
            if profile:
                replace_str.append(profile.handle)
                name = profile.data.get('name')
                if name:
                    name = name.split(' ')
                    for ele in name:
                        replace_str.append(ele)

        review = self.comment
        for ele in replace_str:
            review = re.sub(ele, 'NAME', review, flags=re.I)

        return review


class Coupon(SuperModel):
    code = models.CharField(unique=True, max_length=10)
    fee_percentage = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    expiry_date = models.DateField()

    def __str__(self):
        """Return the string representation of Coupon."""
        return f'code: {self.code} | fee: {self.fee_percentage} %'


class ProfileView(SuperModel):
    """Records profileviews ."""

    target = models.ForeignKey('dashboard.Profile', related_name='viewed_by', on_delete=models.CASCADE, db_index=True)
    viewer = models.ForeignKey('dashboard.Profile', related_name='viewed_profiles', on_delete=models.CASCADE, db_index=True)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f"{self.viewer} => {self.target} on {self.created_on}"


@receiver(post_save, sender=ProfileView, dispatch_uid="post_add_profileview")
def post_add_profileview(sender, instance, created, **kwargs):
    # disregard other profileviews added within 30 minutes of each other
    if created:
        dupes = ProfileView.objects.exclude(pk=instance.pk)
        dupes = dupes.filter(created_on__gte=(instance.created_on - timezone.timedelta(minutes=30)))
        dupes = dupes.filter(created_on__lte=(instance.created_on + timezone.timedelta(minutes=30)))
        dupes = dupes.filter(target=instance.target)
        dupes = dupes.filter(viewer=instance.viewer)
        for dupe in dupes:
            dupe.delete()


class Earning(SuperModel):
    """Records Earning - the generic object for all earnings on the platform ."""

    from_profile = models.ForeignKey('dashboard.Profile', related_name='sent_earnings', on_delete=models.CASCADE, db_index=True, null=True)
    to_profile = models.ForeignKey('dashboard.Profile', related_name='earnings', on_delete=models.CASCADE, db_index=True, null=True)
    org_profile = models.ForeignKey('dashboard.Profile', related_name='org_earnings', on_delete=models.CASCADE, db_index=True, null=True, blank=True)
    value_usd = models.DecimalField(decimal_places=2, max_digits=50, null=True)
    source_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    source_id = models.PositiveIntegerField(db_index=True)
    source = GenericForeignKey('source_type', 'source_id')
    network = models.CharField(max_length=50, default='')
    url = models.CharField(max_length=500, default='')
    txid = models.CharField(max_length=255, default='')
    token_name = models.CharField(max_length=255, default='')
    token_value = models.DecimalField(decimal_places=18, max_digits=50, default=0)
    network = models.CharField(max_length=50, default='')
    success = models.BooleanField(default=False, help_text=_('Was txn successful?'))


    def has_read_perms(self, profile):
        if self.source_type_human == 'grant':
            return self.source.team_members.filter(pk__in=profile.pk)
        if self.source_type_human in ['tip', 'kudos transfer']:
            return self.source.receiver_profile == profile or self.source.sender_profile == profile
        if self.source_type_human == 'bounty':
            return self.source.profile == profile or self.source.funder_profile == profile
        return False

    @property
    def source_type_human(self):
        source_type = str(self.source_type)
        if source_type == 'contribution':
            source_type = 'grant'
        return source_type


    def __str__(self):
        return f"{self.from_profile} => {self.to_profile} of ${self.value_usd} on {self.created_on} for {self.source}"

    def create_auto_follow(self):
        profiles = [self.to_profile, self.from_profile, self.org_profile]
        count = 0
        for p1 in profiles:
            for p2 in profiles:
                if not p1 or not p2:
                    continue
                if p1.pk == p2.pk:
                    continue
                if not p1.dont_autofollow_earnings:
                    try:
                        TribeMember.objects.update_or_create(
                            profile=p1,
                            org=p2,
                            defaults={'why':'auto'}
                            )
                        count += 1
                    except:
                        pass
        return count

@receiver(post_save, sender=Earning, dispatch_uid="post_save_earning")
def post_save_earning(sender, instance, created, **kwargs):
    if created:
        instance.create_auto_follow()

        from economy.utils import watch_txn
        if instance.txid and instance.network == 'mainnet':
                watch_txn(instance.txid)

def get_my_earnings_counter_profiles(profile_pk):
    # returns profiles that a user has done business with
    from_profile_earnings = Earning.objects.filter(from_profile=profile_pk)
    to_profile_earnings = Earning.objects.filter(to_profile=profile_pk)
    org_profile_earnings = Earning.objects.filter(org_profile=profile_pk)

    from_profile_earnings = list(from_profile_earnings.values_list('to_profile', flat=True))
    to_profile_earnings = list(to_profile_earnings.values_list('from_profile', flat=True))
    org_profile_earnings = list(org_profile_earnings.values_list('from_profile', flat=True)) + list(org_profile_earnings.values_list('to_profile', flat=True))

    all_earnings = from_profile_earnings + to_profile_earnings + org_profile_earnings
    return all_earnings


def get_my_grants(profile):
    # returns grants that a profile has done business with
    relevant_grants = list(profile.grant_contributor.all().values_list('grant', flat=True)) \
        + list(profile.grant_teams.all().values_list('pk', flat=True)) \
        + list(profile.grant_admin.all().values_list('pk', flat=True)) \
        + list(profile.grant_phantom_funding.values_list('grant__pk', flat=True))
    return relevant_grants


class PortfolioItem(SuperModel):
    """Define the structure of PortfolioItem object."""

    title = models.CharField(max_length=255)
    tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    link = models.URLField(null=True)
    profile = models.ForeignKey('dashboard.Profile', related_name='portfolio_items', on_delete=models.CASCADE, db_index=True)

    def __str__(self):
        return f"{self.title} by {self.profile.handle}"


class ProfileStatHistory(SuperModel):
    """ProfileStatHistory - generalizable model for tracking history of a profiles info"""

    profile = models.ForeignKey('dashboard.Profile', related_name='stats', on_delete=models.CASCADE, db_index=True)
    key = models.CharField(max_length=50, default='', db_index=True)
    payload = JSONField(default=dict, blank=True, null=True)

    def __str__(self):
        return f"{self.key} <> {self.profile.handle}"


class TribeMember(SuperModel):
    MEMBER_STATUS = [
        ('accepted', 'accepted'),
        ('pending', 'pending'),
        ('rejected', 'rejected'),
    ]
    #from
    profile = models.ForeignKey('dashboard.Profile', related_name='follower', on_delete=models.CASCADE)
    # to
    org = models.ForeignKey('dashboard.Profile', related_name='org', on_delete=models.CASCADE, null=True, blank=True)
    leader = models.BooleanField(default=False, help_text=_('tribe leader'))
    title = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(
        max_length=20,
        choices=MEMBER_STATUS,
        blank=True
    )
    why = models.CharField(
        max_length=20,
        blank=True
    )

    @property
    def mutual_follow(self):
        return TribeMember.objects.filter(profile=self.org, org=self.profile).exists()

    @property
    def mutual_follower(self):
        tribe_following = Subquery(TribeMember.objects.filter(profile=self.profile).values_list('org', flat=True))
        return TribeMember.objects.filter(org=self.org, profile__in=tribe_following).exclude(profile=self.profile)

    @property
    def mutual_following(self):
        tribe_following = Subquery(TribeMember.objects.filter(org=self.profile).values_list('profile', flat=True))
        return TribeMember.objects.filter(org__in=tribe_following, profile=self.org).exclude(org=self.org)


class Poll(SuperModel):
    title = models.CharField(max_length=350, blank=True, null=True)
    active = models.BooleanField(default=False)
    hackathon = models.ManyToManyField(HackathonEvent)


class PollMedia(SuperModel):
    name = models.CharField(max_length=350)
    image = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('Poll media asset')
    )

    def __str__(self):
        return f'{self.id} - {self.name}'


class Question(SuperModel):
    TYPE_QUESTIONS = (
        ('SINGLE_OPTION', 'Single option'),
        ('SINGLE_CHOICE', 'Single Choice'),
        ('MULTIPLE_CHOICE', 'Multiple Choices'),
        ('OPEN', 'Open'),
    )

    TYPE_HOOKS = (
        ('NO_ACTION', 'No trigger any action'),
        ('TOWNSQUARE_INTRO', 'Create intro on Townsquare'),
        ('LOOKING_TEAM_PROJECT', 'Looking for team or project')
    )

    hook = models.CharField(default='NO_ACTION', choices=TYPE_HOOKS, max_length=50)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True, blank=True)
    question_type = models.CharField(choices=TYPE_QUESTIONS, max_length=50, blank=False, null=False)
    text = models.CharField(max_length=350, blank=True, null=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    header = models.ForeignKey(PollMedia, null=True, on_delete=models.SET_NULL)
    mandatory = models.BooleanField(default=False)
    minimum_character_count = models.PositiveIntegerField(default=0)

    class Meta(object):
        ordering = ['order']

    def __str__(self):
        return f'Question.{self.id} {self.text}'


class Option(SuperModel):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=350, blank=True, null=True)

    def __str__(self):
        return f'Option.{self.id} {self.text}'


class Answer(SuperModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    open_response = models.CharField(max_length=350, blank=True, null=True)
    choice = models.ForeignKey(Option, on_delete=models.CASCADE, null=True, blank=True)
    checked = models.BooleanField(default=False)
    hackathon = models.ForeignKey(HackathonEvent, null=True, on_delete=models.CASCADE)


@receiver(post_save, sender=Answer, dispatch_uid='hooks_on_question_response')
def psave_answer(sender, instance, created, **kwargs):
    if created:
        if instance.question.hook == 'TOWNSQUARE_INTRO':
            registration = HackathonRegistration.objects.filter(hackathon=instance.hackathon,
                                                                registrant=instance.user.profile).first()

            Activity.objects.create(
                profile=instance.user.profile,
                hackathonevent=instance.hackathon,
                activity_type='hackathon_new_hacker',
                metadata={
                    'answer': instance.id,
                    'intro_text': f'{instance.open_response or ""} #intro',
                    'looking_members': registration.looking_team_members if registration else False,
                    'looking_project': registration.looking_project if registration else False,
                    'hackathon_registration': registration.id if registration else 0
                }
            )
        elif instance.question.hook == 'LOOKING_TEAM_PROJECT':
            registration = HackathonRegistration.objects.filter(hackathon=instance.hackathon,
                                                                registrant=instance.user.profile).first()
            print(instance)
            if registration:
                if instance.choice.text.lower().find('team') != -1:
                    registration.looking_team_members = True

                if instance.choice.text.lower().find('project') != -1:
                    registration.looking_project = True

                registration.save()

                activity = Activity.objects.filter(
                    profile=instance.user.profile,
                    hackathonevent=instance.hackathon,
                    activity_type='hackathon_new_hacker').last()

                if activity:
                    activity.metadata['looking_team_members'] = registration.looking_team_members
                    activity.metadata['looking_project'] = registration.looking_project
                    activity.save()


class Investigation(SuperModel):
    profile = models.ForeignKey(
        'dashboard.Profile', on_delete=models.CASCADE, related_name='investigations', blank=True
    )
    key = models.CharField(max_length=350, blank=True, default='', db_index=True)
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return f"{self.profile.handle} / {self.key}"

    def investigate_sybil(instance):
        htmls = []
        visits = instance.actions.filter(action='Visit')
        userActions = visits
        from django.db.models import Count
        import time
        from django.contrib.humanize.templatetags.humanize import naturaltime
        ipAddresses = (userActions.values('ip_address').annotate(Count("id")).order_by('-id__count'))
        cities = (userActions.values('location_data__city').annotate(Count("id")).order_by('-id__count'))
        total_sybil_score = 0

        htmls.append(f'User has visited the site {visits.count()} times')
        if visits.count() > 25:
            total_sybil_score -= 2
            htmls.append('(REDEMPTIONx2)')
        elif visits.count() > 10:
            total_sybil_score -= 1
            htmls.append('(REDEMPTION)')
        elif visits.count() < 1:
            total_sybil_score += 1
            htmls.append('(DING)')

        htmls.append(f'Bright ID Verified: {instance.is_brightid_verified}')
        if instance.is_brightid_verified:
            total_sybil_score -= 2
            htmls.append('(REDEMPTIONx2)')

        htmls.append(f'Idena Verified: {instance.is_idena_verified}')
        if instance.is_idena_verified:
            total_sybil_score -= 4
            htmls.append('(REDEMPTIONx4)')

        htmls.append(f'Twitter Verified: {instance.is_twitter_verified}')
        if instance.is_twitter_verified:
            total_sybil_score -= 1
            htmls.append('(REDEMPTIONx1)')

        htmls.append(f'Google Verified: {instance.is_google_verified}')
        if instance.is_google_verified:
            total_sybil_score -= 1
            htmls.append('(REDEMPTIONx1)')

        htmls.append(f'POAP Verified: {instance.is_poap_verified}')
        if instance.is_poap_verified:
            total_sybil_score -= 1
            htmls.append('(REDEMPTIONx1)')

        htmls.append(f'Facebook Verified: {instance.is_facebook_verified}')
        if instance.is_facebook_verified:
            total_sybil_score -= 1
            htmls.append('(REDEMPTIONx1)')

        htmls.append(f'POH Verified: {instance.is_poh_verified}')
        if instance.is_poh_verified:
            total_sybil_score -= 1
            htmls.append('(REDEMPTIONx1)')

        if instance.squelches.filter(active=True).exists():
            htmls.append('USER HAS ACTIVE SQUELCHES')
            total_sybil_score += 3
            htmls.append('(DINGx3)')

        if not instance.sms_verification:
            htmls.append('Not SMS Verified (DING)')
            total_sybil_score += 1
        else:
            htmls.append('SMS Verified')

        htmls += [f"<a href=/_administrationdashboard/useraction/?profile={instance.pk}>View Recent User Actions</a><BR>"]

        htmls += [ f"Github Created: {instance.github_created_on.strftime('%Y-%m-%d')} ({naturaltime(instance.github_created_on)})<BR>"]

        if instance.github_created_on > (timezone.now() - timezone.timedelta(days=7)):
            htmls.append('New Github (DING)')
            total_sybil_score += 1
        if instance.github_created_on > (timezone.now() - timezone.timedelta(days=1)):
            total_sybil_score += 1
            htmls.append('VERY New Github (DING)')
        if instance.created_on > (timezone.now() - timezone.timedelta(days=1)):
            total_sybil_score += 1
            htmls.append('New Profile (DING)')

        print(f" - preferred payout {time.time()}")
        if instance.preferred_payout_address:
            htmls.append('Preferred Payout Address')
            htmls.append(f' - {instance.preferred_payout_address}')
            other_Profiles = Profile.objects.filter(preferred_payout_address=instance.preferred_payout_address).exclude(pk=instance.pk).values_list('handle', flat=True)
            if other_Profiles.count() > 0:
                total_sybil_score += 1
                htmls.append('Other Profiles with this addr (DING)')
            if other_Profiles.count() > 3:
                total_sybil_score += 1
                htmls.append('Many other Profiles with this addr (DING)')
            url = f'/_administrationdashboard/profile/?preferred_payout_address={instance.preferred_payout_address}'
            _other_Profiles = [f'<a href=/{handle}>{handle}</a>' for handle in other_Profiles]
            htmls += [f" -- <a href={url}>{len(_other_Profiles)} other profiles share this ppa: {', '.join(list(_other_Profiles))}</a><BR>"]

        print(f" - ip ({len(ipAddresses)}) {time.time()}")
        htmls.append('IP Addresses')
        htmls.append("<div style='max-height: 300px; overflow-y: scroll'>")
        ip_flagged = False
        for ip in ipAddresses:
            html = f"- <a href=/_administrationdashboard/useraction/?ip_address={ip['ip_address']}>{ip['ip_address']} ({ip['id__count']} Visits)</a>"
            other_Profiles = UserAction.objects.filter(ip_address=ip['ip_address'], profile__isnull=False).exclude(profile=instance).distinct('profile').values_list('profile__handle', flat=True)
            if len(other_Profiles):
                _other_Profiles = [f'<a href=/{handle}>{handle}</a>' for handle in other_Profiles]
                html += f"<BR> -- {len(_other_Profiles)} other profiles share this IP: {', '.join(list(_other_Profiles))}"
            if other_Profiles.count() > 0:
                if not ip_flagged:
                    ip_flagged = True
                    total_sybil_score += 1
                    htmls.append('Other Profiles with this IP Addr (DING)')

            htmls.append(html)
        htmls.append("</div>'")

        print(f" - cities ({len(cities)}) {time.time()}")
        htmls.append('Cities')
        htmls.append("<div style='max-height: 300px; overflow-y: scroll'>")
        for city in cities:
            html = f"- <a href=/_administrationdashboard/useraction/?location_data__city={city['location_data__city']}>{city['location_data__city']} ({city['id__count']} Visits)</a>"
            htmls.append(html)
        htmls.append("</div>'")

        earnings = instance.earnings.filter(network='mainnet').all()
        print(f" - Earnings ({len(earnings)}) {time.time()}")
        htmls.append('Earnings')
        htmls.append("<div style='max-height: 300px; overflow-y: scroll'>")
        for earning in earnings:
            html = f"- <a href={earning.admin_url}>{earning}</a>"
            htmls.append(html)
            #TODO: if shared with a known sybil, then total_sybil_score += 1
        htmls.append("</div>'")

        sent_earnings = instance.sent_earnings.filter(network='mainnet').all()
        print(f" - Sent Earnings ({len(sent_earnings)}) {time.time()}")
        htmls.append('Sent Earnings')
        htmls.append("<div style='max-height: 300px; overflow-y: scroll'>")
        for earning in sent_earnings:
            html = f"- <a href={earning.admin_url}>{earning}</a>"
            htmls.append(html)
        htmls.append("</div>'")

        htmls += [f"SYBIL_SCORE: {total_sybil_score} "]

        print(f" - End {time.time()}")
        htmls = ("<BR>".join(htmls))
        instance.investigations.filter(key='sybil').delete()
        Investigation.objects.create(
            profile=instance,
            description=htmls,
            key='sybil',
        )

        instance.sybil_score = total_sybil_score


class ObjectView(SuperModel):
    """Records object views ."""
    viewer = models.ForeignKey(User, related_name='objectviews', on_delete=models.SET_NULL, null=True, db_index=True)
    target_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(db_index=True)
    target = GenericForeignKey('target_type', 'target_id')
    view_type = models.CharField(max_length=255)

    class Meta:
        ordering = ['-pk']

    def __str__(self):
        return f"{self.viewer} => {self.target} on {self.created_on}"


class ProfileVerification(SuperModel):
    profile = models.ForeignKey('dashboard.Profile', on_delete=models.CASCADE, related_name='verifications')
    caller_type = models.CharField(max_length=20, null=True, blank=True)
    carrier_error_code = models.CharField(max_length=10, null=True, blank=True)
    mobile_network_code = models.CharField(max_length=10, null=True, blank=True)
    mobile_country_code = models.PositiveSmallIntegerField(default=0, null=True)
    carrier_name = models.CharField(max_length=100, null=True, blank=True)
    carrier_type = models.CharField(max_length=20, null=True, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    phone_number = models.CharField(max_length=150, null=True, blank=True)
    delivery_method = models.CharField(max_length=255, null=True, blank=True)
    validation_passed = models.BooleanField(help_text=_('Did the initial validation pass?'), default=False)
    validation_comment = models.CharField(max_length=255, null=True, blank=True)
    success = models.BooleanField(help_text=_('Was a successful transaction verification?'), default=False)


    def __str__(self):
        return f'{self.phone_number} ({self.caller_type}) from {self.country_code} request ${self.delivery_method} code at {self.created_on}'


class HackathonWorkshop(SuperModel):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    cover = models.ImageField()
    hackathon = models.ForeignKey(
        'dashboard.HackathonEvent',
        related_name='workshop_event',
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    speaker = models.ForeignKey(
        'dashboard.Profile',
        related_name='workshop_speaker',
        on_delete=models.CASCADE,
        help_text='Main speaker profile.'
    )
    url = models.URLField(help_text='Blog link, calendar link, or other.')
    visible = models.BooleanField(help_text=_('Can this HackathonWorkshop be seen on /hackathons ?'), default=True)


class TransactionHistory(SuperModel):

    earning = models.ForeignKey('dashboard.Earning', related_name='history', on_delete=models.CASCADE, db_index=True, null=True)
    txid = models.CharField(max_length=255, default='')
    status = models.CharField(max_length=50, default='', db_index=True)
    payload = JSONField(default=dict, blank=True, null=True)
    network = models.CharField(max_length=255, blank=True, db_index=True)
    captured_at = models.DateTimeField()

    def __str__(self):
        return f"{self.status} <> {self.earning.pk} at {self.captured_at}"


class MediaFile(SuperModel):
    filename = models.CharField(max_length=350, blank=True, null=True)
    file = models.FileField(upload_to=get_upload_filename, null=True, blank=True, help_text=_('The file.'), )

    def __str__(self):
        return f'{self.id} - {self.filename}'
