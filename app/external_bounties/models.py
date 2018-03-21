from django.db import models
from economy.models import SuperModel
from django.contrib.postgres.fields import ArrayField
from django.template.defaultfilters import slugify
from django.forms import ModelForm
from django.conf import settings
from github.utils import org_name, repo_name


class ExternalBounty(SuperModel):
    action_url = models.URLField(db_index=True)
    active = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    description = models.TextField(default='', blank=True)
    source_project = models.CharField(max_length=255)
    amount = models.IntegerField(default=1)
    amount_denomination = models.CharField(max_length=255, help_text="ex: ETH, LTC, BTC")
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_sync_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=200), blank=True, default=[], help_text="comma delimited")

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
            return '/static/v2/images/mission/interact/1.png'


class ExternalBountyForm(ModelForm):
    class Meta:
        model = ExternalBounty
        fields = ['title', 'description', 'amount', 'amount_denomination', 'source_project', 'tags', 'action_url']