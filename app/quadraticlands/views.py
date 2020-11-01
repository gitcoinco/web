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
from eth_utils import is_checksum_address, is_normalized_address, to_checksum_address
from ratelimit.decorators import ratelimit

from .forms import ClaimForm

logger = logging.getLogger(__name__)

# TODO - add a new envar for Token Request Siging micro service URL
# TODO - add a new envar for HMAC or other auth key for communicating with micro service 


# @Richard, please feel free to adjust these as necessary. 
# This is mostly a matter of preference and I don't know what you prefer 
# it's worth note, these do not denote the URI path for user, but just where the files live in our app 
# the URIs from a user perspective are defined in urls.py ;) 

def index(request):
    return TemplateResponse(request, 'quadraticlands/index.html')

def about(request):
    return TemplateResponse(request, 'quadraticlands/about.html')

def terms(request):
    return TemplateResponse(request, 'quadraticlands/terms-of-service.html')

def privacy(request):
    return TemplateResponse(request, 'quadraticlands/privacy.html')

def faq(request):
    return TemplateResponse(request, 'quadraticlands/faq.html')

def dashboard(request):
    return TemplateResponse(request, 'quadraticlands/dashboard.html')

def mission(request):
    return TemplateResponse(request, 'quadraticlands/mission/index.html')   

