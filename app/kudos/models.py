# -*- coding: utf-8 -*-
"""Define models.

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

"""
import logging
import urllib.request
from os import path

from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.core.files import File
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.templatetags.static import static
from django.utils import timezone
from django.utils.text import slugify

import environ
import pyvips
from dashboard.models import SendCryptoAsset
from economy.models import SuperModel
from eth_utils import to_checksum_address
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from pyvips.error import Error as VipsError
from unidecode import unidecode

logger = logging.getLogger(__name__)


class TokenQuerySet(models.QuerySet):
    """Handle the manager queryset for Tokens."""

    def visible(self):
        """Filter results down to visible tokens only."""
        return self.filter(hidden=False)

    def keyword(self, keyword):
        """Filter results to all Token objects containing the keywords.

        Args:
            keyword (str): The keyword to search title, issue description, and issue keywords by.

        Returns:
            kudos.models.TokenQuerySet: The QuerySet of tokens filtered by keyword.

        """
        return self.filter(
            Q(name__icontains=keyword) |
            Q(description__icontains=keyword) |
            Q(artist__icontains=keyword) |
            Q(tags__icontains=keyword)
        )


class Token(SuperModel):
    """Model representing a Kudos ERC721 token on the blockchain.

    The model attempts to match the actual blockchain data as much as possible, without being duplicative.

    Attributes:
        artist (str): The artist that created the kudos image.
        background_color (str): 6 digit hex code background color.  See Open Sea docs for details.
        cloned_from_id (int): Orignal Kudos that this one was cloned from.
        contract (FK): Foreing key to the Contract model.
        description (str): Description of the kudos.
        external_url (str): External URL pointer to image asset.  See Open Sea docs for details.
        image (str): Image file name.
        name (str): Kudos name.
        num_clones_allowed (int): How many clones are allowed to be made.
        num_clones_available (int): How many clones the Kudos has left.
        num_clones_in_wild (int): How many clones there are in the wild.
        owner_address (str): ETH address of the owner.  Pulled from the `ownerOf` contract function.
        platform (str): Where the Kudos originated from.
        price_finney (int): Price to clone the Kudos in finney.
        rarity (str): Rarity metric, defined in kudos.utils.py
        tags (str): Comma delimited tags.  TODO:  change to array
        token_id (int): the token_id on the blockchain.
        txid (str): The ethereum transaction id that generated this kudos.

    """

    class Meta:
        """Define metadata associated with Kudos."""

        verbose_name_plural = 'Kudos'
        index_together = [['name', 'description', 'tags'], ]
        unique_together = ('token_id', 'contract',)

    # Kudos Struct (also in contract)
    price_finney = models.IntegerField()
    num_clones_allowed = models.IntegerField(null=True, blank=True)
    num_clones_in_wild = models.IntegerField(null=True, blank=True)
    num_clones_available_counting_indirect_send = models.IntegerField(blank=True, default=0)

    cloned_from_id = models.IntegerField()
    popularity = models.IntegerField(default=0)
    popularity_week = models.IntegerField(default=0)
    popularity_month = models.IntegerField(default=0)
    popularity_quarter = models.IntegerField(default=0)

    # Kudos metadata from tokenURI (also in contract)
    name = models.CharField(max_length=255, db_index=True)
    override_display_name = models.CharField(max_length=255, blank=True)
    description = models.CharField(max_length=510, db_index=True)
    image = models.CharField(max_length=255, null=True)
    rarity = models.CharField(max_length=255, null=True)
    tags = models.CharField(max_length=255, null=True, db_index=True)
    artist = models.CharField(max_length=255, null=True, blank=True, db_index=True)
    platform = models.CharField(max_length=255, null=True, blank=True)
    external_url = models.CharField(max_length=255, null=True)
    background_color = models.CharField(max_length=255, null=True)
    metadata = JSONField(default=dict, blank=True)

    # Extra fields added to database (not on blockchain)
    owner_address = models.CharField(max_length=255)
    txid = models.CharField(max_length=255, null=True, blank=True)
    token_id = models.IntegerField()
    contract = models.ForeignKey(
        'kudos.Contract', related_name='kudos_contract', on_delete=models.SET_NULL, null=True
    )
    hidden = models.BooleanField(default=False, help_text=('Hide from marketplace?'))
    hidden_token_details_page = models.BooleanField(default=False, help_text=('Hide token details page'))
    send_enabled_for_non_gitcoin_admins = models.BooleanField(default=True)
    preview_img_mode = models.CharField(max_length=255, default='png')
    suppress_sync = models.BooleanField(default=False)

    # Token QuerySet Manager
    objects = TokenQuerySet.as_manager()

    @property
    def is_owned_by_gitcoin(self):
        return self.owner_address.lower() == settings.KUDOS_OWNER_ACCOUNT.lower()

    @property
    def on_xdai(self):
        # returns a kudos token object thats on the xdai network; a mirro
        # a mirror of the mainnet with 1000x better costs ( https://github.com/gitcoinco/web/pull/7702/ )
        return self.on_network('xdai')

    @property
    def on_mainnet(self):
        return self.on_network('mainnet')

    @property
    def on_rinkeby(self):
        return self.on_network('rinkeby')

    @property
    def on_networks(self):
        return_me = []
        for network in ['xdai', 'rinkeby', 'mainnet']:
            ref = self.on_network(network)
            if ref:
                return_me.append((network, ref))
        return return_me

    @property
    def on_other_networks(self):
        return [ele for ele in self.on_networks if ele[0] != self.contract.network]

    def on_network(self, network):
        if self.contract.network == network:
            return self
        target = self
        if self.gen > 1:
            target = self.kudos_token_cloned_from
        for token in Token.objects.filter(contract__network=network, num_clones_allowed__gt=1, name=target.name, owner_address=self.owner_address):
            if token.gen == 1:
                return token
        return None


    def save(self, *args, **kwargs):
        if self.owner_address:
            self.owner_address = to_checksum_address(self.owner_address)

        super().save(*args, **kwargs)

    @property
    def artist_count(self):
        return self.artist_others.count()

    @property
    def artist_others(self):
        if not self.artist:
            return Token.objects.none()
        return Token.objects.filter(artist=self.artist, num_clones_allowed__gt=1, hidden=False)

    @property
    def static_image(self):
        if 'v2' in self.image:
            return static(self.image)
        return self.image

    @property
    def ui_name(self):
        from kudos.utils import humanize_name
        return self.override_display_name if self.override_display_name else humanize_name(self.name)

    @property
    def price_in_eth(self):
        """Convert price from finney to eth.

        Returns:
            float or int:  price in eth.

        """
        return self.price_finney / 1000

    @property
    def price_in_wei(self):
        """Convert price from finney to wei.

        Returns:
            float or int:  price in wei.

        """
        return self.price_in_eth * 10**18

    @property
    def price_in_gwei(self):
        """Convert price from finney to gwei.

        Returns:
            float or int:  price in gwei.

        """
        return self.price_in_eth * 10**9

    @property
    def price_in_usdt(self):
        from economy.utils import ConversionRateNotFoundError, convert_token_to_usdt
        if hasattr(self, 'price_usdt'):
            return self.price_usdt
        try:
            self.price_usdt = round(convert_token_to_usdt('ETH') * self.price_in_eth, 2)
            return self.price_usdt
        except ConversionRateNotFoundError:
            return None


    @property
    def shortened_address(self):
        """Shorten ethereum address to only the first and last 4 digits.

        Returns:
            str: shortened address.

        """
        return self.owner_address[:6] + '...' + self.owner_address[38:]

    @property
    def capitalized_name(self):
        """Capitalize name

        Returns:
            str: Capitalized name.

        """
        return ' '.join([x.capitalize() for x in self.name.split('_')])

    @property
    def num_clones_available(self):
        """Calculate the number of clones available for a kudos.

        Returns:
            int: Number of clones available.

        """
        r = self.num_clones_allowed - self.num_clones_in_wild
        if r < 0:
            r = 0
        return r

    @property
    def humanized_name(self):
        """Turn snake_case into Snake Case.

        Returns:
            str: The humanized name.

        """
        return ' '.join([x.capitalize() for x in self.name.split('_')])

    @property
    def tags_as_array(self):
        return [tag.strip() for tag in self.tags.split(',')]

    @property
    def owners_profiles(self):
        """.

        Returns:
            array: QuerySet of Profiles

        """
        from dashboard.models import Profile
        related_kudos_transfers = KudosTransfer.objects.filter(kudos_token_cloned_from=self.pk).send_happy_path()
        related_profiles_pks = related_kudos_transfers.values_list('recipient_profile_id', flat=True)
        related_profiles = Profile.objects.filter(pk__in=related_profiles_pks).distinct()
        return related_profiles

    @property
    def owners_handles(self):
        """.
            differs from `owners_profiles` in that not everyone who has received a kudos has a profile
        Returns:
            array: array of handles

        """
        from dashboard.models import Profile
        related_kudos_transfers = KudosTransfer.objects.filter(kudos_token_cloned_from=self.pk).exclude(recipient_profile__isnull=True)
        related_kudos_transfers = related_kudos_transfers.send_success() | related_kudos_transfers.send_pending()
        related_kudos_transfers = related_kudos_transfers.distinct('id')

        return related_kudos_transfers.values_list('recipient_profile__handle', flat=True)

    @property
    def _num_clones_available_counting_indirect_send(self):
        return self.num_clones_allowed - self.num_clones_in_wild_counting_indirect_send

    @property
    def num_clones_in_wild_counting_indirect_send(self):
        num_total_sends_we_know_about = len(self.owners_handles)
        if num_total_sends_we_know_about > self.num_clones_in_wild:
            return num_total_sends_we_know_about
        return self.num_clones_in_wild

    def humanize(self):
        self.owner_address = self.shortened_address
        self.name = self.capitalized_name
        self.num_clones_available = self.get_num_clones_available()
        return self

    @property
    def gen(self):
        if self.num_clones_allowed > 0:
            return 1
        return 2

    def __str__(self):
        """Return the string representation of a model."""
        return f"{self.contract.network} Gen {self.gen} Kudos Token: {self.humanized_name}"

    @property
    def as_img(self):
        """Convert the provided buffer to another format.

        Args:
            obj (File): The File/ContentFile object.

        Exceptions:
            Exception: Cowardly catch blanket exceptions here, log it, and return None.

        Returns:
            BytesIO: The BytesIO stream containing the converted File data.
            None: If there is an exception, the method returns None.

        """
        root = environ.Path(__file__) - 2  # Set the base directory to two levels.
        file_path = root('assets') + '/' + self.image

        # download it if file is remote
        if settings.AWS_STORAGE_BUCKET_NAME and settings.AWS_STORAGE_BUCKET_NAME in self.image:
            file_path = f'cache/{self.pk}.png'
            if not path.exists(file_path):
                safe_url = self.image.replace(' ', '%20')
                filedata = urllib.request.urlopen(safe_url)
                datatowrite = filedata.read()
                with open(file_path, 'wb') as f:
                    f.write(datatowrite)

        # serve file
        try:
            with open(file_path, 'rb') as f:
                obj = File(f)
                from avatar.utils import svg_to_png
                return svg_to_png(obj.read(), scale=3, width=333, height=384, index=self.pk, prefer='inkscape')
        except:
            return None


    @property
    def img_url(self):
        return f'{settings.BASE_URL}dynamic/kudos/{self.pk}/{slugify(unidecode(self.name))}'

    @property
    def preview_img_url(self):
        if self.preview_img_mode == 'png':
            return self.img_url
        if "https:" in self.image:
            return self.image
        return static(self.image)

    @property
    def url(self):
        return f'{settings.BASE_URL}kudos/{self.pk}/{slugify(unidecode(self.name))}'

    def get_absolute_url(self):
        return self.url

    def get_relative_url(self):
        """Get the relative URL for the Bounty.

        Attributes:
            preceding_slash (bool): Whether or not to include a preceding slash.

        Returns:
            str: The relative URL for the Bounty.

        """
        return f'/kudos/{self.pk}/{slugify(unidecode(self.name))}'

    @property
    def is_available(self):
        return self.num_clones_allowed > 0 and self.num_clones_available_counting_indirect_send > 0

    def send_enabled_for(self, user):
        """

        Arguments:
        - user: a django user object

        Returns:
            bool: Wehther a send should be enabled for this user
        """
        if not self.is_available:
            return False
        is_enabled_for_user_in_general = self.send_enabled_for_non_gitcoin_admins
        is_enabled_for_this_user = hasattr(user, 'profile') and TransferEnabledFor.objects.filter(profile=user.profile, token=self).exists()
        is_enabled_because_staff = user.is_authenticated and user.is_staff
        return is_enabled_for_this_user or is_enabled_for_user_in_general or is_enabled_because_staff


