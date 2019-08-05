# -*- coding: utf-8 -*-
"""Define view for the Kudos app.

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
import logging
import random
import re
import urllib.parse

from django.conf import settings
from django.contrib import messages
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Activity, Profile
from dashboard.notifications import maybe_market_kudos_to_email, maybe_market_kudos_to_github
from dashboard.utils import get_nonce, get_web3
from dashboard.views import record_user_action
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from git.utils import get_emails_by_category, get_emails_master, get_github_primary_email
from kudos.utils import kudos_abi
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from web3 import Web3

from .forms import KudosSearchForm
from .helpers import get_token
from .models import BulkTransferCoupon, BulkTransferRedemption, KudosTransfer, Token, TransferEnabledFor

logger = logging.getLogger(__name__)

confirm_time_minutes_target = 4


def get_profile(handle):
    """Get the gitcoin profile.
    TODO:  This might be depreacted in favor of the sync_profile function in the future.

    Args:
        handle (str): The github handle.

    Returns:
        obj: The profile model object.
    """
    try:
        to_profile = Profile.objects.get(handle__iexact=handle)
    except Profile.MultipleObjectsReturned:
        to_profile = Profile.objects.filter(handle__iexact=handle).order_by('-created_on').first()
    except Profile.DoesNotExist:
        to_profile = None
    return to_profile


def about(request):
    """Render the Kudos 'about' page."""
    activity_limit = 5
    listings = Token.objects.select_related('contract').filter(
        num_clones_allowed__gt=0,
        contract__is_latest=True,
        contract__network=settings.KUDOS_NETWORK,
        hidden=False,
    ).order_by('-popularity_week').cache()
    activities = Activity.objects.filter(
        activity_type='new_kudos',
    ).order_by('-created').cache()[0:activity_limit]

    context = {
        'is_outside': True,
        'active': 'about',
        'activities': [a.view_props for a in activities],
        'title': 'Kudos',
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos/assets/kudos-image.png'),
        'card_player_override': 'https://www.youtube.com/embed/EOlMTOzmKKk',
        'card_player_stream_override': static('v2/card/kudos.mp4'),
        'card_player_thumb_override': static('v2/card/kudos.png'),
        "listings": listings
    }
    return TemplateResponse(request, 'kudos_about.html', context)


def marketplace(request):
    """Render the Kudos 'marketplace' page."""
    q = request.GET.get('q')
    order_by = request.GET.get('order_by', '-created_on')
    title = str(_('Kudos Marketplace'))
    network = request.GET.get('network', settings.KUDOS_NETWORK)

    # Only show the latest contract Kudos for the current network.
    query_kwargs = {
        'num_clones_allowed__gt': 0,
        'contract__is_latest': True,
        'contract__network': network,
    }
    token_list = Token.objects.select_related('contract').visible().filter(**query_kwargs)

    if q:
        title = f'{q.title()} Kudos'
        token_list = token_list.keyword(q)

    listings = token_list.order_by(order_by).cache()
    context = {
        'is_outside': True,
        'active': 'marketplace',
        'title': title,
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos/assets/kudos-image.png'),
        'listings': listings,
        'network': network
    }
    return TemplateResponse(request, 'kudos_marketplace.html', context)


def search(request):
    """Render the search page.

    TODO:  This might no longer be used.

    """
    context = {}

    if request.method == 'GET':
        form = KudosSearchForm(request.GET)
        context = {'form': form}

    return TemplateResponse(request, 'kudos_marketplace.html', context)


def image(request, kudos_id, name):
    kudos = Token.objects.get(pk=kudos_id)
    img = kudos.as_img
    if not img:
        raise Http404

    response = HttpResponse(img.getvalue(), content_type='image/png')
    return response


def details_by_address_and_token_id(request, address, token_id, name):
    kudos = get_token(token_id=token_id, network=settings.KUDOS_NETWORK, address=address)
    return redirect(f'/kudos/{kudos.id}/{kudos.name}')


def details(request, kudos_id, name):
    """Render the Kudos 'detail' page."""
    if not re.match(r'\d+', kudos_id):
        raise ValueError(f'Invalid Kudos ID found.  ID is not a number:  {kudos_id}')

    # Find other profiles that have the same kudos name
    kudos = get_object_or_404(Token, pk=kudos_id)
    num_kudos_limit = 100

    context = {
        'send_enabled': kudos.send_enabled_for(request.user),
        'is_outside': True,
        'active': 'details',
        'title': 'Details',
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos/assets/kudos-image.png'),
        'kudos': kudos,
        'related_handles': list(set(kudos.owners_handles))[:num_kudos_limit],
    }
    if kudos:
        token = Token.objects.select_related('contract').get(
            token_id=kudos.cloned_from_id,
            contract__address=kudos.contract.address,
        )
        # The real num_cloned_in_wild is only stored in the Gen0 Kudos token
        kudos.num_clones_in_wild = token.num_clones_in_wild
        # Create a new attribute to reference number of gen0 clones allowed
        kudos.num_gen0_clones_allowed = token.num_clones_allowed

        context['title'] = kudos.ui_name
        context['card_title'] = kudos.humanized_name
        context['card_desc'] = kudos.description
        context['avatar_url'] = kudos.img_url
        context['kudos'] = kudos
        if not kudos.send_enabled_for_non_gitcoin_admins:
            context['send_enabled_for'] = TransferEnabledFor.objects.filter(token=kudos)

    return TemplateResponse(request, 'kudos_details.html', context)


def mint(request):
    """Render the Kudos 'mint' page.  This is mostly a placeholder for future functionality."""
    return TemplateResponse(request, 'kudos_mint.html', {})


def get_primary_from_email(params, request):
    """Find the primary_from_email address.  This function finds the address using this priority:

    1. If the email field is filed out in the Send POST request, use the `fromEmail` field.
    2. If the user is logged in, they should have an email address associated with their account.
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


