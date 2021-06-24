
# -*- coding: utf-8 -*-
'''
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

'''
import json
import logging
import re
from json import loads as json_parse

from django.conf import settings
from django.db.models import Count, Q, Subquery
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from app.utils import get_profiles_from_text
from cacheops import cached_view
from dashboard.models import Activity, HackathonEvent, Profile, Tip, get_my_earnings_counter_profiles, get_my_grants
from dashboard.notifications import amount_usdt_open_work, open_bounties
from dashboard.tasks import grant_update_email_task
from economy.models import Token
from marketing.mails import mention_email, new_funding_limit_increase_request, new_token_request, wall_post_email
from marketing.models import EmailInventory
from perftools.models import JSONStore
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from townsquare.tasks import increment_view_counts
from townsquare.utils import can_pin

from .forms import FundingLimitIncreaseRequestForm
from .utils import articles, press, programming_languages, reasons, testimonials

logger = logging.getLogger(__name__)

connect_types = ['status_update', 'wall_post', 'new_bounty', 'created_quest', 'new_grant', 'created_kudos', 'consolidated_leaderboard_rank', 'consolidated_mini_clr_payout', 'hackathon_new_hacker']

def get_activities(tech_stack=None, num_activities=15):
    # get activity feed

    activities = Activity.objects.select_related('bounty').filter(bounty__network='mainnet').order_by('-created')
    if tech_stack:
        activities = activities.filter(bounty__metadata__icontains=tech_stack)
    activities = activities[0:num_activities]
    return activities

def index(request):
    context = {
        'title': 'Build and Fund the Open Web Together',
        'card_title': 'Gitcoin - Build and Fund the Open Web Together',
        'card_desc': 'Connect with the community developing digital public goods, creating financial freedom, and defining the future of the open web.',
        'card_type': 'summary_large_image',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/twitter-landing-large.png')),
    }

    try:
        data = JSONStore.objects.get(view='results').data
        data_results = {
            'universe_total_usd': data['universe_total_usd'] if data['universe_total_usd'] else 0,
            'human_universe_total_usd': f"${round(data['universe_total_usd'] / 1000000, 1)}m" if data['universe_total_usd'] else 0,
            'mau': data['mau'] if data['mau'] else 0,
            'bounties_gmv': data['bounties_gmv'] if data['bounties_gmv'] else 0
        }
    except:
        data_results = {
            'universe_total_usd': 18874053.680999957,
            'human_universe_total_usd': "$18.9m",
            'mau': 161205.0,
            'bounties_gmv': '3.43m'
        }
    context.update(data_results)

    return TemplateResponse(request, 'home/index2021.html', context)

def index_old(request):
    products = [
        {
            'group' : 'grow_oss',
            'products': [
                {
                    'img': static('v2/images/home/bounties.svg'),
                    'name': 'BOUNTIES',
                    'description': 'Get paid for solving open source bounties.',
                    'link': '/bounties/funder'
                }
            ]
        },
        {
            'group' : 'maintain_oss',
            'products': [
                {
                    'img': static('v2/images/home/codefund.svg'),
                    'name': 'CODEFUND',
                    'description': 'Ethical advertising for open source.',
                    'link': 'https://codefund.app'
                },
                {
                    'img': static('v2/images/home/grants.svg'),
                    'name': 'GRANTS',
                    'description': 'Sustainable funding for open source.',
                    'link': '/grants'
                }
            ]
        },
        {
            'group' : 'build_oss',
            'products': [
                {
                    'img': static('v2/images/home/kudos.svg'),
                    'name': 'KUDOS',
                    'description': 'A new way to show appreciation.',
                    'link': '/kudos'
                }
            ]
        }
    ]

    know_us = [
        {
            'text': 'Our Vision',
            'link': '/vision'
        },
        {
            'text': 'Our Products',
            'link': '/products'
        },
        {
            'text': 'Our Team',
            'link': '/about#team'
        },
        {
            'text': 'Our Results',
            'link': '/results'
        },
        {
            'text': 'Our Values',
            'link': '/mission'
        },
        {
            'text': 'Our Token',
            'link': '/not_a_token'
        }
    ]

    context = {
        'products': products,
        'know_us': know_us,
        'press': press(),
        'articles': articles(),
        'hide_newsletter_caption': True,
        'hide_newsletter_consent': True,
        'newsletter_headline': _("Get the Latest Gitcoin News! Join Our Newsletter."),
        'title': _('Grow Open Source: Get crowdfunding and find freelance developers for your software projects, paid in crypto'),
    }
    return TemplateResponse(request, 'home/index.html', context)


def funder_bounties_redirect(request):
    return redirect(funder_bounties)


