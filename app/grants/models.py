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
        return f"{self.pk}: {self.title}, {self.description}, " \
               f"{self.adminAddress} @ {naturaltime(self.created_on)}"


class Stakeholder(models.Model):
    """Define relationship for profiles expressing interest on a bounty."""

    eth_address = models.CharField(max_length=50)
    name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=255, blank=True)
    url = models.URLField(db_index=True)

    def __str__(self):
        return self.name
