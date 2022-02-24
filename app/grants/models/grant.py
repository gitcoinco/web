import json

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.postgres.fields import ArrayField, JSONField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.core import serializers
from django.db import models
from django.db.models import Q
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_extensions.db.fields import AutoSlugField
from economy.models import SuperModel
from grants.utils import get_upload_filename, is_grant_team_member
from townsquare.models import Favorite
from web3 import Web3

from .clr_match import CLRMatch
from .contribution import Contribution
from .grant_clr_calculation import GrantCLRCalculation
from .grant_collection import GrantCollection
from .subscription import Subscription


class GrantPayout(SuperModel):
    PAYOUT_STATUS = [
        ('pending', 'pending'),
        ('ready', 'ready'),
        ('expired', 'expired'),
        ('funding_withdrawn', 'funding_withdrawn')
    ]
    NETWORKS = [
        ('mainnet', 'mainnet'),
        ('rinkeby', 'rinkeby'),
        # ('polygon', 'polygon'),
        # ('mumbai', 'mumbai'),
    ]

    name = models.CharField(
        max_length=25,
        help_text=_('Display Name for Payout')
    )
    contract_address = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Payout Contract from which funds would be claimed')
    )
    network = models.CharField(
        max_length=15,
        default='mainnet',
        choices=NETWORKS,
        help_text=_('Network where contract is deployed')
    )
    token = models.ForeignKey(
        'economy.Token',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=_('Token in which amount should be paid out')
    )
    conversion_rate = models.FloatField(
        default=1.0,
        help_text=_('token to USD conversion rate')
    )
    conversion_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('date on which conversion_rate was set')
    )
    status = models.CharField(
        max_length=20,
        choices=PAYOUT_STATUS,
        default='pending'
    )
    funding_withdrawal_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When was funding in Matching Contract withdrawn?')
    )

    def __str__(self):
        return f"{self.name} Payout"


