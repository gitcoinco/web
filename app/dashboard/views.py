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
import logging

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from app.utils import ellipses, sync_profile
from dashboard.helpers import normalizeURL, process_bounty_changes, process_bounty_details
from dashboard.models import Bounty, BountySyncRequest, Interest, Profile, ProfileSerializer, Subscription, Tip
from dashboard.notifications import maybe_market_tip_to_email, maybe_market_tip_to_github, maybe_market_tip_to_slack
from gas.utils import conf_time_spread, eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from github.utils import get_auth_url, get_github_emails, get_github_primary_email, is_github_token_valid
from marketing.models import Keyword
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip

logging.basicConfig(level=logging.DEBUG)

confirm_time_minutes_target = 60


def send_tip(request):
    """Handle the first stage of sending a tip."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Send Tip',
        'class': 'send',
    }

    return TemplateResponse(request, 'yge/send1.html', params)


@require_POST
@csrf_exempt
def new_interest(request, bounty_id):
    """Claim Work for a Bounty.

    :request method: POST

    Args:
        post_id (int): ID of the Bounty.

    Returns:
        dict: The success key with a boolean value and accompanying error.

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

    return JsonResponse({'success': True, 'profile': ProfileSerializer(interest.profile).data})


@require_POST
@csrf_exempt
def remove_interest(request, bounty_id):
    """Unclaim work from the Bounty.

    :request method: POST

    post_id (int): ID of the Bounty.

    Returns:
        dict: The success key with a boolean value and accompanying error.

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
        .select_related('profile') \
        .order_by('created')

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

    if request.is_ajax():
        return JsonResponse(json.dumps(interests_data), safe=False)

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
    if request.body:
        status = 'OK'
        message = 'Tip has been received'
        params = json.loads(request.body)

        # db mutations
        try:
            tip = Tip.objects.get(txid=params['txid'])
            tip.receive_address = params['receive_address']
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
    """Handle the second stage of sending a tip.

    TODO:
        * Convert this view-based logic to a django form.

    Returns:
        JsonResponse: If submitting tip, return response with success state.
        TemplateResponse: Render the submission form.

    """
    from_username = request.session.get('handle', '')
    primary_from_email = request.session.get('email', '')
    access_token = request.session.get('access_token')
    to_emails = []

    if request.body:
        # http response
        response = {
            'status': 'OK',
            'message': 'Notification has been sent',
        }
        params = json.loads(request.body)

        to_username = params['username'].lstrip('@')
        try:
            to_profile = Profile.objects.get(handle__iexact=to_username)
            if to_profile.email:
                to_emails.append(to_profile.email)
            if to_profile.github_access_token:
                to_emails = get_github_emails(to_profile.github_access_token)
        except Profile.DoesNotExist:
            pass

        if params.get('email'):
            to_emails.append(params['email'])

        # If no primary email in session, try the POST data. If none, fetch from GH.
        if params.get('fromEmail'):
            primary_from_email = params['fromEmail']
        elif access_token and not primary_from_email:
            primary_from_email = get_github_primary_email(access_token)

        to_emails = list(set(to_emails))
        expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])

        # db mutations
        tip = Tip.objects.create(
            emails=to_emails,
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
            from_username=from_username,
            username=params['username'],
            network=params['network'],
            tokenAddress=params['tokenAddress'],
            txid=params['txid'],
            from_address=params['from_address'],
        )
        # notifications
        maybe_market_tip_to_github(tip)
        maybe_market_tip_to_slack(tip, 'new_tip')
        maybe_market_tip_to_email(tip, to_emails)
        if not to_emails:
            response['status'] = 'error'
            response['message'] = 'Uh oh! No email addresses for this user were found via Github API.  Youll have to let the tipee know manually about their tip.'

        return JsonResponse(response)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'title': 'Send Tip',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'from_email': primary_from_email,
        'from_handle': from_username,
    }

    return TemplateResponse(request, 'yge/send2.html', params)


def process_bounty(request):
    """Process the bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Process Issue',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
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

def external_bounties(request):
    """Handle Dummy External Bounties index page."""
    params = {
        'active': 'dashboard',
        'title': 'Issue Explorer',
    }
    return TemplateResponse(request, 'external_bounties.html', params)


def gas(request):
    context = {
        'conf_time_spread': conf_time_spread(),
        'title': 'Live Gas Usage => Predicted Conf Times'
        }
    return TemplateResponse(request, 'gas.html', context)


def new_bounty(request):
    """Create a new bounty."""
    issue_url = request.GET.get('source') or request.GET.get('url', '')
    params = {
        'issueURL': issue_url,
        'active': 'submit_bounty',
        'title': 'Create Funded Issue',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'from_email': request.session.get('email', ''),
        'from_handle': request.session.get('handle', '')
    }

    return TemplateResponse(request, 'submit_bounty.html', params)


