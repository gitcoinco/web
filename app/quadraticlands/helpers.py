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

import json
import logging

import requests
from quadraticlands.models import InitialTokenDistribution

logger = logging.getLogger(__name__)

def get_initial_dist(request):
    '''retrieve initial dist info from the DB'''
    if request.user.id == None:
        return {'total_claimable': 0}
    # user_id = 0 should be replaced with user_id = request.user.id once the DB has more data 
    initial_dist = InitialTokenDistribution.objects.get(user_id=0).num_tokens
    context = {'total_claimable': initial_dist}
    return context


def get_initial_dist_from_CF(request):
    '''hit the CF KV pairs list and return user claim data. 
       this has been tabled for now. maybe will be used 
       as backup to confirm/deny dist amounts are correct 
    '''
    if request.user.id == None:
        return False

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
