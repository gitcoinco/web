# -*- coding: utf-8 -*-
"""Define Dashboard related utilities and miscellaneous logic.

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
import base64
import json
import logging
import re
from json.decoder import JSONDecodeError

from django.conf import settings
from django.urls import URLPattern, URLResolver
from django.utils import timezone

import ens
import ipfshttpclient
import requests
from app.utils import sync_profile
from avatar.models import CustomAvatar
from compliance.models import Country, Entity
from cytoolz import compose
from dashboard.helpers import UnsupportedSchemaException, normalize_url, process_bounty_changes, process_bounty_details
from dashboard.models import Activity, BlockedUser, Bounty, Profile, UserAction
from dashboard.sync.algorand import sync_algorand_payout
from dashboard.sync.binance import sync_binance_payout
from dashboard.sync.btc import sync_btc_payout
from dashboard.sync.casper import sync_casper_payout
from dashboard.sync.celo import sync_celo_payout
from dashboard.sync.etc import sync_etc_payout
from dashboard.sync.eth import sync_eth_payout
from dashboard.sync.filecoin import sync_filecoin_payout
from dashboard.sync.harmony import sync_harmony_payout
from dashboard.sync.nervos import sync_nervos_payout
from dashboard.sync.polkadot import sync_polkadot_payout
from dashboard.sync.rsk import sync_rsk_payout
from dashboard.sync.sia import sync_sia_payout
from dashboard.sync.tezos import sync_tezos_payout
from dashboard.sync.xinfin import sync_xinfin_payout
from dashboard.sync.zil import sync_zil_payout
from ens.utils import name_to_hash
from eth_abi import decode_single, encode_single
from eth_utils import keccak, to_checksum_address, to_hex
from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time
from graphqlclient import GraphQLClient
from hexbytes import HexBytes
from ipfshttpclient.exceptions import CommunicationError
from pytz import UTC
from web3 import HTTPProvider, Web3, WebsocketProvider
from web3.exceptions import BadFunctionCallOutput
from web3.middleware import geth_poa_middleware

from .abi import erc20_abi

logger = logging.getLogger(__name__)

SEMAPHORE_BOUNTY_SALT = '1'
SEMAPHORE_BOUNTY_NS = 'bounty_processor'

GRAPHQL_CLIENTS = {}

def all_sendcryptoasset_models():
    from dashboard.models import Tip
    from kudos.models import KudosTransfer
    from revenue.models import DigitalGoodPurchase

    return [DigitalGoodPurchase, Tip, KudosTransfer]


class ProfileNotFoundException(Exception):
    pass


class ProfileHiddenException(Exception):
    pass


class BountyNotFoundException(Exception):
    pass


class UnsupportedNetworkException(Exception):
    pass


class IPFSCantConnectException(Exception):
    pass


class NoBountiesException(Exception):
    pass


def humanize_event_name(name):
    """Humanize an event name.

    Args:
      name (str): The event name

    Returns:
        str: The humanized representation.

    """
    humanized_event_names = {
        'new_bounty': 'New funded issue',
        'start_work': 'Work started',
        'stop_work': 'Work stopped',
        'work_submitted': 'Work submitted',
        'increased_bounty': 'Increased funds for issue',
        'killed_bounty': 'Cancelled funded issue',
        'worker_approved': 'Worker approved',
        'worker_rejected': 'Worker rejected',
        'work_done': 'Work done',
        'issue_remarketed': 'Issue re-marketed'
    }

    return humanized_event_names.get(name, name).upper()


def create_user_action(user, action_type, request=None, metadata=None):
    """Create a UserAction for the specified action type.

    Args:
        user (User): The User object.
        action_type (str): The type of action to record.
        request (Request): The request object. Defaults to: None.
        metadata (dict): Any accompanying metadata to be added.
            Defaults to: {}.

    Returns:
        bool: Whether or not the UserAction was created successfully.

    """
    from app.utils import handle_location_request
    if action_type not in dict(UserAction.ACTION_TYPES).keys():
        print('UserAction.create_action received an invalid action_type')
        return False

    if metadata is None:
        metadata = {}

    kwargs = {
        'metadata': metadata,
        'action': action_type,
        'user': user
    }

    if request:
        geolocation_data, ip_address = handle_location_request(request)

        if geolocation_data:
            kwargs['location_data'] = geolocation_data
        if ip_address:
            kwargs['ip_address'] = ip_address

        utmJson = _get_utm_from_cookie(request)

        if utmJson:
            kwargs['utm'] = utmJson

    if user and hasattr(user, 'profile'):
        kwargs['profile'] = user.profile if user and user.profile else None

    try:
        UserAction.objects.create(**kwargs)
        return True
    except Exception as e:
        logger.error(f'Failure in UserAction.create_action - ({e})')
        return False


def _get_utm_from_cookie(request):
    """Extract utm* params from Cookie.

    Args:
        request (Request): The request object.

    Returns:
        utm_source: if it's not in cookie should be None.
        utm_medium: if it's not in cookie should be None.
        utm_campaign: if it's not in cookie should be None.

    """
    utmDict = {}
    utm_source = request.COOKIES.get('utm_source')
    if not utm_source:
        utm_source = request.GET.get('utm_source')
    utm_medium = request.COOKIES.get('utm_medium')
    if not utm_medium:
        utm_medium = request.GET.get('utm_medium')
    utm_campaign = request.COOKIES.get('utm_campaign')
    if not utm_campaign:
        utm_campaign = request.GET.get('utm_campaign')

    if utm_source:
        utmDict['utm_source'] = utm_source
    if utm_medium:
        utmDict['utm_medium'] = utm_medium
    if utm_campaign:
        utmDict['utm_campaign'] = utm_campaign

    if bool(utmDict):
        return utmDict
    else:
        return None


def get_ipfs(host=None, port=settings.IPFS_API_PORT):
    """Establish a connection to IPFS.

    Args:
        host (str): The IPFS host to connect to.
            Defaults to environment variable: IPFS_HOST.  The host name should be of the form 'ipfs.infura.io' and not
            include 'https://'.
        port (int): The IPFS port to connect to.
            Defaults to environment variable: env IPFS_API_PORT.

    Raises:
        CommunicationError: The exception is raised when there is a
            communication error with IPFS.

    Returns:
        ipfshttpclient.client.Client: The IPFS connection client.

    """
    if host is None:
        clientConnectString = f'/dns/{settings.IPFS_HOST}/tcp/{settings.IPFS_API_PORT}/{settings.IPFS_API_SCHEME}'
    else:
        clientConnectString = f'/dns/{host}/tcp/{settings.IPFS_API_PORT}/https'
    try:
        return ipfshttpclient.connect(clientConnectString)
    except CommunicationError as e:
        logger.exception(e)
        raise IPFSCantConnectException('Failed while attempt to connect to IPFS')
    return None


def ipfs_cat(key):
    try:
        # Attempt connecting to IPFS via Infura
        response, status_code = ipfs_cat_requests(key)
        if status_code == 200:
            return response

        # Attempt connecting to IPFS via hosted node
        response = ipfs_cat_ipfsapi(key)
        if response:
            return response

        raise IPFSCantConnectException('Failed to connect cat key against IPFS - Check IPFS/Infura connectivity')
    except IPFSCantConnectException as e:
        logger.exception(e)


def ipfs_cat_ipfsapi(key):
    ipfs = get_ipfs()
    if ipfs:
        try:
            return ipfs.cat(key)
        except Exception:
            return None


def ipfs_cat_requests(key):
    try:
        url = f'https://ipfs.infura.io:5001/api/v0/cat?arg={key}'
        response = requests.get(url, timeout=1)
        return response.text, response.status_code
    except:
        return None, 500


def get_web3(network, sockets=False, chain='std'):
    """Get a Web3 session for the provided network.

    Attributes:
        network (str): The network to establish a session with.

    Raises:
        UnsupportedNetworkException: The exception is raised if the method
            is passed an invalid network.

    Returns:
        web3.main.Web3: A web3 instance for the provided network.

    """
    if network in ['mainnet', 'rinkeby', 'ropsten', 'testnet']:
        if network == 'mainnet' and chain == 'polygon':
            network = 'polygon-mainnet'
        elif network == 'testnet':
            network = 'polygon-mumbai'

        if sockets and chain != 'polygon': # polygon doesn't yet have socket support in infura
            if settings.INFURA_USE_V3:
                provider = WebsocketProvider(f'wss://{network}.infura.io/ws/v3/{settings.INFURA_V3_PROJECT_ID}')
            else:
                provider = WebsocketProvider(f'wss://{network}.infura.io/ws')
        else:
            if settings.INFURA_USE_V3:
                provider = HTTPProvider(f'https://{network}.infura.io/v3/{settings.INFURA_V3_PROJECT_ID}')
            else:
                provider = HTTPProvider(f'https://{network}.infura.io')

        w3 = Web3(provider)
        if network == 'rinkeby':
            w3.middleware_stack.inject(geth_poa_middleware, layer=0)
        return w3
    elif network == 'xdai':
        if sockets:
            provider = WebsocketProvider(f'wss://rpc.xdaichain.com/wss')
        else:
            provider = HTTPProvider(f'https://dai.poa.network/')
        return Web3(provider)
    elif network == 'localhost' or 'custom network':
        return Web3(Web3.HTTPProvider("http://testrpc:8545", request_kwargs={'timeout': 60}))

    raise UnsupportedNetworkException(network)


def get_graphql_client(uri):
    """Get a graphQL client attached to the given uri

    Returns:
        GraphQLClient: an established GraphQLClient assoicated with the given uri
    """

    # memoize
    if uri not in GRAPHQL_CLIENTS:
        GRAPHQL_CLIENTS[uri] = GraphQLClient(uri)

    # return the client connection
    return GRAPHQL_CLIENTS.get(uri)


def get_graphql_result(uri, query):
    """Get result of the query from the uri

    Returns:
        dict: result of the graphQL query
    """

    # get connection to uri
    client = get_graphql_client(uri)
    # pull the result
    result = client.execute(query)

    return json.loads(result)


def get_bounty_invite_url(inviter, bounty_id):
    """Returns a unique url for each bounty and one who is inviting
    Returns:
        A unique string for each bounty
    """
    salt = "X96gRAVvwx52uS6w4QYCUHRfR3OaoB"
    string = str(inviter) + salt + str(bounty_id)
    return base64.urlsafe_b64encode(string.encode()).decode()


def get_bounty_from_invite_url(invite_url):
    """Returns a unique url for each bounty and one who is inviting

    Returns:
        A unique string for each bounty
    """
    salt = "X96gRAVvwx52uS6w4QYCUHRfR3OaoB"
    decoded_string = base64.urlsafe_b64decode(invite_url.encode()).decode()
    data_array = decoded_string.split(salt)
    inviter = data_array[0]
    bounty = data_array[1]
    return {'inviter': inviter, 'bounty': bounty}


def get_unrated_bounties_count(user):
    if not user:
        return 0
    unrated_contributed = Bounty.objects.current().prefetch_related('feedbacks').filter(interested__profile=user) \
        .filter(interested__status='okay') \
        .filter(interested__pending=False).filter(idx_status='submitted') \
        .exclude(
            feedbacks__feedbackType='worker',
            feedbacks__sender_profile=user,
        )
    unrated_funded = Bounty.objects.current().prefetch_related('fulfillments', 'interested', 'interested__profile', 'feedbacks') \
    .filter(
        bounty_owner_github_username__iexact=user.handle,
        idx_status='done'
    ).exclude(
        feedbacks__feedbackType='approver',
        feedbacks__sender_profile=user,
    )
    unrated_count = unrated_funded.count() + unrated_contributed.count()
    return unrated_count


def getStandardBountiesContractAddresss(network):
    if network == 'mainnet':
        return to_checksum_address('0x2af47a65da8cd66729b4209c22017d6a5c2d2400')
    elif network == 'rinkeby':
        return to_checksum_address('0xf209d2b723b6417cbf04c07e733bee776105a073')
    raise UnsupportedNetworkException(network)


# http://web3py.readthedocs.io/en/latest/contracts.html
def getBountyContract(network):
    web3 = get_web3(network)
    standardbounties_abi = '[{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"}],"name":"killBounty","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_bountyId","type":"uint256"}],"name":"getBountyToken","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_data","type":"string"}],"name":"fulfillBounty","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newDeadline","type":"uint256"}],"name":"extendDeadline","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"getNumBounties","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_fulfillmentId","type":"uint256"},{"name":"_data","type":"string"}],"name":"updateFulfillment","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newFulfillmentAmount","type":"uint256"},{"name":"_value","type":"uint256"}],"name":"increasePayout","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newFulfillmentAmount","type":"uint256"}],"name":"changeBountyFulfillmentAmount","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newIssuer","type":"address"}],"name":"transferIssuer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_value","type":"uint256"}],"name":"activateBounty","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"name":"_issuer","type":"address"},{"name":"_deadline","type":"uint256"},{"name":"_data","type":"string"},{"name":"_fulfillmentAmount","type":"uint256"},{"name":"_arbiter","type":"address"},{"name":"_paysTokens","type":"bool"},{"name":"_tokenContract","type":"address"}],"name":"issueBounty","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_issuer","type":"address"},{"name":"_deadline","type":"uint256"},{"name":"_data","type":"string"},{"name":"_fulfillmentAmount","type":"uint256"},{"name":"_arbiter","type":"address"},{"name":"_paysTokens","type":"bool"},{"name":"_tokenContract","type":"address"},{"name":"_value","type":"uint256"}],"name":"issueAndActivateBounty","outputs":[{"name":"","type":"uint256"}],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"_bountyId","type":"uint256"}],"name":"getBountyArbiter","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_value","type":"uint256"}],"name":"contribute","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newPaysTokens","type":"bool"},{"name":"_newTokenContract","type":"address"}],"name":"changeBountyPaysTokens","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_bountyId","type":"uint256"}],"name":"getBountyData","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_fulfillmentId","type":"uint256"}],"name":"getFulfillment","outputs":[{"name":"","type":"bool"},{"name":"","type":"address"},{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newArbiter","type":"address"}],"name":"changeBountyArbiter","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newDeadline","type":"uint256"}],"name":"changeBountyDeadline","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_fulfillmentId","type":"uint256"}],"name":"acceptFulfillment","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"bounties","outputs":[{"name":"issuer","type":"address"},{"name":"deadline","type":"uint256"},{"name":"data","type":"string"},{"name":"fulfillmentAmount","type":"uint256"},{"name":"arbiter","type":"address"},{"name":"paysTokens","type":"bool"},{"name":"bountyStage","type":"uint8"},{"name":"balance","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_bountyId","type":"uint256"}],"name":"getBounty","outputs":[{"name":"","type":"address"},{"name":"","type":"uint256"},{"name":"","type":"uint256"},{"name":"","type":"bool"},{"name":"","type":"uint256"},{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_bountyId","type":"uint256"},{"name":"_newData","type":"string"}],"name":"changeBountyData","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_bountyId","type":"uint256"}],"name":"getNumFulfillments","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"inputs":[{"name":"_owner","type":"address"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"}],"name":"BountyIssued","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"},{"indexed":false,"name":"issuer","type":"address"}],"name":"BountyActivated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"},{"indexed":true,"name":"fulfiller","type":"address"},{"indexed":true,"name":"_fulfillmentId","type":"uint256"}],"name":"BountyFulfilled","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_bountyId","type":"uint256"},{"indexed":false,"name":"_fulfillmentId","type":"uint256"}],"name":"FulfillmentUpdated","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"},{"indexed":true,"name":"fulfiller","type":"address"},{"indexed":true,"name":"_fulfillmentId","type":"uint256"}],"name":"FulfillmentAccepted","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"},{"indexed":true,"name":"issuer","type":"address"}],"name":"BountyKilled","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"},{"indexed":true,"name":"contributor","type":"address"},{"indexed":false,"name":"value","type":"uint256"}],"name":"ContributionAdded","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"},{"indexed":false,"name":"newDeadline","type":"uint256"}],"name":"DeadlineExtended","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"bountyId","type":"uint256"}],"name":"BountyChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_bountyId","type":"uint256"},{"indexed":true,"name":"_newIssuer","type":"address"}],"name":"IssuerTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"name":"_bountyId","type":"uint256"},{"indexed":false,"name":"_newFulfillmentAmount","type":"uint256"}],"name":"PayoutIncreased","type":"event"}]'
    standardbounties_addr = getStandardBountiesContractAddresss(network)
    bounty_abi = json.loads(standardbounties_abi)
    getBountyContract = web3.eth.contract(standardbounties_addr, abi=bounty_abi)
    return getBountyContract


def get_poap_tokens(uri, address):

    # query the tokens held for an address
    return get_graphql_result(uri, '''
    {
        account(id: "%s") {
            tokens(orderBy: id, orderDirection: asc){
                id
            }
        }
    }
    ''' % address)


def get_poap_transfers(uri, address):

    # query the transfers associated with an address (oldest token first then most recent transfer first)
    return get_graphql_result(uri, '''
    {
        account(id: "%s") {
            tokens(orderBy: id, orderDirection: asc){
                id
                transfers(orderBy: timestamp, orderDirection: desc, where: { to: "%s" }){
                    timestamp
                }
            }
        }
    }
    ''' % (address, address))


def get_poap_earliest_owned_token_timestamp(network, address):
    # returning None when no tokens are held for address
    tokens_timestamps = []
    # must query the graph using lowercase address
    address = address.lower()

    # graphQL api uri
    uri = 'https://api.thegraph.com/subgraphs/name/poap-xyz/poap%s' % ('-xdai' if network == 'xdai' else '')

    # get all tokens held by this address
    poap_tokens = get_poap_tokens(uri, address)

    try:
        # check if the address has tokens
        has_tokens = poap_tokens['data']['account']
        poap_tokens = has_tokens['tokens'] if has_tokens else None

        # if the address holds no tokens then stop
        if not has_tokens or len(poap_tokens) == 0:
            pass
        else:
            # flatten tokenIds into a dict
            tokens_list = []
            for token in poap_tokens:
                tokens_list.append(token['id'])

            # pull the transfers so that we can check timestamps
            poap_transfers = get_poap_transfers(uri, address)
            tokens_transfered = poap_transfers['data']['account']['tokens']

            # check the earliest received token that is still owned by the address
            for token in tokens_transfered:
                # token still owned by the address?
                if token['id'] in tokens_list:
                    # use timestamp of most recent transfer
                    tokens_timestamps.append(int(token['transfers'][0]['timestamp']))
    except:
        # returning 0 will print a failed (try again) error
        tokens_timestamps[0] = 0

    # sort to discover earliest
    tokens_timestamps.sort()

    # return the earliest timestamp
    return tokens_timestamps[0] if len(tokens_timestamps) else None


def get_ens_contract_addresss(network, legacy=False):
    if network == 'mainnet':
        if not legacy:
            return to_checksum_address('0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e')
        return to_checksum_address('0x314159265dd8dbb310642f98f50c066173c1259b')
    raise UnsupportedNetworkException(network)


def get_ens_resolver_contract(network, node):
    web3 = get_web3(network)
    ens_resolver_json = '[{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"a","type":"address"}],"name":"AddrChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"coinType","type":"uint256"},{"indexed":false,"name":"newAddress","type":"bytes"}],"name":"AddressChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"name","type":"string"}],"name":"NameChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":true,"name":"contentType","type":"uint256"}],"name":"ABIChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"x","type":"bytes32"},{"indexed":false,"name":"y","type":"bytes32"}],"name":"PubkeyChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":true,"name":"indexedKey","type":"string"},{"indexed":false,"name":"key","type":"string"}],"name":"TextChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"hash","type":"bytes"}],"name":"ContenthashChanged","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"node","type":"bytes32"},{"indexed":false,"name":"hash","type":"bytes32"}],"name":"ContentChanged","type":"event"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"},{"name":"contentTypes","type":"uint256"}],"name":"ABI","outputs":[{"name":"","type":"uint256"},{"name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"},{"name":"coinType","type":"uint256"}],"name":"addr","outputs":[{"name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"addr","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"contenthash","outputs":[{"name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"dnsrr","outputs":[{"name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"pubkey","outputs":[{"name":"x","type":"bytes32"},{"name":"y","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"},{"name":"key","type":"string"}],"name":"text","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"},{"name":"interfaceID","type":"bytes4"}],"name":"interfaceImplementer","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"contentType","type":"uint256"},{"name":"data","type":"bytes"}],"name":"setABI","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"addr","type":"address"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"coinType","type":"uint256"},{"name":"a","type":"bytes"}],"name":"setAddr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"hash","type":"bytes"}],"name":"setContenthash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"data","type":"bytes"}],"name":"setDnsrr","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"_name","type":"string"}],"name":"setName","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"x","type":"bytes32"},{"name":"y","type":"bytes32"}],"name":"setPubkey","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"key","type":"string"},{"name":"value","type":"string"}],"name":"setText","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"interfaceID","type":"bytes4"},{"name":"implementer","type":"address"}],"name":"setInterface","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"interfaceID","type":"bytes4"}],"name":"supportsInterface","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"pure","type":"function"},{"constant":false,"inputs":[{"name":"data","type":"bytes[]"}],"name":"multicall","outputs":[{"name":"results","type":"bytes[]"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"content","outputs":[{"name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"node","type":"bytes32"}],"name":"multihash","outputs":[{"name":"","type":"bytes"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"hash","type":"bytes32"}],"name":"setContent","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"node","type":"bytes32"},{"name":"hash","type":"bytes"}],"name":"setMultihash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
    ens_addr = get_ens_contract_addresss(network)
    ens_resolver_abi = json.loads(ens_resolver_json)
    ens_registry = ens.ENS.fromWeb3(web3, ens_addr)
    resolver_address = ens_registry.ens.resolver(name_to_hash(node))

    ens_resolver_contract = web3.eth.contract(resolver_address, abi=ens_resolver_abi)
    return ens_resolver_contract

def get_bounty(bounty_enum, network):
    if (settings.DEBUG or settings.ENV != 'prod') and network == 'mainnet':
        # This block will return {} if env isn't prod and the network is mainnet.
        print("--*--")
        return {}

    standard_bounties = getBountyContract(network)

    try:
        issuer, contract_deadline, fulfillmentAmount, paysTokens, bountyStage, balance = standard_bounties.functions.getBounty(bounty_enum).call()
    except BadFunctionCallOutput:
        raise BountyNotFoundException
    # pull from blockchain
    bountydata = standard_bounties.functions.getBountyData(bounty_enum).call()
    arbiter = standard_bounties.functions.getBountyArbiter(bounty_enum).call()
    token = standard_bounties.functions.getBountyToken(bounty_enum).call()
    bounty_data_str = ipfs_cat(bountydata)
    bounty_data = json.loads(bounty_data_str)

    # fulfillments
    num_fulfillments = int(standard_bounties.functions.getNumFulfillments(bounty_enum).call())
    fulfillments = []
    for fulfill_enum in range(0, num_fulfillments):

        # pull from blockchain
        accepted, fulfiller, data = standard_bounties.functions.getFulfillment(bounty_enum, fulfill_enum).call()
        try:
            data_str = ipfs_cat(data)
            data = json.loads(data_str)
        except JSONDecodeError:
            logger.error(f'Could not get {data} from ipfs')
            continue

        # validation
        if 'Failed to get block' in str(data_str):
            raise IPFSCantConnectException("Failed to connect to IPFS")

        fulfillments.append({
            'id': fulfill_enum,
            'accepted': accepted,
            'fulfiller': fulfiller,
            'data': data,
        })

    # validation
    if 'Failed to get block' in str(bounty_data_str):
        raise IPFSCantConnectException("Failed to connect to IPFS")

    # https://github.com/Bounties-Network/StandardBounties/issues/25
    ipfs_deadline = bounty_data.get('payload', {}).get('expire_date', False)
    deadline = contract_deadline
    if ipfs_deadline:
        deadline = ipfs_deadline

    # assemble the data
    bounty = {
        'id': bounty_enum,
        'issuer': issuer,
        'deadline': deadline,
        'contract_deadline': contract_deadline,
        'ipfs_deadline': ipfs_deadline,
        'fulfillmentAmount': fulfillmentAmount,
        'paysTokens': paysTokens,
        'bountyStage': bountyStage,
        'balance': balance,
        'data': bounty_data,
        'arbiter': arbiter,
        'token': token,
        'fulfillments': fulfillments,
        'network': network,
        'review': bounty_data.get('review',{}),
    }
    return bounty


# processes a bounty returned by get_bounty
def web3_process_bounty(bounty_data):
    """Process web3 bounty data by creating new or updated Bounty objects."""
    # Check whether or not the bounty data payload is for mainnet and env is prod or other network and not mainnet.
    if not bounty_data or (settings.DEBUG or settings.ENV != 'prod') and bounty_data.get('network') == 'mainnet':
        # This block will return None if running in debug/non-prod env and the network is mainnet.
        print(f"--*--")
        return None

    did_change, old_bounty, new_bounty = process_bounty_details(bounty_data)

    if did_change and new_bounty:
        _from = old_bounty.pk if old_bounty else None
        print(f"- processing changes, {_from} => {new_bounty.pk}")
        process_bounty_changes(old_bounty, new_bounty)

    return did_change, old_bounty, new_bounty


def has_tx_mined(txid, network):
    web3 = get_web3(network)
    try:
        transaction = web3.eth.getTransaction(txid)
        if not transaction:
            return False
        if not transaction.blockHash:
            return False
        return transaction.blockHash != HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000')
    except Exception:
        return False


def sync_payout(fulfillment):
    token_name = fulfillment.token_name
    if not token_name:
        token_name = fulfillment.bounty.token_name

    if fulfillment.payout_type == 'web3_modal':
        sync_eth_payout(fulfillment)

    elif fulfillment.payout_type == 'qr':
        if token_name == 'ETC':
            sync_etc_payout(fulfillment)
        elif token_name == 'BTC':
            sync_btc_payout(fulfillment)
        elif token_name == 'CELO' or token_name == 'cUSD':
            sync_celo_payout(fulfillment)
        elif token_name == 'ZIL':
            sync_zil_payout(fulfillment)
        elif token_name == 'FIL':
            sync_filecoin_payout(fulfillment)

    elif fulfillment.payout_type == 'polkadot_ext':
        sync_polkadot_payout(fulfillment)

    elif fulfillment.payout_type == 'binance_ext':
        sync_binance_payout(fulfillment)

    elif fulfillment.payout_type == 'harmony_ext':
        sync_harmony_payout(fulfillment)

    elif fulfillment.payout_type == 'rsk_ext':
        sync_rsk_payout(fulfillment)

    elif fulfillment.payout_type == 'xinfin_ext':
        sync_xinfin_payout(fulfillment)

    elif fulfillment.payout_type == 'nervos_ext':
        sync_nervos_payout(fulfillment)

    elif fulfillment.payout_type == 'algorand_ext':
        sync_algorand_payout(fulfillment)

    elif fulfillment.payout_type == 'sia_ext':
        sync_sia_payout(fulfillment)

    elif fulfillment.payout_type == 'tezos_ext':
        sync_tezos_payout(fulfillment)

    elif fulfillment.payout_type == 'casper_ext':
        sync_casper_payout(fulfillment)


def get_bounty_id(issue_url, network):
    issue_url = normalize_url(issue_url)
    bounty_id = get_bounty_id_from_db(issue_url, network)
    if bounty_id:
        return bounty_id

    all_known_stdbounties = Bounty.objects.filter(
        web3_type='bounties_network',
        network=network,
    ).nocache().order_by('-standard_bounties_id')

    try:
        highest_known_bounty_id = get_highest_known_bounty_id(network)
        bounty_id = get_bounty_id_from_web3(issue_url, network, highest_known_bounty_id, direction='down')
    except NoBountiesException:
        last_known_bounty_id = 0
        if all_known_stdbounties.exists():
            last_known_bounty_id = all_known_stdbounties.first().standard_bounties_id
        bounty_id = get_bounty_id_from_web3(issue_url, network, last_known_bounty_id, direction='up')

    return bounty_id


def get_bounty_id_from_db(issue_url, network):
    bounties = Bounty.objects.filter(
        github_url=issue_url,
        network=network,
        web3_type='bounties_network',
    ).nocache().order_by('-standard_bounties_id')
    if not bounties.exists():
        return None
    return bounties.first().standard_bounties_id


def get_highest_known_bounty_id(network):
    standard_bounties = getBountyContract(network)
    num_bounties = int(standard_bounties.functions.getNumBounties().call())
    if num_bounties == 0:
        raise NoBountiesException()
    return num_bounties - 1


def get_bounty_id_from_web3(issue_url, network, start_bounty_id, direction='up'):
    issue_url = normalize_url(issue_url)

    # iterate through all the bounties
    bounty_enum = start_bounty_id
    more_bounties = True
    while more_bounties:
        try:

            # pull and process each bounty
            print(f'** get_bounty_id_from_web3; looking at {bounty_enum}')
            bounty = get_bounty(bounty_enum, network)
            url = bounty.get('data', {}).get('payload', {}).get('webReferenceURL', False)
            if url == issue_url:
                return bounty['id']

        except BountyNotFoundException:
            more_bounties = False
        except UnsupportedSchemaException:
            pass
        finally:
            # prepare for next loop
            if direction == 'up':
                bounty_enum += 1
            else:
                bounty_enum -= 1

    return None


def build_profile_pairs(bounty):
    """Build the profile pairs list of tuples for ingestion by notifications.

    Args:
        bounty (dashboard.models.Bounty): The Bounty to build profile pairs for.

    Returns:
        list of tuples: The list of profile pair tuples.

    """
    profile_handles = []
    for fulfillment in bounty.fulfillments.select_related('profile').all().order_by('pk'):
        if fulfillment.profile and fulfillment.profile.handle.strip() and fulfillment.profile.absolute_url:
            profile_handles.append((fulfillment.profile.handle, fulfillment.profile.absolute_url))
        else:
            if bounty.tenant == 'ETH':
                addr = f"https://etherscan.io/address/{fulfillment.fulfiller_address}"
            elif bounty.tenant == 'ZIL':
                addr = f"https://viewblock.io/zilliqa/address/{fulfillment.fulfiller_address}"
            elif bounty.tenant == 'CELO':
                addr = f"https://explorer.celo.org/address/{fulfillment.fulfiller_address}"
            elif bounty.tenant == 'ETC':
                addr = f"https://blockscout.com/etc/mainnet/address/{fulfillment.fulfiller_address}"
            elif bounty.tenant == 'BTC':
                addr = f"https://blockstream.info/api/address/{fulfillment.fulfiller_address}"
            else:
                addr = None
            profile_handles.append((fulfillment.fulfiller_address, addr))
    return profile_handles


def get_ordinal_repr(num):
    """Handle cardinal to ordinal representation of numeric values.

    Args:
        num (int): The integer to be converted from cardinal to ordinal numerals.

    Returns:
        str: The ordinal representation of the provided integer.

    """
    ordinal_suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    if 10 <= num % 100 <= 20:
        suffix = 'th'
    else:
        suffix = ordinal_suffixes.get(num % 10, 'th')
    return f'{num}{suffix}'


def record_funder_inaction_on_fulfillment(bounty_fulfillment):
    payload = {
        'profile': bounty_fulfillment.bounty.bounty_owner_profile,
        'metadata': {
            'bounties': list(bounty_fulfillment.bounty.pk),
            'bounty_fulfillment_pk': bounty_fulfillment.pk,
            'needs_review': True
        }
    }
    Activity.objects.create(activity_type='bounty_abandonment_escalation_to_mods', bounty=bounty_fulfillment.bounty, **payload)


def record_user_action_on_interest(interest, event_name, last_heard_from_user_days):
    """Record User actions and activity for the associated Interest."""
    payload = {
        'profile': interest.profile,
        'metadata': {
            'bounties': list(interest.bounty_set.values_list('pk', flat=True)),
            'interest_pk': interest.pk,
            'last_heard_from_user_days': last_heard_from_user_days,
        }
    }
    UserAction.objects.create(action=event_name, **payload)

    if event_name in ['bounty_abandonment_escalation_to_mods', 'bounty_abandonment_warning']:
        payload['needs_review'] = True

    Activity.objects.create(activity_type=event_name, bounty=interest.bounty_set.last(), **payload)


def get_context(ref_object=None, github_username='', user=None, confirm_time_minutes_target=4,
                confirm_time_slow=120, confirm_time_avg=15, confirm_time_fast=1, active='',
                title='', update=None):
    """Get the context dictionary for use in view."""
    context = {
        'githubUsername': github_username,  # TODO: Deprecate this field.
        'action_urls': ref_object.action_urls() if hasattr(ref_object, 'action_urls') else None,
        'active': active,
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(confirm_time_slow),
        'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(confirm_time_avg),
        'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(confirm_time_fast),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'email': getattr(user, 'email', ''),
        'handle': getattr(user, 'username', ''),
        'title': title,
        'gas_advisories': gas_advisories(),
    }
    if ref_object is not None:
        context.update({f'{ref_object.__class__.__name__}'.lower(): ref_object})
    if update is not None and isinstance(update, dict):
        context.update(update)
    return context


def clean_bounty_url(url):
    """Clean the Bounty URL of unsavory characters.

    The primary utility of this method is to drop #issuecomment blocks from
    Github issue URLs copy/pasted via comments.

    Args:
        url (str): The Bounty VC URL.

    TODO:
        * Deprecate this in favor of Django forms.

    Returns:
        str: The cleaned Bounty URL.

    """
    try:
        return url.split('#')[0]
    except Exception:
        return url


def get_bounty_semaphore_ns(standard_bounty_id):
    return f'{SEMAPHORE_BOUNTY_NS}_{standard_bounty_id}_{SEMAPHORE_BOUNTY_SALT}'


def profile_helper(handle, suppress_profile_hidden_exception=False, current_user=None, disable_cache=False, full_profile=False):
    """Define the profile helper.

    Args:
        handle (str): The profile handle.

    Raises:
        DoesNotExist: The exception is raised if a Profile isn't found matching the handle.
            Remediation is attempted by syncing the profile data.
        MultipleObjectsReturned: The exception is raised if multiple Profiles are found.
            The latest Profile will be returned.

    Returns:
        dashboard.models.Profile: The Profile associated with the provided handle.

    """

    current_profile = getattr(current_user, 'profile', None)
    if current_profile and current_profile.handle == handle:
        return current_profile

    base = Profile.objects if not full_profile else Profile.objects_full
    try:
        if disable_cache:
            base = base.nocache()
        profile = base.get(handle=handle.lower())
    except Profile.DoesNotExist:
        profile = sync_profile(handle)
        if not profile:
            raise ProfileNotFoundException
    except Profile.MultipleObjectsReturned as e:
        # Handle edge case where multiple Profile objects exist for the same handle.
        # We should consider setting Profile.handle to unique.
        # TODO: Should we handle merging or removing duplicate profiles?
        profile = base.filter(handle=handle.lower()).latest('id')
        logging.error(e)

    if profile.hide_profile and not profile.is_org and not suppress_profile_hidden_exception:
        raise ProfileHiddenException

    return profile


def is_valid_eth_address(eth_address):
    return (bool(re.match(r"^0x[a-zA-Z0-9]{40}$", eth_address)) or eth_address == "0x0")


def get_tx_status(txid, network, created_on, chain='std'):
    status, timestamp, tx = get_tx_status_and_details(txid, network, created_on, chain=chain)
    return status, timestamp


def get_tx_status_and_details(txid, network, created_on, chain='std'):
    from django.utils import timezone

    import pytz
    from dashboard.utils import get_web3

    DROPPED_DAYS = 4

    # get status
    tx = {}
    status = None
    if txid == 'override':
        return 'success', None #overridden by admin
    try:
        web3 = get_web3(network, chain=chain)
        tx = web3.eth.getTransactionReceipt(txid)
        if not tx:
            drop_dead_date = created_on + timezone.timedelta(days=DROPPED_DAYS)
            if timezone.now() > drop_dead_date:
                status = 'dropped'
            else:
                status = 'pending'
        elif tx and 'status' not in tx.keys():
            if bool(tx['blockNumber']) and bool(tx['blockHash']):
                status = 'success'
            else:
                raise Exception("got a tx but no blockNumber or blockHash")
        elif tx.status == 1:
            status = 'success'
        elif tx.status == 0:
            status = 'error'
        else:
            status = 'unknown'
    except Exception as e:
        logger.debug(f'Failure in get_tx_status for {txid} - ({e})')
        status = 'unknown'

    # get timestamp
    timestamp = None
    try:
        if tx:
            block = web3.eth.getBlock(tx['blockNumber'])
            timestamp = block.timestamp
            timestamp = timezone.datetime.fromtimestamp(timestamp).replace(tzinfo=pytz.UTC)
    except:
        pass
    return status, timestamp, tx


def is_blocked(handle):
    # check admin block list
    is_on_blocked_list = BlockedUser.objects.filter(handle=handle.lower(), active=True).exists()
    if is_on_blocked_list:
        return True
    return False

def should_be_blocked(handle):
    # check banned country list
    profiles = Profile.objects.filter(handle=handle.lower())
    if profiles.exists():
        profile = profiles.first()
        last_login = profile.actions.filter(action='Login').order_by('pk').last()
        if last_login:
            last_login_country = last_login.location_data.get('country_name')
            if last_login_country:
                is_on_banned_countries = Country.objects.filter(name=last_login_country)
                if is_on_banned_countries:
                    return True

        # check banned entity list
        if profile.user:
            first_name = profile.user.first_name
            last_name = profile.user.last_name
            full_name = '{first_name} {last_name}'
            is_on_banned_user_list = Entity.objects.filter(fullName__icontains=full_name)
            if is_on_banned_user_list:
                return True

    return False


def get_nonce(network, address, ignore_db=False):
    # this function solves the problem of 2 pending tx's writing over each other
    # by checking both web3 RPC *and* the local DB for the nonce
    # and then using the higher of the two as the tx nonce
    from dashboard.utils import get_web3
    from perftools.models import JSONStore
    w3 = get_web3(network)

    # web3 RPC node: nonce
    nonce_from_web3 = w3.eth.getTransactionCount(address)
    if ignore_db:
        return nonce_from_web3

    # db storage
    key = f"nonce_{network}_{address}"
    view = 'get_nonce'
    nonce_from_db = 0
    try:
        nonce_from_db = JSONStore.objects.get(key=key, view=view).data[0]
        nonce_from_db += 1 # increment by 1 bc we need to be 1 higher than last txid
    except:
        pass

    new_nonce = max(nonce_from_db, nonce_from_web3)

    # update JSONStore
    JSONStore.objects.filter(key=key, view=view).all().delete()
    JSONStore.objects.create(key=key, view=view, data=[new_nonce])

    return new_nonce


def re_market_bounty(bounty, auto_save = True):
    remarketed_count = bounty.remarketed_count
    if remarketed_count < settings.RE_MARKET_LIMIT:
        now = timezone.now()
        minimum_wait_after_remarketing = bounty.last_remarketed + timezone.timedelta(minutes=settings.MINUTES_BETWEEN_RE_MARKETING) if bounty.last_remarketed else now
        if now >= minimum_wait_after_remarketing:
            bounty.remarketed_count = remarketed_count + 1
            bounty.last_remarketed = now

            if auto_save:
                bounty.save()

            result_msg = 'The issue will appear at the top of the issue explorer. '
            further_permitted_remarket_count = settings.RE_MARKET_LIMIT - bounty.remarketed_count
            if further_permitted_remarket_count >= 1:
                result_msg += f'You will be able to remarket this bounty {further_permitted_remarket_count} more time if a contributor does not pick this up.'
            elif further_permitted_remarket_count == 0:
                result_msg += 'Please note this is the last time the issue is able to be remarketed.'

            return {
                "success": True,
                "msg": result_msg
            }
        else:
            time_delta_wait_time = minimum_wait_after_remarketing - now
            minutes_to_wait = round(time_delta_wait_time.total_seconds() / 60)
            return {
                "success": False,
                "msg": f'As you recently remarketed this issue, you need to wait {minutes_to_wait} minutes before remarketing this issue again.'
            }
    else:
        return {
            "success": False,
            "msg": f'The issue was not remarketed due to reaching the remarket limit ({settings.RE_MARKET_LIMIT}).'
        }


def apply_new_bounty_deadline(bounty, deadline, auto_save = True):
    bounty.expires_date = timezone.make_aware(
        timezone.datetime.fromtimestamp(deadline),
        timezone=UTC)
    result = re_market_bounty(bounty, False)

    if auto_save:
        bounty.save()

    base_result_msg = "You've extended expiration of this issue."
    result['msg'] = base_result_msg + " " + result['msg']

    return result


def release_bounty_to_the_public(bounty, auto_save = True):
    if bounty:
        bounty.reserved_for_user_handle = None
        bounty.reserved_for_user_from = None
        bounty.reserved_for_user_expiration = None

        if auto_save:
            bounty.save()

        return True
    else:
        return False


def get_orgs_perms(profile):
    orgs = profile.profile_organizations.all()

    response_data = []
    for org in orgs:
        org_perms = {'name': org.name, 'users': []}
        groups = org.groups.all().filter(user__isnull=False)
        for g in groups: # "admin", "write", "pull", "none"
            group_data = g.name.split('-')
            if group_data[1] != "role": #skip repo level groups
                continue
            org_perms['users'] = [{
                'handle': u.profile.handle,
                'role': group_data[2],
                'name': '{} {}'.format(u.first_name, u.last_name)
            } for u in g.user_set.prefetch_related('profile').all()]
        response_data.append(org_perms)
    return response_data

def get_all_urls():
    urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])

    def list_urls(lis, acc=None):
        if acc is None:
            acc = []
        if not lis:
            return
        l = lis[0]
        if isinstance(l, URLPattern):
            yield acc + [str(l.pattern)]
        elif isinstance(l, URLResolver):
            yield from list_urls(l.url_patterns, acc + [str(l.pattern)])

        yield from list_urls(lis[1:], acc)

    return list_urls(urlconf.urlpatterns)

def get_url_first_indexes():

    return ['_administration','about','action','actions','activity','api','avatar','blog','bounties','bounty','btctalk','casestudies','casestudy','chat','community','contributor','contributor_dashboard','credit','dashboard','docs','dynamic','explorer','extension','fb','feedback','funder','funder_dashboard','funding','gas','ghlogin','github','gitter','grant','grants','hackathon','hackathonlist','hackathons','health','help','home','how','impersonate','inbox','interest','issue','itunes','jobs','jsi18n','kudos','l','labs','landing','lazy_load_kudos','lbcheck','leaderboard','legacy','legal','livestream','login','logout','mailing_list','medium','mission','modal','new','not_a_token','o','onboard','podcast','postcomment','press','presskit','products','profile','quests','reddit','refer','register_hackathon','requestincrease','requestmoney','requests','results','revenue','robotstxt','schwag','send','service','settings','sg_sendgrid_event_processor','sitemapsectionxml','sitemapxml','slack','spec','strbounty_network','submittoken','sync','terms','tip','townsquare','tribe','tribes','twitter','users','verified','vision','wallpaper','wallpapers','web3','whitepaper','wiki','wikiazAZ09azdAZdazd','youtube']
    # TODO: figure out the recursion issue with the URLs at a later date
    # or just cache them in the backend dynamically

    urls = []
    for p in get_all_urls():
        url = p[0].split('/')[0]
        url = re.sub(r'\W+', '', url)
        urls.append(url)

    return set(urls)

def get_custom_avatars(profile):
    return CustomAvatar.objects.filter(profile=profile).order_by('-id')


def _trim_null_address(address):
    if address == '0x0000000000000000000000000000000000000000':
        return '0x0'
    else:
        return address


def _construct_transfer_filter_params(
        recipient_address,
        token_address,):

    event_topic = keccak(text="Transfer(address,address,uint256)")

    # [event, from, to]
    topics = [
        to_hex(event_topic),
        None,
        to_hex(encode_single('address', recipient_address))
    ]

    return {
        "topics": topics,
        "fromBlock": 0,
        "toBlock": "latest",
        "address": token_address,
    }


def _extract_sender_address_from_log(log):
    return decode_single("address", log['topics'][1])


def get_token_recipient_senders(network, recipient_address, token_address):
    w3 = get_web3(network)

    contract = w3.eth.contract(
        address=token_address,
        abi=erc20_abi,
    )

    # TODO: This can be made less brittle/opaque
    # see usage of contract.events.Transfer.getLogs in
    # commit 99a44cd3036ace8fcd886ed1e96747528f105d10
    # after migrating to web3 >= 5.
    filter_params = _construct_transfer_filter_params(
        recipient_address,
        token_address,
    )

    logs = w3.eth.getLogs(filter_params)

    process_log = compose(
        _trim_null_address,
        _extract_sender_address_from_log
    )

    return [process_log(log) for log in logs]


def get_hackathons_page_default_tabs():
    from perftools.models import JSONStore

    return JSONStore.objects.get(key='hackathons', view='hackathons').data[0]


def get_hackathon_events():
    from perftools.models import JSONStore

    return JSONStore.objects.get(key='hackathons', view='hackathons').data[1]


def set_hackathon_event(type, event):
    return {
        'type': type,
        'name': event.name,
        'slug': event.slug,
        'background_color': event.background_color,
        'logo': event.logo.name or event.logo_svg.name,
        'start_date': event.start_date.isoformat(),
        'end_date': event.end_date.isoformat(),
        'summary': event.hackathon_summary,
        'sponsor_profiles': [
            {
                'absolute_url': sponsor.absolute_url,
                'avatar_url': sponsor.avatar_url,
                'handle': sponsor.handle,
            }
            for sponsor in event.sponsor_profiles.all()
        ],
        'display_showcase': event.display_showcase,
        'show_results': event.show_results,
    }


def tx_id_to_block_explorer_url(txid, network):
    if network == 'xdai':
        return f"https://blockscout.com/xdai/mainnet/tx/{txid}"
    if network == 'mainnet':
        return f"https://etherscan.io/tx/{txid}"
    return f"https://{network}.etherscan.io/tx/{txid}"
