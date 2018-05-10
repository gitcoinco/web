# -*- coding: utf-8 -*-
"""Define the EthOS views.

Copyright (C) 2018 Gitcoin Core

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

import base64
import json

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

import matplotlib
import networkx as nx
import numpy as np
import pandas as pd
import twitter
from ethos.models import Hop, ShortCode, TwitterProfile
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import HTTPProvider, Web3

from .exceptions import DuplicateTransactionException

matplotlib.use('Agg')



w3 = Web3(HTTPProvider(settings.WEB3_HTTP_PROVIDER))

abi = json.loads(
    '[{"constant":true,"inputs":[],"name":"mintingFinished","outputs":[{"name":"","type":"bool"}],'
    '"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],'
    '"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view",'
    '"type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},'
    '{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],'
    '"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],'
    '"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from",'
    '"type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],'
    '"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,'
    '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals",'
    '"outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},'
    '{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_amount","type":"uint256"}],'
    '"name":"mint","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable",'
    '"type":"function"},{"constant":true,"inputs":[],"name":"version","outputs":[{"name":"",'
    '"type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,'
    '"inputs":[{"name":"_spender","type":"address"},{"name":"_subtractedValue","type":"uint256"}],'
    '"name":"decreaseApproval","outputs":[{"name":"","type":"bool"}],"payable":false,'
    '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner",'
    '"type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],'
    '"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],'
    '"name":"finishMinting","outputs":[{"name":"","type":"bool"}],"payable":false,'
    '"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner",'
    '"outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view",'
    '"type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"",'
    '"type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,'
    '"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer",'
    '"outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable",'
    '"type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},'
    '{"name":"_addedValue","type":"uint256"}],"name":"increaseApproval","outputs":[{"name":"",'
    '"type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,'
    '"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],'
    '"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,'
    '"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner",'
    '"type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,'
    '"stateMutability":"nonpayable","type":"function"},{"payable":false,"stateMutability":"nonpayable",'
    '"type":"fallback"},{"anonymous":false,"inputs":[{"indexed":true,"name":"to","type":"address"},'
    '{"indexed":false,"name":"amount","type":"uint256"}],"name":"Mint","type":"event"},'
    '{"anonymous":false,"inputs":[],"name":"MintFinished","type":"event"},{"anonymous":false,'
    '"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,'
    '"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},'
    '{"anonymous":false,"inputs":[{"indexed":true,"name":"owner","type":"address"},{"indexed":true,'
    '"name":"spender","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],'
    '"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"from",'
    '"type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value",'
    '"type":"uint256"}],"name":"Transfer","type":"event"}]')

# Instantiate EthOS contract
try:
    contract = w3.eth.contract(Web3.toChecksumAddress(settings.ETHOS_CONTRACT_ADDRESS), abi=abi)
except Exception:
    contract = None


def render_graph(request):
    matplotlib.use('Agg')
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt
    nodes_labels = {}
    nodes_images = {}

    # Maybe a pandas dataframe from the values_list of our QS would work better?
    # df = pd.DataFrame(hops.values_list('previous_hop', 'twitter_profile'))

    hops = Hop.objects.select_related('previous_hop', 'previous_hop__twitter_profile', 'twitter_profile').all()
    graph = nx.star_graph(hops.count())
    hops_list = list(hops.values_list('id', flat=True))
    for i, hop in enumerate(hops):
        try:
            profile_image = mpimg.imread(hop.twitter_profile.profile_picture.file)
            twitter_username = hop.twitter_profile.username
            nodes_labels[i] = twitter_username
            nodes_images[i] = profile_image
            graph.add_node(i, image=profile_image, label=twitter_username)
            print('\nNODES AFTER GRAPH ADD NODE: ', graph.nodes(data=True), '\n\n')
            graph.node[i]['image'] = profile_image
            graph.node[i]['label'] = twitter_username
            print('\nNODES AFTER GRAPH MANUAL NODE: ', graph.nodes(data=True), '\n\n')
            if i != 0:
                if hop and hop.previous_hop:
                    time_lapsed = round((hop.created_on - hop.previous_hop.created_on).total_seconds()/60)
                    if 0 < time_lapsed < 30:
                        distance = time_lapsed * 10
                    else:
                        distance = 300
                    distance = 5
                    previous_hop = hops_list.index(hop.previous_hop.id)
                    graph.add_edge(previous_hop, i, color='gray', edge_color='gray', arrowstyle='->', arrowsize=10, length=distance)
        except:
            pass

    M = graph.number_of_edges()
    pos = nx.spring_layout(graph)
    print('POS: ', pos)
    fig = plt.figure(figsize=(10, 10))
    print('FIG: ', fig)
    ax = plt.subplot(111)
    print('AX: ', ax)
    ax.set_aspect('equal')
    print('AX: ', ax)
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    nx.draw_networkx_edges(graph, pos, ax=ax)
    nx.draw_networkx_labels(graph, pos=pos, labels=nodes_labels)

    trans = ax.transData.transform
    trans2 = fig.transFigure.inverted().transform
    avatar_image_size = 0.04  # this is the image size
    p2 = avatar_image_size / 2.0
    for n in graph:
        # Plop images on top of nodes.
        xx, yy = trans(pos[n])  # Grab the figure coordinates.
        xa, ya = trans2((xx, yy))  # Grab the axes coordinates.
        a = plt.axes([xa-p2, ya-p2, avatar_image_size, avatar_image_size])
        a.set_aspect('equal')
        try:
            a.imshow(graph.node[n]['image'])
        except:
            pass
        a.axis('off')
    nx.draw(graph)
    print('GRAPH: ', graph)
    plt.savefig('graph_test.png', format='PNG')
    with open('graph_test.png', "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")


def graphzz(request):
    # Just a random graph with below data as an example.
    import matplotlib.pyplot as plt
    nodes = [0, 1, 2, 3]

    edges_dicts = [
        {'length': 200},
        {'length': 50},
        {'length': 100},
    ]
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
    ]
    G = nx.DiGraph()
    # G.add_nodes_from(nodes)
    for node in nodes:
        G.add_node(node, label='derp')
    for i, edge in enumerate(edges):
        G.add_edge(edge[0], edge[1], length=edges_dicts[i])
    # G.add_edges_from(edges)
    M = G.number_of_edges()
    pos = nx.layout.spectral_layout(G)
    nx.draw_networkx_labels(G, pos=pos, labels={0: 'derp', 1: 'dingo', 2: 'flash', 3: 'derpy'})

    nodes = nx.draw_networkx_nodes(G, pos, node_size=25, node_color='green', with_labels=True)
    edges = nx.draw_networkx_edges(G, pos, node_size=25, arrowstyle='->',
                                   arrowsize=10, edge_color='gray', width=2, with_labels=True)
    plt.savefig('test.png', format='png')
    with open('test.png', "rb") as f:
        return HttpResponse(f.read(), content_type="image/png")


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def redeem_coin(request, shortcode):
    """Redeem an EthOS coin.

    Args:
        shortcode (str): The EthOS unique shortcode.

    Returns:
        JsonResponse: The redemption status in JSON format, if request.body is present.
        TemplateResponse: The templated response, if no request.body is present.

    """
    if request.body:
        status = 'OK'

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        try:
            address = body.get('address')
            username = body.get('username')

            if not username or not address:
                raise Http404

            twitter_profile, __ = TwitterProfile.objects.prefetch_related('hops').get_or_create(username=username)
            ethos = ShortCode.objects.get(shortcode=shortcode)
            user_hop = Hop.objects.select_related('twitter_profile') \
                .filter(
                    shortcode=ethos,
                    twitter_profile=twitter_profile,
                    web3_address=address,
                ).order_by('-id').first()

            # Restrict same user from redeeming the same coin within 30 minutes
            if user_hop and (timezone.now() - user_hop.created_on).total_seconds() < 1800:
                raise DuplicateTransactionException(_('Duplicate transaction detected'))

            # Number of EthOS tokens = 30 - number of minutes lapsed between the hop. Minimum = 5
            n = 30

            previous_hop = Hop.objects.select_related('shortcode').filter(shortcode=ethos).order_by('-id').first()
            if previous_hop:
                time_lapsed = round((timezone.now() - previous_hop.created_on).total_seconds()/60)
                n = 5

                if time_lapsed < 25:
                    n = 30 - time_lapsed

            address = Web3.toChecksumAddress(address)

            tx = contract.functions.transfer(address, n * 10**18).buildTransaction({
                'nonce': w3.eth.getTransactionCount(settings.ETHOS_ACCOUNT_ADDRESS),
                'gas': 100000,
                'gasPrice': recommend_min_gas_price_to_confirm_in_time(1) * 10**9
            })

            signed = w3.eth.account.signTransaction(tx, settings.ETHOS_ACCOUNT_PRIVATE_KEY)
            message = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

            Hop.objects.create(
                shortcode=ethos,
                ip=get_ip(request),
                created_on=timezone.now(),
                txid=message,
                web3_address=address,
                twitter_profile=twitter_profile,
                previous_hop=previous_hop
            )

            ethos.num_scans += 1
            ethos.save()

            # TODO: Send `this coin has been shared <num_scans> times. The top coin has been shared <num_scans> times`

            nodes = []
            edges = []

            # construct json for the graph viz
            for h in Hop.objects.select_related('previous_hop', 'previous_hop__twitter_profile').all():
                node = {
                    'name': h.twitter_profile.username,
                    'img': h.twitter_profile.profile_picture.url
                }

                try:
                    target = nodes.index(node)
                except ValueError:
                    nodes.append(node)
                    target = len(nodes) - 1

                # Add edge
                if h.previous_hop:
                    # try:
                    #     node_prev = nodes.index({
                    #         'name': h.previous_hop.twitter_username,
                    #         'img': '/ethos/proxy/?image=' + h.previous_hop.twitter_profile_pic
                    #     })
                    #     distance = 200
                    #     distance = int(math.sqrt(h.previous_hop.created_on - h.created_on).total_seconds/10)
                    #     edges.append({'source': node_prev, 'target': target, 'distance': distance})
                    # except:
                    #     pass
                    node_prev = nodes.index({
                        'name': h.previous_hop.twitter_profile.username,
                        'img': h.previous_hop.twitter_profile.profile_picture.url
                    })

                    time_lapsed = round((h.created_on - h.previous_hop.created_on).total_seconds()/60)
                    if 0 < time_lapsed < 30:
                        distance = time_lapsed * 10
                    else:
                        distance = 300

                    edges.append({'source': node_prev, 'target': target, 'distance': distance})

        except ShortCode.DoesNotExist:
            status = 'error'
            message = _('Bad request')
        except ValueError as e:
            if 'replacement transaction underpriced' in str(e):
                # TODO: Handle replacement tx
                print('replacement transaction underpriced')
            else:
                raise e
            status = 'error'
            message = _('Error while creating transaction. Please try again')
        except Exception as e:
            status = 'error'
            message = str(e)

        # API Response
        response = {
            'status': status,
            'message': message,
        }

        if status == 'OK':
            response['dataset'] = {'nodes': nodes, 'edges': edges}

        print('EDGES: ', edges)
        print('NODES: ', nodes)
        return JsonResponse(response)

    try:
        ShortCode.objects.get(shortcode=shortcode)
    except ShortCode.DoesNotExist:
        raise Http404

    params = {
        'class': 'redeem',
        'title': _('EthOS Coin'),
    }

    return TemplateResponse(request, 'redeem_ethos.html', params)


@csrf_exempt
def tweet_to_twitter(request):

    if request.body:
        status = 'OK'

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        media = body['media']
        username = body['username']

        twitter_api = get_twitter_api()

        if not twitter_api:
            status = 'error'
        else:
            try:
                data = ContentFile(base64.b64decode(media), name='graph.png')
                data.mode = 'rb'
                tweet_txt = f'@{username} has earned some #EthOS \n\n'
                twitter_api.PostUpdate(tweet_txt, media=data)
            except twitter.error.TwitterError:
                status = 'error'

        # http response
        response = {
            'status': status
        }

        return JsonResponse(response)
    else:
        raise Http404


def get_twitter_api():

    if not settings.ETHOS_TWITTER_CONSUMER_KEY:
        return False

    try:
        twitter_api = twitter.Api(
            consumer_key=settings.ETHOS_TWITTER_CONSUMER_KEY,
            consumer_secret=settings.ETHOS_TWITTER_CONSUMER_SECRET,
            access_token_key=settings.ETHOS_TWITTER_ACCESS_TOKEN,
            access_token_secret=settings.ETHOS_TWITTER_ACCESS_SECRET,
        )
    except twitter.error.TwitterError:
        return False

    return twitter_api
