# -*- coding: utf-8 -*-
'''
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

'''
from __future__ import print_function, unicode_literals

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.search import SearchVector
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import redirect

from .models import Token, Wallet, KudosTransfer
from dashboard.models import Profile, Activity
from dashboard.utils import get_web3
from dashboard.views import record_user_action
from avatar.models import Avatar
from .forms import KudosSearchForm
import re

from dashboard.notifications import maybe_market_kudos_to_email

import json
from ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from git.utils import get_emails_master, get_github_primary_email
from retail.helpers import get_ip
from web3 import Web3
from eth_utils import to_checksum_address, to_normalized_address
from .helpers import reconcile_kudos_preferred_wallet

from .utils import KudosContract

import logging

logger = logging.getLogger(__name__)

confirm_time_minutes_target = 4


def get_profile(handle):
    try:
        to_profile = Profile.objects.get(handle__iexact=handle)
    except Profile.MultipleObjectsReturned:
        to_profile = Profile.objects.filter(handle__iexact=handle).order_by('-created_on').first()
    except Profile.DoesNotExist:
        to_profile = None
    return to_profile


def about(request):
    """Render the about kudos response."""
    context = {
        'is_outside': True,
        'active': 'kudos-about',
        'title': 'Kudos | About',
        'card_title': _('About Kudos | Gitcoin '),
        'card_desc': _('Each Kudos is a unique work of art.. It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos-flower.gif'),
        "listings": Token.objects.all(),
    }
    return TemplateResponse(request, 'kudos_about.html', context)


def marketplace(request):
    """Render the marketplace kudos response."""
    q = request.GET.get('q')
    logger.info(q)

    results = Token.objects.annotate(
        search=SearchVector('name', 'description', 'tags')
    ).filter(num_clones_allowed__gt=0, search=q)
    logger.info(results)

    if results:
        listings = results
    else:
        listings = Token.objects.filter(num_clones_allowed__gt=0)
    context = {
        'is_outside': True,
        'active': 'marketplace',
        'title': 'Kudos | Marketplace',
        'card_title': _('Kudos Marketplace | Gitcoin '),
        'card_desc': _('Each Kudos is a unique work of art.. It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos-flower.gif'),
        'listings': listings
    }

    return TemplateResponse(request, 'kudos_marketplace.html', context)


def search(request):
    context = {}
    logger.info(request.GET)

    if request.method == 'GET':
        form = KudosSearchForm(request.GET)
        context = {'form': form}

    return TemplateResponse(request, 'kudos_marketplace.html', context)


def details(request):
    """Render the detail kudos response."""
    kudos_id = request.path.split('/')[-1]
    logger.info(f'kudos id: {kudos_id}')

    if not re.match(r'\d+', kudos_id):
        raise ValueError(f'Invalid Kudos ID found.  ID is not a number:  {kudos_id}')

    # Find other profiles that have the same kudos name
    kudos = Token.objects.get(pk=kudos_id)
    # Find other Kudos rows that are the same kudos.name, but of a different owner
    related_kudos = Token.objects.exclude(
        owner_address='0xD386793F1DB5F21609571C0164841E5eA2D33aD8').filter(name=kudos.name)
    logger.info(f'Related Kudos Tokens: {related_kudos}')
    # Find the Wallet rows that match the Kudos.owner_addresses
    # related_wallets = Wallet.objects.filter(address__in=[rk.owner_address for rk in related_kudos]).distinct()[:20]

    # Find the related Profiles assuming the preferred_payout_address is the kudos owner address.
    # Note that preferred_payout_address is most likely in normalized form.
    # https://eth-utils.readthedocs.io/en/latest/utilities.html#to-normalized-address-value-text
    related_profiles = Profile.objects.filter(preferred_payout_address__in=[to_normalized_address(rk.owner_address) for rk in related_kudos]).distinct()[:20]
    # profile_ids = [rw.profile_id for rw in related_wallets]
    logger.info(f'Related Profiles:  {related_profiles}')

    # Avatar can be accessed via Profile.avatar
    # related_profiles = Profile.objects.filter(pk__in=profile_ids).distinct()

    context = {
        'is_outside': True,
        'active': 'details',
        'title': 'Kudos | Details',
        'card_title': _('Kudos Details | Gitcoin '),
        'card_desc': _('Each Kudos is a unique work of art.. It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos-flower.gif'),
        'kudos': kudos,
        'related_profiles': related_profiles,
    }
    if kudos:
        context['title'] = kudos.name
        context['card_title'] = kudos.name
        context['card_desc'] = kudos.description
        context['avatar_url'] = kudos.image

    return TemplateResponse(request, 'kudos_details.html', context)


