# -*- coding: utf-8 -*-
"""Define view for the inbox app.

Copyright (C) 2019 Gitcoin Core

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

import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from dashboard.models import (
    Activity, Bounty, BountyDocuments, BountyFulfillment, BountyInvites, FeedbackEntry, HackathonEvent, Interest,
    Profile, ProfileSerializer, UserAction, UserVerificationModel,
)
from dashboard.utils import profile_helper

# from board.models import Notification

# Create your views here.
@login_required
def board(request):
    """Handle the board view."""

    context = {
        'is_outside': True,
        'active': 'dashboard',
        'title': 'dashboard',
        'card_title': _('Dashboard'),
        'card_desc': _('Manage all your activity.'),
        'avatar_url': static('v2/images/helmet.png'),
    }
    return TemplateResponse(request, 'board.html', context)

@login_required
def get_bounties(request):
    if not settings.DEBUG:
        network = 'mainnet'
    else:
        network = 'rinkeby'

    current_user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
    profile = ProfileSerializer(current_user.profile).data
    bounties = Bounty.objects.current().filter(
                bounty_owner_github_username__iexact=current_user.profile.handle,
                network=network
            ).values(
                'id','bounty_owner_github_username', 'github_comments', 'value_true', 'value_in_usdt_now', 'token_name',
                'github_url', 'idx_status', 'standard_bounties_id', 'title', 'bounty_type', 'bountyinvites',
                'interested', 'fulfillments' )

    return JsonResponse(
                {
                    'bounties': list(bounties),
                    'profile': profile
                },
                status=200)