def funder_bounties(request):

    onboard_slides = [
        {
            'img': static("v2/images/prime.png"),
            'title': _('Are you a developer or designer?'),
            'subtitle': _('Contribute to exciting OSS project and get paid!'),
            'type': 'contributor',
            'active': 'active',
            'more': '/bounties/contributor'
        },
        {
            'img': static("v2/images/prime.png"),
            'title': _('Are you a funder or project organizer?'),
            'subtitle': _('Fund your OSS bounties and get work done!'),
            'type': 'funder',
            'more': '/how/funder'
        }
    ]

    slides = [
        ("Dan Finlay", static("v2/images/testimonials/dan.jpg"),
         _("Once we had merged in multiple language support from a bounty, it unblocked the \
         path to all other translations, and what better way to get lots of dif erent \
         translations than with bounties from our community? A single tweet of publicity \
         and we had something like 20 language requests, and 10 language pull requests. It’s been total magic."),
         'https://github.com/danfinlay', "Metamask -- Internationalization"),
        ("Phil Elsasser", static("v2/images/testimonials/phil.jpg"),
         _("​By design or not, there is an element of trust inherent within Gitcoin. This isn’t \
         the bad kind of “trust” that we are all trying to move away from in a centralized world, \
         but a much better sense of community trust that gets established through the bounty process."),
         'http://www.marketprotocol.io/', 'Market'),
        ("John Maurelian", static("v2/images/testimonials/maurelian.jpg"),
         _("Gitcoin helps us to finally close out the issues we've been meaning to get around to for too long"),
         "https://consensys.github.io/smart-contract-best-practices/", 'Consensys Diligence -- Documentation Bounties'),
        ("Kames CG", static("v2/images/testimonials/kames.jpg"),
         _("uPort is still in the process of Open Sourcing all of our code, so Gitcoin at the present moment, \
         helps uPort plant seeds within the growing Ethereum developer community, that we expect will blossom \
         into flourishing opportunities in the future. Put simply, as opposed to running marketing campaign, \
         we can use bounties to stay present in front of potential developers we want to engage with."),
         'https://github.com/KamesCG', 'Uport'),
        ("Piper", static("v2/images/testimonials/pipermerriam.jpg"),
         _("Although we’ve only hired two developers, there is no doubt that we could have sourced more. \
         Gitcoin has been the strongest hiring signal in all of the hiring I’ve ever done."),
         'https://github.com/pipermerriam', 'Pipermerriam'),
        ("Joseph Schiarizzi", static("v2/images/testimonials/jschiarizzi.jpeg"),
         _("On a Friday I needed a front end done for a project due in 48 hours.  When everyone I knew was busy, \
         gitcoiners were able to help me make my deadline, with fast, affordable, & high quality work."),
         'https://github.com/jschiarizzi', 'Fourth Wave')
    ]

    gitcoin_description = _(
        "A community at the intersection of blockchain and open source. A place for developers to collaborate in a new system, where open source money builds in monetization for open source repositories."
    )

    context = {
        'onboard_slides': onboard_slides,
        'activities': get_activities(),
        'is_outside': True,
        'slides': slides,
        'slideDurationInMs': 6000,
        'active': 'bounties_funder',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/tw_cards-01.png')),
        'hide_newsletter_caption': True,
        'hide_newsletter_consent': True,
        'gitcoin_description': gitcoin_description,
        'newsletter_headline': _("Get the Latest Gitcoin News! Join Our Newsletter."),
        'meta_title': "Grow Open Source: Find Freelance Developers & Open Source Bug Bounties - Gitcoin",
        'meta_description': "The Gitcoin platform connects freelance developers with open bug bounties or online jobs, paid in crypto (ETH). Leverage a global workforce to quickly complete software development and coding jobs."
    }
    return TemplateResponse(request, 'bounties/funder.html', context)


def contributor_bounties_redirect(request, tech_stack):
    return redirect(contributor_bounties, tech_stack= '/'+ tech_stack)


def contributor_bounties(request, tech_stack):

    onboard_slides = [
        {
            'img': static("v2/images/prime.png"),
            'title': _('Are you a funder or project organizer?'),
            'subtitle': _('Fund your OSS bounties and get work done!'),
            'type': 'funder',
            'active': 'active',
            'more': '/bounties/funder'
        },
        {
            'img': static("v2/images/prime.png"),
            'title': _('Are you a developer or designer?'),
            'subtitle': _('Contribute to exciting OSS project and get paid!'),
            'type': 'contributor',
            'more': '/how/contributor'
        }
    ]

    slides = [
        ("Daniel", static("v2/images/testimonials/gitcoiners/daniel.jpeg"),
         _("When I found Gitcoin I was gladly surprised that it took one thing and did it well. \
         It took the Ethereum tech and used it as a bridge to technology with open source Jobs.  \
         Even though Gitcoin is still in it’s early stages, I think it’s filled with potential to grow."),
         'https://github.com/dmerrill6'),
        ("CryptoMental", static("v2/images/testimonials/gitcoiners/cryptomental.png"),
         _(" think the great thing about GitCoin is how easy it is for projects to reach out to worldwide talent. \
         GitCoin helps to find people who have time to contribute and increase speed of project development. \
         Thanks to GitCoin a bunch of interesting OpenSource projects got my attention!"),
         'https://github.com/cryptomental'),
        ("Elan", static("v2/images/testimonials/gitcoiners/elan.jpeg"),
         _("The bounty process with Gitcoin is pretty amazing.  Just go on the website, find an issue you can \
         work on, you claim it.  All you do then is submit your code to Github, get the code merged.  \
         Once it’s merged, the smart contract kicks in and sends the money to your Ethereum account.  \
         The whole process is pretty smooth.  There’s a giant slack community.  It puts the freelance \
         market back in the hands of the community!"),
         "https://github.com/elaniobro"),
        ("Jack", static("v2/images/testimonials/gitcoiners/jack.jpeg"),
         _("I really like Gitcoin because it’s allowed me to get involved in some really interesting \
         Open Source Projects.  I’ve written code for MyEtherWallet and Gitcoin itself.  \
         I think Gitcoin is becoming a great asset for the Ethereum ecosystem."),
         'https://github.com/jclancy93'),
        ("Miguel Angel Rodriguez Bermudez", static("v2/images/testimonials/gitcoiners/miguel.jpeg"),
         _("I came across Gitcoin 3 months ago.  I was hearing lots of ideas about projects involving \
         cryptocurrencies, and I kept thinking \"what about open source projects?\".  I see Gitcoin as \
         the next level of freelance, where you can not only help repos on Github, but get money out of \
         it.  It is that simple and it works."),
         'https://github.com/marbrb'),
        ("Octavio Amuchástegui", static("v2/images/testimonials/gitcoiners/octavioamu.jpeg"),
         _("I'm in love with Gitcoin. It isn't only a platform, it's a community that gives me the \
         opportunity to open my network and work with amazing top technology projects and earn some \
         money in a way I'm visible to the dev community and work opportunities. Open source is amazing, \
         and is even better to make a living from it, I think is the future of development."),
         'https://github.com/octavioamu')
    ]

    gitcoin_description = _(
        "A community for developers to collaborate and monetize their skills while working \
        on Open Source projects through bounties."
    )

    projects = [
        {
            'name': 'Augur Logo',
            'source': 'v2/images/project_logos/augur.png'
        },
        {
            'name': 'Bounties Logo',
            'source': 'v2/images/project_logos/bounties.png'
        },
        {
            'name': 'Balance Logo',
            'source': 'v2/images/project_logos/balance.png'
        },
        {
            'name': 'Metamask Logo',
            'source': 'v2/images/project_logos/metamask.png'
        },
        {
            'name': 'uPort Logo',
            'source': 'v2/images/project_logos/uport.png'
        },
        {
            'name': 'Market Protocol Logo',
            'source': 'v2/images/project_logos/market.png'
        },
        {
            'name': 'Trust Wallet Logo',
            'source': 'v2/images/project_logos/trust.png'
        },
        {
            'name': 'MCrypto Logo',
            'source': 'v2/images/project_logos/mycrypto.png'
        },
        {
            'name': 'Truffle Logo',
            'source': 'v2/images/project_logos/truffle.png'
        },
        {
            'name': 'Solidity Logo',
            'source': 'v2/images/project_logos/solidity.png'
        },
        {
            'name': 'Casper Logo',
            'source': 'v2/images/project_logos/casper.png'
        },
        {
            'name': 'Wyvern Logo',
            'source': 'v2/images/project_logos/wyvern.png'
        },
        {
            'name': 'Ethereum Logo',
            'source': 'v2/images/project_logos/eth.png'
        },
        {
            'name': 'Livepeer Logo',
            'source': 'v2/images/project_logos/livepeer.png'
        },
        {
            'name': 'Raiden Logo',
            'source': 'v2/images/project_logos/raiden.png'
        },
        {
            'name': 'Databroker Logo',
            'source': 'v2/images/project_logos/databroker.png'
        }
    ]

    # tech_stack = '' #uncomment this if you wish to disable contributor specific LPs
    context = {
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/tw_cards-01.png')),
        'onboard_slides': onboard_slides,
        'slides': slides,
        'slideDurationInMs': 6000,
        'active': 'bounties_coder',
        'newsletter_headline': _("Be the first to find out about newly posted freelance jobs."),
        'hide_newsletter_caption': True,
        'hide_newsletter_consent': True,
        'gitcoin_description': gitcoin_description,
        'projects': projects,
        'contributor_list': [
            { 'link': "/python", 'text': "Python"},
            { 'link': "/javascript", 'text': "JavaScript"},
            { 'link': "/rust", 'text': "Rust"},
            { 'link': "/solidity", 'text': "Solidity"},
            { 'link': "/design", 'text': "Design"},
            { 'link': "/html", 'text': "HTML"},
            { 'link': "/ruby", 'text': "Ruby"},
            { 'link': "/css", 'text': "CSS"},
        ]
    }

    if tech_stack == 'new':
        return redirect('new_funding_short')

    try:
        store = JSONStore.objects.filter(view='contributor_landing_page', key=tech_stack).first()

        if not store:
            store = JSONStore.objects.get(view='contributor_landing_page', key='')

        new_context = store.data

        for key, value in new_context.items():
            context[key] = value
    except Exception as e:
        logger.exception(e)
        raise Http404

    return TemplateResponse(request, 'bounties/contributor.html', context)


