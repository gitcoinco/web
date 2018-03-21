from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.forms import ModelForm
from django.template.defaultfilters import slugify
import random
from economy.utils import convert_amount

from economy.models import SuperModel
from github.utils import org_name, repo_name


class ExternalBounty(SuperModel):
    action_url = models.URLField(db_index=True, help_text="Where to send interested parties")
    active = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True, help_text="Plainext only please!")
    source_project = models.CharField(max_length=255, help_text="The upstream project being linked it..")
    amount = models.IntegerField(default=1)
    amount_denomination = models.CharField(max_length=255, help_text="ex: ETH, LTC, BTC")
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_sync_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True, default=[], help_text="comma delimited")
    github_handle = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return "{} {} {}".format(self.title, self.active, self.created_on)

    @property
    def url(self):
        return f'/offchain/{self.pk}/{slugify(self.title)}'

    @property
    def github_url(self):
        if not "https://github.com" in self.action_url:
            raise Exception("not a github url")
        _repo_name = repo_name(self.action_url)
        _org_name = org_name(self.action_url)
        return f"https://github.com/{_org_name}/{_repo_name}"

    @property
    def github_avatar_url(self):
        return f"{settings.BASE_URL}funding/avatar?repo={self.github_url}&v=3"

    @property
    def avatar(self):
        try:
            return self.github_avatar_url
        except:
            icons = ['paperplane.png', 'mixer2.png', 'lock.png', 'link.png', 'laptop.png', 'life_buoy.png', 'keyword.png', 'lightbulk.png', 'pencil_ruler.png', 'pin1.png', 'pin2.png']
            i = self.pk % len(icons)
            icon = icons[i]
            return f'/static/v2/images/icons/{icon}'

    @property
    def fiat_price(self):
        fiat_price = None
        try:
            fiat_price = round(convert_amount(self.amount, self.amount_denomination, 'USDT') ,2)
        except:
            pass
        return fiat_price


class ExternalBountyForm(ModelForm):
    class Meta:
        model = ExternalBounty
        fields = ['title', 'description', 'amount', 'amount_denomination', 'source_project', 'tags', 'action_url']
