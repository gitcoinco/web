# -*- coding: utf-8 -*-
"""Define the Account models.

Copyright (C) 2018 Gitcoin Core

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

"""
from __future__ import unicode_literals

import logging

from django.contrib.auth.models import Group, User
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from avatar.models import Avatar
from dashboard.models import Profile
from django_extensions.db.fields import AutoSlugField
from git.utils import github_connect
from taggit.managers import TaggableManager

logger = logging.getLogger(__name__)


class OrganizationQuerySet(models.QuerySet):
    """Define the Organization queryset and manager behavior."""

    def active(self):
        """Filter results to Organization objects that are active.

        Returns:
            models.QuerySet: The active Organization filtered QS.

        """
        return self.select_related('bounty', 'profile').filter(needs_review=True)

    def is_hiring(self):
        """Filter results to Organization objects that are hiring.

        Returns:
            models.QuerySet: The hiring Organization filtered QS.

        """
        return self.select_related('bounty', 'profile').filter(is_visible=True)


    def is_visible(self):
        """Define the Organization queryset and manager behavior."""
        pass

    def active(self):
        """Filter results to Organization objects that are active.

        Returns:
            models.QuerySet: The active Organization filtered QS.

        """
        return self.select_related('bounty', 'profile').filter(is_visible=True)


class Organization(Group):
    """Define the structure of an Organization."""

    avatar = models.ForeignKey(
        'avatar.Avatar', blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_('Avatar')
    )
    created_on = models.DateTimeField(auto_now_add=True, verbose_name=_('Created'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    email = models.CharField(blank=True, max_length=200, verbose_name=_('Email'))
    followers = models.ManyToManyField(
        'dashboard.Profile', related_name='organizations_following', verbose_name=_('Followers')
    )
    gh_repos_data = JSONField(blank=True, default=dict, verbose_name=_('Repository Data'))
    gh_data = JSONField(blank=True, default=dict, verbose_name=_('Github Data'))
    gh_members = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list,
        help_text=_('comma delimited'),
        verbose_name=_('Github Members')
    )
    gh_admins = ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list,
        help_text=_('comma delimited'),
        verbose_name=_('Github Administrators')
    )
    github_bot_enabled = models.BooleanField(default=True, verbose_name=_('Is Github Bot Enabled?'))
    github_username = models.CharField(blank=True, max_length=80, verbose_name=_('Github Username'))
    is_hiring = models.BooleanField(default=False, verbose_name=_('Is Hiring?'))
    is_visible = models.BooleanField(default=True, verbose_name=_('Is Visible?'))
    modified_on = models.DateTimeField(auto_now=True, verbose_name=_('Last Modified'))
    slug = AutoSlugField(blank=True, max_length=80, populate_from='name', verbose_name=_('Slug'))
    tags = TaggableManager(blank=True, related_name='organization_tags', verbose_name=_('Tags'))
    website_url = models.URLField(blank=True, verbose_name=_('Website'))
    admins = models.ManyToManyField(User, related_name='organizations_owned', verbose_name=_('Administrators'))
    location = models.CharField(blank=True, max_length=255, verbose_name=_('Location'))
    profile = models.OneToOneField(
        'dashboard.Profile',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='org',
        verbose_name=_('Profile'),
    )

    objects = OrganizationQuerySet.as_manager()

    def update_basic_fields(self, org, save=False):
        self.email = org.email if org.email else ''
        self.name = org.name if org.name else ''
        self.github_username = org.login if org.login else ''
        self.website_url = org.blog if org.blog else ''
        self.gh_data = org.raw_data if org.raw_data else {}
        self.location = org.location if hasattr(org, 'location') else ''
        self.description = self.gh_data.get('description', '')
        if save:
            self.save()

    def check_profile(self):
        """Check whether or not a Profile exists matching the Organization name."""
        if not hasattr(self, 'profile'):
            try:
                profile = Profile.objects.get(handle=self.github_username)
                self.profile = profile
                self.save()
                return profile
            except Profile.DoesNotExist:
                return None
            except Exception as e:
                logger.error(e)

    def sync_github(self, token=None, created=False):
        gh_client = github_connect(token)
        username = self.github_username or self.name
        org = gh_client.get_organization(login=username)
        self.update_basic_fields(org, save=created)

        for member in org.get_members(role='admin'):
            try:
                member_profile = User.objects.get(username__iexact=member.login)
                self.admins.add(member_profile)
            except User.DoesNotExist:
                pass
            except User.MultipleObjectsReturned:
                member_profile = User.objects.filter(username__iexact=member.login).first()
                self.admins.add(member_profile)
            self.gh_admins.append(member.name)
        for member in org.get_members():
            try:
                member_profile = User.objects.get(username__iexact=member.login)
                self.user_set.add(member_profile)
            except User.DoesNotExist:
                pass
            self.gh_members.append(member.name)
        self.update_basic_fields(org, save=True)
        self.check_profile()
        return org

    def get_issues(self, state='open', issue_filter=None, labels=None, token=None):
        kwargs = {'state': state}
        if issue_filter is not None:
            kwargs['filter'] = issue_filter
        if labels is not None:
            kwargs['labels'] = labels
        gh_client = github_connect(token)
        org_user = gh_client.get_organization(login=self.slug)
        return org_user.get_issues(state=state)

    def is_gh_member(self, username, token=None, public_only=True):
        gh_client = github_connect(token)
        org_user = gh_client.get_organization(login=self.slug)
        if not public_only:
            return org_user.has_in_members(username)
        return org_user.has_in_public_members(username)

    def get_absolute_url(self):
        return reverse('account_organization_detail', args=(self.slug, ))

    def get_update_url(self):
        return reverse('account_organization_update', args=(self.slug, ))

    def is_member(self, active_user):
        return self.prefetch_related('user_set').user_set.filter(username__iexact=active_user).exists()

    def is_admin(self, active_user):
        return self.select_related('admins').admins.filter(username__iexact=active_user).exists()

    def bounties(self, queryset=None):
        from dashboard.models import Bounty
        if queryset is None:
            queryset = Bounty.objects.current().filter(github_url__icontains=self.github_username)
        return queryset

    @property
    def avatar_url(self):
        if not self.avatar:
            self.avatar = Avatar.objects.create()
            self.save()
            self.avatar.use_github_avatar = True
            print('ORG NAME: ', self.github_username)
            self.avatar.pull_github_avatar(handle=self.github_username, is_org=True)
            self.avatar.save()
        return self.avatar.avatar_url

    @property
    def current_bounties(self):
        return self.bounties()

    @property
    def bounty_count(self):
        return self.bounties().count()

    def to_dict(self, active_user=None):
        """Provide a dictionary representation of the Organization.

        Returns:
            dict: The Organization as a dictionary.

        """
        org_dict = {
            'name': self.name,
            'slug': self.slug,
            'login': self.github_username,
            'avatar_url': self.avatar_url if self.avatar_url else '',
            'is_visible': self.is_visible,
            'created_on': self.created_on,
            'modified_on': self.modified_on,
            'description': self.description,
            'website_url': self.website_url,
            'location': self.location,
            'email': self.email,
            'bounty_count': self.bounty_count,
        }
        if active_user:
            org_dict['is_member'] = self.is_member(active_user)
            if org_dict['is_member']:
                org_dict['is_admin'] = self.is_admin(active_user)


@receiver(post_save, sender=Organization, dispatch_uid='org_post_save')
def organization_post_save(sender, instance, created, **kwargs):
    """Define the Organization post save logic."""
    if created:
        instance.sync_github(created=True)
