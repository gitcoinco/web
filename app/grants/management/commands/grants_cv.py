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

from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

import requests
from grants.models import Grant


class Command(BaseCommand):

    help = 'pulls data from https://twitter.com/austingriffith/status/1529825114597908484 and inserts into db'

    def handle(self, *args, **options):

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
              amount
              createdAt
            }
          }
        }
        """

        urls = []
        if not settings.DEBUG or True:
            urls += ['https://api.studio.thegraph.com/query/20308/gtc-conviction-voting-mainnet/v0.0.1']
            urls += ['https://api.thegraph.com/subgraphs/name/danielesalatti/gtc-conviction-voting-optimism']
        else:
            urls += ['https://api.thegraph.com/subgraphs/name/danielesalatti/gtc-conviction-voting-rinkeby']


        for url in urls:
            grantsResult = run_query(queryGrants, url)

            # sum amounts
            results = {}
            for result in grantsResult['data']['grants']:
                id = int(result['id'], 16)
                amount = sum([int(ele['amount']) for ele in result['votes']])
                amount = amount / 10**18
                if id not in results.keys():
                    results[id] = 0
                results[id] += amount

            # store in db
            for id, val in results.items():
                    if settings.DEBUG:
                        print(id, amount)
                    try:
                        grant = Grant.objects.get(pk=id)
                        grant.metadata['cv'] = amount
                        grant.save()
                    except Exception as e:
                        print(e)
