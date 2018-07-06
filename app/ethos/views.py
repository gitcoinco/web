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
import json

from django.conf import settings
from django.http import Http404, HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

import twitter
from ethos.models import Hop, ShortCode, TwitterProfile
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import HTTPProvider, Web3

from .exceptions import DuplicateTransactionException
from .utils import get_ethos_tweet, get_twitter_api, tweet_message

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

    hops = Hop.objects.all()
    key = request.GET.get('key', False)
    if key:
        if key == 'latest':
            hops = Hop.objects.all().order_by('-pk')[:1]
        if key == 'optimize':
            hops = list(Hop.objects.all().order_by('pk'))[-20:]
    print(f"got {len(hops)} hops")

    try:
        for hop in hops:
            img = hop.build_graph(latest=False)
    except Hop.DoesNotExist:
        raise Http404

    movie = 'assets/tmp/_movie.gif'
    import imageio
    images = []
    filenames = [f"assets/tmp/{hop.pk}.gif" for hop in hops]
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(movie, images)

    # Return image with right content-type
    response = HttpResponse(content_type="image/jpeg")
    with open(movie, "rb") as f:
        return HttpResponse(f.read(), content_type="image/jpeg")
    return response


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
    message = None

    if request.body:
        status = 'OK'

        body_unicode = request.body.decode('utf-8')
        body = json.loads(body_unicode)

        try:
            address = body.get('address')
            username = body.get('username', '').lstrip('@')

            if not username:
                raise Http404

            twitter_profile, __ = TwitterProfile.objects.prefetch_related('hops').get_or_create(username=username)
            ethos = ShortCode.objects.get(shortcode=shortcode)
            previous_hop = None 

            if address:
                address = Web3.toChecksumAddress(address)

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

                tx = contract.functions.transfer(address, n * 10**18).buildTransaction({
                    'nonce': w3.eth.getTransactionCount(settings.ETHOS_ACCOUNT_ADDRESS),
                    'gas': 100000,
                    'gasPrice': recommend_min_gas_price_to_confirm_in_time(1) * 10**9
                })

                signed = w3.eth.account.signTransaction(tx, settings.ETHOS_ACCOUNT_PRIVATE_KEY)
                message = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

            hop = Hop(
                shortcode=ethos,
                ip=get_ip(request),
                created_on=timezone.now(),
                twitter_profile=twitter_profile,
            )
            if message and message.startswith('0x'):
                hop.txid = message
            if address and address.startswith('0x'):
                hop.web3_address = address
            if previous_hop:
                hop.previous_hop = previous_hop
            hop.save()

            ethos.num_scans += 1
            ethos.save()

            num_scans = ethos.num_scans
            num_scans_top = ShortCode.objects.order_by('-num_scans').first().num_scans

            twitter_api = get_twitter_api()

            if not twitter_api:
                status = 'error'
                message = _('Error while fetching Twitter account. Please try again')
            else:
                tweet = get_ethos_tweet(twitter_profile.username, message)
                try:
                    tweet_id_str = tweet_message(twitter_api, tweet)
                except twitter.error.TwitterError as e:
                    status = 'error'
                    message = _(f'Error while tweeting to Twitter. {e}')

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
            response['num_scans'] = num_scans
            response['num_scans_top'] = num_scans_top
            response['tweet_url'] = f'https://twitter.com/EthOSEthereal/status/{tweet_id_str}'

        return JsonResponse(response)

    try:
        ShortCode.objects.get(shortcode=shortcode)
    except ShortCode.DoesNotExist:
        raise Http404

    params = {
        'class': 'redeem',
        'title': _('EthOS Coin'),
        'hide_send_tip': True
    }

    return TemplateResponse(request, 'redeem_ethos.html', params)
