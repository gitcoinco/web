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
import urllib

from django.conf import settings
from django.core.files.base import ContentFile
from django.http import Http404, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

import twitter
from ethos.models import Hop, ShortCode
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import HTTPProvider, Web3

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
contract = w3.eth.contract(Web3.toChecksumAddress(settings.ETHOS_CONTRACT_ADDRESS), abi=abi)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def redeem_coin(request, shortcode):

    if request.body:
        status = 'OK'

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        try:
            address = body['address']
            username = body['username']

            profile_pic = f'https://twitter.com/{username}/profile_image?size=original'

            ethos = ShortCode.objects.get(shortcode=shortcode)

            user_hop = Hop.objects.filter(
                shortcode=ethos,
                twitter_username=username,
                web3_address=address).order_by('-id').first()

            # Restrict same user from redeeming the same coin within 30 minutes
            if user_hop and (timezone.now() - user_hop.created_on).total_seconds() < 1800:
                raise Exception(_('Duplicate transaction detected'))

            # Number of EthOS tokens = 30 - number of minutes lapsed between the hop. Minimum = 5
            n = 30

            previous_hop = Hop.objects.filter(shortcode=ethos).order_by('-id').first()

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
                twitter_username=username,
                twitter_profile_pic=profile_pic,
                previous_hop=previous_hop
            )

            ethos.num_scans += 1
            ethos.save()

            num_scans = ethos.num_scans
            num_scans_top = ShortCode.objects.order_by('-num_scans').first().num_scans

            nodes = []
            edges = []

            # construct json for the graph viz
            for h in Hop.objects.all():
                node = {
                    'name': h.twitter_username,
                    'img': '/ethos/proxy/?image=' + h.twitter_profile_pic
                }

                try:
                    target = nodes.index(node)
                except ValueError:
                    nodes.append(node)
                    target = len(nodes) - 1

                # Add edge
                if h.previous_hop:
                    node_prev = nodes.index({
                        'name': h.previous_hop.twitter_username,
                        'img': '/ethos/proxy/?image=' + h.previous_hop.twitter_profile_pic
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
            response['num_scans'] = num_scans
            response['num_scans_top'] = num_scans_top

        return JsonResponse(response)

    try:
        ShortCode.objects.get(shortcode=shortcode)

        params = {
            'class': 'redeem',
            'title': _('EthOS Coin'),
        }

        return TemplateResponse(request, 'redeem_ethos.html', params)
    except ShortCode.DoesNotExist:
        raise Http404


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
                tweet_txt = f'Ethos has been earned by @{username} at #ethereal'
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


def proxy(request):

    image = urllib.parse.unquote(request.GET.get('image'))
    req = urllib.request.Request(image)
    resp = urllib.request.urlopen(req)

    return HttpResponse(resp.read())