@receiver(pre_save, sender=Token, dispatch_uid="psave_token")
def psave_token(sender, instance, **kwargs):
    instance.num_clones_available_counting_indirect_send = instance._num_clones_available_counting_indirect_send

    from django.contrib.contenttypes.models import ContentType
    from search.models import SearchResult
    if instance.pk and instance.gen == 1 and not instance.hidden:
        SearchResult.objects.update_or_create(
            source_type=ContentType.objects.get(app_label='kudos', model='token'),
            source_id=instance.pk,
            defaults={
                "created_on":instance.created_on,
                "title":instance.humanized_name,
                "description":instance.description,
                "url":instance.url,
                "visible_to":None,
                'img_url': instance.img_url,
            }
            )


@receiver(post_save, sender=Token, dispatch_uid="postsave_token")
def postsave_token(sender, instance, created, **kwargs):
    if created:
        if instance.pk and instance.gen == 1 and not instance.hidden:
            from dashboard.models import Activity, Profile
            gcb = Profile.objects.filter(handle='gitcoinbot').first()
            if not gcb:
                return
            kwargs = {
                'activity_type': 'created_kudos',
                'kudos': instance,
                'profile': gcb,
                'metadata': {
                }
            }
            Activity.objects.create(**kwargs)


class KudosTransfer(SendCryptoAsset):
    """Model that represents a request to clone a Kudos.

    Typically this gets created when using the "kudos send" functionality.
    The model is inherited from the SendCryptoAsset model, which is also used by Tips.

    Attributes:
        from_address (str): Eth address of the person that is sending the kudos.
        kudos_token (kudos.Token): Foreign key to the kudos_token that was cloned.
            This is filled in after the kudos has been cloned.
        kudos_token_cloned_from (kudos.Token): Foreign key to the kudos_token that will be cloned and sent.
        recipient_profile (dashboard.Profile): Foreign key to the profile of the person that is being sent the kudos.
        sender_profile (dashboard.Profile): Foreign key to the profile of the person that is sending the kudos.

    """

    # kudos_token_cloned_from is a reference to the original Kudos Token that is being cloned.
    kudos_token_cloned_from = models.ForeignKey(
        'kudos.Token', related_name='kudos_token_cloned_from', on_delete=models.SET_NULL, null=True
    )
    # kudos_token is a reference to the new Kudos Token that is soon to be minted
    kudos_token = models.OneToOneField(
        'kudos.Token', related_name='kudos_transfer', on_delete=models.SET_NULL, null=True, blank=True
    )

    recipient_profile = models.ForeignKey(
        'dashboard.Profile', related_name='received_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )
    sender_profile = models.ForeignKey(
        'dashboard.Profile', related_name='sent_kudos', on_delete=models.SET_NULL, null=True, blank=True
    )
    trust_url = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.from_address:
            self.from_address = to_checksum_address(self.from_address)
        if self.receive_address:
            self.receive_address = to_checksum_address(self.receive_address)

        super().save(*args, **kwargs)

    @property
    def receive_url(self):
        """URL used for indirect send.  Deprecated in favor of receive_url_for_recipient

        Returns:
            str: URL for recipient.

        """
        return self.receive_url_for_recipient

    @property
    def receive_url_for_recipient(self):
        """URL used for indirect send.  Deprecated in favor of receive_url_for_recipient

        Returns:
            str: URL for recipient.

        """
        try:
            key = self.metadata['reference_hash_for_receipient']
            return f"{settings.BASE_URL}kudos/receive/v3/{key}/{self.txid}/{self.network}"
        except KeyError as e:
            logger.debug(e)
            return ''

    def __str__(self):
        """Return the string representation of a model."""
        status = 'funded' if self.txid else 'not funded'
        if self.receive_txid:
            status = 'received'
        if self.txid == "pending_celery":
            status = 'pending broadcast'
        to = self.username if self.username else self.receive_address
        return f"({status}) transfer of {self.kudos_token_cloned_from} from {self.sender_profile} to {to} on {self.network}"


@receiver(post_save, sender=KudosTransfer, dispatch_uid="psave_kt")
def psave_kt(sender, instance, **kwargs):
    token = instance.kudos_token_cloned_from
    if token:
        all_transfers = KudosTransfer.objects.filter(kudos_token_cloned_from=token).send_happy_path()
        token.popularity = all_transfers.count()
        token.popularity_week = all_transfers.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=7))).count()
        token.popularity_month = all_transfers.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=30))).count()
        token.popularity_quarter = all_transfers.filter(created_on__gt=(timezone.now() - timezone.timedelta(days=90))).count()
        token.save()

    from django.contrib.contenttypes.models import ContentType
    from dashboard.models import Earning
    Earning.objects.update_or_create(
        source_type=ContentType.objects.get(app_label='kudos', model='kudostransfer'),
        source_id=instance.pk,
        defaults={
            "created_on":instance.created_on,
            "from_profile":instance.sender_profile,
            "org_profile":instance.org_profile,
            "to_profile":instance.recipient_profile,
            "value_usd":instance.value_in_usdt_then,
            "url":instance.kudos_token_cloned_from.url if instance.kudos_token_cloned_from else '',
            "network":instance.network,
            "txid":instance.txid,
            "token_name":'ETH',
            "token_value":token.price_in_eth if token else 0,
            "success":instance.tx_status == 'success',
        }
        )


