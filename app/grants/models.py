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
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel
from economy.utils import ConversionRateNotFoundError, convert_amount, convert_token_to_usdt
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from grants.utils import get_upload_filename
from web3 import Web3


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
        help_text=_('The contribution goal amount for the Grant in DAI.'),
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

    @property
    def abi(self):
        """Return grants abi."""
        abi = [    {      "constant": True,      "inputs": [],      "name": "requiredGasPrice",      "outputs": [        {          "name": "",          "type": "uint256"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [],      "name": "requiredTokenAmount",      "outputs": [        {          "name": "",          "type": "uint256"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [],      "name": "requiredToAddress",      "outputs": [        {          "name": "",          "type": "address"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [],      "name": "requiredPeriodSeconds",      "outputs": [        {          "name": "",          "type": "uint256"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [],      "name": "requiredTokenAddress",      "outputs": [        {          "name": "",          "type": "address"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [],      "name": "contractVersion",      "outputs": [        {          "name": "",          "type": "uint8"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [        {          "name": "",          "type": "address"        }      ],      "name": "extraNonce",      "outputs": [        {          "name": "",          "type": "uint256"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [],      "name": "author",      "outputs": [        {          "name": "",          "type": "address"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [        {          "name": "",          "type": "bytes32"        }      ],      "name": "nextValidTimestamp",      "outputs": [        {          "name": "",          "type": "uint256"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "inputs": [        {          "name": "_toAddress",          "type": "address"        },        {          "name": "_tokenAddress",          "type": "address"        },        {          "name": "_tokenAmount",          "type": "uint256"        },        {          "name": "_periodSeconds",          "type": "uint256"        },        {          "name": "_gasPrice",          "type": "uint256"        },        {          "name": "_version",          "type": "uint8"        }      ],      "payable": False,      "stateMutability": "nonpayable",      "type": "constructor"    },    {      "payable": True,      "stateMutability": "payable",      "type": "fallback"    },    {      "anonymous": False,      "inputs": [        {          "indexed": True,          "name": "from",          "type": "address"        },        {          "indexed": True,          "name": "to",          "type": "address"        },        {          "indexed": False,          "name": "tokenAddress",          "type": "address"        },        {          "indexed": False,          "name": "tokenAmount",          "type": "uint256"        },        {          "indexed": False,          "name": "periodSeconds",          "type": "uint256"        },        {          "indexed": False,          "name": "gasPrice",          "type": "uint256"        },        {          "indexed": False,          "name": "nonce",          "type": "uint256"        }      ],      "name": "ExecuteSubscription",      "type": "event"    },    {      "anonymous": False,      "inputs": [        {          "indexed": True,          "name": "from",          "type": "address"        },        {          "indexed": True,          "name": "to",          "type": "address"        },        {          "indexed": False,          "name": "tokenAddress",          "type": "address"        },        {          "indexed": False,          "name": "tokenAmount",          "type": "uint256"        },        {          "indexed": False,          "name": "periodSeconds",          "type": "uint256"        },        {          "indexed": False,          "name": "gasPrice",          "type": "uint256"        },        {          "indexed": False,          "name": "nonce",          "type": "uint256"        }      ],      "name": "CancelSubscription",      "type": "event"    },    {      "constant": True,      "inputs": [        {          "name": "subscriptionHash",          "type": "bytes32"        },        {          "name": "gracePeriodSeconds",          "type": "uint256"        }      ],      "name": "isSubscriptionActive",      "outputs": [        {          "name": "",          "type": "bool"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [        {          "name": "from",          "type": "address"        },        {          "name": "to",          "type": "address"        },        {          "name": "tokenAddress",          "type": "address"        },        {          "name": "tokenAmount",          "type": "uint256"        },        {          "name": "periodSeconds",          "type": "uint256"        },        {          "name": "gasPrice",          "type": "uint256"        },        {          "name": "nonce",          "type": "uint256"        }      ],      "name": "getSubscriptionHash",      "outputs": [        {          "name": "",          "type": "bytes32"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": True,      "inputs": [        {          "name": "subscriptionHash",          "type": "bytes32"        },        {          "name": "signature",          "type": "bytes"        }      ],      "name": "getSubscriptionSigner",      "outputs": [        {          "name": "",          "type": "address"        }      ],      "payable": False,      "stateMutability": "pure",      "type": "function"    },    {      "constant": True,      "inputs": [        {          "name": "from",          "type": "address"        },        {          "name": "to",          "type": "address"        },        {          "name": "tokenAddress",          "type": "address"        },        {          "name": "tokenAmount",          "type": "uint256"        },        {          "name": "periodSeconds",          "type": "uint256"        },        {          "name": "gasPrice",          "type": "uint256"        },        {          "name": "nonce",          "type": "uint256"        },        {          "name": "signature",          "type": "bytes"        }      ],      "name": "isSubscriptionReady",      "outputs": [        {          "name": "",          "type": "bool"        }      ],      "payable": False,      "stateMutability": "view",      "type": "function"    },    {      "constant": False,      "inputs": [        {          "name": "from",          "type": "address"        },        {          "name": "to",          "type": "address"        },        {          "name": "tokenAddress",          "type": "address"        },        {          "name": "tokenAmount",          "type": "uint256"        },        {          "name": "periodSeconds",          "type": "uint256"        },        {          "name": "gasPrice",          "type": "uint256"        },        {          "name": "nonce",          "type": "uint256"        },        {          "name": "signature",          "type": "bytes"        }      ],      "name": "cancelSubscription",      "outputs": [        {          "name": "success",          "type": "bool"        }      ],      "payable": False,      "stateMutability": "nonpayable",      "type": "function"    },    {      "constant": False,      "inputs": [        {          "name": "from",          "type": "address"        },        {          "name": "to",          "type": "address"        },        {          "name": "tokenAddress",          "type": "address"        },        {          "name": "tokenAmount",          "type": "uint256"        },        {          "name": "periodSeconds",          "type": "uint256"        },        {          "name": "gasPrice",          "type": "uint256"        },        {          "name": "nonce",          "type": "uint256"        },        {          "name": "signature",          "type": "bytes"        }      ],      "name": "executeSubscription",      "outputs": [        {          "name": "success",          "type": "bool"        }      ],      "payable": False,      "stateMutability": "nonpayable",      "type": "function"    },    {      "constant": False,      "inputs": [],      "name": "endContract",      "outputs": [],      "payable": False,      "stateMutability": "nonpayable",      "type": "function"    }  ]
        return abi

    @property
    def contract(self):
        """Return grants contract."""
        from dashboard.utils import get_web3
        web3 = get_web3(self.network)
        grant_contract = web3.eth.contract(self.contract_address, abi=self.abi)
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
    last_contribution_date = models.DateField(help_text=_('The last contribution date'), default=timezone.datetime(1990, 1, 1))
    next_contribution_date = models.DateField(help_text=_('The next contribution date'), default=timezone.datetime(1990, 1, 1))

    def __str__(self):
        """Return the string representation of a Subscription."""
        return f"id: {self.pk}, active: {self.active}, subscription_hash: {self.subscription_hash}"

    def get_nonce(self, address):
        return self.grant.contract.functions.extraNonce(address).call() + 1

    def get_next_valid_timestamp(self, address):
        return self.grant.contract.functions.nextValidTimestamp(address).call()

    def get_is_ready_to_be_processed_from_db(self):
        """Return true if subscription is ready to be processed according to the DB."""
        if not self.subscription_contribution.exists():
            return True
        last_contribution = self.subscription_contribution.order_by('created_on').last()
        period = self.real_period_seconds
        return (last_contribution.created_on.timestamp() + period > (timezone.now()))

    def get_are_we_past_next_valid_timestamp(self):
        address = self.contributor_address
        return timezone.now().timestamp() > self.get_next_valid_timestamp(address)


    def get_is_subscription_ready_from_web3(self):
        """Return true if subscription is ready to be processed according to web3."""
        the_args = args = self.get_subscription_hash_arguments()
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
        """Checks the return value of the previous function. Returns true if the previous function."""
        return self.grant.contract.functions.checkSuccess().call()

    def do_cancel_subscription_via_web3(self, minutes_to_confirm_within = 5):
        """.Cancels the subscripion on the blockchain"""
        from dashboard.utils import get_web3
        args = self.get_subscription_hash_arguments()
        tx = self.grant.contract.functions.cancelSubscription(
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
        return web3.eth.sendRawTransaction(signed_txn.rawTransaction)

    def do_execute_subscription_via_web3(self, minutes_to_confirm_within = 5):
        """.Executes the subscription on the blockchain"""
        from dashboard.utils import get_web3
        args = self.get_subscription_hash_arguments()
        tx = self.grant.contract.functions.executeSubscription(
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
        return web3.eth.sendRawTransaction(signed_txn.rawTransaction)



    def helper_tx_dict(self, minutes_to_confirm_within=5):
        """returns a dict like this: {'to': '0xd3cda913deb6f67967b99d67acdfa1712c293601', 'from': web3.eth.coinbase, 'value': 12345}"""
        from dashboard.utils import get_nonce
        return {
            'from': settings.GRANTS_OWNER_ACCOUNT,
            'nonce': get_nonce(self.grant.network, settings.GRANTS_OWNER_ACCOUNT),
            'value': 0,
            'gasPrice': recommend_min_gas_price_to_confirm_in_time(minutes_to_confirm_within) * 10**9,
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
        """Returns the grants subscription hash (has to get it from web3)."""
        """
            from = Subscription.contributor_address,
            to = Grant.admin_address,
            tokenAddress = Subscription.token_address,
            tokenAmount = Subscription.amount_per_period,
            periodSeconds = real_period_seconds in the Subscription model
            gasPrice = Subscription.gas_price,
            nonce = The nonce is stored in the Contribution model. its created / managed by sync_geth
            signature = Subscription.contributor_signature
        """
        from dashboard.tokens import addr_to_token

        subs = self
        grant = subs.grant

        _from = subs.contributor_address
        to = grant.admin_address
        tokenAddress = subs.token_address
        tokenAmount = subs.amount_per_period
        periodSeconds = subs.real_period_seconds
        gasPrice = subs.gas_price
        nonce = subs.get_nonce(_from)
        signature = subs.contributor_signature

        #TODO - figure out the number of decimals
        token = addr_to_token(subs.token_address, subs.grant.network)
        decimals = token.get('decimals', 0)

        return {
            'from': Web3.toChecksumAddress(_from),
            'to': Web3.toChecksumAddress(to),
            'tokenAddress': Web3.toChecksumAddress(tokenAddress),
            'tokenAmount': int(tokenAmount  * 10**decimals),
            'periodSeconds': int(periodSeconds),
            'gasPrice': int(gasPrice * 10**9),
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


    def successful_contribution(self, kwargs):
        """Create a contribution object."""
        from marketing.mails import successful_contribution
        self.last_contribution_date = timezone.now()
        self.next_contribution_date = timezone.now() + timezone.timedelta(seconds=self.real_period_seconds)
        self.save()
        contribution_kwargs = {
            'tx_id': kwargs.tx_id,
            'gas_price': kwargs.gas_price,
            'nonce': kwargs.nonce,
            'subscription': self
        }
        contribution = Contribution.objects.create(**contribution_kwargs)
        grant = self.grant
        grant.amount_received = (grant.amount_received + convert_amount(self.amount_per_period, self.token_symbol, "USDT", timezone.now()))
        grant.save()
        successful_contribution(self.grant, self)
        return contribution


class ContributionQuerySet(models.QuerySet):
    """Define the Contribution default queryset and manager."""

    pass


class Contribution(SuperModel):
    """Define the structure of a subscription agreement."""

    tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction ID of the Contribution.'),
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