def get_contributor_landing_page_context(tech_stack):
    available_bounties_count = open_bounties().count()
    available_bounties_worth = amount_usdt_open_work()
    activities = get_activities(tech_stack)
    return {
        'activities': activities,
        'title': tech_stack.title() + str(_(" Open Source Opportunities")) if tech_stack else str(_("Open Source Opportunities")),
        'available_bounties_count': available_bounties_count,
        'available_bounties_worth': available_bounties_worth,
        'tech_stack': tech_stack,

    }


def how_it_works(request, work_type):
    """Show How it Works / Funder page."""
    if work_type not in ['funder', 'contributor']:
        raise Http404
    if work_type == 'contributor':
        title = _('How to Find & Complete Open Bounties | Gitcoin')
        desc = _('Learn how to get paid for open bug bounties and get paid in crypto (ETH or any ERC-20 token)')
    elif work_type == 'funder':
        title = _('How to Create & Fund Issues/Bounties | Gitcoin')
        desc = _('Learn how to create open bug bounties and get freelance developers to complete your job/task.')
    context = {
        'active': f'how_it_works_{work_type}',
        'title': title,
        'desc': desc
    }
    return TemplateResponse(request, 'how_it_works/index.html', context)


def robotstxt(request):
    context = {
        'settings': settings,
    }
    return TemplateResponse(request, 'robots.txt', context, content_type='text')


def about(request):

    data_about = JSONStore.objects.get(view='about', key='general').data

    try:
        kernel = JSONStore.objects.get(view='about', key='kernel').data

    except JSONStore.DoesNotExist:
        kernel = [{
            "img": "harshricha.jpg",
            "name": "Harsh & Richa",
            "position": "Founders",
            "company": "EPNS"
        },
        {
            "img": "tomgreenaway.jpg",
            "name": "Tom Greenaway",
            "position": "Senior Dev Advocate",
            "company": "Google"
        },
        {
            "img": "sparrowread.jpg",
            "name": "Sparrow Read",
            "position": "Cofounder",
            "company": "DADA, WOCA"
        },
        {
            "img": "colinfortuner.jpg",
            "name": "Colin Fortuner",
            "position": "Indie Game Developer",
            "company": "ex-Twitch"
        },
        {
            "img": "shreyashariharan.jpg",
            "name": "Shreyas Hariharan",
            "position": "Founder",
            "company": "Llama Community"
        },
        {
            "img": "ramanshalupau.jpg",
            "name": "Raman Shalupau",
            "position": "Founder",
            "company": "CryptoJobList"
        },
        {
            "img": "omergoldberg.jpg",
            "name": "Omer Goldberg",
            "position": "Founder",
            "company": "devclass.io, ex-Instagram"
        },
        {
            "img": "kristiehuang.jpg",
            "name": "Kristie Huang ",
            "position": "Member",
            "company": "Pantera Capital, she256"
        }]

    context = {
        'title': 'Gitcoin - Support open web development.',
        'card_title': 'Gitcoin - Support open web development.',
        'card_desc': "We are the community of builders, creators, and protocols at the center of the open web.",
        'card_type': 'summary_large_image',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/twitter-landing-large.png')),
        'data': data_about if data_about else None,
        'kernel': kernel if kernel else None,
    }

    try:
        data = JSONStore.objects.get(view='results').data
        data_results = {
            'universe_total_usd': data['universe_total_usd'] if data['universe_total_usd'] else 0,
            'mau': data['mau'] if data['mau'] else 0,
            'num_grants': data['num_grants'] if data['num_grants'] else 0
        }
    except:
        data_results = {
            'universe_total_usd': 18874053.680999957,
            'mau': 161205.0,
            'num_grants': 1606,
        }
    context.update(data_results)
    return TemplateResponse(request, 'about.html', context)


