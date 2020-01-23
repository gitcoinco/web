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
from datetime import datetime, timedelta

from dateutil import parser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from pytz import UTC

from dashboard.models import Profile
from .models import Sessions, MentoringAvailable
from .serializers import AvailabilitySerializer

logger = logging.getLogger(__name__)


def mentor_home(request):
    """Render the sessions home page."""
    listings = []
    if not request.user.is_anonymous:
        listings = Sessions.objects.filter(Q(mentor=request.user.profile) | Q(mentee=request.user.profile), active=True)
    mentoring = Sessions.objects.filter(active=True).values_list('mentor__id', flat=True)
    available_mentors = MentoringAvailable.objects.filter(active=True, active_until__gt=datetime.now()).exclude(mentor__in=mentoring)
    unavailable_mentors = MentoringAvailable.objects.filter(active=True, active_until__gte=datetime.now(UTC),
                                                            mentor__in=mentoring)

    context = {
        'title': 'Mentor',
        "sessions": listings,
        'available_mentors': available_mentors,
        'unavailable_mentors': unavailable_mentors
    }
    return TemplateResponse(request, 'mentor_home.html', context)


@login_required
def join_session(request, session):
    """Render the sessions home page."""
    # DEMO: Comment for demo
    session = get_object_or_404(Sessions, mentor__id=session)

    is_mentor = session.mentor_id == request.user.profile.id

    # If no meentee, then another user join the url is set as mentee
    if session.mentee is None and not is_mentor:
        session.mentee_join = datetime.now()
        session.mentee = request.user.profile.id
        session.save()

    if is_mentor and not session.mentor_join:
        session.mentor_join = datetime.now()
        session.save()

    is_mentee = session.mentee_id == request.user.profile.id

    if not is_mentor and not is_mentee:
        return TemplateResponse(request, 'waiting_session.html')

    # Prod
    context = {
        'title': 'Mentor',
        "session": session,
        "is_mentor": is_mentor,
        "is_mentee": is_mentee,
        # TODO: finished* ? typo here
        'finised': session.active is False,
        # TODO: Not sure about the merge here
        # 'is_mentor': session.mentor.id == request.user.profile.id
        "session": {
            "name": "Get help with your bug!",
            "description": "I'm a very knowledgable dev",
            "mentee":{
                "name": "Jean Louis"
            },
            "mentor": {
                "name": "Jean Francois",
                "address": '0x5268b3d996b375Bf39777ffdE95D615d0D7bd56B'
            },
            "rate_per_min": 50000000000000000
        },
        "role": "mentee"
    }

    # DEMO: Decomment here for demo
    # context = {
    #     'title': 'Mentor',
    #     # "session": session,
    #     # 'is_mentor': session.mentor.id == request.user.profile.id
    #     "session": {
    #         "name": "Get help with your bug!",
    #         "description": "I'm a very knowledgable dev",
    #         "mentee":{
    #             "name": "Jean Louis"
    #         },
    #         "mentor": {
    #             "address": '0x8401Eb5ff34cc943f096A32EF3d5113FEbE8D4Eb'
    #         }
    #         "rate_per_min": 50000000000000000
    #     },
    #     "role": "mentee"
    # }

    return TemplateResponse(request, 'active_session.html', context)


@csrf_exempt
@login_required
def finish_session(request, session):
    """Render the sessions home page."""
    session = get_object_or_404(Sessions, id=session)
    is_mentor = session.mentor_id == request.user.profile.id
    is_mentee = session.mentee_id == request.user.profile.id

    if is_mentee and not session.mentee_leave:
        session.mentee_leave = datetime.now()
        session.save()

        return JsonResponse({'status': 'ok', 'msg': ''})

    if is_mentor:
        if session.active:
            session.active = False
            session.end_datetime = datetime.now()
            session.mentor_leave = datetime.now()
            session.save()
        return JsonResponse({'status': 'ok', 'msg': ''})

    return JsonResponse({'status': 'error', 'msg': 'Only the owner finsh the session'}, status=403)


@login_required
def new_session(request):
    """Render the sessions home page."""

    if request.method == "POST":
        name = request.POST.get('name', 'Mentoring')
        desc = request.POST.get('description', '')
        # Not used
        network = request.POST.get('network', 4)
        # Not used
        mentee = request.POST.get('mentee', None)
        try:
            price_per_min = request.POST.get('price_per_min')
        except ValueError:
            raise Exception("Price is needed")
        # amount = 0
        # Not used 
        mentee_profile = None

        try:
            to_address = request.POST.get('to_address')
        except ValueError:
            raise Exception("Ethereum address is needed")

        print("to_address", to_address)

        # TO REMOVE
        # if mentee:
        #     mentee_profile = get_object_or_404(Profile, handle=mentee)

        session = Sessions(name=name,
                           description=desc,
                           network=network,
                           active=True,
                           price_per_min=price_per_min,
                           mentor=request.user.profile,
                           mentee=mentee_profile,
                           start_datetime=datetime.now(),
                           to_address=to_address
                           )
        session.save()

        return redirect('session_join', session=session.id)

    listings = Sessions.objects.all()
    context = {
        'title': 'Mentor',
        "sessions": listings
    }
    return TemplateResponse(request, 'new_session.html', context)


