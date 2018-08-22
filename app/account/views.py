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

from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from .models import Organization

logger = logging.getLogger(__name__)


@staff_member_required
def explorer_organzations(request, org_name):
    """Handle displaying the organizations on the explorer."""
    orgs = [{
        'logo': '/v2/images/project_logos/metamask.png',
        'profile': 'metamask',
        'is_hiring': True,
    }, {
        'logo': '/v2/images/project_logos/augur.png',
        'profile': 'augur',
    }, {
        'logo': '/v2/images/project_logos/augur.png',
        'profile': 'augur',
    }, {
        'logo': '/v2/images/project_logos/augur.png',
        'profile': 'augur',
    }]

    try:
        org = Organization.objects.prefetch_related('user_set').get(github_username=org_name)
        org_members = org.user_set.all()
    except Organization.DoesNotExist:
        return JsonResponse({'status': 404, 'message': 'Not found.'}, status=404)

    params = {
        'active': 'organizations',
        'title': _('Organizations Explorer'),
        'orgs': orgs,
        'view_org': org,
        'org_members': org_members,
    }

    return TemplateResponse(request, '_dashboard/organizations.html', params)


def organizations(request):
    """Handle displaying the organizations."""
    orgs = [{
        'name': 'Metamask',
        'about': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean sollicitudin sapien vitae sapien porttitor euismod. Pellentesque fermentum ligula in risus vulputate, in auctor leo tristique. Fusce sollicitudin enim aliquam nunc',
        'logo': '/v2/images/project_logos/metamask.png',
        'profile': 'metamask',
        'bounty_count': 2,
    }, {
        'name': 'Angur',
        'about': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean sollicitudin sapien vitae sapien porttitor euismod. Pellentesque fermentum ligula in risus vulputate, in auctor leo tristique. Fusce sollicitudin enim aliquam nunc',
        'logo': '/v2/images/project_logos/augur.png',
        'profile': 'augur',
        'bounty_count': 4,
    }]

    params = {
        'active': 'organizations',
        'title': _('Organizations'),
        'caption': _('Inspiring Projects that are Pushing Open Source Forward'),
        'orgs': orgs,
    }
    return TemplateResponse(request, 'organizations.html', params)