def mission(request):
    """Render the Mission response."""

    context = {
        'is_outside': True,
        'active': 'mission',
        'avatar_width': 2614,
        'avatar_height': 1286,
        'title': 'Gitcoin - Support open web development.',
        'card_title': _('Gitcoin - Support open web development.'),
        'card_desc': _('We empower open source builders.'),
        'card_type': 'summary_large_image',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/twitter-landing-large.png')),
    }
    return TemplateResponse(request, 'mission.html', context)


def jobs(request):
    return redirect('https://angel.co/company/gitcoin/jobs')


def avatar(request):
    """Render the avatar response."""
    from avatar.models import AvatarTheme

    default_back = get_leaderboard_back(request)
    back = request.GET.get('back', default_back[1])
    img = request.GET.get('img', default_back[0])

    context = {
        'is_outside': True,
        'active': 'avatar',
        'title': 'Avatar Builder',
        'card_title': _("Free Avatar Builder"),
        'card_desc': _('Gitcoin\'s Free Avatar Creator is an online tool to build a character for yourself.  It has dozens of options to show off your bad-self.  No strings attached, Always free.'),
        'avatar_url': "https://c.gitcoin.co/avatars/d1a33d2bcb7bbfef50368bca73111fae/fryggr.png",
        'back': back,
        'img': img,
        'avatar_options': AvatarTheme.objects.filter(active=True).order_by('-popularity'),
    }
    return TemplateResponse(request, 'avatar_landing.html', context)

def get_leaderboard_back(request):
    default_back_safe = [['s10.png', i] for i in range(24, 33)]
    default_back_crazy = [['s9.png', 3], ['s10.png', 10], ['s10.png', 25], ['s10.png', 33], ['s10.png', 4], ['s10.png', 8], ['s9.png', 14]]
    default_back = default_back_safe

    default_back_i = int(request.GET.get('i', int(timezone.now().strftime("%j")))) % len(default_back)
    default_back = default_back[default_back_i]
    return default_back

def products(request):
    """Render the Products response."""
    products = [
        {
            'name': 'Town Square',
            'heading': _("A Web3-enabled social networking bazaar."),
            'description': _("Gitcoin offers social features that uses mechanism design create a community that #GivesFirst."),
            'link': 'https://gitcoin.co/townsquare',
            'img': static('v2/images/products/social.png'),
            'logo': static('v2/images/helmet.svg'),
            'service_level': '',
            'traction': '100s of posts per day',
        },
        {
            'name': 'Discord',
            'heading': _("Reach your favorite Gitcoiner's in realtime.."),
            'description': _("Gitcoin Chat is hosted on Discord, and is an option to connect with your favorite Gitcoiners in realtime."),
            'link': 'https://discord.gg/gitcoin',
            'img': static('v2/images/products/chat.png'),
            'logo': static('v2/images/helmet.svg'),
            'service_level': '',
            'traction': '100s of DAUs',
        },
        {
            'name': 'hackathons',
            'heading': _("Hack with the best companies in web3."),
            'description': _("Gitcoin offers Virtual Hackathons about once a month; Earn Prizes by working with some of the best projects in the decentralization space."),
            'link': 'https://gitcoin.co/hackathons',
            'img': static('v2/images/products/graphics-hackathons.png'),
            'logo': static('v2/images/top-bar/hackathons-symbol-neg.svg'),
            'service_level': 'Full Service',
            'traction': '1-3 hacks/month worth $40k/mo',
        },
        {
            'name': 'grants',
            'heading': _("Sustainable funding for open source"),
            'description': _("Gitcoin Grants are a fast, easy & secure way to provide recurring token \
                            contributions to your favorite OSS maintainers. Plus, with our NEW quarterly $100k+ matching funds it's now even easier to fund your OSS work! "),
            'link': '/grants',
            'img': static('v2/images/products/graphics-Grants.png'),
            'logo': static('v2/images/top-bar/grants-symbol-neg.svg'),
            'service_level': 'Self Service',
            'traction': 'over $1mm in GMV',
        },
        {
            'name': 'kudos',
            'heading': _("Show your appreciation with collectible tokens"),
            'description': _("Kudos is a way of showing your appreciation to another Gitcoin member.\
                            It's also a way to showcase special skills that a member might have."),
            'link': '/kudos',
            'img': static('v2/images/products/graphics-Kudos.png'),
            'logo': static('v2/images/top-bar/kudos-symbol-neg.svg'),
            'service_level': 'Self Service',
            'traction': '1200+ kudos sent/month',
        },
        {
            'name': 'bounties',
            'heading': _("Solve bounties. Get paid. Contribute to open source"),
            'description': _("Collaborate and monetize your skills while working on Open Source projects \
                            through bounties."),
            'link': '/explorer',
            'img': static('v2/images/products/graphics-Bounties.png'),
            'logo': static('v2/images/top-bar/bounties-symbol-neg.svg'),
            'service_level': 'Self Service',
            'traction': '$25k/mo',
        },
        {
            'name': 'kernel',
            'heading': _("Accelerate your web3 entrepreneurial career."),
            'description': _("An exciting 8 week fellowship program for experienced entrepreneurs, top hackers, and elite Gitcoin builders in the early stages of building or joining Web3 companies."),
            'link': 'https://kernel.community/',
            'img': static('v2/images/products/graphics-Codefund.svg'),
            'logo': static('v2/images/top-bar/kernel-symbol-neg.svg'),
            'service_level': 'Full Service',
            'traction': '100s of top devs',
        },
        {
            'name': 'matching engine',
            'heading': _("Find the Right Dev. Every Time."),
            'description': _("It's not about finding *a* developer.  It's about finding *the right developer for your needs*. Our matching engine powers each of our products, and can target the right community members for you."),
            'link': '/users',
            'img': static('v2/images/products/engine.svg'),
            'logo': static('v2/images/products/engine-logo.png'),
            'service_level': 'Integrated',
            'traction': 'Matching 20k devs/mo',
        }
    ]

    if settings.QUESTS_LIVE:
        products.append({
            'name': 'quests',
            'heading': _("Engaging Onboarding Experiences for the Web3 Ecosystem"),
            'description': _("Gitcoin Quests is a fun, gamified way to learn about the web3 ecosystem, earn rewards, and level up your decentralization-fu!"),
            'link': '/quests',
            'img': static('v2/images/products/graphics-Quests.png'),
            'logo': static('v2/images/top-bar/quests-symbol-neg.svg'),
            'service_level': 'Self Service',
            'traction': 'over 3000 plays/month',
        })

    default_back = get_leaderboard_back(request)
    back = request.GET.get('back', default_back[1])
    img = request.GET.get('img', default_back[0])

    context = {
        'is_outside': True,
        'active': 'products',
        'title': 'Products',
        'card_title': _("Gitcoin's Products."),
        'card_desc': _('At Gitcoin, we build products that allow for better incentivized collaboration \
                        in the realm of open source software'),
        'avatar_url': f"/static/v2/images/quests/backs/back{back}.jpeg",
        'back': back,
        'img': img,
        'products': products,
    }
    return TemplateResponse(request, 'products.html', context)


