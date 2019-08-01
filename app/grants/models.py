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
import logging
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.timezone import localtime
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel
from economy.utils import ConversionRateNotFoundError, convert_amount
from gas.utils import eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from grants.utils import get_upload_filename
from web3 import Web3

logger = logging.getLogger(__name__)


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
    description_rich = models.TextField(default='', blank=True, help_text=_('HTML rich description.'))
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
        help_text=_('The wallet address where subscription funds will be sent.'),
    )
    contract_owner_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The wallet address that owns the subscription contract and is able to call endContract()'),
    )
    amount_goal = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The monthly contribution goal amount for the Grant in DAI.'),
    )
    monthly_amount_subscribed = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The monthly subscribed to by contributors USDT/DAI.'),
    )
    amount_received = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The total amount received for the Grant in USDT/DAI.'),
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
    deploy_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for contract deployment.'),
    )
    cancel_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for endContract.'),
    )
    contract_version = models.DecimalField(
        default=0,
        decimal_places=0,
        max_digits=3,
        help_text=_('The contract version the Grant.'),
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
    request_ownership_change = models.ForeignKey(
        'dashboard.Profile',
        related_name='request_ownership_change',
        on_delete=models.CASCADE,
        help_text=_('The Grant\'s potential new administrator profile.'),
        null=True,
        blank=True,
    )
    team_members = models.ManyToManyField(
        'dashboard.Profile',
        related_name='grant_teams',
        help_text=_('The team members contributing to this Grant.'),
    )
    image_css = models.CharField(default='', blank=True, max_length=255, help_text=_('additional CSS to attach to the grant-banner img.'))
    clr_matching = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=20,
        help_text=_('The TOTAL CLR matching amount across all rounds'),
    )
    activeSubscriptions = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    hidden = models.BooleanField(default=False, help_text=_('Hide the grant from the /grants page?'))

    # Grant Query Set used as manager.
    objects = GrantQuerySet.as_manager()

    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, active: {self.active}, title: {self.title}"

    def percentage_done(self):
        """Return the percentage of token received based on the token goal."""
        if not self.amount_goal:
            return 0
        return ((self.amount_received / self.amount_goal) * 100)


    def updateActiveSubscriptions(self):
        """updates the active subscriptions list"""
        handles = []
        for handle in Subscription.objects.filter(grant=self, active=True).distinct('contributor_profile').values_list('contributor_profile__handle', flat=True):
            handles.append(handle)
        self.activeSubscriptions = handles

    @property
    def abi(self):
        """Return grants abi."""
        if self.contract_version == 0:
            from grants.abi import abi_v0
            return abi_v0
        elif self.contract_version == 1:
            from grants.abi import abi_v1
            return abi_v1


    @property
    def url(self):
        """Return grants url."""
        from django.urls import reverse
        return reverse('grants:details', kwargs={'grant_id': self.pk, 'grant_slug': self.slug})


    @property
    def contract(self):
        """Return grants contract."""
        from dashboard.utils import get_web3
        web3 = get_web3(self.network)
        grant_contract = web3.eth.contract(Web3.toChecksumAddress(self.contract_address), abi=self.abi)
        return grant_contract


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

    def __str__(self):
        """Return the string representation of this object."""
        return self.title


class SubscriptionQuerySet(models.QuerySet):
    """Define the Subscription default queryset and manager."""

    pass