class Contract(SuperModel):

    address = models.CharField(max_length=255, unique=True)
    is_latest = models.BooleanField(default=False)
    network = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if self.address:
            self.address = to_checksum_address(self.address)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return the string representation of a model."""
        return f"{self.address} / {self.network} / {self.is_latest}"


class Wallet(SuperModel):
    """DEPRECATED.  Kudos Address where the tokens are stored.

    Currently not used.  Instead we are using preferred_payout_address for now.

    Attributes:
        address (TYPE): Description
        profile (TYPE): Description

    """

    address = models.CharField(max_length=255, unique=True)
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='kudos_wallets', on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        """Return the string representation of a model."""
        return f"Wallet: {self.address} Profile: {self.profile}"


class BulkTransferCoupon(SuperModel):

    """Model representing a bulk send of Kudos
    """
    token = models.ForeignKey(
        'kudos.Token', related_name='bulk_transfers', on_delete=models.CASCADE
    )
    num_uses_total = models.IntegerField()
    num_uses_remaining = models.IntegerField()
    current_uses = models.IntegerField(default=0)
    secret = models.CharField(max_length=255, unique=True)
    comments_to_put_in_kudos_transfer = models.CharField(max_length=255, blank=True)
    sender_profile = models.ForeignKey(
        'dashboard.Profile', related_name='bulk_transfers', on_delete=models.CASCADE
    )

    sender_address = models.CharField(max_length=255, blank=True)
    sender_pk = models.CharField(max_length=255, blank=True)
    tag = models.CharField(max_length=255, blank=True)
    metadata = JSONField(default=dict, blank=True)
    make_paid_for_first_minutes = models.IntegerField(default=0)

    def __str__(self):
        """Return the string representation of a model."""
        return f"Token: {self.token} num_uses_total: {self.num_uses_total}"

    def get_absolute_url(self):
        return settings.BASE_URL + f"kudos/redeem/{self.secret}"

    @property
    def url(self):
        return f"/kudos/redeem/{self.secret}"

    @property
    def paid_until(self):
        return self.created_on + timezone.timedelta(minutes=self.make_paid_for_first_minutes)

    @property
    def is_paid_right_now(self):
        return timezone.now() < self.paid_until

@receiver(pre_save, sender=BulkTransferCoupon, dispatch_uid="psave_BulkTransferCoupon")
def psave_BulkTransferCoupon(sender, instance, **kwargs):
    is_owned_by_gitcoin = instance.token.owner_address.lower() == "0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F".lower()
    is_kudos_token_deployed_to_gitcoin = not bool(instance.sender_pk)

    if not is_owned_by_gitcoin and is_kudos_token_deployed_to_gitcoin:
        raise Exception("This bulk transfer kudos has been created to airdrop a kudos.. But the kudos is not owned by Gitcoin... If this kudos goes live, people will redeem it and it will deplete the ETH in the kudos airdropper; which is bad!  Please correct the kudos to either be one that is owned by Gitcoin, or one that has a seperate source of ETH (by sending sender_pk).  Thank you and have a nice day -- Kevin Owocki, protector of Gitcoin's ETH")


class BulkTransferRedemption(SuperModel):

    """Model representing a bulk send of Kudos
    """
    coupon = models.ForeignKey(
        'kudos.BulkTransferCoupon', related_name='bulk_transfer_redemptions', on_delete=models.CASCADE
    )
    redeemed_by = models.ForeignKey(
        'dashboard.Profile', related_name='bulk_transfer_redemptions', on_delete=models.CASCADE
    )
    ip_address = models.GenericIPAddressField(default=None, null=True)
    kudostransfer = models.ForeignKey(
        'kudos.KudosTransfer', related_name='bulk_transfer_redemptions', on_delete=models.CASCADE
    )

    def __str__(self):
        """Return the string representation of a model."""
        return f"coupon: {self.coupon} redeemed_by: {self.redeemed_by}"


class TokenRequest(SuperModel):
    """Define the TokenRequest model."""

    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(max_length=500, default='')
    priceFinney = models.IntegerField(default=18)
    network = models.CharField(max_length=25, db_index=True)
    artist = models.CharField(max_length=255)
    platform = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    bounty_url = models.CharField(max_length=255, blank=True, default='')
    artwork_url = models.CharField(max_length=255)
    numClonesAllowed = models.IntegerField(default=18)
    metadata = JSONField(null=True, default=dict, blank=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    approved = models.BooleanField(default=True)
    processed = models.BooleanField(default=False)
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='token_requests', on_delete=models.CASCADE,
    )
    rejection_reason = models.TextField(max_length=500, default='', blank=True)
    gas_price_overide = models.IntegerField(default=0, help_text=('If non-zero, then the celery task will use this gas price to mint hte kudos'))

    def __str__(self):
        """Define the string representation of a conversion rate."""
        return f"approved: {self.approved}, rejected: {bool(self.rejection_reason)} -- {self.name} on {self.network} on {self.created_on};"


    def mint(self, gas_price_gwei=None):
        """Approve / mint this token."""
        from kudos.management.commands.mint_all_kudos import mint_kudos # avoid circular import
        from kudos.utils import KudosContract # avoid circular import
        account = settings.KUDOS_OWNER_ACCOUNT
        private_key = settings.KUDOS_PRIVATE_KEY
        kudos = {
            'name': self.name,
            'description': self.description,
            'priceFinney': self.priceFinney,
            'artist': self.artist,
            'platform': self.platform,
            'numClonesAllowed': self.numClonesAllowed,
            'tags': self.tags,
            'artwork_url': self.artwork_url,
        }
        kudos_contract = KudosContract(network=self.network)
        gas_price_gwei = recommend_min_gas_price_to_confirm_in_time(1) * 2 if not gas_price_gwei else None
        tx_id = mint_kudos(kudos_contract, kudos, account, private_key, gas_price_gwei, mint_to=self.to_address, live=True, dont_wait_for_kudos_id_return_tx_hash_instead=True)
        self.processed = True
        self.approved = True
        self.save()
        return tx_id

class TransferEnabledFor(SuperModel):
    """Model that represents the ability to send a Kudos, i
    f token.send_enabled_for_non_gitcoin_admins is true.

    """

    token = models.ForeignKey(
        'kudos.Token', related_name='transfers_enabled', on_delete=models.CASCADE,
    )
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='transfers_enabled', on_delete=models.CASCADE,
    )

    def __str__(self):
        """Return the string representation of a model."""
        return f"{self.token} <> {self.profile}"
