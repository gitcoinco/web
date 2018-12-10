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
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Tip, Bounty, BountyFulfillment 
from kudos.models import KudosTransfer

def standardize(username):
    import re
    
    if not username:
        return ""
    _str = "user_" + username.replace('@','').lower().replace("-", "_").replace(" ", "_").replace(' ','').replace('.','');
    return re.sub(r'\W+', '', _str)

class Command(BaseCommand):

    help = 'exports data for https://github.com/davidpiegza/Graph-Visualization'

    def handle(self, *args, **options):

        # config
        onlyshowuserswithedges = True
        show = 'all'

        bountiesfulfillments = BountyFulfillment.objects.filter(bounty__network='mainnet')
        bounties = Bounty.objects.filter(network='mainnet')

        edges = []
        usernames = []
        if show in ['all', 'bounties']:
            usernames += bounties.values_list('bounty_owner_github_username', flat=True)
            usernames += bountiesfulfillments.values_list('fulfiller_github_username', flat=True)
            edges += bountiesfulfillments.values_list('fulfiller_github_username', 'bounty__bounty_owner_github_username')

        ca_objs = []
        if show in ['all', 'tips']:
            ca_objs += [Tip]
        if show in ['all', 'kudos']:
            ca_objs += [KudosTransfer]
        for ca in ca_objs:
            cas = ca.objects.filter(network='mainnet')
            usernames += cas.values_list('username', flat=True)
            usernames += cas.values_list('from_username', flat=True)
            edges += cas.values_list('username', 'from_username')

        if onlyshowuserswithedges:
            usernames = []
            for edge in edges:
                usernames += [edge[0]]
                usernames += [edge[1]]


        i = 0;
        for username in list(set(usernames)):
            if not username:
                continue
            username = standardize(username)
            print(f"  var {username} = new GRAPHVIS.Node({i}); {username}.data.title = \"{username}\";  graph.addNode({username}); drawNode({username}); ")
            i += 1

        for edge in edges:
            username1 = standardize(edge[0])
            username2 = standardize(edge[1])
            if not username1 or not username2:
                continue
            print(f"  graph.addEdge({username1}, {username2}); drawEdge({username1}, {username2}); ")



