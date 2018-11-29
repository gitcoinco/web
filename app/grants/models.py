# -*- coding: utf-8 -*-
"""Define the Grant models.

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
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel
from grants.utils import get_upload_filename


class GrantQuerySet(models.QuerySet):
    """Define the Grant default queryset and manager."""

    def active(self):
        """Filter results down to active grants only."""
        return self.filter(active=True)

    def inactive(self):
        """Filter results down to inactive grants only."""
        return self.filter(active=False)

    def keyword(self, keyword):
        """Filter results to all Grant objects containing the keywords.

        Args:
            keyword (str): The keyword to search title, description, and reference URL by.

        Returns:
            dashboard.models.GrantQuerySet: The QuerySet of grants filtered by keyword.

        """
        return self.filter(
            Q(description__icontains=keyword) |
            Q(title__icontains=keyword) |
            Q(reference_url__icontains=keyword)
        )


class Grant(SuperModel):
    """Define the structure of a Grant."""

    class Meta:
        """Define the metadata for Grant."""

        ordering = ['-created_on']

    active = models.BooleanField(default=True, help_text=_('Whether or not the Grant is active.'))
    title = models.CharField(default='', max_length=255, help_text=_('The title of the Grant.'))
    slug = AutoSlugField(populate_from='title')
    description = models.TextField(default='', blank=True, help_text=_('The description of the Grant.'))
    reference_url = models.URLField(blank=True, help_text=_('The associated reference URL of the Grant.'))
    logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('The Grant logo image.'),
    )
    logo_svg = models.FileField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('The Grant logo SVG.'),
    )
    admin_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The wallet address for the administrator of this Grant.'),
    )
    amount_goal = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The contribution goal amount for the Grant.'),
    )
    amount_received = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The total amount received for the Grant.'),
    )
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Grant.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='',
        help_text=_('The token symbol to be used with the Grant.'),
    )
    contract_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The contract address of the Grant.'),
    )
    contract_version = models.DecimalField(
        default=0,
        decimal_places=0,
        max_digits=3,
        help_text=_('The contract version the Grant.'),
    )
    transaction_hash = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction hash of the Grant.'),
    )
    metadata = JSONField(
        default=dict,
        blank=True,
        help_text=_('The Grant metadata. Includes creation and last synced block numbers.'),
    )
    network = models.CharField(
        max_length=8,
        default='mainnet',
        help_text=_('The network in which the Grant contract resides.'),
    )
    required_gas_price = models.DecimalField(
        default='0',
        decimal_places=0,
        max_digits=50,
        help_text=_('The required gas price for the Grant.'),
    )
    admin_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_admin',
        on_delete=models.CASCADE,
        help_text=_('The Grant administrator\'s profile.'),
        null=True,
    )
    team_members = models.ManyToManyField(
        'dashboard.Profile',
        related_name='grant_teams',
        help_text=_('The team members contributing to this Grant.'),
    )

    # Grant Query Set used as manager.
    objects = GrantQuerySet.as_manager()

    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, active: {self.active}, title: {self.title}, description: {self.description}"

    def percentage_done(self):
        """Return the percentage of token received based on the token goal."""
        return ((self.amount_received / self.amount_goal) * 100)



class Milestone(SuperModel):
    """Define the structure of a Grant Milestone"""

    title = models.CharField(max_length=255, help_text=_('The Milestone title.'))
    description = models.TextField(help_text=_('The Milestone description.'))
    due_date = models.DateField(help_text=_('The requested Milestone completion date.'))
    completion_date = models.DateField(
        default=None,
        blank=True,
        null=True,
        help_text=_('The Milestone completion date.'),
    )
    grant = models.ForeignKey(
        'Grant',
        related_name='milestones',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Grant.'),
    )

    def __str__(self):
        """Return the string representation of a Milestone."""
        return (
            f" id: {self.pk}, title: {self.title}, description: {self.description}, "
            f"due_date: {self.due_date}, completion_date: {self.completion_date}, grant: {self.grant_id}"
        )


class UpdateQuerySet(models.QuerySet):
    """Define the Update default queryset and manager."""

    pass


class Update(SuperModel):
    """Define the structure of a Grant Update."""
    title = models.CharField(
        default='',
        max_length=255,
        help_text=_('The title of the Grant.')
    )
    description = models.TextField(
        default='',
        blank=True,
        help_text=_('The description of the Grant.')
    )
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='updates',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Grant.'),
    )


class SubscriptionQuerySet(models.QuerySet):
    """Define the Subscription default queryset and manager."""

    pass


class Subscription(SuperModel):
    """Define the structure of a subscription agreement."""

    active = models.BooleanField(default=True, help_text=_('Whether or not the Subscription is active.'))
    subscription_hash = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s Subscription hash.'),
    )
    contributor_signature = models.CharField(default='', max_length=255, help_text=_('The contributor\'s signature.'))
    contributor_address = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s wallet address of the Subscription.'),
    )
    amount_per_period = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The promised contribution amount per period.'),
    )
    real_period_seconds = models.DecimalField(
        default=2592000,
        decimal_places=0,
        max_digits=50,
        help_text=_('The real payout frequency of the Subscription in seconds.'),
    )
    frequency_unit = models.CharField(
        max_length=255,
        default='',
        help_text=_('The text version of frequency units e.g. days, months'),
    )
    frequency = models.DecimalField(
        default=0,
        decimal_places=0,
        max_digits=50,
        help_text=_('The real payout frequency of the Subscription in seconds.'),
    )
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Subscription.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token symbol to be used with the Subscription.'),
    )
    gas_price = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The required gas price for the Subscription.'),
    )
    network = models.CharField(
        max_length=8,
        default='mainnet',
        help_text=_('The network in which the Subscription resides.'),
    )
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='subscriptions',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Grant.'),
    )
    contributor_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_contributor',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The Subscription contributor\'s Profile.'),
    )

    def __str__(self):
        """Return the string representation of a Subscription."""
        return f"id: {self.pk}, active: {self.active}, subscription_hash: {self.subscription_hash}"


class ContributionQuerySet(models.QuerySet):
    """Define the Contribution default queryset and manager."""

    pass


class Contribution(SuperModel):
    """Define the structure of a subscription agreement."""

    tx_id = models.CharField(max_length=255, default='0x0', help_text=_('The transaction ID of the Contribution.'))
    from_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The wallet address tokens are sent from.'),
    )
    to_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The wallet address tokens are sent to.'),
    )
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Subscription.'),
    )
    token_amount = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The promised contribution amount per period.'),
    )
    period_seconds = models.DecimalField(
        default=0,
        decimal_places=0,
        max_digits=50,
        help_text=_('The number of seconds thats constitues a period.'),
    )
    gas_price = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The amount of token used to incentivize subminers.'),
    )
    nonce = models.DecimalField(
        default=0,
        decimal_places=0,
        max_digits=50,
        help_text=_('The of the subscription metaTx.'),
    )
    subscription = models.ForeignKey(
        'grants.Subscription',
        related_name='subscription_contribution',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Subscription.'),
    )
