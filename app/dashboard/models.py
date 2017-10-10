'''
    Copyright (C) 2017 Gitcoin Core 

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

'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models

# Create your models here.
from economy.models import SuperModel
from economy.utils import convert_amount
from django.contrib.postgres.fields import JSONField
from dashboard.tokens import addr_to_token
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Bounty(SuperModel):
    BOUNTY_TYPES = [
        ('Bug', 'Bug'),
        ('Security', 'Security'),
        ('Feature', 'Feature'),
        ('Unknown', 'Unknown'),
    ]
    EXPERIENCE_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Unknown', 'Unknown'),
    ]
    PROJECT_LENGTHS = [
        ('Hours', 'Hours'),
        ('Days', 'Days'),
        ('Weeks', 'Weeks'),
        ('Months', 'Months'),
        ('Unknown', 'Unknown'),
    ]
    title = models.CharField(max_length=255)
    web3_created = models.DateTimeField()
    value_in_token = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    bounty_type = models.CharField(max_length=50, choices=BOUNTY_TYPES)
    project_length = models.CharField(max_length=50, choices=PROJECT_LENGTHS)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS)
    github_url = models.URLField()
    bounty_owner_address = models.CharField(max_length=50)
    bounty_owner_email = models.CharField(max_length=255, null=True)
    bounty_owner_github_username = models.CharField(max_length=255, null=True)
    claimeee_address = models.CharField(max_length=50)
    claimee_email = models.CharField(max_length=255, null=True)
    claimee_github_username = models.CharField(max_length=255, null=True)
    is_open = models.BooleanField()
    expires_date = models.DateTimeField()
    raw_data = JSONField()
    metadata = JSONField(default={})
    claimee_metadata = JSONField(default={})
    current_bounty = models.BooleanField(default=False) # whether this bounty is the most current revision one or not
    _val_usd_db = models.DecimalField(default=0, decimal_places=2, max_digits=20)
    contract_address = models.CharField(max_length=50,default='')
    network = models.CharField(max_length=255, null=True)
    idx_experience_level = models.IntegerField(default=0, db_index=True)
    idx_project_length = models.IntegerField(default=0, db_index=True)
    idx_status = models.CharField(max_length=50, default='')
    avatar_url = models.CharField(max_length=255, default='')
    issue_description = models.TextField(default='')

    def __str__(self):
        return "{}{} {} {} {}".format( "(CURRENT) " if self.current_bounty else "" , self.title, self.value_in_token, self.token_name, self.web3_created)

    def get_absolute_url(self):
        return "{}funding/details?url={}".format(settings.BASE_URL, self.github_url)

    def get_natural_value(self):
        token = addr_to_token(self.token_address)
        decimals = token['decimals']
        return float(self.value_in_token) / 10**decimals

    @property
    def title_or_desc(self):
        return self.title if self.title else self.github_url

    @property
    def org_name(self):
        try:
            from app.github import org_name
            _org_name = org_name(self.github_url)
            return _org_name
        except Exception as e:
            return None

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def get_avatar_url(self):
        try:
            from app.github import get_user
            response = get_user(self.org_name)
            return response['avatar_url']
        except Exception as e:
            print(e)
            return 'https://avatars0.githubusercontent.com/u/31359507?v=4'

    @property
    def local_avatar_url(self):
        return "https://gitcoin.co/funding/avatar?repo={}".format(self.github_url)

    @property
    def keywords(self):
        try:
            return self.metadata.get('issueKeywords', False)
        except:
            return False

    @property
    def now(self):
        return timezone.now()

    @property
    def status(self):
        try:
            if not self.is_open:
                return 'fulfilled'
            if timezone.now() > self.expires_date:
                return 'expired'
            if self.claimeee_address == '0x0000000000000000000000000000000000000000':
                return 'submitted'
            if self.claimeee_address != '0x0000000000000000000000000000000000000000':
                return 'claimed'
            return 'unknown'
        except Exception as e:
            return 'unknown'

    @property
    def value_true(self):
        return self.get_natural_value()

    @property
    def value_in_eth(self):
        if self.token_name == 'ETH':
            return self.value_in_token
        try:
            return convert_amount(self.value_in_token, self.token_name, 'ETH')
        except:
            return None

    @property
    def value_in_usdt(self):
        if self.token_name == 'USDT':
            return self.value_in_token
        try:
            return round(float(convert_amount(self.value_in_eth, 'ETH', 'USDT')) / 10**18, 2)
        except:
            return None

    def fetch_issue_description(self):
        import requests
        from bs4 import BeautifulSoup

        url = self.github_url
        if url.lower()[:19] != 'https://github.com/':
            return

        try:
            html_response = requests.get(url)
        except Exception as e:
            print(e)
            return

        body = None
        try:
            soup = BeautifulSoup(html_response.text, 'html.parser')

            eles = soup.findAll("td", {"class": "comment-body"})
            if len(eles):
                body = eles[0].prettify()


        except Exception as e:
            print(e)
            return

        self.issue_description = body


class BountySyncRequest(SuperModel):
    github_url = models.URLField()
    processed = models.BooleanField()


class Subscription(SuperModel):
    email = models.EmailField(max_length=255)
    raw_data = models.TextField()
    ip = models.CharField(max_length=50)

    def __str__(self):
        return "{} {}".format(self.email, (self.created_on))


class Tip(SuperModel):
    emails = JSONField()
    url = models.CharField(max_length=255, default='')
    tokenName = models.CharField(max_length=255)
    tokenAddress = models.CharField(max_length=255)
    amount = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    comments = models.TextField(default='')
    ip = models.CharField(max_length=50)
    expires_date = models.DateTimeField()
    github_url = models.URLField(null=True)
    from_name = models.CharField(max_length=255, default='')
    username = models.CharField(max_length=255, default='')
    network = models.CharField(max_length=255, default='')
    txid = models.CharField(max_length=255, default='')
    receive_txid = models.CharField(max_length=255, default='')
    received_on = models.DateTimeField(null=True)

    def __str__(self):
        from django.contrib.humanize.templatetags.humanize import naturalday
        return "{} -- {} {}.  created: {}, expires: {}".format(self.network, self.amount, self.tokenName, naturalday(self.created_on), naturalday(self.expires_date))


# method for updating
@receiver(pre_save, sender=Bounty, dispatch_uid="psave_bounty")
def psave_bounty(sender, instance, **kwargs):

    idx_experience_level = {
        'Unknown': 1,
        'Beginner': 2,
        'Intermediate': 3,
        'Advanced': 4,
    }

    idx_project_length = {
        'Unknown': 1,
        'Hours': 2,
        'Days': 3,
        'Weeks': 4,
        'Months': 5,
    }

    instance.idx_status = instance.status
    instance._val_usd_db = instance.value_in_usdt if instance.value_in_usdt else 0
    instance.idx_experience_level = idx_experience_level.get(instance.experience_level, 0)
    instance.idx_project_length = idx_project_length.get(instance.project_length, 0)
