'''
    Copyright (C) 2019 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation,either version 3 of the License,or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not,see <http://www.gnu.org/licenses/>.

'''
import re

from django.conf import settings
from django.core.management.base import BaseCommand


def is_an_edge(handle, edges):
    for edge in edges:
        if handle == edge[0]:
            return True
        if handle == edge[1]:
            return True
    return False

def normalize_handle(handle):
    return re.sub(r'\W+', '', handle)

class Command(BaseCommand):

    help = 'exports graph visualizations for http://experiments.owocki.com/Graph-Visualization/all/simple_graph.js:L157'

    def handle(self, *args, **options):
        handles = []
        edges = []

        from dashboard.models import BountyFulfillment
        for obj in BountyFulfillment.objects.filter(accepted=True):
            handle1 = obj.bounty.bounty_owner_github_username
            handle2 = obj.fulfiller_github_username
            handles.append(handle1)
            handles.append(handle2)
            edges.append([handle1, handle2])

        from dashboard.models import Tip
        for obj in Tip.objects.filter(network='mainnet'):
            handle1 = obj.from_username
            handle2 = obj.username
            handles.append(handle1)
            handles.append(handle2)
            edges.append([handle1, handle2])

        from kudos.models import KudosTransfer
        for obj in KudosTransfer.objects.filter(network='mainnet'):
            handle1 = obj.from_username
            handle2 = obj.username
            handles.append(handle1)
            handles.append(handle2)
            edges.append([handle1, handle2])

        from grants.models import Contribution
        for obj in Contribution.objects.filter(subscription__network='mainnet'):
            handle1 = obj.subscription.grant.admin_profile.handle
            handle2 = obj.subscription.contributor_profile.handle
            handles.append(handle1)
            handles.append(handle2)
            edges.append([handle1, handle2])

        handles = set(handles)
        handles = [handle for handle in handles if is_an_edge(handle, edges)]

        counter = 1
        for handle in handles:
            if handle:
                handle = normalize_handle(handle)
                counter += 1
                print(f'var user_{handle} = new GRAPHVIS.Node({counter}); user_{handle}.data.title = "user_{handle}";  graph.addNode(user_{handle}); drawNode(user_{handle});')

        for edge in edges:
            handle1 = edge[0]
            handle2 = edge[1]
            handle1 = normalize_handle(handle1)
            handle2 = normalize_handle(handle2)
            if handle1 and handle2:
                print(f"graph.addEdge(user_{handle1}, user_{handle2}); drawEdge(user_{handle1}, user_{handle2}); ");