def not_a_token(request):
    """Render the not_a_token response."""
    return redirect('/')


def results(request, keyword=None):
    """Render the Results response."""
    if keyword and keyword not in programming_languages:
        raise Http404
    js = JSONStore.objects.get(view='results', key=keyword)
    context = js.data
    context['updated'] = js.created_on
    context['is_outside'] = True
    context['prefix'] = 'data-'
    import json
    context['avatar_url'] = static('v2/images/results_preview.gif')
    return TemplateResponse(request, 'results.html', context)

def get_specific_activities(what, trending_only, user, after_pk, request=None):
    only_profile_cards = ['mint_ptoken', 'edit_price_ptoken', 'accept_redemption_ptoken',
                          'denies_redemption_ptoken', 'incoming_redemption_ptoken', 'buy_ptoken']
    # create diff filters
    activities = Activity.objects.filter(hidden=False).order_by('-created_on').exclude(pin__what__iexact=what)

    network = 'rinkeby' if settings.DEBUG else 'mainnet'
    filter_network = 'rinkeby' if network == 'mainnet' else 'mainnet'

    if 'grant:' in what:
        activities = activities.exclude(subscription__network=filter_network)

    activities = activities.exclude(activity_type__in=only_profile_cards)
    view_count_threshold = 10

    is_auth = user and user.is_authenticated

    ## filtering
    relevant_profiles = []
    relevant_grants = []
    if what == 'tribes':
        relevant_profiles = get_my_earnings_counter_profiles(user.profile.pk) if is_auth else []
    elif what == 'all_grants':
        activities = activities.filter(grant__isnull=False)
    elif what == 'grants':
        relevant_grants = get_my_grants(user.profile) if is_auth else []
    elif what == 'my_threads' and is_auth:
        activities = user.profile.subscribed_threads.all().order_by('-created') if is_auth else []
    elif what == 'my_favorites' and is_auth:
        favorites = user.favorites.all().values_list('activity_id')
        activities = Activity.objects.filter(id__in=Subquery(favorites)).order_by('-created')
    elif 'keyword-' in what:
        keyword = what.split('-')[1]
        relevant_profiles = Profile.objects.filter(keywords__icontains=keyword)
    elif 'search-' in what:
        keyword = what.split('-')[1]
        view_count_threshold = 5
        base_filter = Q(metadata__icontains=keyword, activity_type__in=connect_types)
        keyword_filter = Q(pk=0) #noop
        if keyword == 'meme':
            keyword_filter = Q(metadata__type='gif') | Q(metadata__type='png') | Q(metadata__type='jpg')
        if keyword == 'meme':
            keyword_filter = Q(metadata__icontains='spotify') | Q(metadata__type='soundcloud') | Q(metadata__type='pandora')
        activities = activities.filter(keyword_filter | base_filter)
    elif 'hackathon:' in what:
        terms = what.split(':')
        pk = terms[1]

        if len(terms) > 2:
            if terms[2] == 'tribe':
                key = terms[3]
                profile_filter = Q(profile__handle=key.lower())
                other_profile_filter = Q(other_profile__handle=key.lower())
                keyword_filter = Q(metadata__icontains=key)
                activities = activities.filter(keyword_filter | profile_filter | other_profile_filter)
                activities = activities.filter(activity_type__in=connect_types).filter(
                    Q(hackathonevent=pk) | Q(bounty__event=pk))
            else:
                activities = activities.filter(activity_type__in=connect_types, metadata__icontains=terms[2]).filter(
                    Q(hackathonevent=pk) | Q(bounty__event=pk))
        else:
            activities = activities.filter(activity_type__in=connect_types).filter(
                Q(hackathonevent=pk) | Q(bounty__event=pk))
    elif 'tribe:' in what:
        key = what.split(':')[1]
        profile_filter = Q(profile__handle=key.lower())
        other_profile_filter = Q(other_profile__handle=key.lower())
        keyword_filter = Q(metadata__icontains=key)
        activities = activities.filter(keyword_filter | profile_filter | other_profile_filter)
    elif 'activity:' in what:
        view_count_threshold = 0
        pk = what.split(':')[1]
        activities = Activity.objects.filter(pk=pk) if pk and pk.isdigit() else Activity.objects.none()
        if request:
            page = int(request.GET.get('page', 1))
            if page > 1:
                activities = Activity.objects.none()
    elif 'project:' in what:
        terms = what.split(':')
        pk = terms[1]

        if len(terms) > 2:
            activities = activities.filter(activity_type__in=connect_types, metadata__icontains=terms[2]).filter(project_id=pk)
        else:
            activities = activities.filter(activity_type__in=connect_types).filter(project_id=pk)
    elif ':' in what:
        pk = what.split(':')[1]
        key = what.split(':')[0] + "_id"
        if key == 'activity_id':
            key = 'pk'
        kwargs = {}
        kwargs[key] = pk
        activities = activities.filter(**kwargs)


    # filters
    if len(relevant_profiles):
        activities = activities.filter(profile__in=relevant_profiles)
    if len(relevant_grants):
        activities = activities.filter(grant__in=relevant_grants)
    if what == 'connect':
        activities = activities.filter(activity_type__in=connect_types)
    if what == 'kudos':
        activities = activities.filter(activity_type__in=['new_kudos', 'receive_kudos'])

    # after-pk filters
    if after_pk:
        activities = activities.filter(pk__gt=after_pk)
    if trending_only:
        if what == 'everywhere':
            view_count_threshold = 40
        activities = activities.filter(view_count__gt=view_count_threshold)

    activities = activities.filter().exclude(pin__what=what)

    return activities


