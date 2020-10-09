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

from django.conf import settings # Global Envars 
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
# from django.utils import timezone
# from django.utils.crypto import get_random_string
# from django.utils.translation import gettext_lazy as _
# from django.views.decorators.cache import cache_page
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

# settings.DATABASE_URL

def index(request):
    return TemplateResponse(request, 'quadraticlands/index.html')

def claim_tokens(request):
    return TemplateResponse(request, 'quadraticlands/claim.html')

def about(request):
    return TemplateResponse(request, 'quadraticlands/about.html')

def governance(request):
    return TemplateResponse(request, 'quadraticlands/governance.html')

def mission(request):
    return TemplateResponse(request, 'quadraticlands/mission.html')