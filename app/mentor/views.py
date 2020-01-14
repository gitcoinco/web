# -*- coding: utf-8 -*-
"""Define view for the Mentor app.

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

import json
import logging

from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Profile
from .models import Sessions

logger = logging.getLogger(__name__)


def mentor_home(request):
    """Render the sessions home page."""
    listings = Sessions.objects.all()
    context = {
        'title': 'Mentor',
        "sessions": listings
    }
    return TemplateResponse(request, 'mentor_home.html', context)



def join_session(request, session):
    """Render the sessions home page."""
    session = get_object_or_404(Sessions, id=session)
    context = {
        'title': 'Mentor',
        "session": session,
        'is_mentor': session.mentor.id == request.user.profile.id
    }
    return TemplateResponse(request, 'active_session.html', context)


def new_session(request):
    """Render the sessions home page."""

    for p in Profile.objects.all():
        print(p.handle)

    if request.method == "POST":
        name = request.POST.get('name')
        desc = request.POST.get('description')
        network = request.POST.get('network')
        mentee = request.POST.get('mentee')
        amount = 0
        mentee_profile = get_object_or_404(Profile, handle=mentee)
        session = Sessions(name=name,
                           description=desc,
                           priceFinney=amount,
                           network=network,
                           active=True,
                           mentor=request.user.profile,
                           mentee=mentee_profile
                           )
        session.save()

        return redirect('session_join', session=session.id)

    listings = Sessions.objects.filter()
    context = {
        'title': 'Mentor',
        "sessions": listings
    }
    return TemplateResponse(request, 'new_session.html', context)
