# -*- coding: utf-8 -*-
"""Define the quadraticlands views.

Copyright (C) 2020 Gitcoin Core

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

from django.conf import settings  # Global Envars
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.humanize.templatetags.humanize import intword
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Avg, Count, Max, Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from ratelimit.decorators import ratelimit

from .forms import ClaimForm

# from django.utils import timezone
# from django.utils.crypto import get_random_string
# from django.views.decorators.cache import cache_page
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

# TODO - add a new envar for Token Request Siging micro service URL
# TODO - add a new envar for HMAC or other auth key for communicating with micro service 
# settings.DATABASE_URL

def index(request):
    return TemplateResponse(request, 'quadraticlands/index.html')


# ratelimit.UNSAFE is a shortcut for ('POST', 'PUT', 'PATCH', 'DELETE').
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def claim_tokens(request):
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None
   
    # if POST 
    if request.method == 'POST':
        # create a form instance and populate it with data from the request (from forms.py)
        form = ClaimForm(request.POST)

        # iterate through post keys and log them for debugging/learning   
        for key in request.POST.keys():
             logger.info(f'claim_tokens post key logger: {request.POST.get(key)}')
    
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            return TemplateResponse(request, 'quadraticlands/welcome-to-the-quadratic-lands.html')
    # if GET 
    else:
        # from forms.py 
        form = ClaimForm()
        
        context = {
            'active': 'verified',
            'title': _('Claim GTC'),
            'profile': profile,
            'user' : user,
            'form' : form,
        }

        return TemplateResponse(request, 'quadraticlands/claim.html', context)

def welcome(request):
    return TemplateResponse(request, 'quadraticlands/welcome-to-the-quadratic-lands.html')

def about(request):
    return TemplateResponse(request, 'quadraticlands/about.html')

def governance(request):
    return TemplateResponse(request, 'quadraticlands/governance.html')

def missions(request):
    return TemplateResponse(request, 'quadraticlands/missions.html')