def mint(request):
    context = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'kudos_mint.html', context)


def get_user_request_info(request):
    """ Returns """
    pass


def get_primary_from_email(params, request):
    """Find the primary_from_email address.  This function finds the address using this priority:
        1. If the email field is filed out in the Send POST request, use the `fromEmail` field.
        2. If the user is logged in, they should have an email address associated with thier account.
           Use this as the second option.  `request_user_email`.
        3. If all else fails, attempt to pull the email from the user's github account.

    Args:
        params (dict): A dictionary parsed form the POST request.  Typically this is a POST
                       request coming in from a Tips/Kudos send.

    Returns:
        str: The primary_from_email string.
    """

    request_user_email = request.user.email if request.user.is_authenticated else ''
    logger.info(request.user.profile)
    access_token = request.user.profile.get_access_token() if request.user.is_authenticated else ''

    if params.get('fromEmail'):
        primary_from_email = params['fromEmail']
    elif request_user_email:
        primary_from_email = request_user_email
    elif access_token:
        primary_from_email = get_github_primary_email(access_token)
    else:
        primary_from_email = 'unknown@gitcoin.co'

    return primary_from_email


def get_to_emails(params):
    """Get a list of email address to send the alert to, in this priority:

        1. get_emails_master() pulls email addresses from the user's public Github account.
        2. If an email address is included in the Tips/Kudos form, append that to the email list.


    Args:
        params (dict): A dictionary parsed form the POST request.  Typically this is a POST
                       request coming in from a Tips/Kudos send.

    Returns:
        list: An array of email addresses to send the email to.
    """
    to_emails = []

    to_username = params['username'].lstrip('@')
    to_emails = get_emails_master(to_username)

    if params.get('email'):
        to_emails.append(params['email'])

    return list(set(to_emails))


