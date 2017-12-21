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
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import json

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from app.github import (
    get_auth_url, get_github_emails, get_github_primary_email, get_github_user_data, get_github_user_token,
)
from app.utils import ellipses, sync_profile
from dashboard.helpers import normalizeURL, process_bounty_changes, process_bounty_details
from dashboard.models import Bounty, BountySyncRequest, Interest, Profile, ProfileSerializer, Subscription, Tip
from dashboard.notifications import maybe_market_tip_to_github, maybe_market_tip_to_slack
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from marketing.mails import tip_email
from marketing.models import Keyword
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip

confirm_time_minutes_target = 3


@require_GET
def github_callback(request):
    """Handle the Github authentication callback."""
    # Get request parameters to handle authentication and the redirect.
    code = request.GET.get('code', None)
    redirect_uri = request.GET.get('redirect_uri')

    if not code or not redirect_uri:
        raise Http404

    # Get OAuth token and github user data.
    access_token = get_github_user_token(code)
    github_user_data = get_github_user_data(access_token)
    handle = github_user_data.get('login')

    if handle:
        # Create or update the Profile with the github user data.
        user_profile, _ = Profile.objects.update_or_create(
            handle=handle,
            defaults={
                'data': github_user_data or {},
                'email': get_github_primary_email(access_token),
                'github_access_token': access_token
            })

        # Update the user's session with handle and email info.
        session_data = {
            'handle': user_profile.handle,
            'email': user_profile.email,
            'access_token': user_profile.github_access_token,
            'profile_id': user_profile.pk
        }
        for k, v in session_data.items():
            request.session[k] = v

    return redirect(redirect_uri)


@require_GET
def github_authentication(request):
    """Handle Github authentication."""
    redirect_uri = request.GET.get('redirect_uri', '/')
    return redirect(get_auth_url(redirect_uri))


