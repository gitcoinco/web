# -*- coding: utf-8 -*-
"""

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
import time
from decimal import *

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import requests
from grants.models import Grant
from web3 import Web3


class Command(BaseCommand):

    help = 'pulls data from https://twitter.com/austingriffith/status/1529825114597908484 and inserts into db'

    def handle(self, *args, **options):

        class DecimalEncoder(json.JSONEncoder):
            def default(self, obj):
                # 👇️ if passed in object is instance of Decimal
                # convert it to a string
                if isinstance(obj, Decimal):
                    return str(obj)
                # 👇️ otherwise use the default behavior
                return json.JSONEncoder.default(self, obj)

        def run_query(q, url):
            request = requests.post(url,
                                    '',
                                    json={'query': q})
            if request.status_code == 200:
                return request.json()
            else:
                raise Exception('Query failed. return code is {}.      {}'.format(request.status_code, query))

        queryGrants = """
            query getGrants {
                grants(orderBy: id, orderDirection: asc, first: 100) {
                    id
                    votes {
                    id
                    amount
                    createdAt
                    }
                    releases {
                    id
                    voteId
                    amount
                    createdAt
                    }
                }
            }
        """

        urls = []
        if not settings.DEBUG or True:
            urls += ['https://api.studio.thegraph.com/query/20308/gtc-conviction-voting-mainnet/v0.0.2']
            urls += ['https://api.thegraph.com/subgraphs/name/danielesalatti/gtc-conviction-voting-optimism']
        else:
            urls += ['https://api.thegraph.com/subgraphs/name/danielesalatti/gtc-conviction-voting-rinkeby']


        maxMultiplier = 50
        secondsInSixMonths = 60 * 60 * 24 * 30 * 6
        alphaDecay = 0.8
        beta = pow(maxMultiplier, 1 / secondsInSixMonths) - 1

        def mapReleasesToVoteId(grant):
            releases = grant['releases']
            releaseByVoteId = {}
            for release in releases:
                releaseByVoteId[int(release['voteId'])] = release
            return releaseByVoteId

        def calculate_voting_power(grant):
            totalVotingPower = 0

            releaseByVoteId = mapReleasesToVoteId(grant)

            for vote in grant['votes']:
                secondsSinceVote = (time. time() - int(vote['createdAt']))

                secondsSinceRelease = 0

                voteIdInt = int(vote['id'], 16)

                if (voteIdInt in releaseByVoteId):
                    secondsSinceRelease = (time. time() - int(releaseByVoteId[voteIdInt]['createdAt']))
                    secondsSinceVote = secondsSinceVote - secondsSinceRelease

                
                secondsSinceVote = min(secondsSinceVote, secondsInSixMonths)

                votingPower = Web3.fromWei(int(vote['amount']), 'ether') * Decimal(pow(1 + beta, secondsSinceVote))

                for i in range(0, int(secondsSinceRelease)):
                    votingPower = votingPower - Decimal(((1 - alphaDecay) / (24 * 60 * 60))) * votingPower
                
                totalVotingPower = totalVotingPower + votingPower
            
            return totalVotingPower

        grantVotingPower = {}

        for url in urls:
            grantsResult = run_query(queryGrants, url)
            grants = grantsResult['data']['grants']
            for grant in grants:
                grantId = int(grant['id'], 16)
                vp = calculate_voting_power(grant)
                if grantId not in grantVotingPower:
                    grantVotingPower[grantId] = vp
                else:
                    grantVotingPower[grantId] = grantVotingPower[grantId] + vp


        for grantId in grantVotingPower:
            # store in db
            if settings.DEBUG:
                print("Grant ID: " + str(grantId) + " Voting Power: " + str(grantVotingPower[grantId]))
            try:
                grant = Grant.objects.get(pk=grantId)
                grant.metadata['cv'] = json.dumps(grantVotingPower[grantId], cls=DecimalEncoder)
                grant.save()
            except Exception as e:
                print("Error:", e)
