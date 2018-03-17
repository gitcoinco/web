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

import logging
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturalday, naturaltime
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

import requests
from dashboard.tokens import addr_to_token
from economy.models import SuperModel
from economy.utils import convert_amount, convert_token_to_usdt
from github.utils import (
    _AUTH, HEADERS, TOKEN_URL, build_auth_dict, get_issue_comments, get_user, issue_number, org_name, repo_name,
)
from rest_framework import serializers
from web3 import Web3

from .signals import m2m_changed_interested

logger = logging.getLogger(__name__)


class BountyQuerySet(models.QuerySet):
    """Handle the manager queryset for Bounties."""

    def current(self):
        """Filter results down to current bounties only."""
        return self.filter(current_bounty=True)


class Bounty(SuperModel):
    """Define the structure of a Bounty.

    Attributes:
        BOUNTY_TYPES (list of tuples): The valid bounty types.
        EXPERIENCE_LEVELS (list of tuples): The valid experience levels.
        PROJECT_LENGTHS (list of tuples): The possible project lengths.

    """

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
    web3_type = models.CharField(max_length=50, default='bounties_network')
    title = models.CharField(max_length=255)
    web3_created = models.DateTimeField(db_index=True)
    value_in_token = models.DecimalField(default=1, decimal_places=2, max_digits=50)
    token_name = models.CharField(max_length=50)
    token_address = models.CharField(max_length=50)
    bounty_type = models.CharField(max_length=50, choices=BOUNTY_TYPES)
    project_length = models.CharField(max_length=50, choices=PROJECT_LENGTHS)
    experience_level = models.CharField(max_length=50, choices=EXPERIENCE_LEVELS)
    github_url = models.URLField(db_index=True)
    github_comments = models.IntegerField(default=0)
    bounty_owner_address = models.CharField(max_length=50)
    bounty_owner_email = models.CharField(max_length=255, blank=True)
    bounty_owner_github_username = models.CharField(max_length=255, blank=True)
    bounty_owner_name = models.CharField(max_length=255, blank=True)
    is_open = models.BooleanField(help_text='Whether the bounty is still open for fulfillments.')
    expires_date = models.DateTimeField()
    raw_data = JSONField()
    metadata = JSONField(default={})
    current_bounty = models.BooleanField(
        default=False, help_text='Whether this bounty is the most current revision one or not')
    _val_usd_db = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    contract_address = models.CharField(max_length=50, default='')
    network = models.CharField(max_length=255, blank=True, db_index=True)
    idx_experience_level = models.IntegerField(default=0, db_index=True)
    idx_project_length = models.IntegerField(default=0, db_index=True)
    idx_status = models.CharField(max_length=50, default='', db_index=True)
    avatar_url = models.CharField(max_length=255, default='')
    issue_description = models.TextField(default='', blank=True)
    standard_bounties_id = models.IntegerField(default=0)
    num_fulfillments = models.IntegerField(default=0)
    balance = models.DecimalField(default=0, decimal_places=2, max_digits=50)
    accepted = models.BooleanField(default=False, help_text='Whether the bounty has been done')
    interested = models.ManyToManyField('dashboard.Interest', blank=True)
    interested_comment = models.IntegerField(null=True, blank=True)
    submissions_comment = models.IntegerField(null=True, blank=True)
    override_status = models.CharField(max_length=255, blank=True)

    objects = BountyQuerySet.as_manager()

    class Meta:
        """Define metadata associated with Bounty."""

        verbose_name_plural = 'Bounties'
        index_together = [
            ["network", "idx_status"],
        ]

    def __str__(self):
        """Return the string representation of a Bounty."""
        return f"{'(CURRENT) ' if self.current_bounty else ''}{self.title} {self.value_in_token} " \
               f"{self.token_name} {self.web3_created}"

    def save(self, *args, **kwargs):
        """Define custom handling for saving bounties."""
        if self.bounty_owner_github_username:
            self.bounty_owner_github_username = self.bounty_owner_github_username.lstrip('@')
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get the absolute URL for the Bounty.

        Returns:
            str: The absolute URL for the Bounty.

        """
        return settings.BASE_URL + self.get_relative_url(preceding_slash=False)

    def get_relative_url(self, preceding_slash=True):
        """Get the relative URL for the Bounty.

        Attributes:
            preceding_slash (bool): Whether or not to include a preceding slash.

        Returns:
            str: The relative URL for the Bounty.

        """
        try:
            _org_name = org_name(self.github_url)
            _issue_num = issue_number(self.github_url)
            _repo_name = repo_name(self.github_url)
            return f"{'/' if preceding_slash else ''}issue/{_org_name}/{_repo_name}/{_issue_num}"
        except Exception:
            return f"{'/' if preceding_slash else ''}funding/details?url={self.github_url}"

    def get_natural_value(self):
        token = addr_to_token(self.token_address)
        if not token:
            return 0
        decimals = token.get('decimals', 0)
        return float(self.value_in_token) / 10**decimals

    @property
    def url(self):
        return self.get_relative_url()

    @property
    def can_submit_after_expiration_date(self):
        return self.is_legacy or self.raw_data.get('payload', {}).get('expire_date', False)

    @property
    def title_or_desc(self):
        """Return the title of the issue."""
        if not self.title:
            title = self.fetch_issue_item('title') or self.github_url
            return title
        return self.title

    @property
    def issue_description_text(self):
        import re
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        return tag_re.sub('', self.issue_description).strip()

    @property
    def org_name(self):
        try:
            _org_name = org_name(self.github_url)
            return _org_name
        except Exception:
            return None

    def is_hunter(self, handle):
        """Determine whether or not the profile is the bounty hunter.

        Args:
            handle (str): The profile handle to be compared.

        Returns:
            bool: Whether or not the user is the bounty hunter.

        """
        return any(profile.fulfiller_github_username == handle for profile in self.fulfillments.all())

    def is_funder(self, handle):
        """Determine whether or not the profile is the bounty funder.

        Args:
            handle (str): The profile handle to be compared.

        Returns:
            bool: Whether or not the user is the bounty funder.

        """
        return handle.lower().lstrip('@') == self.bounty_owner_github_username.lower().lstrip('@')

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def get_avatar_url(self):
        try:
            response = get_user(self.org_name)
            return response['avatar_url']
        except Exception as e:
            print(e)
            return 'https://avatars0.githubusercontent.com/u/31359507?v=4'

    @property
    def local_avatar_url(self):
        """Return the local avatar URL."""
        return f"{settings.BASE_URL}funding/avatar?repo={self.github_url}&v=3"

    @property
    def keywords(self):
        try:
            return self.metadata.get('issueKeywords', False)
        except Exception:
            return False

    @property
    def now(self):
        """Return the time now in the current timezone."""
        return timezone.now()

    @property
    def status(self):
        """Determine the status of the Bounty.

        Raises:
            Exception: Catch whether or not any exception is encountered and
                return unknown for status.

        Returns:
            str: The status of the Bounty.

        """
        if self.override_status:
            return self.override_status
        if self.is_legacy:
            # TODO: Remove following full deprecation of legacy bounties
            try:
                fulfillments = self.fulfillments \
                    .exclude(fulfiller_address='0x0000000000000000000000000000000000000000') \
                    .exists()
                if not self.is_open:
                    if timezone.now() > self.expires_date and fulfillments:
                        return 'expired'
                    return 'done'
                elif not fulfillments:
                    if self.pk and self.interested.exists():
                        return 'started'
                    return 'open'
                return 'submitted'
            except Exception as e:
                logger.warning(e)
                return 'unknown'
        else:
            try:
                if not self.is_open:
                    if timezone.localtime().replace(tzinfo=None) > self.expires_date.replace(tzinfo=None) and self.num_fulfillments == 0:
                        return 'expired'
                    if self.accepted:
                        return 'done'
                    # If its not expired or done, it must be cancelled.
                    return 'cancelled'
                if self.num_fulfillments == 0:
                    if self.pk and self.interested.exists():
                        return 'started'
                    return 'open'
                return 'submitted'
            except Exception as e:
                logger.warning(e)
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
        except Exception:
            return None

    @property
    def value_in_usdt(self):
        decimals = 10**18
        if self.token_name == 'USDT':
            return self.value_in_token
        try:
            return round(float(convert_amount(self.value_in_eth, 'ETH', 'USDT')) / decimals, 2)
        except Exception:
            return None

    @property
    def token_value_in_usdt(self):
        return round(convert_token_to_usdt(self.token_name), 2)

    @property
    def desc(self):
        return "{} {} {} {}".format(naturaltime(self.web3_created), self.idx_project_length, self.bounty_type,
                                    self.experience_level)

    @property
    def turnaround_time(self):
        return (self.created_on - self.web3_created).total_seconds()

    @property
    def is_legacy(self):
        """Determine if the Bounty is legacy based on sunset date.

        Todo:
            * Remove this method following legacy bounty sunsetting.

        Returns:
            bool: Whether or not the Bounty is using the legacy contract.

        """
        return (self.web3_type == 'legacy_gitcoin')

    def get_github_api_url(self):
        """Get the Github API URL associated with the bounty.

        Returns:
            str: The Github API URL associated with the issue.

        """
        from urllib.parse import urlparse
        if self.github_url.lower()[:19] != 'https://github.com/':
            return ''
        url_path = urlparse(self.github_url).path
        return 'https://api.github.com/repos' + url_path

    def fetch_issue_item(self, item_type='body'):
        """Fetch the item type of an issue.

        Args:
            type (str): The github API response body item to be fetched.

        Returns:
            str: The item content.

        """
        issue_description = requests.get(self.get_github_api_url(), auth=_AUTH)
        if issue_description.status_code == 200:
            item = issue_description.json().get(item_type, '')
            if item_type == 'body' and item:
                self.issue_description = item
            elif item_type == 'title' and item:
                self.title = item
            self.save()
            return item
        return ''

    def fetch_issue_comments(self, save=True):
        """Fetch issue comments for the associated Github issue.

        Args:
            save (bool): Whether or not to save the Bounty after fetching.

        Returns:
            dict: The comments data dictionary provided by Github.

        """
        if self.github_url.lower()[:19] != 'https://github.com/':
            return []

        parsed_url = urlsplit(self.github_url)
        try:
            github_user, github_repo, _, github_issue = parsed_url.path.split('/')[1:5]
        except ValueError:
            logger.info('Invalid github url for Bounty: %s -- %s', self.pk, self.github_url)
            return []
        comments = get_issue_comments(github_user, github_repo, github_issue)
        if isinstance(comments, dict) and comments.get('message') == 'Not Found':
            logger.info('Bounty %s contains an invalid github url %s', self.pk, self.github_url)
            return []
        comment_count = 0
        for comment in comments:
            if comment['user']['login'] not in settings.IGNORE_COMMENTS_FROM:
                comment_count += 1
        self.github_comments = comment_count
        if save:
            self.save()
        return comments


class BountyFulfillmentQuerySet(models.QuerySet):
    """Handle the manager queryset for BountyFulfillments."""

    def accepted(self):
        """Filter results to accepted bounty fulfillments."""
        return self.filter(accepted=True)

    def submitted(self):
        """Exclude results that have not been submitted."""
        return self.exclude(fulfiller_address='0x0000000000000000000000000000000000000000')


class BountyFulfillment(SuperModel):
    """The structure of a fulfillment on a Bounty."""

    fulfiller_address = models.CharField(max_length=50)
    fulfiller_email = models.CharField(max_length=255, blank=True)
    fulfiller_github_username = models.CharField(max_length=255, blank=True)
    fulfiller_name = models.CharField(max_length=255, blank=True)
    fulfiller_metadata = JSONField(default={}, blank=True)
    fulfillment_id = models.IntegerField(null=True, blank=True)
    accepted = models.BooleanField(default=False)

    bounty = models.ForeignKey(Bounty, related_name='fulfillments', on_delete=models.CASCADE)
    profile = models.ForeignKey('dashboard.Profile', related_name='fulfilled', on_delete=models.CASCADE, null=True)

    def __str__(self):
        """Define the string representation of BountyFulfillment.

        Returns:
            str: The string representation of the object.

        """
        return f'BountyFulfillment ID: ({self.pk}) - Bounty ID: ({self.bounty.pk})'

    def save(self, *args, **kwargs):
        """Define custom handling for saving bounty fulfillments."""
        if self.fulfiller_github_username:
            self.fulfiller_github_username = self.fulfiller_github_username.lstrip('@')
        super().save(*args, **kwargs)

    @property
    def to_json(self):
        """Define the JSON representation of BountyFulfillment.

        Returns:
            dict: A JSON representation of BountyFulfillment.

        """
        return {
            'address': self.fulfiller_address,
            'bounty_id': self.bounty.pk,
            'email': self.fulfiller_email,
            'githubUsername': self.fulfiller_github_username,
            'name': self.fulfiller_name,
        }


class BountySyncRequest(SuperModel):
    """Define the structure for bounty syncing."""

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
    amount = models.DecimalField(default=1, decimal_places=4, max_digits=50)
    comments_priv = models.TextField(default='', blank=True)
    comments_public = models.TextField(default='', blank=True)
    ip = models.CharField(max_length=50)
    expires_date = models.DateTimeField()
    github_url = models.URLField(null=True, blank=True)
    from_name = models.CharField(max_length=255, default='', blank=True)
    from_email = models.CharField(max_length=255, default='', blank=True)
    from_username = models.CharField(max_length=255, default='', blank=True)
    username = models.CharField(max_length=255, default='')  # to username
    network = models.CharField(max_length=255, default='')
    txid = models.CharField(max_length=255, default='')
    receive_txid = models.CharField(max_length=255, default='', blank=True)
    received_on = models.DateTimeField(null=True, blank=True)
    from_address = models.CharField(max_length=255, default='', blank=True)
    receive_address = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        """Return the string representation for a tip."""
        return f"({self.network}) - {self.status}{' ORPHAN' if not self.emails else ''} {self.amount} " \
               f"{self.tokenName} to {self.username}, created: {naturalday(self.created_on)}, " \
               f"expires: {naturalday(self.expires_date)}"

    # TODO: DRY
    def get_natural_value(self):
        token = addr_to_token(self.tokenAddress)
        decimals = token['decimals']
        return float(self.amount) / 10**decimals

    @property
    def value_true(self):
        return self.get_natural_value()

    # TODO: DRY
    @property
    def value_in_eth(self):
        if self.tokenName == 'ETH':
            return self.amount
        try:
            return convert_amount(self.amount, self.tokenName, 'ETH')
        except Exception:
            return None

    # TODO: DRY
    @property
    def value_in_usdt(self):
        decimals = 1
        if self.tokenName == 'USDT':
            return self.amount
        try:
            return round(float(convert_amount(self.value_in_eth, 'ETH', 'USDT')) / decimals, 2)
        except Exception:
            return None

    # TODO: DRY
    @property
    def token_value_in_usdt(self):
        return round(convert_token_to_usdt(self.token_name), 2)

    @property
    def status(self):
        if self.receive_txid:
            return "RECEIVED"
        return "PENDING"


# @receiver(pre_save, sender=Bounty, dispatch_uid="normalize_usernames")
# def normalize_usernames(sender, instance, **kwargs):
#     if instance.bounty_owner_github_username:
#         instance.bounty_owner_github_username = instance.bounty_owner_github_username.lstrip('@')


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


class Interest(models.Model):
    """Define relationship for profiles expressing interest on a bounty."""

    profile = models.ForeignKey('dashboard.Profile', related_name='interested', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        """Define the string representation of an interested profile."""
        return self.profile.handle


@receiver(post_save, sender=Interest, dispatch_uid="psave_interest")
@receiver(post_delete, sender=Interest, dispatch_uid="pdel_interest")
def psave_interest(sender, instance, **kwargs):
    # when a new interest is saved, update the status on frontend
    print("signal: updating bounties psave_interest")
    for bounty in Bounty.objects.filter(interested=instance):
        bounty.save()


class Profile(SuperModel):
    """Define the structure of the user profile."""

    data = JSONField()
    handle = models.CharField(max_length=255, db_index=True)
    last_sync_date = models.DateTimeField(null=True)
    email = models.CharField(max_length=255, blank=True, db_index=True)
    github_access_token = models.CharField(max_length=255, blank=True, db_index=True)

    _sample_data = '''
        {
          "public_repos": 9,
          "site_admin": false,
          "updated_at": "2017-10-09T22:55:57Z",
          "gravatar_id": "",
          "hireable": null,
          "id": 30044474,
          "followers_url": "https:\/\/api.github.com\/users\/gitcoinco\/followers",
          "following_url": "https:\/\/api.github.com\/users\/gitcoinco\/following{\/other_user}",
          "blog": "https:\/\/gitcoin.co",
          "followers": 0,
          "location": "Boulder, CO",
          "type": "Organization",
          "email": "founders@gitcoin.co",
          "bio": "Grow Open Source",
          "gists_url": "https:\/\/api.github.com\/users\/gitcoinco\/gists{\/gist_id}",
          "company": null,
          "events_url": "https:\/\/api.github.com\/users\/gitcoinco\/events{\/privacy}",
          "html_url": "https:\/\/github.com\/gitcoinco",
          "subscriptions_url": "https:\/\/api.github.com\/users\/gitcoinco\/subscriptions",
          "received_events_url": "https:\/\/api.github.com\/users\/gitcoinco\/received_events",
          "starred_url": "https:\/\/api.github.com\/users\/gitcoinco\/starred{\/owner}{\/repo}",
          "public_gists": 0,
          "name": "Gitcoin Core",
          "organizations_url": "https:\/\/api.github.com\/users\/gitcoinco\/orgs",
          "url": "https:\/\/api.github.com\/users\/gitcoinco",
          "created_at": "2017-07-10T10:50:51Z",
          "avatar_url": "https:\/\/avatars1.githubusercontent.com\/u\/30044474?v=4",
          "repos_url": "https:\/\/api.github.com\/users\/gitcoinco\/repos",
          "following": 0,
          "login": "gitcoinco"
        }
    '''
    repos_data = JSONField(default={})

    _sample_data = '''
    [
      {
        "issues_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/issues{\/number}",
        "deployments_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/deployments",
        "has_wiki": true,
        "forks_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/forks",
        "mirror_url": null,
        "issue_events_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/issues\/events{\/number}",
        "stargazers_count": 1,
        "subscription_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/subscription",
        "merges_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/merges",
        "has_pages": false,
        "updated_at": "2017-09-25T11:39:03Z",
        "private": false,
        "pulls_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/pulls{\/number}",
        "issue_comment_url": "https:\/\/api.github.com\/repos\/gitcoinco\/chrome_ext\/issues\/comments{\/number}",
        "full_name": "gitcoinco\/chrome_ext",
        "owner": {
          "following_url": "https:\/\/api.github.com\/users\/gitcoinco\/following{\/other_user}",
          "events_url": "https:\/\/api.github.com\/users\/gitcoinco\/events{\/privacy}",
          "organizations_url": "https:\/\/api.github.com\/users\/gitcoinco\/orgs",
          "url": "https:\/\/api.github.com\/users\/gitcoinco",
          "gists_url": "https:\/\/api.github.com\/users\/gitcoinco\/gists{\/gist_id}",
          "html_url": "https:\/\/github.com\/gitcoinco",
          "subscriptions_url": "https:\/\/api.github.com\/users\/gitcoinco\/subscriptions",
          "avatar_url": "https:\/\/avatars1.githubusercontent.com\/u\/30044474?v=4",
          "repos_url": "https:\/\/api.github.com\/users\/gitcoinco\/repos",
          "received_events_url": "https:\/\/api.github.com\/users\/gitcoinco\/received_events",
          "gravatar_id": "",
          "starred_url": "https:\/\/api.github.com\/users\/gitcoinco\/starred{\/owner}{\/repo}",
          "site_admin": false,
          "login": "gitcoinco",
          "type": "Organization",
          "id": 30044474,
          "followers_url": "https:\/\/api.github.com\/users\/gitcoinco\/followers"
        },
        ...
    ]
    '''

    @property
    def is_org(self):
        return self.data['type'] == 'Organization'

    @property
    def bounties(self):
        fulfilled_bounty_ids = self.fulfilled.all().values_list('bounty_id')
        bounties = Bounty.objects.filter(github_url__istartswith=self.github_url, current_bounty=True)
        for interested in self.interested.all():
            bounties = bounties | Bounty.objects.filter(interested=interested, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(pk__in=fulfilled_bounty_ids, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(bounty_owner_github_username__iexact=self.handle, current_bounty=True) | Bounty.objects.filter(bounty_owner_github_username__iexact="@" + self.handle, current_bounty=True)
        bounties = bounties | Bounty.objects.filter(github_url__in=[url for url in self.tips.values_list('github_url', flat=True)], current_bounty=True)
        bounties = bounties.distinct()
        return bounties.order_by('-web3_created')

    @property
    def tips(self):
        on_repo = Tip.objects.filter(github_url__startswith=self.github_url).order_by('-id')
        tipped_for = Tip.objects.filter(username__iexact=self.handle).order_by('-id')
        return on_repo | tipped_for

    @property
    def authors(self):
        auto_include_contributors_with_count_gt = 40
        limit_to_num = 10

        _return = []

        for repo in sorted(self.repos_data, key=lambda repo: repo.get('contributions', -1), reverse=True):
            for c in repo.get('contributors', []):
                if isinstance(c, dict) and c.get('contributions', 0) > auto_include_contributors_with_count_gt:
                    _return.append(c['login'])

        include_gitcoin_users = len(_return) < limit_to_num
        if include_gitcoin_users:
            for b in self.bounties:
                vals = [b.bounty_owner_github_username]
                for val in vals:
                    if val:
                        _return.append(val.lstrip('@'))
            for t in self.tips:
                vals = [t.username]
                for val in vals:
                    if val:
                        _return.append(val.lstrip('@'))
        _return = list(set(_return))
        _return.sort()
        return _return[:limit_to_num]

    @property
    def desc(self):
        stats = self.stats
        role = stats[0][0]
        total_funded_participated = stats[1][0]
        plural = 's' if total_funded_participated != 1 else ''
        return "@{} is a {} who has participated in {} funded issue{} on Gitcoin".format(self.handle, role, total_funded_participated, plural)

    @property
    def stats(self):
        bounties = self.bounties
        loyalty_rate = 0
        total_funded = sum([bounty.value_in_usdt if bounty.value_in_usdt else 0 for bounty in bounties if bounty.is_funder(self.handle)])
        total_fulfilled = sum([bounty.value_in_usdt if bounty.value_in_usdt else 0 for bounty in bounties if bounty.is_hunter(self.handle)])
        print(total_funded, total_fulfilled)
        role = 'newbie'
        if total_funded > total_fulfilled:
            role = 'funder'
        elif total_funded < total_fulfilled:
            role = 'coder'

        loyalty_rate = self.fulfilled.filter(accepted=True).count()
        success_rate = 0
        if bounties.exists():
            numer = bounties.filter(idx_status__in=['submitted', 'started', 'done']).count()
            denom = bounties.exclude(idx_status__in=['open']).count()
            success_rate = int(round(numer * 1.0 / denom, 2) * 100) if denom != 0 else 'N/A'
        if success_rate == 0:
            success_rate = 'N/A'
            loyalty_rate = 'N/A'
        else:
            success_rate = "{}%".format(success_rate)
            loyalty_rate = "{}x".format(loyalty_rate)
        if role == 'newbie':
            return [
                (role, 'Status'),
                (bounties.count(), 'Total Funded Issues'),
                (bounties.filter(idx_status='open').count(), 'Open Funded Issues'),
                (loyalty_rate, 'Loyalty Rate'),
            ]
        elif role == 'coder':
            return [
                (role, 'Primary Role'),
                (bounties.count(), 'Total Funded Issues'),
                (success_rate, 'Success Rate'),
                (loyalty_rate, 'Loyalty Rate'),
            ]
        # funder
        return [
            (role, 'Primary Role'),
            (bounties.count(), 'Total Funded Issues'),
            (bounties.filter(idx_status='open').count(), 'Open Funded Issues'),
            (success_rate, 'Success Rate'),
        ]

    @property
    def github_url(self):
        return "https://github.com/{}".format(self.handle)

    @property
    def local_avatar_url(self):
        return f"{settings.BASE_URL}funding/avatar?repo={self.github_url}&v=3"

    @property
    def absolute_url(self):
        return self.get_absolute_url()

    def is_github_token_valid(self):
        """Check whether or not a Github OAuth token is valid.

        Args:
            access_token (str): The Github OAuth token.

        Returns:
            bool: Whether or not the provided OAuth token is valid.

        """
        if not self.github_access_token:
            return False

        _params = build_auth_dict(self.github_access_token)
        url = TOKEN_URL.format(**_params)
        response = requests.get(
            url,
            auth=(_params['client_id'], _params['client_secret']),
            headers=HEADERS)

        if response.status_code == 200:
            return True
        return False

    def __str__(self):
        return self.handle

    def get_relative_url(self, preceding_slash=True):
        return f"{'/' if preceding_slash else ''}profile/{self.handle}"

    def get_absolute_url(self):
        return settings.BASE_URL + self.get_relative_url(preceding_slash=False)


class ProfileSerializer(serializers.BaseSerializer):
    """Handle serializing the Profile object."""

    class Meta:
        """Define the profile serializer metadata."""

        model = Profile
        fields = ('handle', 'github_access_token')
        extra_kwargs = {'github_access_token': {'write_only': True}}

    def to_representation(self, instance):
        """Provide the serialized representation of the Profile.

        Args:
            instance (Profile): The Profile object to be serialized.

        Returns:
            dict: The serialized Profile.

        """
        return {
            'handle': instance.handle,
            'github_url': instance.github_url,
            'local_avatar_url': instance.local_avatar_url,
            'url': instance.get_relative_url()
        }


@receiver(pre_save, sender=Tip, dispatch_uid="normalize_tip_usernames")
def normalize_tip_usernames(sender, instance, **kwargs):
    """Handle pre-save signals from Tips to normalize Github usernames."""
    if instance.username:
        instance.username = instance.username.replace("@", '')


m2m_changed.connect(m2m_changed_interested, sender=Bounty.interested.through)
# m2m_changed.connect(changed_fulfillments, sender=Bounty.fulfillments)


class UserAction(SuperModel):
    """Records Actions that a user has taken ."""

    ACTION_TYPES = [
        ('Login', 'Login'),
        ('Logout', 'Logout'),
    ]
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    profile = models.ForeignKey('dashboard.Profile', related_name='actions', on_delete=models.CASCADE)
    metadata = JSONField(default={})

    def __str__(self):
        return "{} by {} at {}".format(self.action, self.profile, self.created_on)


class CoinRedemption(SuperModel):
    """Define the coin redemption schema."""

    class Meta:
        """Define metadata associated with CoinRedemption."""

        verbose_name_plural = 'Coin Redemptions'

    shortcode = models.CharField(max_length=255, default='')
    url = models.URLField(null=True)
    network = models.CharField(max_length=255, default='')
    token_name = models.CharField(max_length=255)
    contract_address = models.CharField(max_length=255)
    amount = models.IntegerField(default=1)
    expires_date = models.DateTimeField()


@receiver(pre_save, sender=CoinRedemption, dispatch_uid="to_checksum_address")
def to_checksum_address(sender, instance, **kwargs):
    """Handle pre-save signals from CoinRemptions to normalize the contract address."""
    if instance.contract_address:
        instance.contract_address = Web3.toChecksumAddress(instance.contract_address)
        print(instance.contract_address)


class CoinRedemptionRequest(SuperModel):
    """Define the coin redemption request schema."""

    class Meta:
        """Define metadata associated with CoinRedemptionRequest."""

        verbose_name_plural = 'Coin Redemption Requests'

    coin_redemption = models.OneToOneField(CoinRedemption, blank=False, on_delete=models.CASCADE)
    ip = models.GenericIPAddressField(protocol='IPv4')
    txid = models.CharField(max_length=255, default='')
    txaddress = models.CharField(max_length=255)
    sent_on = models.DateTimeField(null=True)