def send_tip(request):
    """Handle the first stage of sending a tip."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Send Tip',
        'class': 'send',
    }

    return TemplateResponse(request, 'yge/send1.html', params)


# @require_POST
@csrf_exempt
def new_interest(request, bounty_id):
    """Express interest in a Bounty.

    :request method: POST
    
    Args:
        post_id (int): ID of the Bounty.

    Returns:
        dict: An empty dictionary, if successful.

    """
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return JsonResponse(
            {'error': 'You must be authenticated!'},
            status=401)

    try:
        bounty = Bounty.objects.get(pk=bounty_id)
    except Bounty.DoesNotExist:
        raise Http404

    try:
        Interest.objects.get(profile_id=profile_id, bounty=bounty)
        return JsonResponse({
            'error': 'You have already expressed interest in this bounty!',
            'success': False},
            status=401)
    except Interest.DoesNotExist:
        interest = Interest.objects.create(profile_id=profile_id)
        bounty.interested.add(interest)
    except Interest.MultipleObjectsReturned:
        bounty_ids = bounty.interested \
            .filter(profile_id=profile_id) \
            .values_list('id', flat=True) \
            .order_by('-created')[1:]

        Interest.objects.filter(pk__in=list(bounty_ids)).delete()

        return JsonResponse({
            'error': 'You have already expressed interest in this bounty!',
            'success': False},
            status=401)

    return JsonResponse({'success': True})


# @require_POST
@csrf_exempt
def remove_interest(request, bounty_id):
    """Remove interest from the Bounty.

    :request method: POST

    post_id (int): ID of the Bounty.

    Returns:
        dict: An empty dictionary, if successful.

    """
    profile_id = request.session.get('profile_id')
    if not profile_id:
        return JsonResponse(
            {'error': 'You must be authenticated!'},
            status=401)

    try:
        bounty = Bounty.objects.get(pk=bounty_id)
    except Bounty.DoesNotExist:
        return JsonResponse({'errors': ['Bounty doesn\'t exist!']},
                            status=401)

    try:
        interest = Interest.objects.get(profile_id=profile_id, bounty=bounty)
        bounty.interested.remove(interest)
        interest.delete()
    except Interest.DoesNotExist:
        return JsonResponse({
            'errors': ['You haven\'t expressed interest on this bounty.'],
            'success': False},
            status=401)
    except Interest.MultipleObjectsReturned:
        interest_ids = bounty.interested \
            .filter(
                profile_id=profile_id,
                bounty=bounty
            ).values_list('id', flat=True) \
            .order_by('-created')

        bounty.interested.remove(*interest_ids)
        Interest.objects.filter(pk__in=list(interest_ids)).delete()

    return JsonResponse({'success': True})


@csrf_exempt
@require_GET
def interested_profiles(request, bounty_id):
    """Retrieve memberships who like a Status in a community.

    :request method: GET

    Args:
        bounty_id (int): ID of the Bounty.

    Parameters:
        page (int): The page number.
        limit (int): The number of interests per page.

    Returns:
        django.core.paginator.Paginator: Paged interest results.

    """
    page = request.GET.get('page', 1)
    limit = request.GET.get('limit', 10)
    current_profile = request.session.get('profile_id')
    profile_interested = False

    # Get all interests for the Bounty.
    interests = Interest.objects \
        .filter(bounty__id=bounty_id) \
        .select_related('profile')

    # Check whether or not the current profile has already expressed interest.
    if current_profile and interests.filter(profile__pk=current_profile).exists():
        profile_interested = True

    paginator = Paginator(interests, limit)
    try:
        interests = paginator.page(page)
    except PageNotAnInteger:
        interests = paginator.page(1)
    except EmptyPage:
        return JsonResponse([])

    interests_data = []
    for interest in interests:
        interest_data = ProfileSerializer(interest.profile).data
        interests_data.append(interest_data)

    return JsonResponse({
        'paginator': {
            'num_pages': interests.paginator.num_pages,
        },
        'data': interests_data,
        'profile_interested': profile_interested
    })


@csrf_exempt
@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def receive_tip(request):
    """Receive a tip."""
    if request.body != '':
        status = 'OK'
        message = 'Tip has been received'
        params = json.loads(request.body)

        # db mutations
        try:
            tip = Tip.objects.get(txid=params['txid'])
            tip.receive_txid = params['receive_txid']
            tip.received_on = timezone.now()
            tip.save()
        except Exception as e:
            status = 'error'
            message = str(e)

        # http response
        response = {
            'status': status,
            'message': message,
        }
        return JsonResponse(response)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'receive',
        'title': 'Receive Tip',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
    }

    return TemplateResponse(request, 'yge/receive.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='1/m', method=ratelimit.UNSAFE, block=True)
def send_tip_2(request):
    """Handle the second stage of sending a tip."""
    username = request.session.get('handle')
    primary_email = request.session.get('email', '')

    if request.body != '':
        # http response
        response = {
            'status': 'OK',
            'message': 'Notification has been sent',
        }
        params = json.loads(request.body)

        username = username or params['username']
        access_token = request.session.get('access_token')
        if access_token:
            emails = get_github_emails(access_token) or [primary_email]

        expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])

        # db mutations
        tip = Tip.objects.create(
            emails=emails,
            url=params['url'],
            tokenName=params['tokenName'],
            amount=params['amount'],
            comments_priv=params['comments_priv'],
            comments_public=params['comments_public'],
            ip=get_ip(request),
            expires_date=expires_date,
            github_url=params['github_url'],
            from_name=params['from_name'],
            from_email=params['from_email'],
            username=username,
            network=params['network'],
            tokenAddress=params['tokenAddress'],
            txid=params['txid'],
        )
        # notifications
        maybe_market_tip_to_github(tip)
        maybe_market_tip_to_slack(tip, 'new_tip', tip.txid)
        tip_email(tip, set(emails), True)
        if len(emails) == 0:
            status = 'error'
            message = 'Uh oh! No email addresses for this user were found via Github API.  Youll have to let the tipee know manually about their tip.'

        return JsonResponse(response)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'title': 'Send Tip',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': primary_email,
        'from_handle': username
    }

    return TemplateResponse(request, 'yge/send2.html', params)


def process_bounty(request):
    """Process the bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Process Issue',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
    }

    return TemplateResponse(request, 'process_bounty.html', params)


def dashboard(request):
    """Handle displaying the dashboard."""
    params = {
        'active': 'dashboard',
        'title': 'Issue Explorer',
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'dashboard.html', params)


def new_bounty(request):
    """Create a new bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'active': 'submit_bounty',
        'title': 'Create Funded Issue',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': request.session.get('email', '')
    }

    return TemplateResponse(request, 'submit_bounty.html', params)


def claim_bounty(request):
    """Claim a bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Claim Issue',
        'active': 'claim_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'handle': request.session.get('handle', ''),
        'email': request.session.get('email', '')
    }

    return TemplateResponse(request, 'claim_bounty.html', params)


