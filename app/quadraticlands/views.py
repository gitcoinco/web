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
import binascii
import hashlib
import hmac
import json
import logging
import os

from django.conf import settings
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

import requests
from ratelimit.decorators import ratelimit

from .forms import ClaimForm

logger = logging.getLogger(__name__)

# TODO - add a new envar for Token Request Siging micro service URL
# TODO - add a new envar for HMAC or other auth key for communicating with micro service 
# settings.DATABASE_URL

def index(request):
    return TemplateResponse(request, 'quadraticlands/index.html')


# ratelimit.UNSAFE is a shortcut for ('POST', 'PUT', 'PATCH', 'DELETE').
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
# @require_http_methods(["GET", "POST"])
def claim_tokens(request):
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None
   
    # if POST 
    if request.method == 'POST':
        # create a form instance and populate it with data from the request (from forms.py)
        form = ClaimForm(request.POST)

        # iterate through post keys and log them for debugging
        # for key in request.POST.keys():
        #     logger.info(f'claim_tokens post key logger: {request.POST.get(key)}')
    
        # check whether it's valid:
        if form.is_valid():
                   
            # lets log our cleaned data for debug (for now)
            logger.info(f'cleaned datas: {form.cleaned_data}')
            logger.info(f'USER ID: {user.id}')
            logger.info(f'GTC DIST KEY {settings.GTC_DIST_KEY}')  
            
            post_data = {}
            post_data['user_id'] = user.id
            post_data['user_sig'] = form.cleaned_data['user_sig']
            post_data['user_address'] = profile.preferred_payout_address
            post_data['user_amount'] = 50000000000000000000 # placeholder for amount, need to use big number 

            # create a hash of post data                
            sig = create_sha256_signature(settings.GTC_DIST_KEY, json.dumps(post_data))
            logger.info(f'POST data: {json.dumps(post_data)}')
            logger.info(f'Server side hash: { sig }')
            
            header = { 
                "X-GITCOIN-SIG" : sig,
                "content-type": "application/json",
            }
          
            # POST relevant user data to micro service that returns signed transation data for the user broadcast  
            try: 
                micro_response = requests.post(settings.GTC_DIST_API_URL, data=json.dumps(post_data), headers=header)
                micro_content = micro_response.content
                logger.info(f'micro_service_API: {micro_content}')
            except requests.exceptions.ConnectionError:
                logger.info('ConnectionError while connecting to micro_service_API!')
            except requests.exceptions.Timeout:
                # Maybe set up for a retry
                logger.info('Timeout while connecting to micro_service_API!')
            except requests.exceptions.TooManyRedirects:
                logger.info('Too many redirects while connecting to micro_service_API!')
            except requests.exceptions.RequestException as e:
                # catastrophic error. bail.
                logger.error(f'GTC Distributor - Error posting to signature service - {e}')
                there_is_a_problem = True 

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

# HMAC sig function 
def create_sha256_signature(key, message):
    '''
    Given key & message, returns HMAC digest of the message 
    '''
    try:
        byte_key = binascii.unhexlify(key)
        message = message.encode()
        return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()
    except Exception as e:
        logger.error(f'GTC Distributor - Error Hashing Message: {e}')
        return False 