def fulfill_bounty(request):
    """Fulfill a bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Submit Work',
        'active': 'fulfill_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'handle': request.session.get('handle', ''),
        'email': request.session.get('email', '')
    }

    return TemplateResponse(request, 'fulfill_bounty.html', params)


def kill_bounty(request):
    """Kill an expired bounty."""
    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Kill Bounty',
        'active': 'kill_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
    }

    return TemplateResponse(request, 'kill_bounty.html', params)


def bounty_details(request):
    """Display the bounty details."""
    _access_token = request.session.get('access_token')
    profile_id = request.session.get('profile_id')
    bounty_url = request.GET.get('url')
    params = {
        'issueURL': request.GET.get('issue_'),
        'title': 'Issue Details',
        'card_title': 'Funded Issue Details | Gitcoin',
        'avatar_url': 'https://gitcoin.co/static/v2/images/helmet.png',
        'active': 'bounty_details',
        'is_github_token_valid': is_github_token_valid(_access_token),
        'github_auth_url': get_auth_url(request.path),
        'profile_interested': False
    }

    if bounty_url:
        try:
            b = Bounty.objects.current().get(github_url=bounty_url)
            # Currently its not finding anyting in the database
            if b.title:
                params['card_title'] = f'{b.title} | {b.org_name} Funded Issue Detail | Gitcoin'
                params['title'] = params['card_title']
                params['card_desc'] = ellipses(b.issue_description_text, 255)

            params['bounty_pk'] = b.pk
            params['interested_profiles'] = b.interested.select_related('profile').all()
            params['avatar_url'] = b.local_avatar_url
            params['is_legacy'] = b.is_legacy  # TODO: Remove this following legacy contract sunset.

            if profile_id:
                profile_ids = list(params['interested_profiles'].values_list('profile_id', flat=True))
                params['profile_interested'] = request.session.get('profile_id') in profile_ids
        except Bounty.DoesNotExist:
            pass
        except Exception as e:
            print(e)
            logging.error(e)

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
    params['card_desc'] = profile.desc
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


@require_POST
@csrf_exempt
@ratelimit(key='ip', rate='2/s', method=ratelimit.UNSAFE, block=True)
def sync_web3(request):
    """ Sync up web3 with the database.  This function has a few different uses.  It is typically
        called from the front end using the javascript `sync_web3` function.  The `issueURL` is
        passed in first, followed optionally by a `bountydetails` argument.
    """
    # setup
    result = {}
    issueURL = request.POST.get('issueURL', False)
    bountydetails = json.loads(request.POST.get('bountydetails', "{}"))

    if issueURL:
        issueURL = normalizeURL(issueURL)

        if not bountydetails:
            # create a bounty sync request
            result['status'] = 'OK'
            for existing_bsr in BountySyncRequest.objects.filter(github_url=issueURL, processed=False):
                existing_bsr.processed = True
                existing_bsr.save()
        else:
            contract_address = request.POST.get('contract_address')
            network = request.POST.get('network')
            did_change, old_bounty, new_bounty = process_bounty_details(
                bountydetails, issueURL, contract_address, network)

            print("{} changed, {}".format(did_change, issueURL))
            if did_change:
                print("- processing changes")
                process_bounty_changes(old_bounty, new_bounty, None)

        BountySyncRequest.objects.create(
            github_url=issueURL,
            processed=False,
        )

    return JsonResponse(result)


# LEGAL

def terms(request):
    return TemplateResponse(request, 'legal/terms.txt', {})


def privacy(request):
    return redirect('https://gitcoin.co/terms#privacy')


def cookie(request):
    return redirect('https://gitcoin.co/terms#privacy')


def prirp(request):
    return redirect('https://gitcoin.co/terms#privacy')


def apitos(request):
    return redirect('https://gitcoin.co/terms#privacy')

def toolbox(request):
    actors = [{
        "title": "The Basics",
        "description": "Accelerate your dev workflow with Gitcoin\'s incentivization tools.",
        "tools": [{
            "name": "Issue Explorer",
            "img": "/static/v2/images/why-different/code_great.png",
            "description": '''A searchable index of all of the funded work available in
                            the system.''',
            "link": "https://gitcoin.co/explorer",
            "active": "true",
            'stat_graph': 'bounties_fulfilled',
        }, {
             "name": "Fund Work",
             "img": "/static/v2/images/tldr/bounties.jpg",
             "description": '''Got work that needs doing?  Create an issue and offer a bounty to get folks
                            working on it.''',
             "link": "/funding/new",
             "active": "false",
             'stat_graph': 'bounties_fulfilled',
        }, {
             "name": "Tips",
             "img": "/static/v2/images/tldr/tips.jpg",
             "description": '''Leave a tip to thank someone for
                        helping out.''',
             "link": "https://gitcoin.co/tips",
             "active": "false",
             'stat_graph': 'tips',
        }, {
             "name": "Code Sponsor",
             "img": "/static/v2/images/codesponsor.jpg",
             "description": '''CodeSponsor sustains open source
                        by connecting sponsors with open source projects.''',
             "link": "https://codesponsor.io",
             "active": "false",
             'stat_graph': 'codesponsor',
        }
        ]
      }, {
          "title": "The Powertools",
          "description": "Take your OSS game to the next level!",
          "tools": [ {
              "name": "Browser Extension",
              "img": "/static/v2/images/tools/browser_extension.png",
              "description": '''Browse Gitcoin where you already work.
                    On Github''',
              "link": "/extension",
              "active": "false",
              'stat_graph': 'browser_ext_chrome',
          },
          {
              "name": "iOS app",
              "img": "/static/v2/images/tools/iOS.png",
              "description": '''Gitcoin has an iOS app in alpha. Install it to
                browse funded work on-the-go.''',
              "link": "/ios",
              "active": "false",
              'stat_graph': 'ios_app_users', #TODO
        }
          ]
      }, {
          "title": "Community Tools",
          "description": "Friendship, mentorship, and community are all part of the process.",
          "tools": [
          {
              "name": "Slack Community",
              "img": "/static/v2/images/tldr/community.jpg",
              "description": '''Questions / Discussion / Just say hi ? Swing by
                                our slack channel.''',
              "link": "/slack",
              "active": "false",
              'stat_graph': 'slack_users',
         },
          {
              "name": "Gitter Community",
              "img": "/static/v2/images/tools/community2.png",
              "description": '''The gitter channel is less active than slack, but
                is still a good place to ask questions.''',
              "link": "/gitter",
              "active": "false",
              'stat_graph': 'gitter_users',
        },
          {
              "name": "Refer a Friend",
              "img": "/static/v2/images/freedom.jpg",
              "description": '''Got a colleague who wants to level up their career?
              Refer them to Gitcoin, and we\'ll happily give you a bonus for their
              first bounty. ''',
              "link": "/refer",
              "active": "false",
              'stat_graph': 'email_subscriberse',
        },
          ]
       }, {
          "title": "Tools in Beta",
          "description": "These fresh new tools are looking someone to test ride them!",
          "tools": [{
              "name": "Leaderboard",
              "img": "/static/v2/images/tools/leaderboard.png",
              "description": '''Check out who is topping the charts in
                the Gitcoin community this month.''',
              "link": "https://gitcoin.co/leaderboard/",
              "active": "false",
              'stat_graph': 'bounties_fulfilled',
          },
           {
            "name": "Profiles",
            "img": "/static/v2/images/tools/profiles.png",
            "description": '''Browse the work that you\'ve done, and how your OSS repuation is growing. ''',
            "link": "/profile/mbeacom",
            "active": "true",
            'stat_graph': 'profiles_ingested',
            },
           {
            "name": "ETH Tx Time Predictor",
            "img": "/static/v2/images/tradeoffs.png",
            "description": '''Estimate Tradeoffs between Ethereum Network Tx Fees and Confirmation Times ''',
            "link": "/gas",
            "active": "true",
            'stat_graph': 'gas_page',
            },
          ]
       }, {
          "title": "Tools for Building Gitcoin",
          "description": "Gitcoin is built using Gitcoin.  Purdy cool, huh? ",
          "tools": [{
              "name": "Github Repos",
              "img": "/static/v2/images/tools/science.png",
              "description": '''All of our development is open source, and managed
              via Github.''',
              "link": "/github",
              "active": "false",
              'stat_graph': 'github_stargazers_count',
          },
           {
            "name": "API",
            "img": "/static/v2/images/tools/api.jpg",
            "description": '''Gitcoin provides a simple HTTPS API to access data
                            without having to run your own Ethereum node.''',
            "link": "https://github.com/gitcoinco/web#https-api",
            "active": "true",
            'stat_graph': 'github_forks_count',
            },
          {
              "class": 'new',
              "name": "Build your own",
              "img": "/static/v2/images/dogfood.jpg",
              "description": '''Dogfood.. Yum! Gitcoin is built using Gitcoin.
                Got something you want to see in the world? Let the community know
                <a href="/slack">on slack</a>
                or <a href="https://github.com/gitcoinco/gitcoinco/issues/new">our github repos</a>
                .''',
              "link": "",
              "active": "false",
          }
          ]
       }, {
           "title": "Just for Fun",
           "description": "Some tools that the community built *just because* they should exist.",
           "tools": [{
               "name": "Ethwallpaper",
               "img": "/static/v2/images/tools/ethwallpaper.png",
               "description": '''Repository of
                        Ethereum wallpapers.''',
               "link": "https://ethwallpaper.co",
               "active": "false",
               'stat_graph': 'google_analytics_sessions_ethwallpaper',
           }]
        }]

    context = {
        "active": "tools",
        'title': "Toolbox",
        'card_title': "Gitcoin Toolbox",
        'avatar_url': 'https://gitcoin.co/static/v2/images/tools/api.jpg',
        "card_desc": "Accelerate your dev workflow with Gitcoin\'s incentivization tools.",
        'actors': actors,
        'newsletter_headline': "Don't Miss New Tools!"
    }
    return TemplateResponse(request, 'toolbox.html', context)
