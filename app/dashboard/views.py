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
from __future__ import unicode_literals

import json

from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from app.github import get_user as get_github_user
from app.utils import ellipses, sync_profile
from dashboard.helpers import normalizeURL, process_bounty_changes, process_bounty_details
from dashboard.models import Bounty, BountySyncRequest, Profile, Subscription, Tip
from dashboard.notifications import maybe_market_tip_to_email, maybe_market_tip_to_github, maybe_market_tip_to_slack
from gas.utils import conf_time_spread, eth_usd_conv_rate, recommend_min_gas_price_to_confirm_in_time
from marketing.models import Keyword
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip

confirm_time_minutes_target = 60


def send_tip(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Send Tip',
        'class': 'send',
    }

    return TemplateResponse(request, 'yge/send1.html', params)


@csrf_exempt
@ratelimit(key='ip', rate='2/m', method=ratelimit.UNSAFE, block=True)
def receive_tip(request):

    if request.body != '':
        status = 'OK'
        message = 'Tip has been received'
        params = json.loads(request.body)

        #db mutations
        try:
            tip = Tip.objects.get(
                txid=params['txid'],
                )
            tip.receive_txid = params['receive_txid']
            tip.received_on = timezone.now()
            tip.save()
        except Exception as e:
            status = 'error'
            message = str(e)

        #http response
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

    if request.body != '':
        status = 'OK'
        message = 'Notification has been sent'
        params = json.loads(request.body)
        emails = []

        #basic validation
        username = params['username']

        #get emails
        if params['email']:
            emails.append(params['email'])
        gh_user = get_github_user(username)
        user_full_name = gh_user['name']
        if gh_user.get('email', False):
            emails.append(gh_user['email'])
        gh_user_events = get_github_user(username, '/events/public')
        for event in gh_user_events:
            commits = event.get('payload', {}).get('commits', [])
            for commit in commits:
                email = commit.get('author', {}).get('email', None)
                #print(event['actor']['display_login'].lower() == username.lower())
                #print(commit['author']['name'].lower() == user_full_name.lower())
                #print('========')
                if email and \
                    event['actor']['display_login'].lower() == username.lower() and \
                    commit['author']['name'].lower() == user_full_name.lower() and \
                    'noreply.github.com' not in email and \
                    email not in emails:
                    emails.append(email)
        expires_date = timezone.now() + timezone.timedelta(seconds=params['expires_date'])

        #db mutations
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
            username=params['username'],
            network=params['network'],
            tokenAddress=params['tokenAddress'],
            txid=params['txid'],
            )

        #notifications
        did_post_to_github = maybe_market_tip_to_github(tip)
        maybe_market_tip_to_slack(tip, 'new_tip', tip.txid)
        maybe_market_tip_to_email(tip, emails)
        if len(emails) == 0:
                status = 'error'
                message = 'Uh oh! No email addresses for this user were found via Github API.  Youll have to let the tipee know manually about their tip.'

        #http response
        response = {
            'status': status,
            'message': message,
        }
        return JsonResponse(response)

    params = {
        'issueURL': request.GET.get('source'),
        'class': 'send2',
        'title': 'Send Tip',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
    }

    return TemplateResponse(request, 'yge/send2.html', params)


def process_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Process Issue',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
    }

    return TemplateResponse(request, 'process_bounty.html', params)


def dashboard(request):

    params = {
        'active': 'dashboard',
        'title': 'Issue Explorer',
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'dashboard.html', params)


def gas(request):
    context = {
        'conf_time_spread': conf_time_spread(),
        'title': 'Live Gas Usage => Predicted Conf Times'
        }
    return TemplateResponse(request, 'gas.html', context)


def new_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'active': 'submit_bounty',
        'title': 'Create Funded Issue',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
    }

    return TemplateResponse(request, 'submit_bounty.html', params)


def claim_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Claim Issue',
        'active': 'claim_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
    }

    return TemplateResponse(request, 'claim_bounty.html', params)


def clawback_expired_bounty(request):

    params = {
        'issueURL': request.GET.get('source'),
        'title': 'Clawback Expired Issue',
        'active': 'clawback_expired_bounty',
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(confirm_time_minutes_target),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
    }

    return TemplateResponse(request, 'clawback_expired_bounty.html', params)


def bounty_details(request):
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
    except Exception as e:
        print(e)
        pass

    return TemplateResponse(request, 'bounty_details.html', params)


def profile_helper(handle):

    try:
        profile = Profile.objects.get(handle__iexact=handle)
    except Profile.DoesNotExist as e:
        sync_profile(handle)
        try:
            profile = Profile.objects.get(handle__iexact=handle)
        except Profile.DoesNotExist as e:
            raise Http404
            print(e)
    return profile


def profile_keywords_helper(handle):
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
    keywords = profile_keywords_helper(handle)

    response = {
        'status': 200,
        'keywords': keywords,
    }
    return JsonResponse(response)


def profile(request, handle):

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

    #setup
    result = {}
    issueURL = request.POST.get('issueURL', False)
    bountydetails = request.POST.getlist('bountydetails[]', [])
    if issueURL:

        issueURL = normalizeURL(issueURL)
        if not len(bountydetails):
            #create a bounty sync request
            result['status'] = 'OK'
            for existing_bsr in BountySyncRequest.objects.filter(github_url=issueURL, processed=False):
                existing_bsr.processed = True
                existing_bsr.save()
        else:
            #normalize data
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
            didChange, old_bounty, new_bounty = process_bounty_details(bountydetails, issueURL, contract_address, network)

            print("{} changed, {}".format(didChange, issueURL))
            if didChange:
                print("- processing changes");
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