class Subscription(SuperModel):
    """Define the structure of a subscription agreement."""

    active = models.BooleanField(default=True, help_text=_('Whether or not the Subscription is active.'))
    error = models.BooleanField(default=False, help_text=_('Whether or not the Subscription is erroring out.'))
    subminer_comments = models.TextField(default='', blank=True, help_text=_('Comments left by the subminer.'))

    subscription_hash = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s Subscription hash.'),
        blank=True,
    )
    contributor_signature = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s signature.'),
        blank=True,
        )
    contributor_address = models.CharField(
        default='',
        max_length=255,
        help_text=_('The contributor\'s wallet address of the Subscription.'),
    )
    amount_per_period = models.DecimalField(
        default=1,
        decimal_places=18,
        max_digits=64,
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
    new_approve_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for subscription approve().'),
    )
    end_approve_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for subscription approve().'),
    )
    cancel_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for cancelSubscription.'),
    )
    num_tx_approved = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The number of transactions approved for the Subscription.'),
    )
    num_tx_processed = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The number of transactoins processed by the subminer for the Subscription.'),
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
    last_contribution_date = models.DateTimeField(
        help_text=_('The last contribution date'),
        default=timezone.datetime(1990, 1, 1),
    )
    next_contribution_date = models.DateTimeField(
        help_text=_('The next contribution date'),
        default=timezone.datetime(1990, 1, 1),
    )
    amount_per_period_usdt = models.DecimalField(
        default=0,
        decimal_places=18,
        max_digits=64,
        help_text=_('The amount per contribution period in USDT'),
    )

    @property
    def status(self):
        """Return grants status, current or past due."""
        if self.next_contribution_date < timezone.now():
            return "PAST DUE"
        return "CURRENT"


    def __str__(self):
        """Return the string representation of a Subscription."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        active_details = f"( active: {self.active}, billed {self.subscription_contribution.count()} times, last contrib: {naturaltime(self.last_contribution_date)},  next contrib: {naturaltime(self.next_contribution_date)} )"
        if self.last_contribution_date < timezone.now() - timezone.timedelta(days=10*365):
            active_details = "(NEVER BILLED)"

        return f"id: {self.pk}; {self.status}, {self.amount_per_period} {self.token_symbol} / {self.frequency} {self.frequency_unit} for grant {self.grant.pk} created {naturaltime(self.created_on)} by {self.contributor_profile.handle} {active_details}"

    def get_nonce(self, address):
        return self.grant.contract.functions.extraNonce(address).call() + 1

    def get_debug_info(self):
        """Return grants contract."""
        from dashboard.utils import get_web3
        from dashboard.abi import erc20_abi
        from dashboard.tokens import addr_to_token
        try:
            web3 = get_web3(self.network)
            if not self.token_address:
                return "This subscription has no token_address"
            token_contract = web3.eth.contract(Web3.toChecksumAddress(self.token_address), abi=erc20_abi)
            balance = token_contract.functions.balanceOf(Web3.toChecksumAddress(self.contributor_address)).call()
            allowance = token_contract.functions.allowance(Web3.toChecksumAddress(self.contributor_address), Web3.toChecksumAddress(self.grant.contract_address)).call()
            gasPrice = self.gas_price
            is_active = self.get_is_active_from_web3()
            token = addr_to_token(self.token_address, self.network)
            next_valid_timestamp = self.get_next_valid_timestamp()
            decimals = token.get('decimals', 0)
            balance = balance / 10 ** decimals
            allowance = allowance / 10 ** decimals
            error_reason = "unknown"
            if not is_active:
                error_reason = 'not_active'
            if timezone.now().timestamp() < next_valid_timestamp:
                error_reason = 'before_next_valid_timestamp'
            if (float(balance) + float(gasPrice)) < float(self.amount_per_period):
                error_reason = "insufficient_balance"
            if allowance < self.amount_per_period:
                error_reason = "insufficient_allowance"

            debug_info = f"""