def mission_knowledge_index(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/index.html')
    
def mission_knowledge_intro(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/intro.html')

def mission_knowledge_question_1(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_1.html')

def mission_knowledge_question_1_right(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_1_right.html')

def mission_knowledge_question_1_wrong(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_1_wrong.html')    

def mission_knowledge_question_1_timeout(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_1_timeout.html')    

def mission_knowledge_question_2(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_2.html')

def mission_knowledge_question_2_right(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_2_right.html')

def mission_knowledge_question_2_wrong(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_2_wrong.html')    

def mission_knowledge_question_2_timeout(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/question_2_timeout.html')   

def mission_knowledge_outro(request):
    return TemplateResponse(request, 'quadraticlands/mission/knowledge/outro.html')   

def mission_recieve_index(request):
    return TemplateResponse(request, 'quadraticlands/mission/recieve/index.html')   

def mission_revieve_claim(request):
    return TemplateResponse(request, 'quadraticlands/mission/recieve/claim.html')   

def mission_revieve_claiming(request):
    return TemplateResponse(request, 'quadraticlands/mission/recieve/claiming.html')  

def mission_revieve_claimed(request):
    return TemplateResponse(request, 'quadraticlands/mission/recieve/claimed.html') 

def mission_recieve_outro(request):
    return TemplateResponse(request, 'quadraticlands/mission/recieve/outro.html')   

def mission_use_index(request):
    return TemplateResponse(request, 'quadraticlands/mission/use/index.html')  

def mission_use_snapshot(request):
    return TemplateResponse(request, 'quadraticlands/mission/use/snapshot.html') 

def mission_use_outro(request):
    return TemplateResponse(request, 'quadraticlands/mission/use/outro.html')   

def mission_end(request):
    return TemplateResponse(request, 'quadraticlands/mission/end.html')   


def demo2(request):
    
    user = request.user if request.user.is_authenticated else None
    if user: # is logged in  
        profile = request.user.profile if user and hasattr(request.user, 'profile') else None
   
        try: 
            payout_address = request.user.profile.preferred_payout_address
        except:
            logger.info('QuadraticLands: - User does not have a preferred_payout_address set')
            payout_address = None 

        # testing if user payout addy isn't set in Gitcoin web 
        # payout_address = None
        context = {
                'title': _('Claim GTC'),
                'profile': profile,
                'payout_address' : payout_address
            }
        return TemplateResponse(request, 'quadraticlands/demo2.html', context)
    
    else: # user is not logged in
        context = {
                'title': _('Claim GTC')
            }
        return TemplateResponse(request, 'quadraticlands/demo2.html', context)

# used for testing generic getFetch POSTs from client side JS
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def testPost(request):
            logger.info(f'successfully called testPost')
            resp = {'payload': 'example'}
            return JsonResponse(resp)


# ratelimit.UNSAFE is a shortcut for ('POST', 'PUT', 'PATCH', 'DELETE').
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def claim2(request):
    '''
    Receives AJAX post from CLAIM button 
    Returns JSON response from Ethereum Message Signing Service (emss)
    '''
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None
      
    # if POST 
    if request.method == 'POST' and request.user.is_authenticated:
         
        logger.info(f'USER ID: {user.id}')
        logger.info(f'GTC DIST KEY {settings.GTC_DIST_KEY}')  
        
        post_data_to_emss = {}
        post_data_to_emss['user_id'] = user.id
       

        # IMPORTANT - below is the current central source of truth for address on claim 
        # if user profile address is not set, then we will take the 'address' value 
        # submitted along with a ajax post to /claim2 - 
        # if no address in post and no profile addy then we dont have an addy for the user
        # user claim will return error 
        # feature tracked here - https://github.com/nopslip/gitcoin-web-ql/issues/21
                  
        # if a primary user active wallet address was supplied
        # then we will make sure that it's a checksum'd eth address

        if request.POST.get('address'):
            try:
                if is_checksum_address(request.POST.get('address')):
                    primary_wallet_address = request.POST.get('address')
                elif is_normalized_address(request.POST.get('address')):
                    primary_wallet_address = to_checksum_address(request.POST.get('address'))
                else:
                    primary_wallet_address = None 
                    logger.info('QuadLands: Primary wallet address failed integrity checks')
            except:
                logger.error('QuadLands: There was an issue intreperting user wallet address!')
                
        try:         
            post_data_to_emss['user_address'] = profile.preferred_payout_address
            payout_address = True
            # TODO - this should be sanitized before passing directly to the EMSS as this should be considered un-trusted user supplied data
        except: 
            logger.info('QuadraticLands - No preferred_payout_address set for user!')
            payout_address = None 

        if not payout_address: 
        
            try: 
                post_data_to_emss['user_address'] = primary_wallet_address
            except:
                logger.error('QuadLands: Cannot find an address for the user claim!')
                return JsonResponse({'error': 'no address found for user!'})

        
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
        logger.info('Non authenticated or non-POST requested sent to claim2/ - request ignored!')
        return JsonResponse({'message':'request ignored!'})   


# @Richard please don't adjust anything below here without talking to me first 
# @require_http_methods(["GET", "POST"]) --> not working as likely not used by gitcoin.co app?
# ratelimit.UNSAFE is a shortcut for ('POST', 'PUT', 'PATCH', 'DELETE').
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def claim(request):
    '''
    Used for GTC Token claim
    '''
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None
   
    # if POST 
    if request.method == 'POST' and request.user.is_authenticated:
        # create a form instance and populate it with data from the request (from forms.py)
        # form = ClaimForm(request.POST)
         
        # iterate through post keys and log them for debugging
        # for key in request.POST.keys():
        #     logger.info(f'claim_tokens post key logger: {request.POST.get(key)}')
                
        # lets log our cleaned data for debug (for now)
        # logger.info(f'cleaned datas: {form.cleaned_data}')
        logger.info(f'USER ID: {user.id}')
        logger.info(f'GTC DIST KEY {settings.GTC_DIST_KEY}')  
        
        post_data = {}
        post_data['user_id'] = user.id
        
        # temp fix for handling case where user doens't have default address set in their profile, use my rinkeby addy :) 
        if not profile.preferred_payout_address:
            post_data['user_address'] = '0x8e9d312F6E0B3F511bb435AC289F2Fd6cf1F9C81'
        else:
            post_data['user_address'] = profile.preferred_payout_address
        
        post_data['user_amount'] = 1000000000000000 # placeholder for amount, need to use big number 

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

        # check response status, maybe better to use .raise_for_status()? 
        # maybe need context on return here too?
        if micro_response.status_code == 500:
            logger.info(f'500 received from ESMS! - This probably means there was a problem with token claim!')
            return TemplateResponse(request, 'quadraticlands/demo.html')
        
        # pass returned values from eth signer microservice
        # ESM returns bytes object of json. so, we decode it
        esms_response = json.loads( micro_content.decode('utf-8'))
        # construct nested dict for easy access in templates
        
        ''' This would simplify template side a bit but I wasn't able to get access to the objects via js 
        esms_response = {
            "esms" : {
                "user_id" : esms_decoded_response["user_id"],
                "user_account" : esms_decoded_response["user_address"],
                "user_amount" : esms_decoded_response["user_amount"],
                "msg_hash_hex" : esms_decoded_response["msg_hash_hex"],
                "eth_signed_message_hash_hex" : esms_decoded_response["eth_signed_message_hash_hex"],
                "eth_signed_signature_hex" : esms_decoded_response["eth_signed_signature_hex"],
            }
        }
        '''
        logger.info(f'GTC Token Distributor - ESMS response: {esms_response}') 
        return TemplateResponse(request, 'quadraticlands/demo.html', context=esms_response)
            

    # if GET 
    else:
        # from forms.py 
        form = ClaimForm()
        
        context = {
            'title': _('Claim GTC'),
            'profile': profile,
            'user' : user,
            'form' : form,
        }
       
        return TemplateResponse(request, 'quadraticlands/demo.html', context)


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