def kudos_preferred_wallet(request, handle):
    """Returns the address, if any, that someone would like to be send kudos directly to."""
    response = {'addresses': []}
    profile = get_profile(str(handle).replace('@', ''))

    if profile and profile.preferred_payout_address:
        response['addresses'].append(profile.preferred_payout_address)

    return JsonResponse(response)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_2(request):
    """Handle the first start of the Kudos email send.

    This form is filled out before the 'send' button is clicked.

    """
    if not request.user.is_authenticated or request.user.is_authenticated and not getattr(request.user, 'profile', None):
        return redirect('/login/github?next=' + request.get_full_path())

    _id = request.GET.get('id')
    if _id and not str(_id).isdigit():
        raise Http404

    kudos = Token.objects.filter(pk=_id).first()
    if kudos and not kudos.send_enabled_for(request.user):
        messages.error(request, f'This kudos is not available to be sent.')
        return redirect(kudos.url)

    params = {
        'active': 'send',
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': getattr(request.user, 'email', ''),
        'from_handle': request.user.username,
        'title': _('Send Kudos | Gitcoin'),
        'card_desc': _('Send a Kudos to any github user at the click of a button.'),
        'numbers': range(1,100),
        'kudos': kudos,
    }
    return TemplateResponse(request, 'transaction/send.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_3(request):
    """Handle the third stage of sending a kudos (the POST).

    This function is derived from send_tip_3.
    The request to send the kudos is added to the database, but the transaction
    has not happened yet.  The txid is added in `send_kudos_4`.

    Returns:
        JsonResponse: The response with success state.

    """
    response = {
        'status': 'OK',
        'message': _('Kudos Created'),
    }

    is_user_authenticated = request.user.is_authenticated
    from_username = request.user.username if is_user_authenticated else ''
    primary_from_email = request.user.email if is_user_authenticated else ''
    access_token = request.user.profile.get_access_token() if is_user_authenticated and request.user.profile else ''

    params = json.loads(request.body)

    to_username = params.get('username', '').lstrip('@')
    to_emails = get_emails_by_category(to_username)
    primary_email = ''

    if params.get('email'):
        primary_email = params['email']
    elif to_emails.get('primary', None):
        primary_email = to_emails['primary']
    elif to_emails.get('github_profile', None):
        primary_email = to_emails['github_profile']
    else:
        if len(to_emails.get('events', None)):
            primary_email = to_emails['events'][0]
        else:
            print("TODO: no email found.  in the future, we should handle this case better because it's GOING to end up as a support request")
    if primary_email and isinstance(primary_email, list):
        primary_email = primary_email[0]

    # If no primary email in session, try the POST data. If none, fetch from GH.
    primary_from_email = params.get('fromEmail')

    if access_token and not primary_from_email:
        primary_from_email = get_github_primary_email(access_token)

    # Validate that the token exists on the back-end
    kudos_id = params.get('kudosId')
    if not kudos_id:
        raise Http404

    try:
        kudos_token_cloned_from = Token.objects.get(pk=kudos_id)
    except Token.DoesNotExist:
        raise Http404

    # db mutations
    kt = KudosTransfer.objects.create(
        primary_email=primary_email,
        emails=to_emails,
        # For kudos, `token` is a kudos.models.Token instance.
        kudos_token_cloned_from=kudos_token_cloned_from,
        amount=params['amount'],
        comments_public=params['comments_public'],
        ip=get_ip(request),
        github_url=params['github_url'],
        from_name=params['from_name'],
        from_email=params['from_email'],
        from_username=from_username,
        username=params['username'],
        network=params['network'],
        tokenAddress=params.get('tokenAddress', ''),
        from_address=params['from_address'],
        is_for_bounty_fulfiller=params['is_for_bounty_fulfiller'],
        metadata=params['metadata'],
        recipient_profile=get_profile(to_username),
        sender_profile=get_profile(from_username),
    )

    if params.get('send_type') == 'airdrop' and is_user_authenticated:
        num_redemptions = params['num_redemptions']
        if not params.get('pk'):
            raise Exception('You must provide a pk')

        btc = BulkTransferCoupon.objects.create(
            token=kudos_token_cloned_from,
            num_uses_remaining=num_redemptions,
            num_uses_total=num_redemptions,
            current_uses=0,
            secret=random.randint(10**19, 10**20),
            comments_to_put_in_kudos_transfer=params['comments_public'],
            sender_address=params['metadata']['address'],
            sender_pk=params.get('pk'),
            sender_profile=get_profile(from_username),
            )
        response['url'] = btc.url

    return JsonResponse(response)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_4(request):
    """Handle the fourth stage of sending a tip (the POST).

    Once the metamask transaction is complete, add it to the database.

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
    destination_account = params['destinationAccount']
    is_direct_to_recipient = params.get('is_direct_to_recipient', False)
    kudos_transfer = KudosTransfer.objects.get(
        metadata__address=destination_account,
        metadata__creation_time=params['creation_time'],
        metadata__salt=params['salt'],
    )

    # Return Permission Denied if not authenticated
    is_authenticated_via_login = (kudos_transfer.from_username and kudos_transfer.from_username == from_username)
    is_authenticated_for_this_via_ip = kudos_transfer.ip == get_ip(request)
    is_authed = is_authenticated_for_this_via_ip or is_authenticated_via_login

    if not is_authed:
        return JsonResponse({'status': 'error', 'message': _('Permission Denied')}, status=401)

    # Save the txid to the database once it has been confirmed in MetaMask.  If there is no txid,
    # it means that the user never went through with the transaction.
    kudos_transfer.txid = txid
    kudos_transfer.tx_status = 'pending'
    if is_direct_to_recipient:
        kudos_transfer.receive_txid = txid
        kudos_transfer.receive_tx_status = 'pending'
    kudos_transfer.save()

    # notifications
    maybe_market_kudos_to_email(kudos_transfer)
    maybe_market_kudos_to_github(kudos_transfer)
    record_kudos_activity(
        kudos_transfer,
        kudos_transfer.from_username,
        'new_kudos',
    )
    return JsonResponse(response)


def record_kudos_email_activity(kudos_transfer, github_handle, event_name):
    kwargs = {
        'activity_type': event_name,
        'kudos_transfer': kudos_transfer,
        'metadata': {
            'amount': str(kudos_transfer.amount),
            'token_name': kudos_transfer.tokenName,
            'value_in_eth': str(kudos_transfer.value_in_eth),
            'value_in_usdt_now': str(kudos_transfer.value_in_usdt_now),
            'github_url': kudos_transfer.github_url,
            'to_username': kudos_transfer.username,
            'from_name': kudos_transfer.from_name,
            'received_on': str(kudos_transfer.received_on) if kudos_transfer.received_on else None
        }
    }
    try:
        github_handle = github_handle.lstrip('@')
        kwargs['profile'] = Profile.objects.get(handle=github_handle)
    except Profile.MultipleObjectsReturned:
        kwargs['profile'] = Profile.objects.filter(handle__iexact=github_handle).first()
    except Profile.DoesNotExist:
        logger.warning(f"error in record_kudos_email_activity: profile with github name {github_handle} not found")
        return
    try:
        kwargs['bounty'] = kudos_transfer.bounty
    except KudosTransfer.DoesNotExist:
        logger.info('No bounty is associated with this kudos transfer.')

    try:
        Activity.objects.create(**kwargs)
    except Exception as e:
        logger.debug(f"error in record_kudos_email_activity: {e} - {event_name} - {kudos_transfer} - {github_handle}")


def record_kudos_activity(kudos_transfer, github_handle, event_name):
    logger.debug(kudos_transfer)
    kwargs = {
        'activity_type': event_name,
        'kudos': kudos_transfer,
        'metadata': {
            'amount': str(kudos_transfer.amount),
            'token_name': kudos_transfer.tokenName,
            'value_in_eth': str(kudos_transfer.value_in_eth),
            'value_in_usdt_now': str(kudos_transfer.value_in_usdt_now),
            'github_url': kudos_transfer.github_url,
            'to_username': kudos_transfer.username,
            'from_name': kudos_transfer.from_name,
            'received_on': str(kudos_transfer.received_on) if kudos_transfer.received_on else None
        }
    }

    try:
        kwargs['profile'] = Profile.objects.get(handle__iexact=github_handle)
    except Profile.MultipleObjectsReturned:
        kwargs['profile'] = Profile.objects.filter(handle__iexact=github_handle).first()
    except Profile.DoesNotExist:
        logging.error(f"error in record_kudos_activity: profile with github name {github_handle} not found")
        return

    try:
        if kudos_transfer.bounty:
            kwargs['bounty'] = kudos_transfer.bounty
    except Exception:
        pass

    try:
        Activity.objects.create(**kwargs)
    except Exception as e:
        logging.error(f"error in record_kudos_activity: {e} - {event_name} - {kudos_transfer} - {github_handle}")


def receive(request, key, txid, network):
    """Handle the receiving of a kudos (the POST).

    Returns:
        TemplateResponse: the UI with the kudos confirmed

    """
    these_kudos_transfers = KudosTransfer.objects.filter(web3_type='v3', txid=txid, network=network)
    kudos_transfers = these_kudos_transfers.filter(
        Q(metadata__reference_hash_for_receipient=key) |
        Q(metadata__reference_hash_for_funder=key)
    )
    kudos_transfer = kudos_transfers.first()
    if not kudos_transfer:
        raise Http404

    is_authed = kudos_transfer.trust_url or request.user.username.replace('@', '').lower() in [
        kudos_transfer.username.replace('@', '').lower(),
        kudos_transfer.from_username.replace('@', '').lower()
    ]
    not_mined_yet = get_web3(kudos_transfer.network).eth.getBalance(
        Web3.toChecksumAddress(kudos_transfer.metadata['address'])) == 0
    did_fail = False
    if not_mined_yet:
        kudos_transfer.update_tx_status()
        did_fail = kudos_transfer.tx_status in ['dropped', 'unknown', 'na', 'error']

    if not kudos_transfer.trust_url:
        if not request.user.is_authenticated or request.user.is_authenticated and not getattr(
            request.user, 'profile', None
        ):
            login_redirect = redirect('/login/github?next=' + request.get_full_path())
            return login_redirect

    if kudos_transfer.receive_txid:
        messages.info(request, _('This kudos has been received'))
    elif not is_authed:
        messages.error(
            request, f'This kudos is for {kudos_transfer.username} but you are logged in as {request.user.username}.  Please logout and log back in as {kudos_transfer.username}.')
    elif did_fail:
        messages.info(request, f'This tx {kudos_transfer.txid}, failed.  Please contact the sender and ask them to send the tx again.')
    elif not_mined_yet and not request.GET.get('receive_txid'):
        message = mark_safe(
            f'The <a href="https://etherscan.io/tx/{txid}">transaction</a> is still mining.  '
            'Please wait a moment before submitting the receive form.'
        )
        messages.info(request, message)
    elif request.GET.get('receive_txid') and not kudos_transfer.receive_txid:
        params = request.GET

        # db mutations
        try:
            if params['save_addr']:
                profile = get_profile(kudos_transfer.username.replace('@', ''))
                if profile:
                    # TODO: Does this mean that the address the user enters in the receive form
                    # Will overwrite an already existing preferred_payout_address?  Should we
                    # ask the user to confirm this?
                    profile.preferred_payout_address = params['forwarding_address']
                    profile.save()
            kudos_transfer.receive_txid = params['receive_txid']
            kudos_transfer.receive_address = params['forwarding_address']
            kudos_transfer.received_on = timezone.now()
            if request.user.is_authenticated:
                kudos_transfer.recipient_profile = request.user.profile
            kudos_transfer.save()
            record_user_action(kudos_transfer.from_username, 'receive_kudos', kudos_transfer)
            record_kudos_email_activity(kudos_transfer, kudos_transfer.username, 'receive_kudos')
            record_kudos_activity(
                kudos_transfer,
                kudos_transfer.from_username,
                'new_kudos' if kudos_transfer.username else 'new_crowdfund'
            )
            messages.success(request, _('This kudos has been received'))
        except Exception as e:
            messages.error(request, str(e))
            logger.exception(e)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'receive',
        'gas_price': round(recommend_min_gas_price_to_confirm_in_time(120), 1),
        'kudos_transfer': kudos_transfer,
        'title': f"Receive {kudos_transfer.kudos_token_cloned_from.humanized_name} Kudos" if kudos_transfer and kudos_transfer.kudos_token_cloned_from else _('Receive Kudos'),
        'avatar_url': kudos_transfer.kudos_token_cloned_from.img_url if kudos_transfer and kudos_transfer.kudos_token_cloned_from else None,
        'card_desc': f"You've received a {kudos_transfer.kudos_token_cloned_from.humanized_name} kudos!" if kudos_transfer and kudos_transfer.kudos_token_cloned_from else _('You\'ve received a kudos'),
        'key': key,
        'is_authed': is_authed,
        'disable_inputs': kudos_transfer.receive_txid or not_mined_yet or not is_authed,
        'tweet_text': urllib.parse.quote_plus(f"I just got a {kudos_transfer.kudos_token_cloned_from.humanized_name} Kudos on @gitcoin.  ")
    }

    return TemplateResponse(request, 'transaction/receive.html', params)


def redeem_bulk_coupon(coupon, profile, address, ip_address, save_addr=False):
    try:
        address = Web3.toChecksumAddress(address)
    except:
        error = "You must enter a valid Ethereum address (so we know where to send your Kudos). Please try again."

    # handle form submission
    kudos_transfer = None
    if save_addr:
        profile.preferred_payout_address = address
        profile.save()

    private_key = settings.KUDOS_PRIVATE_KEY if not coupon.sender_pk else coupon.sender_pk
    kudos_owner_address = settings.KUDOS_OWNER_ACCOUNT if not coupon.sender_address else coupon.sender_address
    gas_price_confirmation_time = 2 if not coupon.sender_address else 60
    kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_MAINNET)
    kudos_owner_address = Web3.toChecksumAddress(kudos_owner_address)
    w3 = get_web3(coupon.token.contract.network)
    contract = w3.eth.contract(Web3.toChecksumAddress(kudos_contract_address), abi=kudos_abi())
    nonce = w3.eth.getTransactionCount(kudos_owner_address)
    tx = contract.functions.clone(address, coupon.token.token_id, 1).buildTransaction({
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(gas_price_confirmation_time) * 10**9),
        'value': int(coupon.token.price_finney / 1000.0 * 10**18),
    })

    if not profile.trust_profile and profile.github_created_on > (timezone.now() - timezone.timedelta(days=7)):
        error = f'Your github profile is too new.  Cannot receive kudos.'
        return None, error, None
    else:

        signed = w3.eth.account.signTransaction(tx, private_key)
        try:
            txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()

            with transaction.atomic():
                kudos_transfer = KudosTransfer.objects.create(
                    emails=[profile.email],
                    # For kudos, `token` is a kudos.models.Token instance.
                    kudos_token_cloned_from=coupon.token,
                    amount=coupon.token.price_in_eth,
                    comments_public=coupon.comments_to_put_in_kudos_transfer,
                    ip=ip_address,
                    github_url='',
                    from_name=coupon.sender_profile.handle,
                    from_email='',
                    from_username=coupon.sender_profile.handle,
                    username=profile.handle,
                    network=coupon.token.contract.network,
                    from_address=kudos_owner_address,
                    is_for_bounty_fulfiller=False,
                    metadata={'coupon_redemption': True, 'nonce': nonce},
                    recipient_profile=profile,
                    sender_profile=coupon.sender_profile,
                    txid=txid,
                    receive_txid=txid,
                    tx_status='pending',
                    receive_tx_status='pending',
                )

                # save to DB
                BulkTransferRedemption.objects.create(
                    coupon=coupon,
                    redeemed_by=profile,
                    ip_address=ip_address,
                    kudostransfer=kudos_transfer,
                    )

                coupon.num_uses_remaining -= 1
                coupon.current_uses += 1
                coupon.save()

                # send email
                maybe_market_kudos_to_email(kudos_transfer)
        except Exception as e:
            logger.exception(e)
            error = "Could not redeem your kudos.  Please try again soon."
            return None, error, None

    return True, None, kudos_transfer

@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
def receive_bulk(request, secret):

    coupons = BulkTransferCoupon.objects.filter(secret=secret)
    if not coupons.exists():
        raise Http404

    coupon = coupons.first()
    _class = request.GET.get('class', '')
    if coupon.num_uses_remaining <= 0:
        messages.info(request, f'Sorry but the coupon for a free kudos has has expired.  Contact the person who sent you the coupon link, or you can still purchase one on this page.')
        return redirect(coupon.token.url)

    kudos_transfer = None
    if request.user.is_authenticated:
        redemptions = BulkTransferRedemption.objects.filter(redeemed_by=request.user.profile, coupon=coupon)
        if redemptions.exists():
            kudos_transfer = redemptions.first().kudostransfer

    error = False
    if request.POST:
        if request.user.is_anonymous:
            error = "You must login."
        if not error:
            success, error = redeem_bulk_coupon(coupon, request.user.profile, request.POST.get('forwarding_address'), get_ip(request), request.POST.get('save_addr'))
        if error:
            messages.error(request, error)

    title = f"Redeem {coupon.token.humanized_name} Kudos from @{coupon.sender_profile.handle}"
    desc = f"This Kudos has been AirDropped to you.  About this Kudos: {coupon.token.description}"
    params = {
        'title': title,
        'card_title': title,
        'card_desc': desc,
        'error': error,
        'avatar_url': coupon.token.img_url,
        'coupon': coupon,
        'user': request.user,
        'class': _class,
        'is_authed': request.user.is_authenticated,
        'kudos_transfer': kudos_transfer,
        'tweet_text': urllib.parse.quote_plus(f"I just got a {coupon.token.humanized_name} Kudos on @gitcoin.  ")
    }
    return TemplateResponse(request, 'transaction/receive_bulk.html', params)