error_reason: {error_reason}
==============================
is_active: {is_active}
decimals: {decimals}
balance: {balance}
allowance: {allowance}
amount_per_period: {self.amount_per_period}
next_valid_timestamp: {next_valid_timestamp}
"""
        except Exception as e:
            return str(e)
        return debug_info

    def get_next_valid_timestamp(self):
        _hash = self.get_hash_from_web3()
        return self.grant.contract.functions.nextValidTimestamp(_hash).call()

    def get_is_ready_to_be_processed_from_db(self):
        """Return true if subscription is ready to be processed according to the DB."""
        if not self.subscription_contribution.exists():
            return True
        return self.next_contribution_date < timezone.now() and self.num_tx_processed < self.num_tx_approved

    def get_are_we_past_next_valid_timestamp(self):
        return timezone.now().timestamp() > self.get_next_valid_timestamp()

    def get_is_subscription_ready_from_web3(self):
        """Return true if subscription is ready to be processed according to web3."""
        args = self.get_subscription_hash_arguments()
        return self.grant.contract.functions.isSubscriptionReady(
            args['from'],
            args['to'],
            args['tokenAddress'],
            args['tokenAmount'],
            args['periodSeconds'],
            args['gasPrice'],
            args['nonce'],
            args['signature'],
        ).call()

    def get_check_success_web3(self):
        """Check the return value of the previous function. Returns true if the previous function."""
        return self.grant.contract.functions.checkSuccess().call()

    def _do_helper_via_web3(self, fn, minutes_to_confirm_within=1):
        """Call the specified function fn"""
        from dashboard.utils import get_web3
        args = self.get_subscription_hash_arguments()
        tx = fn(
            args['from'],
            args['to'],
            args['tokenAddress'],
            args['tokenAmount'],
            args['periodSeconds'],
            args['gasPrice'],
            args['nonce'],
            args['signature'],
        ).buildTransaction(
            self.helper_tx_dict(minutes_to_confirm_within)
        )
        web3 = get_web3(self.grant.network)
        signed_txn = web3.eth.account.signTransaction(tx, private_key=settings.GRANTS_PRIVATE_KEY)
        return web3.eth.sendRawTransaction(signed_txn.rawTransaction).hex()

    def do_cancel_subscription_via_web3(self, minutes_to_confirm_within=1):
        """.Cancels the subscripion on the blockchain"""
        return self._do_helper_via_web3(
            self.grant.contract.functions.cancelSubscription,
            minutes_to_confirm_within=minutes_to_confirm_within
        )

    def do_execute_subscription_via_web3(self, minutes_to_confirm_within=1):
        """.Executes the subscription on the blockchain"""
        return self._do_helper_via_web3(
            self.grant.contract.functions.executeSubscription,
            minutes_to_confirm_within=minutes_to_confirm_within
        )

    def helper_tx_dict(self, minutes_to_confirm_within=1):
        """returns a dict like this: {'to': '0xd3cda913deb6f67967b99d67acdfa1712c293601', 'from': web3.eth.coinbase, 'value': 12345}"""
        from dashboard.utils import get_nonce
        return {
            'from': settings.GRANTS_OWNER_ACCOUNT,
            'nonce': get_nonce(self.grant.network, settings.GRANTS_OWNER_ACCOUNT),
            'value': 0,
            'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(minutes_to_confirm_within) * 10**9),
            'gas': 204066,
        }

    def get_is_active_from_web3(self):
        """Return true if subscription is active according to web3."""
        _hash = self.get_hash_from_web3()
        return self.grant.contract.functions.isSubscriptionActive(_hash, 10).call()

    def get_subscription_signer_from_web3(self):
        """Return subscription signer."""
        _hash = self.get_hash_from_web3()
        return self.grant.contract.functions.getSubscriptionSigner(_hash, self.contributor_signature).call()

    def get_subscription_hash_arguments(self):
        """Get the grant subscription hash from web3.

        Attributes:
            from (str): Subscription.contributor_address
            to (str): Grant.admin_address
            tokenAddress (str): Subscription.token_address
            tokenAmount (float): Subscription.amount_per_period
            periodSeconds (int): real_period_seconds in the Subscription model
            gasPrice (float): Subscription.gas_price
            nonce (int): The nonce is stored in the Contribution model. its created / managed by sync_geth
            signature (str): Subscription.contributor_signature

        Returns:
            str: The Subscription hash.

        """
        from dashboard.tokens import addr_to_token

        subs = self
        grant = subs.grant

        _from = subs.contributor_address
        to = grant.admin_address
        if grant.token_address != '0x0000000000000000000000000000000000000000':
            tokenAddress = grant.token_address
        else:
            tokenAddress = subs.token_address

        tokenAmount = subs.amount_per_period
        periodSeconds = subs.real_period_seconds
        gasPrice = subs.gas_price
        nonce = subs.get_nonce(_from)
        signature = subs.contributor_signature

        # TODO - figure out the number of decimals
        token = addr_to_token(tokenAddress, subs.grant.network)
        decimals = token.get('decimals', 0)

        return {
            'from': Web3.toChecksumAddress(_from),
            'to': Web3.toChecksumAddress(to),
            'tokenAddress': Web3.toChecksumAddress(tokenAddress),
            'tokenAmount': int(tokenAmount * 10**decimals),
            'periodSeconds': int(periodSeconds),
            'gasPrice': int(gasPrice),
            'nonce': int(nonce),
            'signature': signature,
        }

    def get_hash_from_web3(self):
        """Returns the grants subscription hash (has to get it from web3)."""
        args = self.get_subscription_hash_arguments()
        return self.grant.contract.functions.getSubscriptionHash(
            Web3.toChecksumAddress(args['from']),
            Web3.toChecksumAddress(args['to']),
            Web3.toChecksumAddress(args['tokenAddress']),
            args['tokenAmount'],
            args['periodSeconds'],
            args['gasPrice'],
            args['nonce'],
            ).call()

    def get_converted_amount(self):
        try:
            if self.token_symbol == "ETH" or self.token_symbol == "WETH":
                return Decimal(float(self.amount_per_period) * float(eth_usd_conv_rate()))
            else:
                value_token_to_eth = Decimal(convert_amount(
                    self.amount_per_period,
                    self.token_symbol,
                    "ETH")
                )

            value_eth_to_usdt = Decimal(eth_usd_conv_rate())
            value_usdt = value_token_to_eth * value_eth_to_usdt
            return value_usdt

        except ConversionRateNotFoundError as e:
            try:
                return Decimal(convert_amount(
                    self.amount_per_period,
                    self.token_symbol,
                    "USDT"))
            except ConversionRateNotFoundError as no_conversion_e:
                logger.info(no_conversion_e)
                return None

    def get_converted_monthly_amount(self):
        converted_amount = self.get_converted_amount()

        total_sub_seconds = Decimal(self.real_period_seconds) * Decimal(self.num_tx_approved)

        if total_sub_seconds < 2592000:
            result = Decimal(converted_amount * Decimal(self.num_tx_approved))
        elif total_sub_seconds >= 2592000:
            result = Decimal(converted_amount * (Decimal(2592000) / Decimal(self.real_period_seconds)))

        return result


    def successful_contribution(self, tx_id):
        """Create a contribution object."""
        from marketing.mails import successful_contribution
        self.last_contribution_date = timezone.now()
        self.next_contribution_date = timezone.now() + timedelta(0, int(self.real_period_seconds))
        self.num_tx_processed += 1
        contribution_kwargs = {
            'tx_id': tx_id,
            'subscription': self
        }
        contribution = Contribution.objects.create(**contribution_kwargs)
        grant = self.grant

        value_usdt = self.get_converted_amount()
        if value_usdt:
            self.amount_per_period_usdt = value_usdt
            grant.amount_received += Decimal(value_usdt)

        if self.num_tx_processed == self.num_tx_approved and value_usdt:
            grant.monthly_amount_subscribed -= self.get_converted_monthly_amount()
            self.active = False

        self.save()
        grant.updateActiveSubscriptions()
        grant.save()
        successful_contribution(self.grant, self, contribution)
        return contribution


@receiver(pre_save, sender=Grant, dispatch_uid="psave_grant")
def psave_grant(sender, instance, **kwargs):

    instance.amount_received = 0
    instance.monthly_amount_subscribed = 0
    #print(instance.id)
    for subscription in instance.subscriptions.all():
        value_usdt = subscription.get_converted_amount()
        for contrib in subscription.subscription_contribution.filter(success=True):
            if value_usdt:
                instance.amount_received += Decimal(value_usdt)

        if subscription.num_tx_processed <= subscription.num_tx_approved and value_usdt:
            if subscription.num_tx_approved != 1:
                instance.monthly_amount_subscribed += subscription.get_converted_monthly_amount()
        #print("-", subscription.id, value_usdt, instance.monthly_amount_subscribed )


class DonationQuerySet(models.QuerySet):
    """Define the Contribution default queryset and manager."""

    pass


class Donation(SuperModel):
    """Define the structure of an optional donation. These donations are
       additional funds sent to Gitcoin as part of contributing or subscribing
       to a grant."""

    from_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_("The sender's address."),
    )
    to_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_("The destination address."),
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='donations',
        on_delete=models.SET_NULL,
        help_text=_("The donator's profile."),
        null=True,
    )
    token_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The token address to be used with the Grant.'),
    )
    token_symbol = models.CharField(
        max_length=255,
        default='',
        help_text=_("The donation token's symbol."),
    )
    token_amount = models.DecimalField(
        default=0,
        decimal_places=18,
        max_digits=64,
        help_text=_('The donation amount in tokens.'),
    )
    token_amount_usdt = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The donation amount converted to USDT/DAI at the moment of donation.'),
    )
    tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction ID of the Contribution.'),
    )
    network = models.CharField(
        max_length=8,
        default='mainnet',
        help_text=_('The network in which the Subscription resides.'),
    )
    donation_percentage = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=5,
        help_text=_('The additional percentage selected when the donation is made'),
    )
    subscription = models.ForeignKey(
        'grants.subscription',
        related_name='donations',
        on_delete=models.SET_NULL,
        help_text=_("The recurring subscription that this donation originated from."),
        null=True,
    )
    contribution = models.ForeignKey(
        'grants.contribution',
        related_name='donation',
        on_delete=models.SET_NULL,
        help_text=_("The contribution that this donation was a part of."),
        null=True,
    )


    def __str__(self):
        """Return the string representation of this object."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        return f"id: {self.pk}; from:{profile.handle}; {tx_id} => ${token_amount_usdt}; {naturaltime(self.created_on)}"