class GrantCLR(SuperModel):

    CLR_TYPES = (
        ('main', 'Main Round'),
        ('ecosystem', 'Ecosystem Round'),
        ('cause', 'Cause Round'),
    )
    class Meta:
        unique_together = ('customer_name', 'round_num', 'sub_round_slug',)

    customer_name = models.CharField(
        max_length=15,
        default='',
        blank=True,
        help_text="used to generate customer_name/round_num/sub_round_slug"
    )
    round_num = models.PositiveIntegerField(
        help_text="CLR Round Number. used to generate customer_name/round_num/sub_round_slug"
    )
    sub_round_slug = models.CharField(
        max_length=25,
        default='',
        blank=True,
        help_text="used to generate customer_name/round_num/sub_round_slug"
    )
    display_text = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        help_text="sets the custom text in CLR banner on the landing page"
    )
    owner = models.ForeignKey(
        'dashboard.Profile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text='sets the owners profile photo in CLR banner on the landing page'
    )
    grant_clr_percentage_cap = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True, help_text="Percentage of total pot at which Grant CLR should be capped")
    is_active = models.BooleanField(default=False, db_index=True, help_text="Is CLR Round currently active")
    start_date = models.DateTimeField(help_text="CLR Round Start Date")
    end_date = models.DateTimeField(help_text="CLR Round End Date")
    claim_start_date = models.DateTimeField(help_text="CLR Claim Start Date", blank=True, null=True)
    claim_end_date = models.DateTimeField(help_text="CLR Claim End Date", blank=True, null=True)
    grant_filters = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grants allowed in this CLR round"
    )
    grant_excludes = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grants excluded in this CLR round"
    )
    subscription_filters = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grant Subscription to be allowed in this CLR round"
    )
    collection_filters = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grant Collections to be allowed in this CLR round"
    )
    verified_threshold = models.DecimalField(
        help_text="This is the verfied CLR threshold. You can generally increase the saturation of the round / increase the CLR match by increasing this value, as it has a proportional relationship. However, depending on the pair totals by grant, it may reduce certain matches. In any case, please use the contribution multiplier first.",
        default=25.0,
        decimal_places=2,
        max_digits=5
    )
    unverified_threshold = models.DecimalField(
        help_text="This is the unverified CLR threshold. The relationship with the CLR match is the same as the verified threshold. If you would like to increase the saturation of round / increase the CLR match, increase this value, but please use the contribution multiplier first.",
        default=5.0,
        decimal_places=2,
        max_digits=5
    )
    total_pot = models.DecimalField(
        help_text="Total CLR Pot",
        default=0,
        decimal_places=2,
        max_digits=10
    )
    contribution_multiplier = models.DecimalField(
        help_text="This contribution multipler is applied to each contribution before running CLR calculations. In order to increase the saturation, please increase this value first, before modifying the thresholds.",
        default=1.0,
        decimal_places=4,
        max_digits=10
    )
    logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        max_length=500,
        help_text=_('sets the background in CLR banner on the landing page'),
    )
    type = models.CharField(
        max_length=25,
        choices=CLR_TYPES,
        default='main',
        help_text="Grant CLR Type"
    )
    logo_text_hex= models.CharField(
        blank=True,
        null=True,
        default='#000000',
        max_length=15,
        help_text=_("sets the text color of the logo")
    )
    banner_bg_hex = models.CharField(
        blank=True,
        null=True,
        default='#11BC92',
        max_length=15,
        help_text=_("sets the bg color on the banner below the logo")
    )
    banner_text_hex = models.CharField(
        blank=True,
        null=True,
        default='#FFF',
        max_length=15,
        help_text=_("sets the text color on the banner below the logo")
    )
    banner_text = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=_("text which appears below banner")
    )

    grant_payout = models.ForeignKey(
        'grants.GrantPayout',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='grant_clrs',
        help_text=_('Grant Payout')
    )

    def __str__(self):
        return f"pk:{self.pk}, round_num: {self.round_num}"

    @property
    def happening_now(self):
        # returns true if we are within the time range for this round
        now = timezone.now()
        return now >= self.start_date and now <= self.end_date

    @property
    def happened_recently(self):
        # returns true if we are within a week or 2 of this round
        days = 14
        now = timezone.now()
        then = timezone.now() - timezone.timedelta(days=days)
        return now >= self.start_date and then <= self.end_date

    @property
    def grants(self):

        grants = Grant.objects.filter(hidden=False, active=True, is_clr_eligible=True, link_to_new_grant=None)
        if self.collection_filters:
            grant_ids = GrantCollection.objects.filter(**self.collection_filters).values_list('grants', flat=True)
            grants = grants.filter(pk__in=grant_ids)
        if self.grant_filters:
            grants = grants.filter(**self.grant_filters)
        if self.subscription_filters:
            grants = grants.filter(**self.subscription_filters)

        return grants


    def record_clr_prediction_curve(self, grant, clr_prediction_curve):
        # update matching records
        self.clr_calculations.filter(grant=grant, latest=True).update(active=False, latest=False)
        # create the new record
        GrantCLRCalculation.objects.create(
            grantclr=self,
            grant=grant,
            clr_prediction_curve=clr_prediction_curve,
            active=True if self.is_active else False,
            latest=True,
        )


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
        if not keyword:
            return self
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
        indexes = (GinIndex(fields=["vector_column"]),)
        index_together = [
            ["last_update", "network", "active", "hidden"],
            ["last_update", "network", "active", "hidden", "weighted_shuffle"],
        ]


    REGIONS = [
        ('north_america', 'North America'),
        ('oceania', 'Oceania'),
        ('latin_america', 'Latin America'),
        ('europe', 'Europe'),
        ('africa', 'Africa'),
        ('middle_east', 'Middle East'),
        ('india', 'India'),
        ('east_asia', 'East Asia'),
        ('southeast_asia', 'Southeast Asia')
    ]

    EXTERNAL_FUNDING = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('unknown', 'Unknown')
    ]

    vector_column = SearchVectorField(null=True, help_text=_('Used for full text search. Generated using [title, description]'))
    active = models.BooleanField(default=True, help_text=_('Whether or not the Grant is active.'), db_index=True)
    grant_type = models.ForeignKey('GrantType', on_delete=models.CASCADE, null=True, help_text="Grant Type")
    title = models.CharField(default='', max_length=255, help_text=_('The title of the Grant.'))
    slug = AutoSlugField(populate_from='title')
    description = models.TextField(default='', blank=True, help_text=_('The description of the Grant.'))
    description_rich = models.TextField(default='', blank=True, help_text=_('HTML rich description.'))
    reference_url = models.URLField(blank=True, help_text=_('The associated reference URL of the Grant.'))
    github_project_url = models.URLField(blank=True, null=True, help_text=_('Grant Github Project URL'))
    is_clr_eligible = models.BooleanField(default=True, help_text="Is grant eligible for CLR")
    admin_message = models.TextField(default='', blank=True, help_text=_('An admin message that will be shown to visitors of this grant.'))
    visible = models.BooleanField(default=True, help_text="Is grant visible on the site")
    region = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        choices=REGIONS,
        help_text="region to which grant belongs to"
    )
    link_to_new_grant = models.ForeignKey(
        'grants.Grant',
        null=True,
        on_delete=models.SET_NULL,
        help_text=_('Link to new grant if migrated')
    )
    logo = models.ImageField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        max_length=500,
        help_text=_('The Grant logo image.'),
    )
    logo_svg = models.FileField(
        upload_to=get_upload_filename,
        null=True,
        blank=True,
        help_text=_('The Grant logo SVG.'),
    )
    # TODO-GRANTS: rename to eth_payout_address
    admin_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        db_index=True,
        help_text=_('The wallet address where subscription funds will be sent.'),
    )
    zcash_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The zcash wallet address where subscription funds will be sent.'),
    )
    celo_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The celo wallet address where subscription funds will be sent.'),
    )
    zil_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The zilliqa wallet address where subscription funds will be sent.'),
    )
    polkadot_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The polkadot wallet address where subscription funds will be sent.'),
    )
    kusama_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The kusama wallet address where subscription funds will be sent.'),
    )
    harmony_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The harmony wallet address where subscription funds will be sent.'),
    )
    binance_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The binance wallet address where subscription funds will be sent.'),
    )
    rsk_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The rsk wallet address where subscription funds will be sent.'),
    )
    algorand_payout_address = models.CharField(
        max_length=255,
        default='0x0',
        null=True,
        blank=True,
        help_text=_('The algorand wallet address where subscription funds will be sent.'),
    )
    # TODO-GRANTS: remove
    contract_owner_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The wallet address that owns the subscription contract and is able to call endContract()'),
    )
    amount_received_in_round = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The amount received in USD this round.'),
    )
    monthly_amount_subscribed = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The monthly subscribed to by contributors USD.'),
    )
    amount_received = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The total amount received for the Grant in USD.'),
    )
    # TODO-GRANTS: remove
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
    # TODO-GRANTS: remove
    contract_address = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The contract address of the Grant.'),
    )
    # TODO-GRANTS: remove
    deploy_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for contract deployment.'),
    )
    # TODO-GRANTS: remove
    cancel_tx_id = models.CharField(
        max_length=255,
        default='0x0',
        help_text=_('The transaction id for endContract.'),
        blank=True,
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
        db_index=True
    )
    required_gas_price = models.DecimalField(
        default='0',
        decimal_places=0,
        max_digits=50,
        help_text=_('The required gas price for the Grant.'),
    )
    admin_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grants',
        on_delete=models.CASCADE,
        help_text=_('The Grant administrator\'s profile.'),
        null=True,
    )
    team_members = models.ManyToManyField(
        'dashboard.Profile',
        related_name='grant_teams',
        help_text=_('The team members contributing to this Grant.'),
    )
    image_css = models.CharField(default='', blank=True, max_length=255, help_text=_('additional CSS to attach to the grant-banner img.'))
    amount_received_with_phantom_funds = models.DecimalField(
        default=0,
        decimal_places=2,
        max_digits=20,
        help_text=_('The fundingamount across all rounds with phantom funding'),
    )
    activeSubscriptions = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    hidden = models.BooleanField(default=False, help_text=_('Hide the grant from the /grants page?'), db_index=True)
    random_shuffle = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    weighted_shuffle = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    contribution_count = models.PositiveIntegerField(blank=True, default=0)
    contributor_count = models.PositiveIntegerField(blank=True, default=0)
    # TODO-GRANTS: remove
    positive_round_contributor_count = models.PositiveIntegerField(blank=True, default=0)
    # TODO-GRANTS: remove
    negative_round_contributor_count = models.PositiveIntegerField(blank=True, default=0)

    defer_clr_to = models.ForeignKey(
        'grants.Grant',
        related_name='defered_clr_from',
        on_delete=models.CASCADE,
        help_text=_('The Grant that this grant defers it CLR contributions to (if any).'),
        null=True,
    )
    # TODO-CROSS-GRANT: [{round: fk1, value: time}]
    last_clr_calc_date = models.DateTimeField(
        help_text=_('The last clr calculation date'),
        null=True,
        blank=True,
    )
    # TODO-CROSS-GRANT: [{round: fk1, value: time}]
    next_clr_calc_date = models.DateTimeField(
        help_text=_('The last clr calculation date'),
        null=True,
        blank=True,
    )
    # TODO-CROSS-GRANT: [{round: fk1, value: time}]
    last_update = models.DateTimeField(
        help_text=_('The last grant admin update date'),
        null=True,
        blank=True,
        db_index=True,
    )
    categories = models.ManyToManyField('GrantCategory', blank=True) # TODO: REMOVE
    tags = models.ManyToManyField('GrantTag', blank=True)
    twitter_handle_1 = models.CharField(default='', max_length=255, help_text=_('Grants twitter handle'), blank=True)
    twitter_handle_2 = models.CharField(default='', max_length=255, help_text=_('Grants twitter handle'), blank=True)
    twitter_handle_1_follower_count = models.PositiveIntegerField(blank=True, default=0)
    twitter_handle_2_follower_count = models.PositiveIntegerField(blank=True, default=0)
    sybil_score = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The Grants Sybil Score'),
    )

    # TODO-GRANTS: remove funding_info
    funding_info = models.CharField(default='', blank=True, null=True, max_length=255, help_text=_('Is this grant VC funded?'))
    has_external_funding = models.CharField(
        max_length=8,
        default='unknown',
        choices=EXTERNAL_FUNDING,
        help_text="Does this grant have external funding"
    )

    clr_prediction_curve = ArrayField(
        ArrayField(
            models.FloatField(),
            size=2,
        ), blank=True, default=list, help_text=_('5 point curve to predict CLR donations.'))

    weighted_risk_score = models.DecimalField(
        default=0,
        decimal_places=4,
        max_digits=50,
        help_text=_('The Grants Weighted Risk Score'),
    )

    in_active_clrs = models.ManyToManyField(
        "GrantCLR",
        help_text="Active Grants CLR Round"
    )
    is_clr_active = models.BooleanField(default=False, help_text=_('CLR Round active or not? (auto computed)'))
    clr_round_num = models.CharField(default='', max_length=255, help_text=_('the CLR round number thats active'), blank=True)

    twitter_verified = models.BooleanField(default=False, help_text='The owner grant has verified the twitter account')
    twitter_verified_by = models.ForeignKey('dashboard.Profile', null=True, blank=True, on_delete=models.SET_NULL, help_text='Team member who verified this grant')
    twitter_verified_at = models.DateTimeField(blank=True, null=True, help_text='At what time and date what verified this grant')

    # Grant Query Set used as manager.
    objects = GrantQuerySet.as_manager()

    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, active: {self.active}, title: {self.title}, type: {self.grant_type}"

    def is_on_team(self, profile):
        return is_grant_team_member(self, profile)


    def calc_clr_round(self):
        clr_round = None

        # create_grant_active_clr_mapping
        clr_rounds = GrantCLR.objects.all()
        for this_clr_round in clr_rounds:
            add_to_round = self.active and not self.hidden and this_clr_round.is_active and this_clr_round.happening_now and self.pk in this_clr_round.grants.all().values_list('pk', flat=True)
            if add_to_round:
                self.in_active_clrs.add(this_clr_round)
            else:
                if this_clr_round in self.in_active_clrs.all():
                    self.in_active_clrs.remove(this_clr_round)

        # create_grant_clr_cache
        if self.in_active_clrs.count() > 0 and self.is_clr_eligible:
            clr_round = self.in_active_clrs.first()

        if clr_round:
            self.is_clr_active = True
            self.clr_round_num = clr_round.round_num
        else:
            self.is_clr_active = False
            self.clr_round_num = ''


    @property
    def tenants(self):
        """returns list of chains the grant can recieve contributions in"""
        tenants = []
        # TODO: rename to eth_payout_address
        if self.admin_address and self.admin_address != '0x0':
            tenants.append('ETH')
        if self.zcash_payout_address and self.zcash_payout_address != '0x0':
            tenants.append('ZCASH')
        if self.celo_payout_address and self.celo_payout_address != '0x0':
            tenants.append('CELO')
        if self.zil_payout_address and self.zil_payout_address != '0x0':
            tenants.append('ZIL')
        if self.polkadot_payout_address and self.polkadot_payout_address != '0x0':
            tenants.append('POLKADOT')
        if self.kusama_payout_address and self.kusama_payout_address != '0x0':
            tenants.append('KUSAMA')
        if self.harmony_payout_address and self.harmony_payout_address != '0x0':
            tenants.append('HARMONY')
        if self.binance_payout_address and self.binance_payout_address != '0x0':
            tenants.append('BINANCE')
        if self.rsk_payout_address and self.rsk_payout_address != '0x0':
            tenants.append('RSK')
        if self.algorand_payout_address and self.algorand_payout_address != '0x0':
            tenants.append('ALGORAND')

        return tenants


    @property
    def calc_clr_round_nums(self):
        """Generates CLR rounds sub_round_slug seperated by comma"""
        if self.pk:
            round_nums = [ele for ele in self.in_active_clrs.values_list('sub_round_slug', flat=True)]
            round_nums = list(filter(None, round_nums))
            return ", ".join(round_nums)
        return ''


    @property
    def calc_clr_round_label(self):
        """Generates CLR rounds display text seperated by comma"""
        if self.pk:
            round_nums = [ele for ele in self.in_active_clrs.values_list('display_text', flat=True)]
            round_nums = list(filter(None, round_nums))
            return ", ".join(round_nums)
        return ''


    @property
    def calc_clr_prediction_curve(self):
        # [amount_donated, match amount, bonus_from_match_amount ], etc..
        # [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]
        _clr_prediction_curve = []
        for insert_clr_calc in self.clr_calculations.using('default').filter(latest=True, active=True).order_by('-created_on'):
            insert_clr_calc = insert_clr_calc.clr_prediction_curve
            if not _clr_prediction_curve:
                _clr_prediction_curve = insert_clr_calc
            else:
                for j in [1,2]:
                    for i in [0,1,2,3,4,5]:
                        # add the 1 and 2 index of each clr prediction cuve
                        _clr_prediction_curve[i][j] += insert_clr_calc[i][j]

        if not _clr_prediction_curve:
            _clr_prediction_curve = [[0.0, 0.0, 0.0] for x in range(0, 6)]

        return _clr_prediction_curve


    def updateActiveSubscriptions(self):
        """updates the active subscriptions list"""
        handles = []
        for handle in Subscription.objects.filter(grant=self, active=True, is_postive_vote=True).distinct('contributor_profile').values_list('contributor_profile__handle', flat=True):
            handles.append(handle)
        self.activeSubscriptions = handles

    @property
    def safe_next_clr_calc_date(self):
        if self.next_clr_calc_date and self.next_clr_calc_date < timezone.now():
            return timezone.now() + timezone.timedelta(minutes=5)
        return self.next_clr_calc_date

    @property
    def recurring_funding_supported(self):
        return self.contract_version < 2

    @property
    def related_grants(self):
        pkg = self.metadata.get('related', [])
        pks = [ele[0] for ele in pkg]
        rg = Grant.objects.filter(pk__in=pks)
        return_me = []
        for ele in pkg:
            grant = rg.get(pk=ele[0])
            return_me.append([grant, ele[1]])
        return return_me


    @property
    def configured_to_receieve_funding(self):
        if self.contract_version == 2:
            return True
        return self.contract_address != '0x0'

    @property
    def clr_match_estimate_this_round(self):
        try:
            return self.clr_prediction_curve[0][1]
        except:
            return 0

    @property
    def contributions(self):
        pks = []
        for subscription in self.subscriptions.all():
            pks += list(subscription.subscription_contribution.values_list('pk', flat=True))
        return Contribution.objects.filter(pk__in=pks)


    @property
    def negative_voting_enabled(self):
        return False

    def is_on_team(self, profile):
        if profile.pk == self.admin_profile.pk:
            return True
        if profile.grant_teams.filter(pk=self.pk).exists():
            return True
        return False

    @property
    def org_name(self):
        from git.utils import org_name
        try:
            return org_name(self.reference_url)
        except Exception:
            return None

    @property
    def get_contribution_count(self):
        num = 0
        num += self.subscriptions.filter(is_postive_vote=True, subscription_contribution__success=True).count()
        num += self.phantom_funding.all().count()
        return num

    @property
    def contributors(self):
        return_me = []
        for sub in self.subscriptions.filter(is_postive_vote=True):
            for contrib in sub.subscription_contribution.filter(success=True):
                return_me.append(contrib.subscription.contributor_profile)
        for pf in self.phantom_funding.all():
            return_me.append(pf.profile)
        return return_me

    def get_contributor_count(self, since=None, is_postive_vote=True):
        if not since:
            since = timezone.datetime(1990, 1, 1)
        num = self.subscriptions.filter(is_postive_vote=is_postive_vote, subscription_contribution__success=True, created_on__gt=since).distinct('contributor_profile').count()
        if is_postive_vote:
            num += self.phantom_funding.filter(created_on__gt=since).exclude(profile__in=self.subscriptions.values_list('contributor_profile')).all().count()
        return num


    @property
    def org_profile(self):
        from dashboard.models import Profile
        profiles = Profile.objects.filter(handle=self.org_name.lower())
        if profiles.count():
            return profiles.first()
        return None

    @property
    def history_by_month(self):
        import math
        # gets the history of contributions to this grant month over month so they can be shown o grant details
        # returns [["", "Subscription Billing",  "New Subscriptions", "One-Time Contributions", "CLR Matching Funds"], ["December 2017", 5534, 2011, 0, 0], ["January 2018", 10396, 0 , 0, 0 ], ... for each monnth in which this grant has contribution history];
        CLR_PAYOUT_HANDLES = ['vs77bb', 'gitcoinbot', 'notscottmoore', 'owocki']
        month_to_contribution_numbers = {}
        subs = self.subscriptions.all().prefetch_related('subscription_contribution')
        for sub in subs:
            contribs = [sc for sc in sub.subscription_contribution.all() if sc.success]
            for contrib in contribs:
                #add all contributions
                year = contrib.created_on.strftime("%Y")
                quarter = math.ceil(int(contrib.created_on.strftime("%m"))/3.)
                key = f"{year}/Q{quarter}"
                subkey = 'One-Time'
                if contrib.subscription.contributor_profile.handle in CLR_PAYOUT_HANDLES:
                    subkey = 'CLR'
                if key not in month_to_contribution_numbers.keys():
                    month_to_contribution_numbers[key] = {"One-Time": 0, "Recurring-Recurring": 0, "New-Recurring": 0, 'CLR': 0}
                if contrib.subscription.amount_per_period_usdt:
                    month_to_contribution_numbers[key][subkey] += float(contrib.subscription.amount_per_period_usdt)

        # sort and return
        return_me = [["", "Contributions", "CLR Matching Funds"]]
        for key, val in (sorted(month_to_contribution_numbers.items(), key=lambda kv:(kv[0]))):
            return_me.append([key, val['One-Time'], val['CLR']])
        return return_me

    @property
    def history_by_month_max(self):
        max_amount = 0
        for ele in self.history_by_month:
            if type(ele[1]) is float:
                max_amount = max(max_amount, ele[1]+ele[2])
        return max_amount

    def get_amount_received_with_phantom_funds(self):
        return float(self.amount_received) + float(sum([ele.value for ele in self.phantom_funding.all()]))

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
        slug = self.slug if self.slug else "-"
        return reverse('grants:details', kwargs={'grant_id': self.pk, 'grant_slug': slug})

    def get_absolute_url(self):
        return self.url


    @property
    def is_idle(self):
        """Return if grants is idle."""
        three_months_ago = timezone.now() - timezone.timedelta(days=90)
        return (self.last_update and self.last_update <= three_months_ago)


    @property
    def contract(self):
        """Return grants contract."""
        from dashboard.utils import get_web3
        web3 = get_web3(self.network)
        grant_contract = web3.eth.contract(Web3.toChecksumAddress(self.contract_address), abi=self.abi)
        return grant_contract

    def cart_payload(self, build_absolute_uri, user=None):
        return {
            'grant_id': str(self.id),
            'grant_slug': self.slug,
            'grant_url': self.url,
            'grant_title': self.title,
            'grant_contract_version': self.contract_version,
            'grant_contract_address': self.contract_address,
            'grant_token_symbol': self.token_symbol,
            'grant_admin_address': self.admin_address,
            'grant_token_address': self.token_address,
            'grant_logo': self.logo.url if self.logo and self.logo.url else build_absolute_uri(static(f'v2/images/grants/logos/{self.id % 3}.png')),
            'grant_clr_prediction_curve': self.clr_prediction_curve,
            'grant_image_css': self.image_css,
            'is_clr_eligible': self.is_clr_eligible,
            'clr_round_num': self.clr_round_num,
            'tenants': self.tenants,
            'zcash_payout_address': self.zcash_payout_address,
            'celo_payout_address': self.celo_payout_address,
            'zil_payout_address': self.zil_payout_address,
            'polkadot_payout_address': self.polkadot_payout_address,
            'harmony_payout_address': self.harmony_payout_address,
            'binance_payout_address': self.binance_payout_address,
            'kusama_payout_address': self.kusama_payout_address,
            'harmony_payout_address': self.harmony_payout_address,
            'rsk_payout_address': self.rsk_payout_address,
            'algorand_payout_address': self.algorand_payout_address,
            'is_on_team': is_grant_team_member(self, user.profile) if user and user.is_authenticated else False,
        }

    def repr(self, user, build_absolute_uri):
        team_members = serializers.serialize('json', self.team_members.all(),
                            fields=['handle', 'url', 'profile__lazy_avatar_url']
                        )
        grant_type = None
        if self.grant_type:
            grant_type = serializers.serialize('json', [self.grant_type], fields=['name', 'label'])

        grant_tags = serializers.serialize('json', self.tags.all(),fields=['id', 'name', 'is_eligibility_tag'])

        active_round_names = list(self.in_active_clrs.values_list('display_text', flat=True))

        clr_matches = CLRMatch.objects.filter(grant=self)

        # has funds which have already been claimed
        has_claim_history = clr_matches.exclude(claim_tx__isnull=True).exclude(claim_tx='').exists()

        # has claims in pending / ready state
        has_funds_to_be_claimed = clr_matches.filter(claim_tx__isnull=True).exists()
        has_claims_in_review = has_funds_to_be_claimed and clr_matches.filter(grant_payout__status='pending').exists()
        has_pending_claim = has_funds_to_be_claimed and clr_matches.filter(grant_payout__status='ready').exists()

        return {
                'id': self.id,
                'active': self.active,
                'logo_url': self.logo.url if self.logo and self.logo.url else build_absolute_uri(static(f'v2/images/grants/logos/{self.id % 3}.png')),
                'details_url': reverse('grants:details', args=(self.id, self.slug)),
                'title': self.title,
                'description': self.description,
                'description_rich': self.description_rich,
                'last_update': self.last_update,
                'last_update_natural': naturaltime(self.last_update),
                'sybil_score': self.sybil_score,
                'weighted_risk_score': self.weighted_risk_score,
                'is_clr_active': self.is_clr_active,
                'clr_round_num': self.clr_round_num,
                'admin_profile': {
                    'url': self.admin_profile.url,
                    'handle': self.admin_profile.handle,
                    'avatar_url': self.admin_profile.lazy_avatar_url
                },
                'favorite': self.favorite(user) if user.is_authenticated else False,
                'is_on_team': is_grant_team_member(self, user.profile) if user.is_authenticated else False,
                'clr_prediction_curve': self.clr_prediction_curve,
                'last_clr_calc_date':  naturaltime(self.last_clr_calc_date) if self.last_clr_calc_date else None,
                'safe_next_clr_calc_date': naturaltime(self.safe_next_clr_calc_date) if self.safe_next_clr_calc_date else None,
                'amount_received_in_round': self.amount_received_in_round,
                'amount_received': self.amount_received,
                'positive_round_contributor_count': self.positive_round_contributor_count,
                'monthly_amount_subscribed': self.monthly_amount_subscribed,
                'is_clr_eligible': self.is_clr_eligible,
                'slug': self.slug,
                'url': self.url,
                'contract_version': self.contract_version,
                'contract_address': self.contract_address,
                'token_symbol': self.token_symbol,
                'admin_address': self.admin_address,
                'zcash_payout_address': self.zcash_payout_address or '',
                'celo_payout_address': self.celo_payout_address,
                'zil_payout_address': self.zil_payout_address,
                'polkadot_payout_address': self.polkadot_payout_address,
                'kusama_payout_address': self.kusama_payout_address,
                'harmony_payout_address': self.harmony_payout_address,
                'binance_payout_address': self.binance_payout_address,
                'rsk_payout_address': self.rsk_payout_address,
                'algorand_payout_address': self.algorand_payout_address,
                'token_address': self.token_address,
                'image_css': self.image_css,
                'verified': self.twitter_verified,
                'tenants': self.tenants,
                'team_members': json.loads(team_members),
                'metadata': self.metadata,
                'grant_type': json.loads(grant_type) if grant_type else None,
                'grant_tags': json.loads(grant_tags),
                'twitter_handle_1': self.twitter_handle_1,
                'twitter_handle_2': self.twitter_handle_2,
                'reference_url': self.reference_url,
                'github_project_url': self.github_project_url or '',
                'funding_info': self.funding_info,
                'admin_message': self.admin_message,
                'link_to_new_grant': self.link_to_new_grant.url if self.link_to_new_grant else self.link_to_new_grant,
                'region': {'name':self.region, 'label':self.get_region_display()} if self.region and self.region != 'null' else None,
                'has_external_funding': self.has_external_funding,
                'active_round_names': active_round_names,
                'is_idle': self.is_idle,
                'is_hidden': self.hidden,
                'has_pending_claim': has_pending_claim,
                'has_claims_in_review': has_claims_in_review,
                'has_claim_history': has_claim_history
            }

    def favorite(self, user):
        return Favorite.objects.filter(user=user, grant=self).exists()

    def save(self, update=True, *args, **kwargs):
        """Override the Grant save to optionally handle modified_on logic."""

        self.clr_prediction_curve = self.calc_clr_prediction_curve
        self.clr_round_num = self.calc_clr_round_label
        self.search_vector = (
            SearchVector('title', weight='A') + SearchVector('description', weight='B')
        )

        if self.modified_on < (timezone.now() - timezone.timedelta(minutes=15)):
            from grants.tasks import update_grant_metadata
            update_grant_metadata.delay(self.pk)

        from economy.models import get_time
        if update:
            self.modified_on = get_time()

        return super(Grant, self).save(*args, **kwargs)
