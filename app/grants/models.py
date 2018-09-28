from django.db import models
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from economy.models import SuperModel


class Grant(SuperModel):
    """Define the structure of a Grant."""

    status = models.BooleanField(default=True)
    title = models.CharField(default='', max_length=255)
    description = models.TextField(default='', blank=True)
    reference_url = models.URLField(db_index=True)
    image_url = models.URLField(default='')
    admin_address = models.CharField(max_length=255, default='0x0')
    frequency = models.DecimalField(default=30, decimal_places=0, max_digits=50)
    amount_goal = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    amount_received = models.DecimalField(default=0, decimal_places=4, max_digits=50)
    token_address = models.CharField(max_length=255, default='0x0')
    contract_address = models.CharField(max_length=255, default='0x0')
    network = models.CharField(max_length=255, default='0x0')
    required_gas_price = models.DecimalField(default='0', decimal_places=0, max_digits=50)

    admin_profile = models.ForeignKey('dashboard.Profile', related_name='grant_admin', on_delete=models.CASCADE, null=True)
    team_member_profiles = models.ManyToManyField('dashboard.Profile', related_name='grant_team_members')

    def percentage_done(self):
        # import ipdb; ipdb.set_trace()
        return ((self.amount_received / self.amount_goal) * 100)


    def __str__(self):
        """Return the string representation of a Grant."""
        return f" id: {self.pk}, status: {self.status}, title: {self.title}, description: {self.description}, reference_url: {self.reference_url}, image_url: {self.image_url}, admin_address: {self.admin_address}, frequency: {self.frequency}, amount_goal: {self.amount_goal}, amount_received: {self.amount_received}, token_adress: {self.token_address}, admin_profile: {self.admin_profile}, team_member_profiles: {self.team_member_profiles} @ {naturaltime(self.created_on)}"

class Subscription(SuperModel):
    """Define the structure of a subscription agreement"""

    status = models.BooleanField(default=True)
    subscription_hash = models.CharField(default='', max_length=255)
    contributor_signature = models.CharField(default='', max_length=255)
    contributor_address = models.CharField(default='', max_length=255)
    amount_per_period = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    token_address = models.CharField(max_length=255, default='0x0')
    gas_price = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    network = models.CharField(max_length=255, default='0x0')


    grant = models.ForeignKey('Grant', related_name='subscriptions', on_delete=models.CASCADE, null=True)
    contributor_profile = models.ForeignKey('dashboard.Profile', related_name='grant_contributor', on_delete=models.CASCADE, null=True)

    def __str__(self):
        """Return the string representation of a Subscription."""
        return f" id: {self.pk}, status: {self.status}, subscription_hash: {self.subscription_hash}, contributor_signature: {self.contributor_signature}, contributor_address: {self.contributor_address}, contributor_profile: {self.contributor_profile}, amount_per_period: {self.amount_per_period}, token_address: {self.token_address}, gas_price: {self.gas_price}, network: {self.network}, @ {naturaltime(self.created_on)}, grant: {self.grant_pk}"

class Contribution(SuperModel):
    """Define the structure of a subscription agreement"""

    tx_id = models.CharField(max_length=255, default='0x0')

    subscription_pk = models.ForeignKey('Subscription', related_name='subscription_contribution', on_delete=models.CASCADE, null=True)
