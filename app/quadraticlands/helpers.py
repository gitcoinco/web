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
CONTROLLER LOGIC 4 Quadratic Lands Initial Distribution--)>
*********
"""

import binascii
import hashlib
import hmac
import json
import logging
import random

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods

import requests
from dashboard.models import Profile
from eth_utils import is_address, is_checksum_address, to_checksum_address
from quadraticlands.models import (
    GTCSteward, InitialTokenDistribution, MissionStatus, QLVote, QuadLandsFAQ, SchwagCoupon,
)
from ratelimit.decorators import ratelimit

logger = logging.getLogger(__name__)

def get_FAQ(request):
    '''Get FAQ objects from the db and bundle them up to be added to faq context'''
    faq_dict = {}
    full_faq = {}
    item = {}

    try:
        faq = QuadLandsFAQ.objects.all()
    except Exception as e:
        logger.info(f'QuadLands - There was an issue getting FAQ DB object - {e}')
        faq = False

    for faq_item in faq:
        item = {
            'question' : faq_item.question,
            'answer' : faq_item.answer
        }
        faq_dict[str(faq_item.position)] = item

    full_faq['FAQ'] = faq_dict

    return full_faq

def get_profile_from_username(request):
    '''Return profile object for a given request'''
    try:
        profile = request.user.profile
    except Exception as e:
        logger.info(f'QuadLands - There was an issue getting user profile object - {e}')
        profile = False
    return profile

@require_http_methods(["GET"])
def get_mission_status(request):
    '''Retrieve mission status/state from the DB'''
    if request.user.is_authenticated:
        profile = get_profile_from_username(request)
        try:
            mission_status = MissionStatus.objects.get(profile=profile)

            completed_missions = 0
            if mission_status.proof_of_use:
                completed_missions += 1
            if mission_status.proof_of_knowledge:
                completed_missions += 1
            if mission_status.proof_of_receive:
                completed_missions += 1

            game_state = {
                "id" : mission_status.id,
                "proof_of_use" : mission_status.proof_of_use,
                "proof_of_knowledge" : mission_status.proof_of_knowledge,
                "proof_of_receive" : mission_status.proof_of_receive,
                "completed_missions": completed_missions 
            }
            return game_state
        except MissionStatus.DoesNotExist:
            pass

    # if state doesn't exist yet or user is not logged in
    no_game_state = {
        "id" : False,
        "proof_of_use" : False,
        "proof_of_knowledge" : False,
        "proof_of_receive" : False,
        "completed_missions": 0
    }
    return no_game_state


@require_http_methods(["POST"])
@login_required
#@ratelimit(key='ip', rate='50/m', method=ratelimit.UNSAFE, block=True)
def set_mission_status(request):
    '''When a mission is completed, the UI will POST here to flip game state completed True for a given mission'''
    if request.user.is_authenticated:
        try:
            mission_name = request.POST.get('mission')
            if type(mission_name) != str:
                logger.info('QuadLands - Non-string received for mission_name.')
                HttpResponse(status=404)
            elif mission_name not in ('proof_of_use', 'proof_of_knowledge','proof_of_receive'):
                logger.info(f'QuadLands - Invalid mission_name received - {mission_name}')
                HttpResponse(status=404)
        except:
            logger.info('QuadLands - Failed to parse set_mission_status')
            return HttpResponse(status=404)

        profile = get_profile_from_username(request)

        # if doesn't exist creates record
        mission = MissionStatus.objects.get_or_create(profile=profile)
        # then get the record
        mission_status = MissionStatus.objects.get(profile=profile)

        if mission_name == 'proof_of_knowledge':
            mission_status.proof_of_knowledge = True
            mission_status.save()

        if mission_name == 'proof_of_use':
            mission_status.proof_of_use = True
            mission_status.save()

        if mission_name == 'proof_of_receive':
            mission_status.proof_of_receive = True
            mission_status.save()

        resp = {'mission_status_set': 'true'}
        return JsonResponse(resp, status=200)


def get_initial_dist(request):
    '''Accpets request, returns initial dist info from the DB in units WEI & GTC'''
    no_claim = {"total_claimable_gtc": 0, "total_claimable_wei": 0}
    if not request.user.is_authenticated:
        return no_claim

    profile = get_profile_from_username(request)
    try:
        initial_dist_wei = InitialTokenDistribution.objects.get(profile=profile).claim_total
        initial_dist_gtc = initial_dist_wei / 10**18
        context = {
            'total_claimable_gtc': initial_dist_gtc,
            'total_claimable_wei': initial_dist_wei
        }
    except InitialTokenDistribution.DoesNotExist: # if user doesn't have a token claim record in DB
        context = {
            'total_claimable_gtc': 0,
            'total_claimable_wei': 0
        }
    return context

def get_initial_dist_breakdown(request):
    '''Accpets request, returns initial dist breakdown info from the DB'''
    profile = get_profile_from_username(request)

    try:
        initial_dist = InitialTokenDistribution.objects.get(profile=profile).distribution
        # logger.info(f'initial dist: {initial_dist}')
        context = {
            'active_user': int(initial_dist["active_user"]) / 10**18,
            'kernel': int(initial_dist["kernel"]) / 10**18,
            'GMV': int(initial_dist["GMV"]) / 10**18
        }
    except Exception as e: # if user doesn't have a token claim record in DB
        logger.error(f'QuadLands: Error getting initial dist: {e}')
        context = {
            'active_user': 0,
            'kernel': 0,
            'GMV': 0
        }

    return context

@login_required
@require_http_methods(["POST"])
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def vote(request):
    '''
    Receives AJAX post from vote.html with sig,r,s,v,full_vote_msg
    Saves to DB and return 200, no data expected on return
    '''
    profile = get_profile_from_username(request)
    logger.info(f'vote save profile id: {profile.id}')
    # extract POST data
    try:
        r = request.POST.get('r')
        s = request.POST.get('s')
        v = request.POST.get('v')
        sig = request.POST.get('sig')
        string_vote_msg = request.POST.get('full_vote_msg')
        full_vote_msg = json.loads(string_vote_msg)

    except Exception as e:
        logger.info(f'QuadLands: There was an error getting vote post data from user: {e}')
        resp = {'vote_save': 'error 1'}
        return JsonResponse(resp, status=400)

    # write to DB
    try:
        voted = QLVote.objects.create(profile=profile, signature=sig, vote=full_vote_msg['message'], full_msg=full_vote_msg)
    except Exception as e:
        logger.error(f'QuadLands: Error saving vote to DB - {e}')
        resp = {'vote_save': 'error 2'}
        return JsonResponse(resp, status=400)

    # all good, send 200
    resp = {'vote_save': 'success'}
    return JsonResponse(resp, status=200)

@require_http_methods(["POST"])
@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
@login_required
def claim(request):
    '''
    Receives AJAX post from CLAIM button on claim.html
    Returns JSON response (signed token claim!) from Eth Signed Message Service
    '''

    if request.user.is_impersonate:
        logger.info('QuadLands: Impersonated user sent request POSTED to /claim - highly sus - request ignored.')
        raise Http404

    profile = get_profile_from_username(request)
    logger.info(f'claim profile id: {profile.id}')

    post_data_to_emss = {}
    post_data_to_emss['user_id'] = profile.id

    # confirm we received a valid, checksummed address for the token claim
    # then add address to post_data_to_emss dict
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

    # confirm we received a valid, checksummed delegate address for the token claim
    # then add address to post_data_to_emss dict
    try:
        if is_checksum_address(request.POST.get('delegate')):
            post_data_to_emss['delegate_address'] = request.POST.get('delegate')
        elif is_address(request.POST.get('delegate')):
            post_data_to_emss['delegate_address'] = to_checksum_address(request.POST.get('delegate'))
        else:
            logger.info('QuadLands: token claim delegate_address failed integrity check. No claim will be generated.')
            return JsonResponse({'error': 'Token claim delegate failed integrity checks.'})
    except:
        logger.error('QuadLands: There was an issue validating delegate address.')
        return JsonResponse({'error': 'Token claim delegate failed validation'})

    claim = get_initial_dist(request)

    post_data_to_emss['user_amount'] = claim['total_claimable_wei']

    # create a hash of post data
    try:
        sig = create_sha256_signature(settings.GTC_DIST_KEY, json.dumps(post_data_to_emss))
    except:
        logger.error('QuadLands: Error creating hash of POST data for EMSS')
        return JsonResponse({'error': 'Hashing token claim data.'})

    header = {
        "X-GITCOIN-SIG" : sig,
        "content-type": "application/json",
    }

    # POST relevant user data to micro service that returns signed transation data for the user broadcast
    try:
        emss_response = requests.post(settings.GTC_DIST_API_URL, data=json.dumps(post_data_to_emss), headers=header)
        emss_response_content = emss_response.content
        emss_response.raise_for_status() # raise exception on error
    except requests.exceptions.ConnectionError:
        logger.error('GTC Distributor: ConnectionError while connecting to EMSS!')
        resp = {'ERROR': 'There was an issue getting token claim.'}
        return JsonResponse(resp, status=503)
    except requests.exceptions.Timeout:
        # Maybe set up for a retry
        logger.error('GTC Distributor: Timeout while connecting to EMSS!')
        resp = {'ERROR': 'There was an issue getting token claim.'}
        return JsonResponse(resp, status=408)
    except requests.exceptions.TooManyRedirects:
        logger.error('GTC Distributor: Too many redirects while connecting to EMSS!')
        resp = {'ERROR': 'There was an issue getting token claim.'}
        return JsonResponse(resp, status=400)
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        logger.error(f'GTC Distributor:  Error posting to EMSS - {e}')
        resp = {'ERROR': 'There was an issue getting token claim.'}
        return JsonResponse(resp, status=400)

    # pass returned values from eth signer microservice
    # ESMS returns bytes object of json. so, we decode it
    esms_response = json.loads( emss_response_content.decode('utf-8'))

    logger.debug(f'GTC Token Distributor - ESMS response: {esms_response}')
    return JsonResponse(esms_response)

def create_sha256_signature(key, message):
    '''Given key & message, returns HMAC digest of the message'''
    try:
        byte_key = binascii.unhexlify(key)
        message = message.encode()
        return hmac.new(byte_key, message, hashlib.sha256).hexdigest().upper()
    except Exception as e:
        logger.error(f'GTC Distributor - Error Hashing Message: {e}')
        return False

def get_stewards():
    '''Return stewards for a given request'''
    steward_dict = {}
    full_stewards = {}
    steward = {}
    try:
        # grab the stewards
        raw_stewards = GTCSteward.objects.all()
        # loop through querySet
        for s in raw_stewards:
            steward = {
                'profile' : s.profile,
                'real_name' : s.real_name,
                'bio': s.bio,
                'gtc_address' : s.gtc_address,
                'profile_link' : s.profile_link,
                'custom_steward_img': s.custom_steward_img
            }
            # add to dict
            steward_dict[str(s.profile)] = steward

        # randomize order of stewards
        steward_list = list(steward_dict.items())
        random.shuffle(steward_list)
        steward_dict = dict(steward_list)

        # one more dict for easy interation on UI
        full_stewards['stewards'] = steward_dict
        return full_stewards

    except Exception as e:
        stewards = {'stewards' : False}
        logger.info(f'QuadLands - There was an issue getting stewards from the DB - {e}')
        return stewards



def get_coupon_code(request):
    '''Return coupon code if user has completed missions and has claimable GTC'''

    coupon_code = None
    initial_dist, game_status = get_initial_dist(request), get_mission_status(request)
    print(initial_dist)
    total_claimable_gtc = initial_dist['total_claimable_gtc']
    profile = get_profile_from_username(request)

    # check to ensure user has completeg missions and has gtc to claim
    if game_status['completed_missions'] < 3 or total_claimable_gtc == 0:
        return coupon_code

    # return coupon code is user already has been assigned
    coupon = SchwagCoupon.objects.filter(profile=profile).first()
    if coupon:
        return coupon.coupon_code

    total_claimable_gtc = total_claimable_gtc / (10 ** 18)

    # fetch empty coupons
    coupons = SchwagCoupon.objects.filter(profile__isnull=True)
    # assign coupon code based on claimable GTC tokens 
    if total_claimable_gtc < 50:
        # 20% coupon
        coupon = coupons.filter(discount_type='20_off').first()

    elif total_claimable_gtc < 1000:
        # 40% coupon
        coupon = coupons.filter(discount_type='40_off').first()

    else:
        # 60% coupon
        coupon = coupons.filter(discount_type='60_off').first()

    if coupon:
        coupon.profile = profile
        coupon.save()
    
    return coupon.coupon_code
