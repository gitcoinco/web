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
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

import requests
from eth_utils import is_address, is_checksum_address, to_checksum_address
from quadraticlands.helpers import get_initial_dist
from ratelimit.decorators import ratelimit

from .forms import ClaimForm

logger = logging.getLogger(__name__)

# TODO - add a new envar for Token Request Siging micro service URL
# TODO - add a new envar for HMAC or other auth key for communicating with micro service 
# TODO - add a new envar for CF KV url in helpers.py 


def index(request):
    '''load the main index page'''
    # initial_dist = get_initial_dist_from_CF(request)
    # objects = InitialTokenDistribution.objects.all()
    # logger.info(f'DB DUMP!: {objects}')
    context = get_initial_dist(request) 
    return TemplateResponse(request, f'quadraticlands/index.html', context)

def base(request, base):
    context = get_initial_dist(request) 
    return TemplateResponse(request, f'quadraticlands/{base}.html', context)

@login_required
def mission_index(request):
    context = get_initial_dist(request)
    return TemplateResponse(request, 'quadraticlands/mission/index.html', context)  

@login_required
def mission_base(request, mission_name):
    '''used to handle quadraticlands/<mission_name>'''
    context = get_initial_dist(request)
    logger.info(f'mission_name: {mission_name}')
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/index.html', context)

@login_required
def mission_state(request, mission_name, mission_state):
    '''quadraticlands/<mission_name>/<mission_state>'''
    context = get_initial_dist(request)
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/{mission_state}.html', context)
    
@login_required
def mission_question(request, mission_name, mission_state, question_num):
    '''Used to handle quadraticlands/<mission_name>/<mission_state>/<question_num>'''
    context = get_initial_dist(request)
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/question_{question_num}.html', context)

@login_required
def mission_answer(request, mission_name, mission_state, question_num, answer):
    '''Used to handle quadraticlands/<mission_name>/<mission_state>/<question_num>/<answer>'''
    context = get_initial_dist(request)
    return TemplateResponse(request, f'quadraticlands/mission/{mission_name}/question_{question_num}_{answer}.html', context)

# move me to helpers.py and rename claim 
# ratelimit.UNSAFE is a shortcut for ('POST', 'PUT', 'PATCH', 'DELETE').
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def claim(request):
    '''
    Receives AJAX post from CLAIM button 
    Returns JSON response from Ethereum Message Signing Service (emss)
    '''
    user = request.user if request.user.is_authenticated else None
      
    # if POST 
    if request.method == 'POST' and request.user.is_authenticated:
         
        logger.info(f'USER ID: {user.id}')
        logger.info(f'GTC DIST KEY {settings.GTC_DIST_KEY}')  
        
        post_data_to_emss = {}
        post_data_to_emss['user_id'] = user.id
       
        # confirm we received a valid, checksummed address for the token claim 
        try:
            if is_checksum_address(request.POST.get('address')):
                post_data_to_emss['user_address'] = request.POST.get('address')
            elif is_address(request.POST.get('address')):
                post_data_to_emss['user_address'] = to_checksum_address(request.POST.get('address'))
            else:
                logger.info('QuadLands: token claim address failed integrity check. No claim will be generated.')
                return JsonResponse({'error': 'Token claim address failed integrity checks.'})
        except:
            logger.error('QuadLands: There was an issue validating user wallet address.')
            return JsonResponse({'error': 'Token claim address failed validation'})
          
        # will pull token claim data from the user, this is hard coded for now 
        post_data_to_emss['user_amount'] = 1000000000000000000000 # 1000 ETH - need to use big number in units WEI 

        # create a hash of post data                
        sig = create_sha256_signature(settings.GTC_DIST_KEY, json.dumps(post_data_to_emss))
        logger.info(f'POST data: {json.dumps(post_data_to_emss)}')
        logger.info(f'Server side hash: { sig }')
        
        header = { 
            "X-GITCOIN-SIG" : sig,
            "content-type": "application/json",
        }
        
        # POST relevant user data to micro service that returns signed transation data for the user broadcast  
        try: 
            emss_response = requests.post(settings.GTC_DIST_API_URL, data=json.dumps(post_data_to_emss), headers=header)
            emss_response_content = emss_response.content
            logger.info(f'GTC Distributor: emss_response_content: {emss_response_content}')
        except requests.exceptions.ConnectionError:
            logger.info('GTC Distributor: ConnectionError while connecting to EMSS!')
        except requests.exceptions.Timeout:
            # Maybe set up for a retry
            logger.info('GTC Distributor: Timeout while connecting to EMSS!')
        except requests.exceptions.TooManyRedirects:
            logger.info('GTC Distributor: Too many redirects while connecting to EMSS!')
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            logger.error(f'GTC Distributor:  Error posting to EMSS - {e}')
            there_is_a_problem = True 

        # check response status, maybe better to use .raise_for_status()? 
        # need to streamline error response for this whole function 
        # TODO - sounds like we'll use custom quadlands 500 https://github.com/nopslip/gitcoin-web-ql/issues/23
        if emss_response.status_code == 500:
            logger.info(f'GTC Distributor: 500 received from ESMS! - This probably means there was a problem with token claim!')
            resp = {'error': 'TRUE'}
            return JsonResponse(resp)
        
        # pass returned values from eth signer microservice
        # ESM returns bytes object of json. so, we decode it
        esms_response = json.loads( emss_response_content.decode('utf-8'))
        # construct nested dict for easy access in templates

        logger.info(f'GTC Token Distributor - ESMS response: {esms_response}') 
        return JsonResponse(esms_response)
    else:
        logger.info('Non authenticated or non-POST requested sent to claim/ - request ignored!')
        return JsonResponse({'message':'request ignored!'})   


# move to helpers.py... 
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