def kudos_preferred_wallet(request, handle):
    """returns the address, if any, that someone would like to be send kudos directly to.

    Returns:
        list of addresse

    """
    response = {
        'addresses': []
    }

    profile = get_profile(str(handle).replace('@', ''))

    if profile:
        # reconcile_kudos_preferred_wallet(profile)
        if profile.preferred_payout_address:
            response['addresses'].append(profile.preferred_payout_address)

    return JsonResponse(response)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def tipee_address(request, handle):
    """returns the address, if any, that someone would like to be tipped directly at

    Returns:
        list of addresse

    """
    response = {
        'addresses': []
    }
    profile = get_profile(str(handle).replace('@', ''))
    if profile and profile.preferred_payout_address:
        response['addresses'].append(profile.preferred_payout_address)
    return JsonResponse(response)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_2(request):
    """ Handle the first start of the Kudos email send.
    This form is filled out before the 'send' button is clicked.
    """

    kudos_name = request.GET.get('name')
    kudos = Token.objects.filter(name=kudos_name, num_clones_allowed__gt=0).first()
    profiles = Profile.objects.all()

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': getattr(request.user, 'email', ''),
        'from_handle': request.user.username,
        'title': 'Send Kudos | Gitcoin',
        'card_desc': 'Send a Kudos to any github user at the click of a button.',
        'kudos': kudos,
        'profiles': profiles
    }

    return TemplateResponse(request, 'transaction/send.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_3(request):
    """ This function is derived from send_tip_3.
    Handle the third stage of sending a kudos (the POST).  The request to send the kudos is
    added to the database, but the transaction has not happened yet.  The txid is added
    in `send_kudos_4`.

    Returns:
        JsonResponse: response with success state.

    """
    response = {
        'status': 'OK',
        'message': _('Kudos Created'),
    }

    params = json.loads(request.body)

    from_username = request.user.username
    from_email = get_primary_from_email(params, request)

    to_username = params['username'].lstrip('@')
    to_emails = get_to_emails(params)

    # Validate that the token exists on the back-end
    kudos_token = Token.objects.filter(name=params['kudosName'], num_clones_allowed__gt=0).first()
    # db mutations
    kudos_email = KudosTransfer.objects.create(
        emails=to_emails,
        # For kudos, `token` is a kudos.models.Token instance.
        kudos_token=kudos_token,
        amount=params['amount'],
        comments_public=params['comments_public'],
        ip=get_ip(request),
        github_url=params['github_url'],
        from_name=params['from_name'],
        from_email=from_email,
        from_username=from_username,
        username=params['username'],
        network=params['network'],
        tokenAddress=params['tokenAddress'],
        from_address=params['from_address'],
        is_for_bounty_fulfiller=params['is_for_bounty_fulfiller'],
        metadata=params['metadata'],
        recipient_profile=get_profile(to_username),
        sender_profile=get_profile(from_username),
    )

    return JsonResponse(response)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_4(request):
    """ Handle the fourth stage of sending a tip (the POST).  Once the metamask transaction is complete,
        add it to the database.

    Returns:
        JsonResponse: response with success state.

    """
    response = {
        'status': 'OK',
        'message': _('Kudos Sent'),
    }

    params = json.loads(request.body)

    from_username = request.user.username

    txid = params['txid']
    destinationAccount = params['destinationAccount']
    is_direct_to_recipient = params.get('is_direct_to_recipient', False)
    if is_direct_to_recipient:
        kudos_email = KudosTransfer.objects.get(
            metadata__direct_address=destinationAccount,
            metadata__creation_time=params['creation_time'],
            metadata__salt=params['salt'],
        )
    else:
        kudos_email = KudosTransfer.objects.get(
            metadata__address=destinationAccount,
            metadata__salt=params['salt'],
        )

    # Return Permission Denied if not authenticated
    is_authenticated_for_this_via_login = (kudos_email.from_username and kudos_email.from_username == from_username)
    is_authenticated_for_this_via_ip = kudos_email.ip == get_ip(request)
    is_authed = is_authenticated_for_this_via_ip or is_authenticated_for_this_via_login
    if not is_authed:
        response = {
            'status': 'error',
            'message': _('Permission Denied'),
        }
        return JsonResponse(response)

    # Save the txid to the database once it has been confirmed in MetaMask.  If there is no txid,
    # it means that the user never went through with the transaction.
    kudos_email.txid = txid
    if is_direct_to_recipient:
        kudos_email.receive_txid = txid
    kudos_email.save()

    # Update kudos.models.Token to reflect the newly cloned Kudos
    if kudos_email.network == 'custom network':
        network = 'localhost'
    kudos_contract = KudosContract(network)
    kudos_contract.sync_db()

    # notifications
    # maybe_market_tip_to_github(kudos_email)
    # maybe_market_tip_to_slack(kudos_email, 'new_tip')
    maybe_market_kudos_to_email(kudos_email)
    # record_user_action(kudos_email.from_username, 'send_kudos', kudos_email)
    # record_tip_activity(kudos_email, kudos_email.from_username, 'new_kudos' if kudos_email.username else 'new_crowdfund')

    return JsonResponse(response)


def record_kudos_email_activity(kudos_email, github_handle, event_name):
    kwargs = {
        'activity_type': event_name,
        'kudos_email': kudos_email,
        'metadata': {
            'amount': str(kudos_email.amount),
            'token_name': kudos_email.tokenName,
            'value_in_eth': str(kudos_email.value_in_eth),
            'value_in_usdt_now': str(kudos_email.value_in_usdt_now),
            'github_url': kudos_email.github_url,
            'to_username': kudos_email.username,
            'from_name': kudos_email.from_name,
            'received_on': str(kudos_email.received_on) if kudos_email.received_on else None
        }
    }
    try:
        kwargs['profile'] = Profile.objects.get(handle=github_handle)
    except Profile.MultipleObjectsReturned:
        kwargs['profile'] = Profile.objects.filter(handle__iexact=github_handle).first()
    except Profile.DoesNotExist:
        logging.error(f"error in record_kudos_email_activity: profile with github name {github_handle} not found")
        return
    try:
        kwargs['bounty'] = kudos_email.bounty
    except:
        pass

    try:
        Activity.objects.create(**kwargs)
    except Exception as e:
        logging.error(f"error in record_kudos_email_activity: {e} - {event_name} - {kudos_email} - {github_handle}")


def receive(request, key, txid, network):
    """Handle the receiving of a kudos (the POST)

    Returns:
        TemplateResponse: the UI with the kudos confirmed

    """

    if request.method == 'POST':
        logger.info('method is post')

    these_kudos_emails = KudosTransfer.objects.filter(web3_type='v3', txid=txid, network=network)
    kudos_emails = these_kudos_emails.filter(metadata__reference_hash_for_receipient=key) | these_kudos_emails.filter(
        metadata__reference_hash_for_funder=key)
    kudos_email = kudos_emails.first()
    is_authed = request.user.username == kudos_email.username or request.user.username == kudos_email.from_username
    not_mined_yet = get_web3(kudos_email.network).eth.getBalance(
        Web3.toChecksumAddress(kudos_email.metadata['address'])) == 0

    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
        request.user, 'profile', None
    ):
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect
    elif kudos_email.receive_txid:
        messages.info(request, 'This kudos has been received')
    elif not is_authed:
        messages.error(
            request, f'This kudos is for {kudos_email.username} but you are logged in as {request.user.username}.  Please logout and log back in as {kudos_email.username}.')
    elif not_mined_yet:
        messages.info(
            request, f'This tx {kudos_email.txid}, is still mining.  Please wait a moment before submitting the receive form.')
    elif request.GET.get('receive_txid') and not kudos_email.receive_txid:
        params = request.GET

        # db mutations
        try:
            if params['save_addr']:
                profile = get_profile(kudos_email.username)
                if profile:
                    # TODO: Does this mean that the address the user enters in the receive form
                    # Will overwrite an already existing preferred_payout_address?  Should we
                    # ask the user to confirm this?
                    profile.preferred_payout_address = params['forwarding_address']
                    profile.save()
            kudos_email.receive_txid = params['receive_txid']
            kudos_email.receive_address = params['forwarding_address']
            kudos_email.received_on = timezone.now()
            kudos_email.save()
            record_user_action(kudos_email.from_username, 'receive_kudos', kudos_email)
            record_kudos_email_activity(kudos_email, kudos_email.username, 'receive_kudos')
            messages.success(request, 'This tip has been received')
        except Exception as e:
            messages.error(request, str(e))
            logger.exception(e)

    logger.info(kudos_email.kudos_token.name)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'receive',
        'title': _('Receive Kudos'),
        'gas_price': round(recommend_min_gas_price_to_confirm_in_time(120), 1),
        'kudos_email': kudos_email,
        'key': key,
        'is_authed': is_authed,
        'disable_inputs': kudos_email.receive_txid or not_mined_yet or not is_authed,
    }

    return TemplateResponse(request, 'transaction/receive.html', params)
