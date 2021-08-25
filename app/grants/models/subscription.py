import logging
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import pytz
from economy.models import SuperModel
from economy.utils import ConversionRateNotFoundError, convert_amount
from gas.utils import eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from web3 import Web3

from .contribution import Contribution

logger = logging.getLogger(__name__)


class Subscription(SuperModel):
    """Define the structure of a subscription agreement."""

    TENANT = [
        ('ETH', 'ETH'),
        ('ZCASH', 'ZCASH'),
        ('CELO', 'CELO'),
        ('ZIL', 'ZIL'),
        ('POLKADOT', 'POLKADOT'),
        ('KUSAMA', 'KUSAMA'),
        ('HARMONY', 'HARMONY'),
        ('BINANCE', 'BINANCE'),
        ('RSK', 'RSK'),
        ('ALGORAND', 'ALGORAND')
    ]

    active = models.BooleanField(default=True, db_index=True, help_text=_('Whether or not the Subscription is active.'))
    error = models.BooleanField(default=False, help_text=_('Whether or not the Subscription is erroring out.'))
    subminer_comments = models.TextField(default='', blank=True, help_text=_('Comments left by the subminer.'))
    comments = models.TextField(default='', blank=True, help_text=_('Comments left by subscriber.'))

    split_tx_id = models.CharField(
        default='',
        max_length=255,
        help_text=_('The tx id of the split transfer'),
        blank=True,
    )
    is_postive_vote = models.BooleanField(default=True, db_index=True, help_text=_('Whether this is positive or negative vote'))
    split_tx_confirmed = models.BooleanField(default=False, help_text=_('Whether or not the split tx succeeded.'))

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
    # TODO: REMOVE
    frequency_unit = models.CharField(
        max_length=255,
        default='',
        help_text=_('The text version of frequency units e.g. days, months'),
    )
    # TODO: REMOVE
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
        decimal_places=18,
        max_digits=50,
        help_text=_('The required gas price for the Subscription.'),
    )
    # TODO: REMOVE
    new_approve_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for subscription approve().'),
    )
    # TODO: REMOVE
    end_approve_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for subscription approve().'),
    )
    # TODO: REMOVE
    cancel_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for cancelSubscription.'),
    )
    # TODO: REMOVE
    num_tx_approved = models.DecimalField(
        default=1,
        decimal_places=4,
        max_digits=50,
        help_text=_('The number of transactions approved for the Subscription.'),
    )
    # TODO: REMOVE
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
    # TODO: REMOVE
    last_contribution_date = models.DateTimeField(
        help_text=_('The last contribution date'),
        default=timezone.datetime(1990, 1, 1),
    )
    # TODO: REMOVE
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
    tenant = models.CharField(max_length=10, null=True, blank=True, default="ETH", choices=TENANT, help_text="specific tenant in which contribution is made")
    visitorId = models.CharField(
        default='',
        max_length=255,
        help_text=_('The visitorID of the contributor'),
        blank=True,
    )

    @property
    def negative(self):
        return self.is_postive_vote == False

    @property
    def status(self):
        """Return grants status, current or past due."""
        if self.next_contribution_date < timezone.now():
            return "PAST DUE"
        return "CURRENT"

    @property
    def amount_per_period_minus_gas_price(self):
        if self.amount_per_period == self.amount_per_period_to_gitcoin:
            return float(self.amount_per_period)

        return float(self.amount_per_period) - float(self.amount_per_period_to_gitcoin)

    @property
    def amount_per_period_to_gitcoin(self):
        from dashboard.tokens import addr_to_token
        token = addr_to_token(self.token_address, self.network)

        # gas prices no longer take this amount times 10**18 decimals
        if self.created_on > timezone.datetime(2020, 6, 16, 15, 0).replace(tzinfo=pytz.utc):
            return self.gas_price

        try:
            decimals = token.get('decimals', 0)
            return (float(self.gas_price) / 10 ** decimals)
        except:
            return 0


    def __str__(self):
        """Return the string representation of a Subscription."""
        from django.contrib.humanize.templatetags.humanize import naturaltime

        return f"id: {self.pk}; {round(float(self.amount_per_period),1)} {self.token_symbol} (${round(float(self.amount_per_period_usdt))}) {int(self.num_tx_approved)} times, created {naturaltime(self.created_on)} by {self.contributor_profile}"

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
            'nonce': get_nonce(self.grant.network, settings.GRANTS_OWNER_ACCOUNT, True),
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

    def get_converted_amount(self, ignore_gitcoin_fee=False, only_gitcoin_fee=False):
        if ignore_gitcoin_fee:
            amount = self.amount_per_period
        elif only_gitcoin_fee:
            amount = self.amount_per_period_to_gitcoin
        else:
            amount = self.amount_per_period_minus_gas_price

        try:
            if self.token_symbol == "ETH" or self.token_symbol == "WETH":
                return Decimal(float(amount) * float(eth_usd_conv_rate(self.created_on)))
            else:
                value_token_to_eth = Decimal(convert_amount(
                    amount,
                    self.token_symbol,
                    "ETH",
                    self.created_on
                    )
                )

            value_eth_to_usdt = Decimal(eth_usd_conv_rate(self.created_on))
            value_usdt = value_token_to_eth * value_eth_to_usdt
            return value_usdt

        except ConversionRateNotFoundError as e:
            try:
                return Decimal(convert_amount(
                    amount,
                    self.token_symbol,
                    "USDT",
                    self.created_on))
            except ConversionRateNotFoundError as no_conversion_e:
                logger.info(no_conversion_e)
                return None

    def get_converted_monthly_amount(self, ignore_gitcoin_fee=False):
        converted_amount = self.get_converted_amount(ignore_gitcoin_fee=ignore_gitcoin_fee) or 0

        total_sub_seconds = Decimal(self.real_period_seconds) * Decimal(self.num_tx_approved)

        if total_sub_seconds < 2592000:
            result = Decimal(converted_amount * Decimal(self.num_tx_approved))
        elif total_sub_seconds >= 2592000:
            result = Decimal(converted_amount * (Decimal(2592000) / Decimal(self.real_period_seconds)))

        return result

    def save_split_tx_to_contribution(self):
        sc = self.subscription_contribution.first()
        sc.split_tx_id = self.split_tx_id
        sc.split_tx_confirmed = self.split_tx_confirmed
        sc.save()

    def successful_contribution(self, tx_id, include_for_clr=True, **kwargs):
        """
        Create a contribution object. Only expected keyword argument is checkout_type, which was
        added as a keyword argument to avoid breaking existing calls to this function
        """
        self.last_contribution_date = timezone.now()
        self.next_contribution_date = timezone.now() + timedelta(0, int(self.real_period_seconds))
        self.num_tx_processed += 1
        contribution_kwargs = {
            'tx_id': tx_id,
            'subscription': self,
            'split_tx_id': self.split_tx_id,
            'split_tx_confirmed': self.split_tx_confirmed,
            'checkout_type': kwargs['checkout_type'] if 'checkout_type' in kwargs else None
        }
        contribution = Contribution.objects.create(**contribution_kwargs)
        grant = self.grant

        value_usdt = self.get_converted_amount(False)
        if value_usdt:
            self.amount_per_period_usdt = value_usdt
            grant.amount_received += Decimal(value_usdt)

        if self.num_tx_processed == self.num_tx_approved and value_usdt:
            grant.monthly_amount_subscribed -= self.get_converted_monthly_amount()
            self.active = False

        self.save()
        grant.updateActiveSubscriptions()
        grant.save()

        if grant.pk == 86:
            # KO 9/28/2020 - per community feedback, contributions that are auto-matched should not count towards
            # CLR matching, as it gives gitcoin an unfair advantage
            is_automatic = bool(contribution.subscription.amount_per_period == contribution.subscription.gas_price)
            from dashboard.models import Profile

            if not include_for_clr:
                contribution.profile_for_clr = Profile.objects.get(handle='gitcoinbot')
                contribution.match = False
            contribution.save()

        return contribution


    def create_contribution(self, tx_id, is_successful_contribution=True):
        from marketing.mails import successful_contribution
        from grants.tasks import update_grant_metadata

        now = timezone.now()
        self.last_contribution_date = now
        self.next_contribution_date = now

        self.num_tx_processed += 1

        contribution = Contribution()

        contribution.success = False
        contribution.tx_cleared = False
        contribution.subscription = self
        contribution.split_tx_id = self.split_tx_id
        contribution.split_tx_confirmed = self.split_tx_confirmed

        if tx_id:
            contribution.tx_id = tx_id

        contribution.save()
        grant = self.grant

        value_usdt = self.get_converted_amount(False)
        if value_usdt:
            self.amount_per_period_usdt = value_usdt
            grant.amount_received += Decimal(value_usdt)

        if self.num_tx_processed == self.num_tx_approved and value_usdt:
            grant.monthly_amount_subscribed -= self.get_converted_monthly_amount()
            self.active = False

        self.save()
        grant.updateActiveSubscriptions()
        grant.save()
        if is_successful_contribution:
            successful_contribution(self.grant, self, contribution)

        update_grant_metadata.delay(self.pk)
        return contribution