class ContributionQuerySet(models.QuerySet):
    """Define the Contribution default queryset and manager."""

    pass


class Contribution(SuperModel):
    """Define the structure of a subscription agreement."""

    success = models.BooleanField(default=True, help_text=_('Whether or not success.'))
    tx_cleared = models.BooleanField(default=False, help_text=_('Whether or not tx cleared.'))
    tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction ID of the Contribution.'),
    )
    subscription = models.ForeignKey(
        'grants.Subscription',
        related_name='subscription_contribution',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Subscription.'),
    )

    def __str__(self):
        """Return the string representation of this object."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        txid_shortened = self.tx_id[0:10] + "..."
        return f"id: {self.pk}; {txid_shortened} => subs:{self.subscription}; {naturaltime(self.created_on)}"

    def update_tx_status(self):
        """Updates tx status."""
        from dashboard.utils import get_tx_status
        tx_status, tx_time = get_tx_status(self.tx_id, self.subscription.network, self.created_on)
        if tx_status != 'pending':
            self.success = tx_status == 'success'
            self.tx_cleared = True

def next_month():
    """Get the next month time."""
    return localtime(timezone.now() + timedelta(days=30))


class CLRMatch(SuperModel):
    """Define the structure of a CLR Match amount."""

    round_number = models.PositiveIntegerField(blank=True, null=True)
    amount = models.FloatField()
    grant = models.ForeignKey(
        'grants.Grant',
        related_name='clr_matches',
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The associated Grant.'),
    )

    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, grant: {self.grant.pk}, round: {self.round_number}, amount: {self.amount}"



class MatchPledge(SuperModel):
    """Define the structure of a MatchingPledge."""

    active = models.BooleanField(default=False, help_text=_('Whether or not the MatchingPledge is active.'))
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='matchPledges',
        on_delete=models.CASCADE,
        help_text=_('The MatchingPledgers profile.'),
        null=True,
    )
    amount = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The matching pledge amount in DAI.'),
    )
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))
    end_date = models.DateTimeField(null=False, default=next_month)
    data = models.TextField(blank=True)

    def __str__(self):
        """Return the string representation of this object."""
        return f"{self.profile} <> {self.amount} DAI"
