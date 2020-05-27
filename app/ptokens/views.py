'''
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

'''
from __future__ import unicode_literals

import csv
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.db.models import Avg, Count, Max, Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.http import Http404, HttpResponse, JsonResponse
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import gettext_lazy as _

from dashboard.models import Profile

def quickstart(request):
    context = {}
    return TemplateResponse(request, 'personal_tokens.html', context)

def faq(request):
    context = {}
    return TemplateResponse(request, 'buy_a_token.html', context)

def tokens(request, token_state):
    """List JSON data for the user tokens"""
    
    user = request.user if request.user.is_authenticated else None
    if not user:
        return JsonResponse(
            {'error': _('You must be authenticated via github to use this feature!')},
            status=401)

    profile = request.user.profile
    if token_state == 'open':
        return JsonResponse([], safe=False)
    elif token_state == 'in_progress':
        return JsonResponse([], safe=False)
    elif token_state == 'completed':
        return JsonResponse([], safe=False)
    elif token_state == 'denied':
        return JsonResponse([], safe=False)