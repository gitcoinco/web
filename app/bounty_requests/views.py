# -*- coding: utf-8 -*-
"""Define bounty request views.

Copyright (C) 2021 Gitcoin Core

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

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import requests
from dashboard.models import Bounty, Profile, TribeMember
from linkshortener.models import Link
from marketing.mails import new_bounty_request
from ratelimit.decorators import ratelimit

from .forms import BountyRequestForm
from .models import BountyRequest


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
@csrf_exempt
def bounty_request(request):
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None

    comments_prefill = None
    if request.GET.get('code', False):
        code = request.GET.get('code')
        ls = Link.objects.filter(shortcode=code, comments__icontains='Gitcoin Request Coin', uses__lt=5)
        if ls.exists():
            ls = ls.first()
            comments_prefill = f"{ls.comments} : {ls.shortcode}"

    if request.body:
        if not user or not profile or not profile.handle:
            return JsonResponse(
                {'error': _('You must be Authenticated via Github to use this feature!')},
                status=401)

        try:
            result = BountyRequestForm(json.loads(request.body))
            if not result.is_valid():
                raise
        except:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        model = result.save(commit=False)

        gh_org_api_url = 'https://api.github.com/orgs/' + model.github_org_name
        gh_org_api_resp = requests.get(url=gh_org_api_url).json()

        gh_org_email = ''
        if gh_org_api_resp is not None and gh_org_api_resp.get('email') is not None:
            gh_org_email = gh_org_api_resp['email']

        model.requested_by = profile
        model.github_org_email = gh_org_email
        model.save()
        new_bounty_request(model)
        return JsonResponse({'msg': _('Bounty Request received.')}, status=200)

    form = BountyRequestForm()
    params = {
        'form': form,
        'title': _('Request a Bounty'),
        'comments_prefill': comments_prefill,
        'card_title': _('Gitcoin Requests'),
        'card_desc': _('Have an open-source issue that you think would benefit the community? '
                       'Suggest it be given a bounty!')
    }

    return TemplateResponse(request, 'bounty_request_form.html', params)



@require_POST
@csrf_exempt
@ratelimit(key='ip', rate='5/s', method=ratelimit.UNSAFE, block=True)
def create_bounty_request_v1(request):
    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to create bounty request'
    }

    user = request.user if request.user.is_authenticated else None

    if not user:
        response['message'] = 'error: user needs to be authenticated to submit bounty request'
        return JsonResponse(response)

    profile = request.user.profile if hasattr(request.user, 'profile') else None

    if not profile:
        response['message'] = 'error: no matching profile found'
        return JsonResponse(response)

    if not request.method == 'POST':
        response['message'] = 'error: create bounty request is a POST operation'
        return JsonResponse(response)

    github_url = request.POST.get("github_url", None)

    if not github_url:
        response['message'] = 'error: missing github_url parameter'
        return JsonResponse(response)

    if Bounty.objects.filter(github_url=github_url).exists():
        response = {
            'status': 303,
            'message': 'bounty already exists for this github issue'
        }
        return JsonResponse(response)

    title = request.POST.get("title", None)
    if not title:
        response['title'] = 'error: missing title parameter'
        return JsonResponse(response)

    comment = request.POST.get("comment", None)
    if not comment:
        response['message'] = 'error: missing comment parameter'
        return JsonResponse(response)

    amount = request.POST.get("amount", None)
    if not amount:
        response['message'] = 'error: missing amount parameter'
        return JsonResponse(response)

    tribe = request.POST.get("tribe", None)
    if not tribe:
        response['message'] = 'error: missing tribe parameter'
        return JsonResponse(response)

    try:
        tribe_profile = Profile.objects.get(handle=tribe)
    except Profile.DoesNotExist:
        response = {
            'status': 400,
            'message': 'error: could not find tribe'
        }
        return JsonResponse(response)
    except Profile.MultipleObjectsReturned:
        response = {
            'status': 500,
            'message': 'error: found multiple tribes'
        }
        return JsonResponse(response)


    token_name = request.POST.get("token_name", 'ETH')
    if token_name == '':
        token_name = 'ETH'

    bounty_request = BountyRequest()
    bounty_request.requested_by = profile
    bounty_request.github_url = github_url
    bounty_request.amount = amount
    bounty_request.token_name = token_name
    bounty_request.comment = comment
    bounty_request.title = title
    bounty_request.tribe = tribe_profile

    bounty_request.save()

    try:
        TribeMember.objects.get(profile=profile, org=tribe_profile)
    except TribeMember.DoesNotExist:
        kwargs = {
            'org': tribe_profile,
            'profile': profile
        }
        tribemember = TribeMember.objects.create(**kwargs)
        tribemember.save()


    response = {
        'status': 204,
        'message': 'bounty request successfully created'
    }

    return JsonResponse(response)


@require_POST
@csrf_exempt
@ratelimit(key='ip', rate='5/s', method=ratelimit.UNSAFE, block=True)
def update_bounty_request_v1(request):
    response = {
        'status': 400,
        'message': 'error: Bad Request. Unable to edit bounty request'
    }

    user = request.user if request.user.is_authenticated else None

    if not user:
        response['message'] = 'error: user needs to be authenticated to edit bounty request'
        return JsonResponse(response)

    profile = request.user.profile if hasattr(request.user, 'profile') else None

    if not profile:
        response['message'] = 'error: no matching profile found'
        return JsonResponse(response)

    if not request.method == 'POST':
        response['message'] = 'error: create bounty edit is a POST operation'
        return JsonResponse(response)

    bounty_request_id = request.POST.get("bounty_request_id", None)

    if not bounty_request_id:
        response['message'] = 'error: missing bounty_request_id parameter'
        return JsonResponse(response)

    try:
        bounty_request = BountyRequest.objects.get(pk=bounty_request_id)
    except BountyRequest.DoesNotExist:
        response = {
            'status': 404,
            'message': 'request bounty request does not exsist'
        }
        return JsonResponse(response)
    except BountyRequest.MultipleObjectsReturned:
        response = {
            'status': 500,
            'message': 'error: found multiple bounty requests'
        }
        return JsonResponse(response)

    is_my_org = any([bounty_request.tribe.handle.lower() == org.lower() for org in request.user.profile.organizations ])
    if not is_my_org:
        response = {
            'status': 405,
            'message': 'operation on bounty request can be performed by tribe owner'
        }
        return JsonResponse(response)

    request_status = request.POST.get("request_status", None)
    if request_status == 'c' and bounty_request.status != 'c':
        bounty_request.status = 'c'
        bounty_request.save()

    response = {
        'status': 200,
        'message': 'bounty request updated successfully'
    }

    return JsonResponse(response)
