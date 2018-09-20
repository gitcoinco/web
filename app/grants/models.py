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
    adminAddress = models.CharField(max_length=255, default='0x0')
    frequency = models.DecimalField(default=30, decimal_places=0, max_digits=50)
    amountGoal = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    amountReceived = models.DecimalField(default=0, decimal_places=4, max_digits=50)
    tokenAddress = models.CharField(max_length=255, default='0x0')

    adminProfile = models.ForeignKey('dashboard.Profile', related_name='grant_admin', on_delete=models.CASCADE, null=True)
    teamMemberProfiles = models.ManyToManyField('dashboard.Profile', related_name='grant_team_members')

    def percentage_done(self):
        # import ipdb; ipdb.set_trace()
        return ((self.amountReceived / self.amountGoal) * 100)


    def __str__(self):
        """Return the string representation of a Grant."""
        return f" id: {self.pk}, status: {self.status}, title: {self.title}, description: {self.description}, reference_url: {self.reference_url}, image_url: {self.image_url}, adminAddress: {self.adminAddress}, frequency: {self.frequency}, amountGoal: {self.amountGoal}, amountReceived: {self.amountReceived}, tokenAdress: {self.tokenAddress}, adminProfile: {self.adminProfile}, teamMemberProfiles: {self.teamMemberProfiles} @ {naturaltime(self.created_on)}"

class Subscription(SuperModel):
    """Define the structure of a subscription agreement"""

    status = models.BooleanField(default=True)
    subscriptionHash = models.CharField(default='', max_length=255)
    contributorSignature = models.CharField(default='', max_length=255)
    contributorAddress = models.CharField(default='', max_length=255)
    amountPerPeriod = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    tokenAddress = models.CharField(max_length=255, default='0x0')
    gasPrice = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    network = models.CharField(max_length=255, default='0x0')


    grantPk = models.ForeignKey('Grant', related_name='grant_subscription', on_delete=models.CASCADE, null=True)
    contributorProfile = models.ForeignKey('dashboard.Profile', related_name='grant_contributor', on_delete=models.CASCADE, null=True)

    def __str__(self):
        """Return the string representation of a Grant."""
        return f" id: {self.pk}, status: {self.status}, subscriptionHash: {self.subscriptionHash}, contributorSignature: {self.contributorSignature}, contributorAddress: {self.contributorAddress}, contributorProfile: {self.contributorProfile}, amountPerPeriod: {self.amountPerPeriod}, tokenAddress: {self.tokenAddress}, gasPrice: {self.gasPrice}, network: {self.network}, @ {naturaltime(self.created_on), grant: {self.grantPk}}"

class Contribution(SuperModel):
    """Define the structure of a subscription agreement"""

    txId = models.CharField(max_length=255, default='0x0')

    subscriptionPk = models.ForeignKey('Subscription', related_name='subscription_contribution', on_delete=models.CASCADE, null=True)
