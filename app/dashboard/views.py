'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from dashboard.models import Subscription, BountySyncRequest
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from dashboard.helpers import normalizeURL

def process_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Process Bounty',
    }

    return TemplateResponse(request, 'process_bounty.html', params)


def dashboard(request):

    params = {
        'active': 'dashboard',
        'title': 'Dashboard',
    }
    return TemplateResponse(request, 'dashboard.html', params)


def new_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'active': 'submit_bounty',
        'title': 'Submit Bounty',
    }

    return TemplateResponse(request, 'submit_bounty.html', params)


def claim_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Claim Bounty',
        'active': 'claim_bounty',
    }

    return TemplateResponse(request, 'claim_bounty.html', params)


def bounty_details(request):

    params = {
        'issueURL': request.GET.get('issue_'),
        'title': 'Bounty Details',
        'active': 'bounty_details',
    }

    return TemplateResponse(request, 'bounty_details.html', params)



@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def save_search(request):

    email = request.POST.get('email')
    if email:
        raw_data = request.POST.get('raw_data')
        Subscription.objects.create(
            email=email,
            raw_data=raw_data,
            ip=get_ip(request),
            )
        response = {
            'status': 200,
            'msg': 'Success!',
        }
        return JsonResponse(response)

    context = {
        'active': 'save',
        'title': 'Save Search',
    }
    return TemplateResponse(request, 'save_search.html', context)

@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def sync_web3(request):
    result = {}
    issueURL = request.POST.get('issueURL', False)
    if issueURL:
        issueURL = normalizeURL(issueURL)
        result['status'] = 'OK'
        for existing_bsr in BountySyncRequest.objects.filter(github_url=issueURL, processed=False):
            existing_bsr.processed = True
            existing_bsr.save()
        BountySyncRequest.objects.create(
            github_url=issueURL,
            processed=False,
            )

    return JsonResponse(result)




