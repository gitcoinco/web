from django.db import models


from django.contrib.postgres.fields import JSONField

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel

from .grant_clr_calculation import GrantCLRCalculation
from .grant_collection import GrantCollection

from grants.utils import get_upload_filename


class GrantCLR(SuperModel):

    class Meta:
        unique_together = ('customer_name', 'round_num', 'sub_round_slug',)

    customer_name = models.CharField(
        max_length=15,
        default='',
        blank=True,
        help_text="used to genrate customer_name/round_num/sub_round_slug"
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
    is_active = models.BooleanField(default=False, db_index=True, help_text="Is CLR Round currently active")
    start_date = models.DateTimeField(help_text="CLR Round Start Date")
    end_date = models.DateTimeField(help_text="CLR Round End Date")
    grant_filters = JSONField(
        default=dict,
        null=True, blank=True,
        help_text="Grants allowed in this CLR round"
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

    def __str__(self):
        return f"{self.round_num}"

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
        for obj in self.clr_calculations.filter(grant=grant):
            obj.latest = False
            obj.save()

        GrantCLRCalculation.objects.create(
            grantclr=self,
            grant=grant,
            clr_prediction_curve=clr_prediction_curve,
            latest=True,
        )

