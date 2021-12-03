from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

import requests
from economy.models import SuperModel, Token
from economy.tx import check_for_replaced_tx
from townsquare.models import Comment
from web3 import Web3


class Contribution(SuperModel):
    """Define the structure of a subscription agreement."""

    CHECKOUT_TYPES = [
        ('eth_std', 'eth_std'),
        ('eth_zksync', 'eth_zksync'),
        ('eth_polygon', 'eth_polygon'),
        ('zcash_std', 'zcash_std'),
        ('celo_std', 'celo_std'),
        ('zil_std', 'zil_std'),
        ('polkadot_std', 'polkadot_std'),
        ('harmony_std', 'harmony_std'),
        ('binance_std', 'binance_std'),
        ('rsk_std', 'rsk_std'),
        ('algorand_std', 'algorand_std')
    ]

    success = models.BooleanField(default=True, db_index=True, help_text=_('Whether or not success.'))
    tx_cleared = models.BooleanField(default=False, help_text=_('Whether or not tx cleared.'))
    tx_override = models.BooleanField(default=False, help_text=_('Whether or not the tx success and tx_cleared have been manually overridden. If this setting is True, update_tx_status will not change this object.'))

    tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction ID of the Contribution.'),
        blank=True,
    )
    split_tx_id = models.CharField(
        default='',
        max_length=255,
        help_text=_('The tx id of the split transfer'),
        blank=True,
    )
    split_tx_confirmed = models.BooleanField(default=False, help_text=_('Whether or not the split tx succeeded.'))
    subscription = models.ForeignKey(
        'grants.Subscription',
        related_name='subscription_contribution',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Subscription.'),
    )

    grant = models.ForeignKey(
        'grants.Grant',
        related_name='contributions',
        on_delete=models.CASCADE,
        null=True,
        help_text=_('The associated Grant.'),
    )

    amount_per_period_usdt = models.DecimalField(
        default=0,
        decimal_places=18,
        max_digits=64,
        db_index=True,
        help_text=_('The amount per contribution period in USDT'),
    )

    normalized_data = JSONField(
        default=dict,
        blank=True,
        help_text=_('the normalized grant data; for easy consumption on read'),
    )
    match = models.BooleanField(default=True, db_index=True, help_text=_('Whether or not this contribution should be matched.'))

    originated_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The origination address of the funds used in this txn'),
    )
    validator_passed = models.BooleanField(default=False, help_text=_('Whether or not the backend validator passed.'))
    validator_comment = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The why or why not validator passed'),
    )

    profile_for_clr = models.ForeignKey(
        'dashboard.Profile',
        related_name='clr_pledges',
        on_delete=models.CASCADE,
        help_text=_('The profile to attribute this contribution to..'),
        null=True,
        blank=True,
    )
    checkout_type = models.CharField(
        max_length=30,
        null=True,
        help_text=_('The checkout method used while making the contribution'),
        blank=True,
        choices=CHECKOUT_TYPES
    )
    anonymous = models.BooleanField(default=False, help_text=_('Whether users can view the profile for this project or not'))

    @property
    def blockexplorer_url(self):
            return self.blockexplorer_url_helper(self.split_tx_id)

    @property
    def blockexplorer_url_split_txid(self):
            return self.blockexplorer_url_helper(self.split_tx_id)

    @property
    def blockexplorer_url_txid(self):
            return self.blockexplorer_url_helper(self.tx_id)

    def blockexplorer_url_helper(self, tx_id):
        if self.checkout_type == 'eth_polygon':
            return f'https://polygonscan.com/tx/{tx_id}'
        elif self.checkout_type == 'eth_zksync':
            return f'https://zkscan.io/explorer/transactions/{tx_id.replace("sync-tx:", "")}'
        elif self.checkout_type == 'eth_std':
            network_sub = f"{self.subscription.network}." if self.subscription and self.subscription.network != 'mainnet' else ''
            return f'https://{network_sub}etherscan.io/tx/{tx_id}'
        # TODO: support all block explorers for diff chains
        return ''

    def get_absolute_url(self):
        return self.subscription.grant.url + '?tab=transactions'

    def __str__(self):
        """Return the string representation of this object."""
        from django.contrib.humanize.templatetags.humanize import naturaltime
        txid_shortened = self.tx_id[0:10] + "..."
        return f"${round(self.subscription.amount_per_period_usdt)}, txids: {self.tx_id}, {self.split_tx_id}, id: {self.pk}, Success:{self.success}, tx_cleared:{self.tx_cleared} - created {naturaltime(self.created_on)} "

    @property
    def is_first_in_sequence(self):
        """returns true only IFF a contribution is the first in a sequence of subscriptions."""
        other_contributions_after_this_one = Contribution.objects.filter(subscription=self.subscription, created_on__lt=self.created_on)
        return not other_contributions_after_this_one.exists()

    def identity_identifier(self, mechanism):
        """Returns the anti sybil identity identiifer for this grant, according to mechanism."""
        if mechanism == 'originated_address':
            return self.originated_address
        else:
            return self.profile_for_clr.id

    def leave_gitcoinbot_comment_for_status(self, status):
        try:
            from dashboard.models import Profile
            comment = f"Transaction status: {status} (as of {timezone.now().strftime('%Y-%m-%d %H:%m %Z')})"
            profile = Profile.objects.get(handle='gitcoinbot')
            activity = self.subscription.activities.first()
            # delete all before recreating
            Comment.objects.filter(
                profile=profile,
                activity=activity,
            ).delete()
            # create new entry
            Comment.objects.create(
                profile=profile,
                activity=activity,
                comment=comment,
                is_edited=True
            )
        except Exception as e:
            print(e)


    def update_tx_status(self):
        """Updates tx status for Ethereum contributions."""
        try:
            from dashboard.utils import get_web3
            from economy.tx import grants_transaction_validator

            # If `tx_override` is True, we don't run the validator for this contribution
            if self.tx_override:
                return

            # Execute transaction validator based on checkout type
            network = self.subscription.network
            if self.checkout_type == 'eth_zksync':
                # zkSync checkout using their zksync-checkout library

                # Get the tx hash
                if not self.split_tx_id.startswith('sync-tx:') or len(self.split_tx_id) != 72:
                    # Tx hash should start with `sync-tx:` and have a 64 character hash (no 0x prefix)
                    raise Exception('Unsupported zkSync transaction hash format')
                tx_hash = self.split_tx_id.replace('sync-tx:', '0x') # replace `sync-tx:` prefix with `0x`

                # First we get a list of zkSync tokens (TODO: this should be fetched with a management command and be cached)
                tokens_url = 'https://rinkeby-api.zksync.io/api/v0.1/tokens' if network == 'rinkeby' else 'https://api.zksync.io/api/v0.1/tokens'
                r = requests.get(tokens_url)
                r.raise_for_status()
                token_data = r.json() # zkSync token data
                tokens = {}
                for token in token_data:
                    tokens[token['symbol']] = token["id"]

                # Get transaction data with zkSync's API: https://zksync.io/api/v0.1.html#transaction-details
                base_url = 'https://rinkeby-api.zksync.io/api/v0.1' if network == 'rinkeby' else 'https://api.zksync.io/api/v0.1'
                r = requests.get(f"{base_url}/transactions_all/{tx_hash}")
                r.raise_for_status()
                tx_data = r.json() # zkSync transaction data

                # get decimals for the token used in this transaction
                token = Token.objects.filter(
                    network_id=1,
                    network=self.subscription.network,
                    symbol=self.subscription.token_symbol,
                    approved=True
                ).first().to_dict

                # This amount should match what is stated in the API response
                has_same_amount = float(tx_data['amount']) == float(self.subscription.amount_per_period * 10 ** token['decimals'])
                # Get the zksync token ID for the expected token_symbol
                has_same_token = tx_data['token'] == tokens[self.subscription.token_symbol]

                # Update contribution values based on transaction data
                self.originated_address = tx_data['from'] # assumes sender is originator

                # Ensure the onchain token data matches the expected contribution data
                if has_same_token and has_same_amount:
                    self.success = tx_data['fail_reason'] is None # if no failure string, transaction was successful
                    self.validator_passed = True
                    self.split_tx_confirmed = True
                    self.tx_cleared = True
                    self.validator_comment = "zkSync checkout. Success" if self.success else f"zkSync Checkout. {tx_data['fail_reason']}"
                else:
                    # mark the failure as a validator comment
                    fail_reason = "Token ids do not match" if has_same_token else "Amounts do not match"
                    # this contribution data has been deliberately altered mid-flight: fail hard
                    self.success = False
                    self.validator_passed = False
                    self.split_tx_confirmed = False
                    self.tx_cleared = False
                    self.validator_comment = f"zkSync Checkout. Failed: {fail_reason}"

            elif self.checkout_type == 'eth_std' or self.checkout_type == 'eth_polygon':
                # Standard L1 and sidechain L2 checkout using the BulkCheckout contract

                # get active chain std/polygon
                chain =  self.checkout_type.split('_')[-1]

                # Prepare web3 provider
                w3 = get_web3(network, chain=chain)

                # Handle dropped/replaced transactions
                _, split_tx_status, _ = check_for_replaced_tx(
                    self.split_tx_id, network, self.created_on, chain=chain
                )

                # Handle pending txns
                if split_tx_status in ['pending']:
                    then = timezone.now() - timezone.timedelta(hours=1)
                    if self.created_on > then:
                        print('txn pending')
                        self.leave_gitcoinbot_comment_for_status('pending')
                    else:
                        self.success = False
                        self.validator_passed = False
                        self.validator_comment = "txn pending for more than 1 hours, assuming failure"
                        print(self.validator_comment)
                        self.leave_gitcoinbot_comment_for_status('dropped')
                    return

                # Handle dropped txns
                if split_tx_status in ['dropped', 'unknown', '']:
                    self.success = False
                    self.validator_passed = False
                    self.validator_comment = "txn not found"
                    print('txn not found')
                    self.leave_gitcoinbot_comment_for_status('dropped')
                    return

                # Validate that the token transfers occurred
                response = grants_transaction_validator(self, w3, chain=chain)
                if len(response['originator']):
                    self.originated_address = response['originator'][0]
                self.validator_passed = response['validation']['passed']
                self.validator_comment = response['validation']['comment']
                self.tx_cleared = response['tx_cleared']
                self.split_tx_confirmed = response['split_tx_confirmed']
                self.success = self.validator_passed

            else:
                # This validator is only for eth_std and eth_zksync, so exit for other contribution types
                self.leave_gitcoinbot_comment_for_status('unknown')
                return

            # Validator complete!

        except Exception as e:
            self.leave_gitcoinbot_comment_for_status('error')
            self.validator_passed = False
            self.validator_comment = str(e)
            print(f"Exception: {self.validator_comment}")
            self.tx_cleared = False
            self.split_tx_confirmed = False
            self.success = False
        if self.success:
            print("TODO: do stuff related to successful contribs, like emails")
            self.leave_gitcoinbot_comment_for_status('success')
        else:
            print("TODO: do stuff related to failed contribs, like emails")
            self.leave_gitcoinbot_comment_for_status('failed')