def clawback_expired_bounty(request):
    """Clawback an expired bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Clawback Expired Issue',
        'active': 'clawback_expired_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
    }

    return TemplateResponse(request, 'clawback_expired_bounty.html', params)


def bounty_details(request):
    """Display the bounty details."""
    params = {
        'issueURL': request.GET.get('issue_'),
        'title': 'Issue Details',
        'card_title': 'Funded Issue Details | Gitcoin',
        'avatar_url': 'https://gitcoin.co/static/v2/images/helmet.png',
        'active': 'bounty_details',
    }

    try:
        b = Bounty.objects.get(github_url=request.GET.get('url'), current_bounty=True)
        if b.title:
            params['card_title'] = "{} | {} Funded Issue Detail | Gitcoin".format(b.title, b.org_name)
            params['title'] = params['card_title']
            params['card_desc'] = ellipses(b.issue_description_text, 255)
        params['avatar_url'] = b.local_avatar_url
        params['interested_profiles'] = b.interested.select_related('profile').all()
    except Exception as e:
        print(e)
        pass

    return TemplateResponse(request, 'bounty_details.html', params)


def profile_helper(handle):
    """Define the profile helper."""
    try:
        profile = Profile.objects.get(handle__iexact=handle)
    except Profile.DoesNotExist:
        sync_profile(handle)
        try:
            profile = Profile.objects.get(handle__iexact=handle)
        except Profile.DoesNotExist:
            raise Http404
    return profile


def profile_keywords_helper(handle):
    """Define the profile keywords helper."""
    profile = profile_helper(handle)

    keywords = []
    for repo in profile.repos_data:
        language = repo.get('language') if repo.get('language') else ''
        _keywords = language.split(',')
        for key in _keywords:
            if key != '' and key not in keywords:
                keywords.append(key)
    return keywords


def profile_keywords(request, handle):
    """Display profile keywords."""
    keywords = profile_keywords_helper(handle)

    response = {
        'status': 200,
        'keywords': keywords,
    }
    return JsonResponse(response)


def profile(request, handle):
    """Display profile details."""
    params = {
        'title': 'Profile',
        'active': 'profile_details',
    }

    profile = profile_helper(handle)
    params['card_title'] = "@{} | Gitcoin".format(handle)
    params['title'] = "@{}".format(handle)
    params['avatar_url'] = profile.local_avatar_url
    params['profile'] = profile
    params['stats'] = profile.stats
    params['bounties'] = profile.bounties

    return TemplateResponse(request, 'profile_details.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def save_search(request):
    """Save the search."""
    email = request.POST.get('email')
    if email:
        raw_data = request.POST.get('raw_data')
        Subscription.objects.create(
            email=email,
            raw_data=raw_data,
            ip=get_ip(request),
        )
        response = {
            'status': 200,
            'msg': 'Success!',
        }
        return JsonResponse(response)

    context = {
        'active': 'save',
        'title': 'Save Search',
    }
    return TemplateResponse(request, 'save_search.html', context)


@csrf_exempt
@ratelimit(key='ip', rate='2/s', method=ratelimit.UNSAFE, block=True)
def sync_web3(request):
    """Sync with web3."""
    # setup
    result = {}
    issueURL = request.POST.get('issueURL', False)
    bountydetails = request.POST.getlist('bountydetails[]', [])
    if issueURL:

        issueURL = normalizeURL(issueURL)
        if not len(bountydetails):
            # create a bounty sync request
            result['status'] = 'OK'
            for existing_bsr in BountySyncRequest.objects.filter(github_url=issueURL, processed=False):
                existing_bsr.processed = True
                existing_bsr.save()
        else:
            # normalize data
            bountydetails[0] = int(bountydetails[0])
            bountydetails[1] = str(bountydetails[1])
            bountydetails[2] = str(bountydetails[2])
            bountydetails[3] = str(bountydetails[3])
            bountydetails[4] = bool(bountydetails[4] == 'true')
            bountydetails[5] = bool(bountydetails[5] == 'true')
            bountydetails[6] = str(bountydetails[6])
            bountydetails[7] = int(bountydetails[7])
            bountydetails[8] = str(bountydetails[8])
            bountydetails[9] = int(bountydetails[9])
            bountydetails[10] = str(bountydetails[10])
            print(bountydetails)
            contract_address = request.POST.get('contract_address')
            network = request.POST.get('network')
            didChange, old_bounty, new_bounty = process_bounty_details(
                bountydetails, issueURL, contract_address, network)

            print("{} changed, {}".format(didChange, issueURL))
            if didChange:
                print("- processing changes")
                process_bounty_changes(old_bounty, new_bounty, None)

        BountySyncRequest.objects.create(
            github_url=issueURL,
            processed=False,
        )

    return JsonResponse(result)


# LEGAL

def terms(request):
    params = {
    }
    return TemplateResponse(request, 'legal/terms.txt', params)


def privacy(request):
    return redirect('https://gitcoin.co/terms#privacy')


def cookie(request):
    return redirect('https://gitcoin.co/terms#privacy')


def prirp(request):
    return redirect('https://gitcoin.co/terms#privacy')


def apitos(request):
    return redirect('https://gitcoin.co/terms#privacy')
