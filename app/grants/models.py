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
        return f" ID: {self.pk}, Status: {self.status}, Title: {self.title}, Description: {self.description}, Reference_url: {self.reference_url}, Image_url: {self.image_url}, AdminAddress: {self.adminAddress}, Frequency: {self.frequency}, AmountGoal: {self.amountGoal}, AmountReceived: {self.amountReceived}, TokenAdress: {self.tokenAddress}, AdminProfile: {self.adminProfile}, TeamMemberProfiles: {self.teamMemberProfiles} @ {naturaltime(self.created_on)}"

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


    # grantPk = models.ForeignKey('Grant', related_name='grantPk', on_delete=models.CASCADE, null=True)
    # contributorProfile = models.ForeignKey('dashboard.Profile', related_name='grant_contributor', on_delete=models.CASCADE, null=True)

    def __str__(self):
        """Return the string representation of a Grant."""
        return f" ID: {self.pk}, GrantPk: {self.grantPk}, Status: {self.status}, SubscriptionHash: {self.subscriptionHash}, ContributorSignature: {self.contributorSignature}, ContributorAddress: {self.contributorAddress}, ContributorProfile: {self.contributorProfile}, AmountPerPeriod: {self.amountPerPeriod}, TokenAddress: {self.tokenAddress}, GasPrice: {self.gasPrice}, Network: {self.network}, @ {naturaltime(self.created_on)}"

class Contribution(SuperModel):
    """Define the structure of a subscription agreement"""

    txId = models.CharField(max_length=255, default='0x0')

    subscriptionPk = models.ForeignKey('Grant', related_name='grantPk', on_delete=models.CASCADE, null=True)