def activity(request):
    """Render the Activity response."""
    page_size = 7
    page = int(request.GET.get('page', 1)) if request.GET.get('page') and request.GET.get('page').isdigit() else 1
    what = request.GET.get('what', 'everywhere')
    trending_only = int(request.GET.get('trending_only', 0)) if request.GET.get('trending_only') and request.GET.get('trending_only').isdigit() else 0
    activities = get_specific_activities(what, trending_only, request.user, request.GET.get('after-pk'), request)
    activities = activities.prefetch_related('profile', 'likes', 'comments', 'kudos', 'grant', 'subscription', 'hackathonevent', 'pin')
    # store last seen
    if activities.exists():
        last_pk = activities.first().pk
        current_pk = request.session.get(what)
        next_pk = last_pk if (not current_pk or current_pk < last_pk) else current_pk
        request.session[what] = next_pk
    # pagination
    next_page = page + 1
    start_index = (page-1) * page_size
    end_index = page * page_size

    #p = Paginator(activities, page_size)
    #page = p.get_page(page)
    page = activities[start_index:end_index]
    suppress_more_link = not len(page)

    # increment view counts
    activities_pks = [obj.pk for obj in page]
    if len(activities_pks):
        increment_view_counts.delay(activities_pks)

    context = {
        'suppress_more_link': suppress_more_link,
        'what': what,
        'can_pin': can_pin(request, what),
        'next_page': next_page,
        'page': page,
        'pinned': None,
        'target': f'/activity?what={what}&trending_only={trending_only}&page={next_page}',
        'title': _('Activity Feed'),
        'TOKENS': request.user.profile.token_approvals.all() if request.user.is_authenticated else [],
        'my_tribes': list(request.user.profile.tribe_members.values_list('org__handle',flat=True)) if request.user.is_authenticated else [],
    }
    context["activities"] = [a.view_props_for(request.user) for a in page]


    return TemplateResponse(request, 'activity.html', context)

@ratelimit(key='ip', rate='30/m', method=ratelimit.UNSAFE, block=True)
def create_status_update(request):
    issue_re = re.compile(r'^(?:https?://)?(?:github\.com)/(?:[\w,\-,\_]+)/(?:[\w,\-,\_]+)/issues/(?:[\d]+)')
    response = {}

    if request.POST:
        profile = request.user.profile
        title = request.POST.get('data')
        resource = request.POST.get('resource', '')
        provider = request.POST.get('resourceProvider', '')
        resource_id = request.POST.get('resourceId', '')
        attach_token = request.POST.get('attachToken', '')
        attach_amount = request.POST.get('attachAmount', '')
        attach_token_name = request.POST.get('attachTokenName', '')
        tx_id = request.POST.get('attachTxId', '')

        if request.user.is_authenticated and (request.user.profile.is_blocked or request.user.profile.shadowbanned):
            response['status'] = 200
            response['message'] = 'Status updated!'
            return JsonResponse(response, status=400)


        kwargs = {
            'activity_type': 'status_update',
            'metadata': {
                'title': title,
                'ask': request.POST.get('ask'),
                'fund_able': provider and issue_re.match(provider) != None,
                'resource': {
                    'type': resource,
                    'provider': provider,
                    'id': resource_id
                }
            }
        }

        if tx_id:
            kwargs['tip'] = Tip.objects.get(txid=tx_id)
            amount = float(attach_amount)
            kwargs['metadata']['attach'] = {
                'amount': amount,
                'token': attach_token,
                'token_name': attach_token_name,
            }

        if resource == 'content':
            meta = kwargs['metadata']['resource']
            meta['title'] = request.POST.get('title', '')
            meta['description'] = request.POST.get('description', '')
            meta['image'] = request.POST.get('image', '')

        kwargs['profile'] = profile
        what = request.POST.get('what')
        if what and ':' in what:
            key = what.split(':')[0]
            result = what.split(':')[1]
            if key and result:
                key = f"{key}_id"
                if key != 'hackathon_id':
                    kwargs[key] = result
                kwargs['activity_type'] = 'wall_post'

        if request.POST.get('has_video'):
            kwargs['metadata']['video'] = True
            kwargs['metadata']['gfx'] = request.POST.get('video_gfx')

        if request.POST.get('option1'):
            poll_choices = []
            for i in range(1, 5):
                key = "option" + str(i)
                val = request.POST.get(key)
                if val:
                    poll_choices.append({
                        'question': val,
                        'answers': [],
                        'i': i,
                        })
            kwargs['metadata']['poll_choices'] = poll_choices

        if ':' in request.POST.get('tab', ''):
            tab = request.POST.get('tab')
            key = tab.split(':')[0]
            result = tab.split(':')[1]
            if key == 'hackathon':
                kwargs['hackathonevent'] = HackathonEvent.objects.get(pk=result)
            if key == 'tribe':
                kwargs['other_profile'] = Profile.objects.get(handle=result.lower())

        try:
            activity = Activity.objects.create(**kwargs)
            response['status'] = 200
            response['message'] = 'Status updated!'

            mentioned_profiles = get_profiles_from_text(title).exclude(user__in=[request.user])
            to_emails = set(mentioned_profiles.values_list('email', flat=True))
            mention_email(activity, to_emails)

            if kwargs['activity_type'] == 'wall_post':
                if activity.grant and activity.grant.is_on_team(request.user.profile):
                    grant = activity.grant
                    grant.last_update = timezone.now()
                    grant.save()
                    if 'Email Grant Funders' in activity.metadata.get('ask'):
                        grant_update_email_task.delay(activity.pk)
                else:
                    wall_post_email(activity)

        except Exception as e:
            response['status'] = 400
            response['message'] = 'Bad Request'
            logger.error('Status Update error - Error: (%s) - Handle: (%s)', e, profile.handle if profile else '')
            return JsonResponse(response, status=400)
    return JsonResponse(response)


