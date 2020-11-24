# -*- coding: utf-8 -*-
"""Handle marketing mail related tests.

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


"""
*********
CONTROLLER LOGIC 4 Quadratic Lands --)> 
*********
"""


import binascii
import hashlib
import hmac
import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

import requests
from eth_utils import is_address, is_checksum_address, to_checksum_address
from quadraticlands.models import InitialTokenDistribution, MissionStatus
from ratelimit.decorators import ratelimit

# from django.shortcuts import redirect # TODO - implement this for redirect on GET to claim 

logger = logging.getLogger(__name__)

@require_http_methods(["GET"])
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def get_mission_status(request):
    '''Retrieve mission status/state from the DB'''
    if request.user.is_authenticated:
        user = request.user
        mission_status = MissionStatus.objects.get(profile_id=user.id)
        game_state = {
            "id" : mission_status.id,
            "proof_of_use" : mission_status.proof_of_use,
            "proof_of_knowledge" : mission_status.proof_of_knowledge,
            "proof_of_receive" : mission_status.proof_of_receive,
        }
        return game_state
    else:
        no_game_state = {
            "id" : 0,
            "proof_of_use" : False,
            "proof_of_knowledge" : False,
            "proof_of_receive" : False
        }
        return no_game_state


@require_http_methods(["POST"])
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def set_mission_status(request):
    '''when a mission is completed, UI will POST here so we can save new game state'''
    if request.user.is_authenticated:
        user = request.user if request.user.is_authenticated else None
        # this could probably be improved, just make sure we're not getting anything sketchy from POST   
        try: 
            mission_name = request.POST.get('mission')
            if type(mission_name) != str:
                logger.info('QuadLands - Non-string received for mission_name.')
                HttpResponse(status=404)
            elif mission_name != 'proof_of_use' or mission_name != 'proof_of_knowledge' or mission_name != 'proof_of_receive':
                logger.info('QuadLands - Invalid mission_name received.')
                HttpResponse(status=404)
        except:
            logger.info('QuadLands - Failed to parse set_mission_status')
            return HttpResponse(status=404)
        
        mission_status = MissionStatus.objects.get(profile_id=user.id)
        
        if mission_name == 'proof_of_knowledge':
            mission_status.proof_of_knowledge = True  
            mission_status.save() 
            return HttpResponse(status=200)
        
        if mission_name == 'proof_of_use': 
            mission_status.proof_of_use = True
            mission_status.save()
            return HttpResponse(status=200)
        
        if mission_name == 'proof_of_receive': 
            mission_status.proof_of_receive = True
            mission_status.save()
            return HttpResponse(status=200)
        

def get_initial_dist(request):
    '''retrieve initial dist info from the DB'''
    if request.user.id == None:
        return {'total_claimable': 0}
    # user_id = 0 should be replaced with user_id = request.user.id once the DB has more data 
    initial_dist = InitialTokenDistribution.objects.get(profile_id=request.user.id).num_tokens
    context = {'total_claimable': initial_dist}
    return context

def get_initial_dist_from_CF(request):
    '''hit the CF KV pairs list and return user claim data. currently unused 
       TODO compare with InitialClaim results as a 2fa check, if error, block claim 
    '''
    if request.user.id == None:
        return {"total_claimable": 0}

    # hit the graph and confirm/deny user has made a claim

    # maybe this URL should be an envar? 
    url=f'https://js-initial-dist.orbit-360.workers.dev/?user_id={request.user.id}'
    try:
        r = requests.get(url,timeout=3)
        r.raise_for_status()

    except requests.exceptions.HTTPError as errh:
        logger.error("Quadratic Lands - Error on request:",errh)
    except requests.exceptions.ConnectionError as errc:
        logger.error("Quadratic Lands - Error on request:",errc)
    except requests.exceptions.Timeout as errt:
        logger.error("Quadratic Lands - Error on request:",errt)
    except requests.exceptions.RequestException as err:
        logger.error("Quadratic Lands - Error on request:",err)

    res = json.loads(r.text)
    
    context = {
        'total_claimable': res[0],
        'bucket_0': res[2][0],
        'bucket_1': res[2][1],
        'bucket_2': res[2][2],
        'bucket_3': res[2][3],
        'bucket_4': res[2][4],
        'bucket_5': res[2][5]
    }

    return context

@require_http_methods(["POST"])
@login_required
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def claim(request):
    '''
    Receives AJAX post from CLAIM button 
    Returns JSON response from Ethereum Message Signing Service (emss)
    '''
    user = request.user if request.user.is_authenticated else None
      
    # if POST, can be removed nowt hat this view is POSt only
    if request.method == 'POST' and request.user.is_authenticated:
         
        logger.info(f'USER ID: {user.id}')
                    
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
          
        claim = get_initial_dist(request)
        logger.info(f"debug claim amount - claim.total_claimable: {claim['total_claimable']}")
        post_data_to_emss['user_amount'] = claim['total_claimable']
        # post_data_to_emss['user_amount'] = 1000000000000000000000 # 1000 ETH - need to use big number in units WEI
         
        # create a hash of post data                
        sig = create_sha256_signature(settings.GTC_DIST_KEY, json.dumps(post_data_to_emss))
        # logger.debug(f'POST data: {json.dumps(post_data_to_emss)}')
        # logger.debug(f'Server side hash: { sig }')
        
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
            there_is_a_problem = True # TODO - fix this

        # check response status, maybe better to use .raise_for_status()? 
        # need to streamline error response for this whole function 
        # TODO - sounds like we'll use custom quadlands 500 https://github.com/nopslip/gitcoin-web-ql/issues/23
        if emss_response.status_code != 200:
            logger.info(f'GTC Distributor: non-200 received from ESMS! - This probably means there was a problem with token claim!')
            resp = {'error': 'TRUE'}
            return JsonResponse(resp)
        
        # pass returned values from eth signer microservice
        # ESM returns bytes object of json. so, we decode it
        esms_response = json.loads( emss_response_content.decode('utf-8'))
        # construct nested dict for easy access in templates

        logger.info(f'GTC Token Distributor - ESMS response: {esms_response}') 
        return JsonResponse(esms_response)
    else:
        # TODO Make this redirect to token claim page I think 
        logger.info('Non authenticated or non-POST requested sent to claim/ - request ignored!')
        # raise Http404
        return JsonResponse({'UNDERGROUND':'QUAD LANDS 4-0-4'})   


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