@receiver(post_save, sender=Contribution, dispatch_uid="psave_contrib")
def psave_contrib(sender, instance, **kwargs):

    from django.contrib.contenttypes.models import ContentType
    from dashboard.models import Earning
    if instance.subscription and not instance.subscription.negative:
        try:
            Earning.objects.update_or_create(
                source_type=ContentType.objects.get(app_label='grants', model='contribution'),
                source_id=instance.pk,
                defaults={
                    "created_on":instance.created_on,
                    "from_profile":instance.subscription.contributor_profile,
                    "org_profile":instance.subscription.grant.org_profile,
                    "to_profile":instance.subscription.grant.admin_profile,
                    "value_usd":instance.subscription.amount_per_period_usdt if instance.subscription.amount_per_period_usdt else instance.subscription.get_converted_amount(False),
                    "url":instance.subscription.grant.url,
                    "network":instance.subscription.network,
                    "txid":instance.subscription.split_tx_id,
                    "token_name":instance.subscription.token_symbol,
                    "token_value":instance.subscription.amount_per_period,
                    "success":instance.success,
                }
            )
        except:
            pass

@receiver(pre_save, sender=Contribution, dispatch_uid="presave_contrib")
def presave_contrib(sender, instance, **kwargs):

    if not instance.profile_for_clr:
        if instance.subscription:
            instance.profile_for_clr = instance.subscription.contributor_profile

    ele = instance
    sub = ele.subscription
    grant = sub.grant

    # save hotpath data to the contribution itself
    instance.grant = grant
    instance.amount_per_period_usdt = float(sub.amount_per_period_usdt)

    # everything else is stored in a JSONField
    instance.normalized_data = {
        'id': grant.id,
        'logo': grant.logo.url if grant.logo else None,
        'url': grant.url,
        'title': grant.title,
        'amount_per_period_minus_gas_price': float(instance.subscription.amount_per_period_minus_gas_price),
        'amount_per_period_to_gitcoin': float(instance.subscription.amount_per_period_to_gitcoin),
        'created_on': ele.created_on.strftime('%Y-%m-%d'),
        'frequency': int(sub.frequency),
        'frequency_unit': sub.frequency_unit,
        'num_tx_approved': int(sub.num_tx_approved),
        'token_symbol': sub.token_symbol,
        'amount_per_period_usdt': float(sub.amount_per_period_usdt),
        'amount_per_period': float(sub.amount_per_period),
        'admin_address': grant.admin_address,
        'tx_id': ele.tx_id,
    }

    if instance.subscription.contributor_profile:
        scp = instance.subscription.contributor_profile
        instance.normalized_data['handle'] = scp.handle
        instance.normalized_data['last_known_ip'] = scp.last_known_ip