def grant_redir(request):
    return redirect('/grants/')


def help(request):
    return redirect('/support/')


def verified(request):
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None

    context = {
        'active': 'verified',
        'title': _('Verified'),
        'profile': profile,
    }
    return TemplateResponse(request, 'verified.html', context)


def presskit(request):

    brand_colors = [
        (
            "Violet",
            "#6F3FF5",
            "11, 63, 245",
            "256, 90, 60"
        ),
        (
            "Teal",
            "#02E2AC",
            "2, 226, 172",
            "166, 98, 45"
        ),
        (
            "Pink",
            "#F3587D",
            "243, 88, 125",
            "346, 87, 65"
        ),
        (
            "Yellow",
            "#FFCC00",
            "255, 204, 0",
            "48, 100, 50"
        ),
        (
            "Light Violet",
            "#8C65F7",
            "140, 101, 247",
            "256, 90, 68"
        ),
        (
            "Light Teal",
            "#5BF1CD",
            "91, 241, 205",
            "166, 84, 65"
        ),
        (
            "Light Pink",
            "#F579A6",
            "245, 121, 166",
            "338, 86, 72"
        ),
        (
            "Light Yellow",
            "#FFDB4C",
            "255, 219, 76",
            "48, 100, 65"
        ),
        (
            "Dark Violet",
            "#5932C4",
            "89, 50, 196",
            "256, 59, 48"
        ),
        (
            "Dark Teal",
            "#11BC92",
            "17, 188, 146",
            "165, 83, 40"
        ),
        (
            "Dark Pink",
            "#D44D6E",
            "212, 77, 110",
            "345, 61, 57"
        ),
        (
            "Dark Yellow",
            "#E1B815",
            "255, 184, 21",
            "48, 83, 48"
        ),

    ]

    context = {
        'brand_colors': brand_colors,
        'active': 'get',
        'title': _('Presskit'),
    }
    return TemplateResponse(request, 'presskit.html', context)


def handler403(request, exception=None):
    return error(request, 403)


def handler404(request, exception=None):
    return error(request, 404)


def handler500(request, exception=None):
    return error(request, 500)


def handler400(request, exception=None):
    return error(request, 400)


def error(request, code):
    context = {
        'active': 'error',
        'code': code,
        'nav': 'home',
    }
    context['title'] = "Error {}".format(code)
    return_as_json = 'api' in request.path

    if return_as_json:
        return JsonResponse(context, status=500)
    return TemplateResponse(request, 'error.html', context, status=code)


def portal(request):
    return redirect('https://gitcoin.co/help')


def community(request):
    return redirect('https://calendar.google.com/calendar/embed?src=7rq7ga2oubv3tk93hk67agdv88%40group.calendar.google.com')


def onboard(request):
    return redirect('https://docs.google.com/document/d/1DQvek5TwASIp1njx5VZeLKEgSxfvxm871vctx1l_33M/edit?')


def podcast(request):
    return redirect('https://itunes.apple.com/us/podcast/gitcoin-community/id1360536677')


def feedback(request):
    return redirect('https://goo.gl/forms/9rs9pNKJDnUDYEeA3')


def wallpaper(request):
    return redirect('https://gitcoincontent.s3-us-west-2.amazonaws.com/Wallpapers.zip')


def help_dev(request):
    return redirect('/support')


def help_pilot(request):
    return redirect('/support')


def help_repo(request):
    return redirect('/support')


def help_faq(request):
    return redirect('/support')


def browser_extension_chrome(request):
    return redirect('https://chrome.google.com/webstore/detail/gdocmelgnjeejhlphdnoocikeafdpaep')


def browser_extension_firefox(request):
    return redirect('https://addons.mozilla.org/en-US/firefox/addon/gitcoin/')


def itunes(request):
    return redirect('https://itunes.apple.com/us/app/gitcoin/id1319426014')


def casestudy(request):
    return redirect('https://docs.google.com/document/d/1M8-5xCGoJ8u-k0C0ncx_dr9LtHwZ32Ccn3KMFtEnsBA/edit')


def schwag(request):
    return redirect('https://goo.gl/forms/X3jAtOVUUNAumo072')


def slack(request):
    return discord(request)


@csrf_exempt
def newtoken(request):
    context = {
        'active': 'newtoken',
        'msg': None,
    }

    if request.POST:
        required_fields = ['email', 'terms', 'not_security', 'address', 'symbol', 'decimals', 'network']
        validtion_passed = True
        for key in required_fields:
            if not request.POST.get(key):
                context['msg'] = str(_('You must provide the following fields: ')) + key
                validtion_passed = False
        if validtion_passed:
            obj = Token.objects.create(
                address=request.POST['address'],
                symbol=request.POST['symbol'],
                decimals=request.POST['decimals'],
                network=request.POST['network'],
                approved=False,
                priority=1,
                metadata={
                    'ip': get_ip(request),
                    'email': request.POST['email'],
                    }
                )
            new_token_request(obj)
            context['msg'] = str(_('Your token has been submitted and will be listed within 2 business days if it is accepted.'))

    return TemplateResponse(request, 'newtoken.html', context)


def btctalk(request):
    return redirect('https://bitcointalk.org/index.php?topic=2206663')


def reddit(request):
    return redirect('https://www.reddit.com/r/gitcoincommunity/')

def blog(request):
    return redirect('https://gitcoin.co/blog')

def calendar(request):
    return redirect('https://calendar.google.com/calendar/embed?src=7rq7ga2oubv3tk93hk67agdv88%40group.calendar.google.com')

def twitter(request):
    return redirect('http://twitter.com/gitcoin')


def discord(request):
    return redirect('https://discord.gg/gitcoin')


def telegram(request):
    return redirect('https://t.me/joinchat/DwEd_xps7gJqWt-Quf-tPA')


def fb(request):
    return redirect('https://www.facebook.com/GetGitcoin/')


def medium(request):
    return redirect('https://medium.com/gitcoin')