@login_required
def get_session(request, session):
    """Update current info of this set"""
    errors = []
    session = get_object_or_404(Sessions, id=session)

    is_mentor = session.mentor_id == request.user.profile.id
    is_mentee = session.mentee_id == request.user.profile.id

    return JsonResponse({
        'name': session.name,
        'description': session.description,
        'network': session.network,
        'to_address': session.to_address,
        'metadata': session.metadata,
        'tags': session.tags,
        'active': session.active,

        'price_per_min': session.price_per_min,
        'amount': session.price_per_min,
        'tokenName': session.tokenName,
        'tokenAddress': session.tokenAddress,

        'tx_status': session.tx_status,
        'tx_id': session.tx_id,
        'tx_time': session.tx_time,

        'mentor_name': session.mentor.name if session.mentor else '',
        'mentor_id': session.mentor.id if session.mentor else None,
        'mentor_handle': session.mentor.handle if session.mentor else '',
        'is_mentor': is_mentor,
        'mentor_leave': session.mentor_leave,
        'mentor_join': session.mentor_join,

        'mentee_join': session.mentee_join,
        'mentee_leave': session.mentee_leave,
        'mentee_name': session.mentee.name if session.mentee else '',
        'mentee_id': session.mentee.id if session.mentee else None,
        'mentee_handle': session.mentee.handle if session.mentee else '',
        'is_mentee': is_mentee,

        'start_datetime': session.start_datetime,
        'end_datetime': session.end_datetime
    })

@csrf_exempt
@login_required
def update_session(request, session):
    """Update current info of this set"""
    errors = []
    session = get_object_or_404(Sessions, id=session)
    name = request.POST.get('name', None)
    description = request.POST.get('description', None)
    metadata = request.POST.get('metadata', None)
    tags = request.POST.get('tags', None)
    active = request.POST.get('active', None)
    amount = request.POST.get('amount', None)
    tx_status = request.POST.get('tx_status', None)
    tx_id = request.POST.get('tx_id', None)
    tx_time = request.POST.get('tx_time', None)
    mentee_handler = request.POST.get('mentee_handler', None)

    if mentee_handler:
        mentee = Profile.objects.get(handle__iexact=mentee_handler)
        if mentee:
            session.mentee = mentee

    if name:
        session.name = name

    if description:
        session.description = description

    if metadata:
        try:
            session.metadata = json.loads(metadata)
        except json.decoder.JSONDecodeError:
            errors.append({'metadata': ['Error parsing json metadata']})

    if not active is None:
        session.active = active == 'true'

    if amount:
        try:
            session.amount = float(amount)
        except ValueError:
            errors.append({'amount': ['Error parsing amount data']})

    if tx_status in ['na', 'pending', 'success''error', 'error', 'unknown', 'dropped']:
        session.tx_status = tx_status

    if not session.tx_id and tx_id:
        session.tx_received_on = datetime.now()
        try:
            session.tx_id = int(tx_id)
        except ValueError:
            errors.append({'tx_id': ['Error parsing tx id']})

        try:
            session.tx_time = parser.parse(tx_time)
        except ValueError:
            errors.append({'tx_time': ['Error parsing tx datetime']})

    if tags:
        try:
            session.tags = json.loads(tags)
            if not type(session.tags) is list:
                raise ValueError('Expected list')
        except (json.decoder.JSONDecodeError, ValueError):
            errors.append({'metadata': ['Error parsing tags data']})

    if errors:
        return JsonResponse({
            'status': 'error',
            'message': 'Validation errors',
            'errors': errors
        }, status=422)

    session.save()

    return JsonResponse({'status': 'ok', 'message': ''})


def get_my_availability(request):
    try:
        available = MentoringAvailable.objects.get(mentor=request.user.profile)

        return JsonResponse(AvailabilitySerializer(available).data)
    except MentoringAvailable.DoesNotExist:
        return JsonResponse({
            'available': False,
            'active_until': '',
            'period_time': '',
            'joined': None
        }, status=404)


@csrf_exempt
@require_POST
def set_mentor_available(request):
    deltas = {
        '5 minutes': timedelta(minutes=5),
        '15 minutes': timedelta(minutes=15),
        '30 minutes': timedelta(minutes=30),
        '1 hour': timedelta(hours=1),
        '2 hours': timedelta(hours=2),
        '6 hours': timedelta(hours=6)
    }

    period_time = request.POST.get('period_time')

    until = datetime.now(UTC) + deltas['30 minutes']
    if period_time in deltas.keys():
        until = datetime.now(UTC) + deltas[period_time]

    try:
        available = MentoringAvailable.objects.get(mentor=request.user.profile)

        available.active_until = until
        available.period_time = period_time
        available.active = True
        available.save()
    except MentoringAvailable.DoesNotExist:
        available = MentoringAvailable(
            mentor=request.user.profile,
            active_until=until,
            active=True,
            period_time=period_time
        )
        available.save()

    return JsonResponse(AvailabilitySerializer(available).data)

@csrf_exempt
@require_POST
def set_mentor_unavailable(request):
    try:
        available = MentoringAvailable.objects.get(mentor=request.user.profile)
        available.active = False
        available.save()
        return JsonResponse(AvailabilitySerializer(available).data)
    except MentoringAvailable.DoesNotExist:
        return JsonResponse({
            'available': False,
            'active_until': '',
            'period_time': '',
            'joined': None
        }, status=404)


@csrf_exempt
@require_POST
def toggle_availability(request):
    try:
        available = MentoringAvailable.objects.get(mentor=request.user.profile)
        if available.active:
            return set_mentor_unavailable(request)
        else:
            return set_mentor_available(request=request)
    except MentoringAvailable.DoesNotExist:
        return set_mentor_available(request=request)


def get_mentors(request):
    available = request.GET.get('status', None)

    if available == 'available':
        mentors = MentoringAvailable.objects.filter(active=True, active_until__gt=datetime.now())
    elif available == 'unavailable':
        mentors = MentoringAvailable.objects.filter(Q(active=False) | Q(active_until__lte=datetime.now()))
    else:
        mentors = MentoringAvailable.objects.all()

    return JsonResponse(AvailabilitySerializer(mentors, many=True).data, safe=False)
