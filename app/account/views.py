# -*- coding: utf-8 -*-
"""Define the Account views.

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
import logging

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from .models import Organization

logger = logging.getLogger(__name__)


def explorer_organzations(request, org_name):
    """Handle displaying the organizations on the explorer."""
    try:
        all_organizations = Organization.objects.select_related('avatar', 'profile').filter(is_visible=True)
        org = Organization.objects.prefetch_related('user_set').get(github_username__iexact=org_name)
        org_members = org.user_set.all()
    except Organization.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Not found.'}, status=404)

    profile = getattr(request.user, 'profile', None)
    if request.user.is_authenticated and profile:
        follows_org = profile.organizations_following.filter(github_username__iexact=org_name)

    keywords = [keyword.name for keyword in org.tags.all().distinct()]
    params = {
        'active': 'organizations',
        'title': _('Organizations Explorer'),
        'orgs': all_organizations,
        'view_org': org,
        'org_members': org_members,
        'keywords': keywords,
        'follows_org': follows_org,
    }

    return TemplateResponse(request, '_dashboard/organizations.html', params)


def organizations(request):
    """Handle displaying the organizations."""
    orgs = Organization.objects.select_related('avatar', 'profile').filter(is_visible=True)

    params = {
        'active': 'organizations',
        'title': _('Organizations'),
        'caption': _('Inspiring Projects that are Pushing Open Source Forward'),
        'orgs': orgs,
    }
    return TemplateResponse(request, 'organizations.html', params)


def follow_organization(request, org_handle='', org_id=None):
    """Follow an Organization."""
    org_kwargs = {}

    if not request.user.is_authenticated or not getattr(request.user, 'profile', None):
        return JsonResponse({'status': 404, 'message': _('You must be authenticated to follow an organization!')}, status=404)
    try:
        if org_handle:
            org_kwargs['github_username'] = org_handle
        if org_id:
            org_kwargs['id'] = org_id
        org = Organization.objects.filter(**org_kwargs)
    except Organization.DoesNotExist:
        return JsonResponse({'status': 404, 'message': _('Organization not found.')}, status=404)

    org.followers.add(request.user.profile)

    return JsonResponse({'status': 404, 'message': _('An exception occurred.  Please try again.')}, status=404)


def unfollow_organization(request, org_handle='', org_id=None):
    """Unfollow an Organization."""
    org_kwargs = {}

    if not request.user.is_authenticated or not getattr(request.user, 'profile', None):
        return JsonResponse({'status': 404, 'message': _('You must be authenticated to follow an organization!')}, status=404)
    try:
        if org_handle:
            org_kwargs['github_username'] = org_handle
        if org_id:
            org_kwargs['id'] = org_id
        org = Organization.objects.filter(**org_kwargs)
    except Organization.DoesNotExist:
        return JsonResponse({'status': 404, 'message': _('Organization not found.')}, status=404)

    org.followers.remove(request.user.profile)

    return JsonResponse({'status': 404, 'message': _('An exception occurred.  Please try again.')}, status=404)
