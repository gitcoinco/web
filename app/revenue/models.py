# -*- coding: utf-8 -*-
"""Define models.

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
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dashboard.models import SendCryptoAsset
from economy.models import SuperModel


class ALaCartePurchase(SendCryptoAsset):
    """Model that represents a ALaCartePurchase.

    """
    purchase = JSONField(default=dict, blank=True)
    purchase_expires = models.DateTimeField(null=True, blank=True)
    sku = models.ForeignKey(
        'revenue.SKU',
        related_name='alacartegoodpurchases',
        on_delete=models.CASCADE,
        help_text=_('The feature that was purchased'),
        null=False,
    )


class SKU(SuperModel):
    """Model that represents a SKU (something that can be delivered).

    """
    slug = models.CharField(max_length=255, help_text=_('The Slug'))
    name = models.CharField(max_length=255, help_text=_('The SKU Name'))
    sku = models.CharField(max_length=255, help_text=_('The SKU'))

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.name} / {self.sku}"


class Plan(SuperModel):
    """Model that represents a Subscription Plan

    """
    slug = models.CharField(max_length=255, help_text=_('The Slug'))
    name = models.CharField(max_length=255, help_text=_('The SKU Name'))
    cost_per_period = models.DecimalField(
        decimal_places=2,
        max_digits=50,
        help_text=_('Cost of this plan in USD'),
    )
    period_length_seconds = models.PositiveIntegerField()
    bounties_discount_percent = models.IntegerField(default=0)
    grant = models.OneToOneField('grants.grant', related_name='paid_plan', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.slug} / {self.cost_per_period}"


class PlanItem(SuperModel):
    """Model that represents an item in a plan

    """
    plan = models.ForeignKey(
        'revenue.plan',
        related_name='items',
        on_delete=models.CASCADE,
        help_text=_('The plan that this item is in'),
    )

    sku = models.ForeignKey(
        'revenue.sku',
        related_name='planitems',
        on_delete=models.CASCADE,
        help_text=_('The sku that is in this item'),
    )
    quantity = models.PositiveIntegerField()

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.plan} / {self.sku}"


class Subscription(SuperModel):
    """Model that represents a subscription

    """
    plan = models.ForeignKey(
        'revenue.plan',
        related_name='subscriptions',
        on_delete=models.CASCADE,
        help_text=_('The plan for this subscription'),
    )

    grant_subscription = models.ForeignKey(
        'grants.subscription',
        related_name='revenue_subscription',
        on_delete=models.CASCADE,
        help_text=_('The grants.subscription for this revenue subscription'),
    )

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.plan} / {self.grant_subscription}"


class Coupon(SuperModel):
    """Model that represents a coupon for this plans

    """
    plan = models.ForeignKey(
        'revenue.plan',
        related_name='coupons',
        on_delete=models.CASCADE,
        help_text=_('The plan that this coupon is for'),
    )
    code = models.CharField(max_length=255, help_text=_('The Coupon Code'))
    discount_per_period = models.DecimalField(
        decimal_places=2,
        max_digits=50,
        help_text=_('Discount, per period, to be applied to this plan in USD. Must not be more than the price per period of the plan.'),
    )
    start_date = models.DateTimeField(
        help_text=_('The start date for validity of this coupon'),
        default=timezone.datetime(1990, 1, 1),
    )
    end_date = models.DateTimeField(
        help_text=_('The end date for validity of this coupon'),
        default=timezone.datetime(1990, 1, 1),
    )

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.code} / {self.discount_per_period}"
