# -*- coding: utf-8 -*-
'''
    Copyright (C) 2017 Gitcoin Core

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
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.search import SearchVector
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from .models import Token, Wallet, Email
from dashboard.models import Profile
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
        'active': 'about',
        'title': 'About',
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
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

    # for x in context['listings']:
    #     x.price = x.price / 1000

    # Adjust the price units.  Change from Finney to ETH
    # updated_listings = []
    # for l in listings:
    #     # l.price = l.price / 1000
    #     logger.info(f'Price in ETH {l.price_in_eth()}')
    #     updated_listings.append(l)

    context = {
        'is_outside': True,
        'active': 'marketplace',
        'title': 'Marketplace',
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
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
    related_kudos = Token.objects.exclude(owner_address='0xD386793F1DB5F21609571C0164841E5eA2D33aD8').filter(name=kudos.name)
    logger.info(f'Kudos rows: {related_kudos}')
    # Find the Wallet rows that match the Kudos.owner_addresses
    related_wallets = Wallet.objects.filter(address__in=[rk.owner_address for rk in related_kudos]).distinct()[:20]
    profile_ids = [rw.profile_id for rw in related_wallets]
    logger.info(f'Related profile_ids:  {profile_ids}')

    # Avatar can be accessed via Profile.avatar
    related_profiles = Profile.objects.filter(pk__in=profile_ids).distinct()

    context = {
        'is_outside': True,
        'active': 'details',
        'title': 'Details',
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
        'kudos': kudos,
        'related_profiles': related_profiles,
    }

    return TemplateResponse(request, 'kudos_details.html', context)


def mint(request):
    context = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'kudos_mint.html', context)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send_api(request):
    """ This function is derived from send_tip_3.
    Handle the third stage of sending a kudos (the POST)

    Returns:
        JsonResponse: response with success state.

    """
    response = {
        'status': 'OK',
        'message': _('Tip Created'),
    }

    is_user_authenticated = request.user.is_authenticated
    from_username = request.user.username if is_user_authenticated else ''
    primary_from_email = request.user.email if is_user_authenticated else ''
    access_token = request.user.profile.get_access_token() if is_user_authenticated else ''
    to_emails = []

    params = json.loads(request.body)
    logger.info(f'params: {params}')
    # return JsonResponse(response)

    to_username = params['username'].lstrip('@')
    to_emails = get_emails_master(to_username)

    if params.get('email'):
        to_emails.append(params['email'])

    # If no primary email in session, try the POST data. If none, fetch from GH.
    if params.get('fromEmail'):
        primary_from_email = params['fromEmail']
    elif access_token and not primary_from_email:
        primary_from_email = get_github_primary_email(access_token)

    to_emails = list(set(to_emails))
    expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])

    # Validate that the token exists on the back-end
    kudos_token = Token.objects.filter(name=params['tokenName'], num_clones_allowed__gt=0).first()
    # db mutations
    kudos_email = Email.objects.create(
        emails=to_emails,
        # For kudos, `token` is a kudos.models.Token instance.  This is to ensure that the 
        # kudos.models.Email instance is tied to a real Token in the database.
        # TODO: Change name to kudosToken
        kudos_token=kudos_token,
        amount=params['amount'],
        comments_priv=params['comments_priv'],
        comments_public=params['comments_public'],
        ip=get_ip(request),
        expires_date=expires_date,
        github_url=params['github_url'],
        from_name=params['from_name'],
        from_email=params['from_email'],
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

    maybe_market_kudos_to_email(kudos_email, to_emails)

    return JsonResponse(response)


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def send(request):
    """ Handle the first start of the Kudos email send.  This form is filled out before the
        'send' button is clicked.
    """

    kudos_name = request.GET.get('name')
    kudos = Token.objects.filter(name=kudos_name, num_clones_allowed__gt=0).first()
    profiles = Profile.objects.all()

    is_user_authenticated = request.user.is_authenticated
    from_username = request.user.username if is_user_authenticated else ''
    primary_from_email = request.user.email if is_user_authenticated else ''

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': primary_from_email,
        'from_handle': from_username,
        'title': 'Send Tip | Gitcoin',
        'card_desc': 'Send a tip to any github user at the click of a button.',
        'kudos': kudos,
        'profiles': profiles
    }

    return TemplateResponse(request, 'transaction/send.html', params)


def receive(request):
    context = dict()
    # kt = KudosToken(name='pythonista', description='Zen', rarity=5, price=10, num_clones_allowed=3,
    #                 num_clones_in_wild=0)

    return TemplateResponse(request, 'transaction/receive.html', context)