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
from dashboard.models import Subscription, BountySyncRequest, Tip
from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from dashboard.helpers import normalizeURL, process_bounty_details, process_bounty_changes
import json
from dashboard.notifications import maybe_market_tip_to_github, maybe_market_tip_to_slack
from marketing.mails import tip_email
from app.github import get_user as get_github_user

def send_tip(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Send Tip',
    }

    return TemplateResponse(request, 'yge/send1.html', params)


def receive_tip(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Receive Tip',
    }

    return TemplateResponse(request, 'yge/receive.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='1/m', method=ratelimit.UNSAFE, block=True)
def send_tip_2(request):

    if request.body != '':
        status = 'OK'
        message = 'Notification has been sent'
        params = json.loads(request.body)
        emails = []
        
        #basic validation
        if params['email']:
            emails.append(params['email'])
        gh_user = get_github_user(params['username'])
        if gh_user.get('email', False):
            emails.append(gh_user['email'])
        if len(emails) == 0:
            status = 'error'
            message = 'No email addresses found'
        expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])

        #db mutations
        tip = Tip.objects.create(
            emails=emails,
            url=params['url'],
            tokenName=params['tokenName'],
            amount=params['amount'],
            comments=params['comments'],
            ip=get_ip(request),
            expires_date=expires_date,
            github_url=params['github_url'],
            from_name=params['from_name'],
            username=params['username'],
            network=params['network'],
            tokenAddress=params['tokenAddress'],
            txid=params['txid'],
            )

        #notifications
        maybe_market_tip_to_github(tip)
        maybe_market_tip_to_slack(tip, 'new_tip', tip.txid)
        tip_email(tip, set(emails), True)

        #http response
        response = {
            'status': status,
            'message': message,
        }
        return JsonResponse(response)

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Send Tip',
    }

    return TemplateResponse(request, 'yge/send2.html', params)


def process_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Process Bounty',
    }

    return TemplateResponse(request, 'process_bounty.html', params)


def dashboard(request):

    params = {
        'active': 'dashboard',
        'title': 'Bounty Explorer',
    }
    return TemplateResponse(request, 'dashboard.html', params)


def new_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'active': 'submit_bounty',
        'title': 'Create Bounty',
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

    #setup
    result = {}
    issueURL = request.POST.get('issueURL', False)
    bountydetails = request.POST.getlist('bountydetails[]', [])
    if issueURL:

        issueURL = normalizeURL(issueURL)
        if not len(bountydetails):
            #create a bounty sync request
            result['status'] = 'OK'
            for existing_bsr in BountySyncRequest.objects.filter(github_url=issueURL, processed=False):
                existing_bsr.processed = True
                existing_bsr.save()
        else:
            #normalize data
            bountydetails[0] = int(bountydetails[0])
            bountydetails[1] = str(bountydetails[1])
            bountydetails[2] = str(bountydetails[2])
            bountydetails[3] = str(bountydetails[3])
            bountydetails[4] = bool(bountydetails[4] == 'true')
            bountydetails[5] = bool(bountydetails[5] == 'true')
            bountydetails[6] = str(bountydetails[6])
            bountydetails[7] = int(bountydetails[7])
            bountydetails[8] = str(bountydetails[8])
            bountydetails[9] = int(bountydetails[9])
            bountydetails[10] = str(bountydetails[10])
            print(bountydetails)
            contract_address = request.POST.get('contract_address')
            network = request.POST.get('network')
            didChange, old_bounty, new_bounty = process_bounty_details(bountydetails, issueURL, contract_address, network)

            print("{} changed, {}".format(didChange, issueURL))
            if didChange:
                print("- processing changes");
                process_bounty_changes(old_bounty, new_bounty, None)


        BountySyncRequest.objects.create(
            github_url=issueURL,
            processed=False,
            )



    return JsonResponse(result)

# LEGAL

def terms(request):
    params = {
    }
    return TemplateResponse(request, 'legal/terms.txt', params)


def privacy(request):
    params = {
    }
    return TemplateResponse(request, 'legal/privacy.txt', params)


def cookie(request):
    params = {
    }
    return TemplateResponse(request, 'legal/cookie.txt', params)


def prirp(request):
    params = {
    }
    return TemplateResponse(request, 'legal/prirp.txt', params)


def apitos(request):
    params = {
    }
    return TemplateResponse(request, 'legal/apitos.txt', params)