def refer(request):
    return redirect('https://gitcoin.co/funding/details?url=https://github.com/gitcoinco/gitcoinco/issues/1')


def gitter(request):
    return redirect('https://gitter.im/gitcoinco/Lobby')


def github(request):
    return redirect('https://github.com/gitcoinco/')


def youtube(request):
    return redirect('https://www.youtube.com/channel/UCeKRqRjzSzq5yP-zUPwc6_w')


def web3(request):
    return redirect('https://www.youtube.com/watch?v=cZZMDOrIo2k')


def support(request):
    return redirect('https://support.gitcoin.co/')


@cached_view(timeout=60)
def tokens(request):
    context = {}
    networks = ['mainnet', 'ropsten', 'rinkeby', 'unknown', 'custom']
    for network in networks:
        key = f"{network}_tokens"
        context[key] = Token.objects.filter(network=network, approved=True)
    return TemplateResponse(request, 'tokens_js.txt', context, content_type='text/javascript')


@cached_view(timeout=60)
def json_tokens(request):
    context = {}
    networks = ['mainnet', 'ropsten', 'rinkeby', 'unknown', 'custom']
    # for network in networks:
        # key = f"{network}_tokens"
        # context[key] = Token.objects.filter(network=network, approved=True)
    tokens=Token.objects.filter(approved=True)
    token_json = []
    for token in tokens:
        _token = {
            'id':  token.id,
            'address': token.address,
            'symbol': token.symbol,
            'network': token.network,
            'networkId': token.network_id,
            'chainId': token.chain_id,
            'decimals': token.decimals,
            'priority': token.priority
        }


        token_json.append(_token)
    # return TemplateResponse(request, 'tokens_js.txt', context, content_type='text/javascript')
    # return JsonResponse(json.loads(json.dumps(list(context), default=str)), safe=False)
    return JsonResponse(json.loads(json.dumps(token_json)), safe=False)


@csrf_exempt
@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
def increase_funding_limit_request(request):
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None
    usdt_per_tx = request.GET.get('usdt_per_tx', None)
    usdt_per_week = request.GET.get('usdt_per_week', None)
    is_staff = user.is_staff if user else False

    if is_staff and usdt_per_tx and usdt_per_week:
        try:
            profile_pk = request.GET.get('profile_pk', None)
            target_profile = Profile.objects.get(pk=profile_pk)
            target_profile.max_tip_amount_usdt_per_tx = usdt_per_tx
            target_profile.max_tip_amount_usdt_per_week = usdt_per_week
            target_profile.save()
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

        return JsonResponse({'msg': _('Success')}, status=200)

    if request.body:
        if not user or not profile or not profile.handle:
            return JsonResponse(
                {'error': _('You must be Authenticated via Github to use this feature!')},
                status=401)

        try:
            result = FundingLimitIncreaseRequestForm(json_parse(request.body))
            if not result.is_valid():
                raise
        except Exception as e:
            return JsonResponse({'error': _('Invalid JSON.')}, status=400)

        new_funding_limit_increase_request(profile, result.cleaned_data)

        return JsonResponse({'msg': _('Request received.')}, status=200)

    form = FundingLimitIncreaseRequestForm()
    params = {
        'form': form,
        'title': _('Request a Funding Limit Increase'),
        'card_title': _('Gitcoin - Request a Funding Limit Increase'),
        'card_desc': _('Do you hit the Funding Limit? Request a increasement!')
    }

    return TemplateResponse(request, 'increase_funding_limit_request_form.html', params)


def tribes_home(request):
    tribes = Profile.objects.filter(is_org=True).annotate(followers=Count('follower')).order_by('-followers')[:8]

    context = {
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/tw_cards-07.png')),
        'testimonials': testimonials(),
        'reasons': reasons(),
        'articles': articles(),
        'press': press(),
        'tribes': tribes,
        'show_sales_action': True,
    }

    return TemplateResponse(request, 'tribes/landing.html', context)


def admin_index(request):
    from dashboard.utils import get_all_urls # avoid circular import
    urls = get_all_urls() # source of truth is the app; email_info data just augments it
    search_str = '_administration/email'
    def clean_url(url):
        url = "".join(url)
        url = url.replace('$', '')
        url = url.replace('^', '')
        return url
    urls = [clean_url(url) for url in urls]
    urls = [url for url in urls if search_str in url]
    urls_dict = {}
    for url in urls:
        key = url.replace('_administration/email','')
        urls_dict[key] = ()
    email_info = EmailInventory.objects.all()
    for val in email_info:
        key = val.path
        urls_dict[key] = val
    del urls_dict['/']
    context = {
        'urls': urls_dict,
    }

    return TemplateResponse(request, 'admin_index.html', context)


def styleguide_components(request):
    if settings.ENV == 'prod':
        raise Http404
    else:
        context = {}
        return TemplateResponse(request, 'styleguide_components.html', context)


def jtbd_template(request, template, title, card_title, card_desc):
    data = JSONStore.objects.filter(view='jtbd', key=template).first().data
    context = {
        'title': _(title),
        'card_title': _(card_title),
        'card_desc': _(card_desc),
        'card_type': 'summary_large_image',
        'avatar_url': request.build_absolute_uri(static('v2/images/twitter_cards/twitter-landing-large.png')),
    }
    context.update(data)
    return TemplateResponse(request, 'jtbd/' + template + '.html', context)


@require_http_methods(["GET",])
def jtbd_earn(request):
    return jtbd_template(
        request,
        'earn',
        'Earn',
        'Gitcoin - Build the open internet.',
        'Earn a living building open source projects that matter.'
    )


@require_http_methods(["GET",])
def jtbd_learn(request):
    return jtbd_template(
        request,
        'learn',
        'Learn',
        'Gitcoin - Learn open source development.',
        'Learn how to build open source projects that matter.'
    )


@require_http_methods(["GET",])
def jtbd_connect(request):
    return jtbd_template(
        request,
        'connect',
        'Connect',
        'Gitcoin - A community of open web builders.',
        'Connect and build with top open source developers.'
    )


@require_http_methods(["GET",])
def jtbd_fund(request):
    return jtbd_template(
        request,
        'fund',
        'Fund',
        'Gitcoin - Support open web development.',
        'Fund open source projects that make the most difference.'
    )
