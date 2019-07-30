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
import logging
from json import loads as json_parse
from os import walk as walkdir

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from app.utils import get_default_network
from cacheops import cached_as, cached_view, cached_view_as
from dashboard.models import Activity, Bounty, Profile
from dashboard.notifications import amount_usdt_open_work, open_bounties
from economy.models import Token
from marketing.mails import new_funding_limit_increase_request, new_token_request
from marketing.models import Alumni, LeaderboardRank
from marketing.utils import get_or_save_email_subscriber, invite_to_slack
from perftools.models import JSONStore
from ratelimit.decorators import ratelimit
from retail.emails import render_nth_day_email_campaign
from retail.helpers import get_ip

from .forms import FundingLimitIncreaseRequestForm
from .utils import programming_languages

logger = logging.getLogger(__name__)

@cached_as(
    Activity.objects.select_related('bounty').filter(bounty__network='mainnet').order_by('-created'),
    timeout=120)
def get_activities(tech_stack=None, num_activities=15):
    # get activity feed

    activities = Activity.objects.select_related('bounty').filter(bounty__network='mainnet').order_by('-created')
    if tech_stack:
        activities = activities.filter(bounty__metadata__icontains=tech_stack)
    activities = activities[0:num_activities]
    return [a.view_props for a in activities]


def index(request):

    user = request.user.profile if request.user.is_authenticated else None

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

    know_us  = [
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

    press = [
        {
            'link': 'https://twit.tv/shows/floss-weekly/episodes/474',
            'img' : 'v2/images/press/floss_weekly.jpg'
        },
        {
            'link': 'https://epicenter.tv/episode/257/',
            'img' : 'v2/images/press/epicenter.jpg'
        },
        {
            'link': 'http://www.ibtimes.com/how-web-30-will-protect-our-online-identity-2667000',
            'img': 'v2/images/press/ibtimes.jpg'
        },
        {
            'link': 'https://www.forbes.com/sites/jeffersonnunn/2019/01/21/bitcoin-autonomous-employment-workers-wanted/',
            'img': 'v2/images/press/forbes.jpg'
        },
        {
            'link': 'https://unhashed.com/cryptocurrency-news/gitcoin-introduces-collectible-kudos-rewards/',
            'img': 'v2/images/press/unhashed.jpg'
        },
        {
            'link': 'https://www.coindesk.com/meet-dapp-market-twist-open-source-winning-developers/',
            'img': 'v2/images/press/coindesk.png'
        },
        {
            'link': 'https://softwareengineeringdaily.com/2018/04/03/gitcoin-open-source-bounties-with-kevin-owocki/',
            'img': 'v2/images/press/se_daily.png'
        },
        {
            'link': 'https://www.ethnews.com/gitcoin-offers-bounties-for-ens-integration-into-dapps',
            'img': 'v2/images/press/ethnews.jpg'
        },
        {
            'link': 'https://www.hostingadvice.com/blog/grow-open-source-projects-with-gitcoin/',
            'img': 'v2/images/press/hosting-advice.png'
        }
    ]

    articles = [
        {
            'link': 'https://medium.com/gitcoin/progressive-elaboration-of-scope-on-gitcoin-3167742312b0',
            'img': 'https://cdn-images-1.medium.com/max/2000/1*ErCNRMzIJguUGUgXgVc-xw.png',
            'title': _('Progressive Elaboration of Scope on Gitcoin'),
            'description': _('What is it? Why does it matter? How can you deal with it on Gitcoin?'),
            'alt': 'gitcoin scope'
        },
        {
            'link': 'https://medium.com/gitcoin/commit-reveal-scheme-on-ethereum-25d1d1a25428',
            'img': 'https://cdn-images-1.medium.com/max/1600/1*GTEu2R4xIxAApx50rAV_qw.png',
            'title': _('Commit Reveal Scheme on Ethereum'),
            'description': _('Hiding Actions and Generating Random Numbers'),
            'alt': 'commit reveal scheme'
        },
        {
            'link': 'https://medium.com/gitcoin/announcing-open-kudos-e437450f7802',
            'img': 'https://cdn-images-1.medium.com/max/2000/1*iPQYV3M-JOlYeFFC-iqfcg.png',
            'title': _('Announcing Open Kudos'),
            'description': _('Our vision for integrating Kudos in any (d)App'),
            'alt': 'open kudos'
        }
    ]

    context = {
        'products': products,
        'know_us': know_us,
        'press': press,
        'articles': articles,
        'hide_newsletter_caption': True,
        'hide_newsletter_consent': True,
        'newsletter_headline': _("Get the Latest Gitcoin News! Join Our Newsletter."),
        'title': _('Grow Open Source: Get crowdfunding and find freelance developers for your software projects, paid in crypto')
    }
    return TemplateResponse(request, 'home/index.html', context)


@staff_member_required
def pricing(request):

    plans= [
        {
            'type': 'basic',
            'img': '/v2/images/pricing/basic.svg',
            'fee': 10,
            'features': [
                '1 free <a href="/kudos">Kudos</a>',
                'Community Support'
            ],
            'features_na': [
                'Job Board Access',
                'Contributor Stats',
                'Multi-Seg Wallet',
                'Featured Bounties',
                'Job Listing'
            ]
        },
        {
            'type': 'pro',
            'img': '/v2/images/pricing/pro.svg',
            'price': 40,
            'features': [
                '5 Free <a href="/kudos">Kudos</a> / mo',
                'Community Support',
                'Job Board - Limited',
                'Contributor Stats'
            ],
            'features_na': [
                'Multi-Seg Wallet',
                'Featured Bounties',
                'Job Listings'
            ]
        },
        {
            'type': 'max',
            'img': '/v2/images/pricing/max.svg',
            'price': 99,
            'features': [
                '5 Free <a href="/kudos">Kudos</a> / mo',
                'Community Support',
                'Job Board Access',
                'Contributor Stats',
                'Multi-Sig Wallet',
                '5 Featured Bounties',
                '5 Job Listings'
            ]
        }
    ]

    companies = [
        {
            'name': 'Market Protocol',
            'img': 'v2/images/project_logos/market.png'
        },
        {
            'name': 'Consensys',
            'img': 'v2/images/consensys.svg'
        },
        {
            'name': 'Metamask',
            'img': 'v2/images/project_logos/metamask.png'
        },
        {
            'name': 'Ethereum Foundation',
            'img': 'v2/images/project_logos/eth.png'
        },
        {
            'name': 'Truffle',
            'img': 'v2/images/project_logos/truffle.png'
        },
    ]

    context = {
        'plans': plans,
        'companies': companies
    }

    return TemplateResponse(request, 'pricing/plans.html', context)


@staff_member_required
def subscribe(request):

    if request.POST:
        return TemplateResponse(request, 'pricing/subscribe.html', {})

    from gas.utils import conf_time_spread, eth_usd_conv_rate, gas_advisories, recommend_min_gas_price_to_confirm_in_time

    plan = {
        'type': 'pro',
        'img': '/v2/images/pricing/sub_pro.svg',
        'price': 40
    }

    if request.GET:
        if 'plan' in request.GET and request.GET['plan'] == 'max':
            plan = {
                'type': 'max',
                'img': '/v2/images/pricing/sub_max.svg',
                'price': 99
            }
        if 'pack' in request.GET and request.GET['pack'] == 'annual':
            plan['price'] = plan['price'] - plan['price'] / 10

    context = {
        'plan': plan,
        'recommend_gas_price': recommend_min_gas_price_to_confirm_in_time(4),
        'recommend_gas_price_slow': recommend_min_gas_price_to_confirm_in_time(120),
        'recommend_gas_price_avg': recommend_min_gas_price_to_confirm_in_time(15),
        'recommend_gas_price_fast': recommend_min_gas_price_to_confirm_in_time(1),
        'eth_usd_conv_rate': eth_usd_conv_rate(),
        'conf_time_spread': conf_time_spread(),
        'gas_advisories': gas_advisories(),
    }
    return TemplateResponse(request, 'pricing/subscribe.html', context)


def funder_bounties_redirect(request):
    return redirect(funder_bounties)


def funder_bounties(request):

    onboard_slides = [
        {
            'img': static("v2/images/presskit/illustrations/prime.svg"),
            'title': _('Are you a developer or designer?'),
            'subtitle': _('Contribute to exciting OSS project and get paid!'),
            'type': 'contributor',
            'active': 'active',
            'more': '/bounties/contributor'
        },
        {
            'img': static("v2/images/presskit/illustrations/regulus-white.svg"),
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
        'active': 'home',
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
            'img': static("v2/images/presskit/illustrations/regulus-white.svg"),
            'title': _('Are you a funder or project organizer?'),
            'subtitle': _('Fund your OSS bounties and get work done!'),
            'type': 'funder',
            'active': 'active',
            'more': '/bounties/funder'
        },
        {
            'img': static("v2/images/presskit/illustrations/prime.svg"),
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
        'onboard_slides': onboard_slides,
        'slides': slides,
        'slideDurationInMs': 6000,
        'active': 'home',
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
        new_context = JSONStore.objects.get(view='contributor_landing_page', key=tech_stack).data

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


@cached_view_as(Profile.objects.hidden())
def robotstxt(request):
    hidden_profiles = Profile.objects.hidden()
    context = {
        'settings': settings,
        'hidden_profiles': hidden_profiles,
    }
    return TemplateResponse(request, 'robots.txt', context, content_type='text')


def about(request):
    core_team = [
        (
            "Kevin Owocki",
            "All the things",
            "owocki",
            "owocki",
            "The Community",
            "Avocado Toast"
        ),
        (
            "Alisa March",
            "User Experience Design",
            "PixelantDesign",
            "pixelant",
            "Tips",
            "Apple Cider Doughnuts"
        ),
        (
            "Eric Berry",
            "OSS Funding",
            "coderberry",
            "ericberry",
            "Chrome/Firefox Extension",
            "Pastel de nata"
        ),
        (
            "Vivek Singh",
            "Community Buidl-er",
            "vs77bb",
            "vivek-singh-b5a4b675",
            "Gitcoin Requests",
            "Tangerine Gelato"
        ),
        (
            "Aditya Anand M C",
            "Engineering",
            "thelostone-mc",
            "aditya-anand-m-c-95855b65",
            "The Community",
            "Cocktail Samosa"
        ),
        (
            "Scott Moore",
            "Biz Dev",
            "ceresstation",
            "scott-moore-a2970075",
            "Issue Explorer",
            "Teriyaki Chicken"
        ),
        (
            "Octavio Amuchástegui",
            "Front End Dev",
            "octavioamu",
            "octavioamu",
            "The Community",
            "Homemade italian pasta"
        ),
        (
            "Frank Chen",
            "Data & Product",
            "frankchen07",
            "frankchen07",
            "Kudos!",
            "Crispy pork belly"
        ),
        (
            "Nate Hopkins",
            "Engineering",
            "hopsoft",
            None,
            "Bounties",
            "Chicken tikka masala"
        ),
        (
            "Dan Lipert",
            "Engineering",
            "danlipert",
            "danlipert",
            "EIP 1337",
            "Tantan Ramen"
        )

    ]
    exclude_community = ['kziemiane', 'owocki', 'mbeacom']
    community_members = [
    ]
    leadeboardranks = LeaderboardRank.objects.filter(active=True, leaderboard='quarterly_earners').exclude(github_username__in=exclude_community).order_by('-amount').cache()[0: 15]
    for lr in leadeboardranks:
        package = (lr.avatar_url, lr.github_username, lr.github_username, '')
        community_members.append(package)

    alumnis = [
    ]
    for alumni in Alumni.objects.select_related('profile').filter(public=True).exclude(organization='gitcoinco').cache():
        package = (alumni.profile.avatar_url, alumni.profile.username, alumni.profile.username, alumni.organization)
        alumnis.append(package)

    context = {
        'core_team': core_team,
        'community_members': community_members,
        'alumni': alumnis,
        'total_alumnis': str(Alumni.objects.count()),
        'active': 'about',
        'title': 'About',
        'is_outside': True,
    }
    return TemplateResponse(request, 'about.html', context)


def mission(request):
    """Render the Mission response."""

    values = [
        {
            'name': _('Self Reliance'),
            'img': 'v2/images/mission/value/collaborative.svg',
            'alt': 'we-collobarate-icon'
        },
        {
            'name': _('Intellectual honesty'),
            'img': 'v2/images/mission/value/love_hands.svg',
            'alt': 'intellectual-honesty-icon'
        },
        {
            'name': _('Collaboration'),
            'img': 'v2/images/mission/value/humble.svg',
            'alt': 'humble-icon'
        },
        {
            'name': _('Empathy'),
            'img': 'v2/images/mission/value/empathetic.svg',
            'alt': 'empathy-icon'
        },
        {
            'name': _('Stress Reducers'),
            'img': 'v2/images/mission/value/stress_reducing.svg',
            'alt': 'stress-reduce-icon'
        },
        {
            'name': _('Inclusivity'),
            'img': 'v2/images/mission/value/inclusive.svg',
            'alt': 'inclusive-icon'
        },
        {
            'name': _('Giving first'),
            'img': 'v2/images/mission/value/give_first.svg',
            'alt': 'give-first-icon'
        }
    ]

    interactions = [
        {
            'text': _('We happen to the world. We don\'t let the world happen to us.'),
            'img': 'v2/images/mission/interact/world.svg',
            'alt': 'world-icon'
        },
        {
            'text': _('We show, don\'t tell.'),
            'img': 'v2/images/mission/interact/book.svg',
            'alt': 'openness-icon'
        },
        {
            'text': _('We are thoughtful, clear, and direct.'),
            'img': 'v2/images/mission/interact/head.svg',
            'alt': 'thoughtful-icon'
        },
        {
            'text': _('We seek balance.'),
            'img': 'v2/images/mission/interact/scale.svg',
            'alt': 'balance-icon'
        },
        {
            'text': _('We challenge the status quo &amp; are willing to be challenged.'),
            'img': 'v2/images/mission/interact/goal.svg',
            'alt': 'goal-icon'
        },
        {
            'text': _('We fix things twice.'),
            'img': 'v2/images/mission/interact/hammer.svg',
            'alt': 'fix-twicw-icon'
        },
        {
            'text': _('We identify and validate our assumptions.'),
            'img': 'v2/images/mission/interact/microscope.svg',
            'alt': 'microscope-icon'
        },
        {
            'text': _('We care about people (not just tasks).'),
            'img': 'v2/images/mission/interact/people_care.svg',
            'alt': 'care-icon'
        },
        {
            'text': _('We listen.'),
            'img': 'v2/images/mission/interact/hear.svg',
            'alt': 'microscope-icon'
        },
        {
            'text': _('We value pragmatism over dogmatism.'),
            'img': 'v2/images/mission/interact/swiss_army.svg',
            'alt': 'pargma-icon'
        }
    ]

    context = {
        'is_outside': True,
        'active': 'mission',
        'title': 'Mission',
        'card_title': _('Gitcoin is a mission-driven organization.'),
        'card_desc': _('Our mission is to grow open source.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
        'values': values,
        'interactions': interactions
    }
    return TemplateResponse(request, 'mission.html', context)


def jobs(request):
    job_listings = [
        {
            'link': "mailto:founders@gitcoin.co",
            'title': "Software Engineer",
            'description': [
                "Gitcoin is always looking for a few good software engineers.",
                "If you are an active member of the community, have python + django + html chops",
                "then we want to talk to you!"]
        },
        {
            'link': "mailto:founders@gitcoin.co",
            'title': "Community Manager",
            'description': [
                "We believe that community management is an important skill in the blockchain space.",
                "We're looking for a solid community, proactive thinker, and someone who loves people",
                "to be our next community manager.  Sound like you?  Apply below!"]
        },
        {
            'link': "mailto:founders@gitcoin.co",
            'title': "Ad Sales Engineer",
            'description': [
                "CodeFund is growing like a weed.  We could use a helping hand",
                "to put CodeFund in front of more great advertisers and publishers.",
                "If you want to be our next highly technical, highly engaging, sales engineer apply below!"]
        }
    ]
    context = {
        'active': 'jobs',
        'title': 'Jobs',
        'job_listings': job_listings
    }
    return TemplateResponse(request, 'jobs.html', context)


def vision(request):
    """Render the Vision response."""
    context = {
        'is_outside': True,
        'active': 'vision',
        'avatar_url': static('v2/images/vision/triangle.jpg'),
        'title': 'Vision',
        'card_title': _("Gitcoin's Vision for a Web3 World"),
        'card_desc': _("Gitcoin's Vision for a web3 world is to make it easy for developers to find paid work in open source."),
    }
    return TemplateResponse(request, 'vision.html', context)


def products(request):
    """Render the Products response."""
    products = [
        {
            'name': 'bounties',
            'heading': _("Solve bounties. Get paid. Contribute to open source"),
            'description': _("Collaborate and monetize your skills while working on Open Source projects \
                            through bounties."),
            'link': '/explorer',
            'img': static('v2/images/products/graphics-Bounties.png'),
            'logo': static('v2/images/products/gitcoin-logo.svg')
        },
        {
            'name': 'kudos',
            'heading': _("Show your appreciation with collectible tokens"),
            'description': _("Kudos is a way of showing your appreciation to another Gitcoin member.\
                            It's also a way to showcase special skills that a member might have."),
            'link': '/kudos',
            'img': static('v2/images/products/graphics-Kudos.png'),
            'logo': static('v2/images/products/kudos-logo.svg')
        },
        {
            'name': 'grants',
            'heading': _("Sustainable funding for open source"),
            'description': _("Gitcoin Grants are a fast, easy & secure way to provide recurring token \
                            contributions to your favorite OSS maintainers. Powered by EIP1337."),
            'link': '/grants',
            'img': static('v2/images/products/graphics-Grants.png'),
            'logo': static('v2/images/products/grants-logo.svg')
        },
        {
            'name': 'codefund',
            'heading': _("Ethical advertising for developers"),
            'description': _("CodeFund is an open source ad platform that funds contributors of the open \
                            source ecosystem"),
            'link': 'https://codefund.app/',
            'img': static('v2/images/products/graphics-Codefund.svg'),
            'logo': static('v2/images/products/codefund-logo.svg')
        },
        {
            'name': 'labs',
            'heading': _("Tools for busy developers"),
            'description': _("Gitcoin Labs provides research reports and toolkits for busy developers, \
                            making Ethereum dapps fast, usable, and secure."),
            'link': '/labs',
            'img': static('v2/images/products/graphics-Labs.png'),
            'logo': static('v2/images/products/labs-logo.svg')
        }
    ]

    context = {
        'is_outside': True,
        'active': 'products',
        'title': 'Products',
        'card_title': _("Gitcoin's Products."),
        'card_desc': _('At Gitcoin, we build products that allow for better incentivized collaboration \
                        in the realm of open source software'),
        'avatar_url': static('v2/images/grow_open_source.png'),
        'products': products,
    }
    return TemplateResponse(request, 'products.html', context)


def not_a_token(request):
    """Render the not_a_token response."""
    context = {
        'is_outside': True,
        'active': 'not_a_token',
        'avatar_url': static('v2/images/no-token/no-token.jpg'),
        'title': 'Gitcoin is not a token',
        'card_title': _("Gitcoin is not a token"),
        'card_desc': _("We didn't do a token because we felt it wasn't the right way to align incentives \
                        with our user base.  Read more about the future of monetization in web3."),
    }
    return TemplateResponse(request, 'not_a_token.html', context)


def results(request, keyword=None):
    """Render the Results response."""
    if keyword and keyword not in programming_languages:
        raise Http404
    context = JSONStore.objects.get(view='results', key=keyword).data
    context['is_outside'] = True
    import json
    context['kudos_tokens'] = [json.loads(obj) for obj in context['kudos_tokens']]
    context['avatar_url'] = static('v2/images/results_preview.gif')
    return TemplateResponse(request, 'results.html', context)


def activity(request):
    """Render the Activity response."""
    page_size = 15
    activities = Activity.objects.all().order_by('-created')
    p = Paginator(activities, page_size)
    page = int(request.GET.get('page', 1))

    context = {
        'p': p,
        'next_page': page + 1,
        'page': p.get_page(page),
        'title': _('Activity Feed'),
    }
    context["activities"] = [a.view_props for a in p.get_page(page)]

    return TemplateResponse(request, 'activity.html', context)


def help(request):
    faq = {
        'Product': [
        {
            'q': _('I am a developer, I want build more Open Source Software. Where can I start?'),
            'a': _("The <a href=https://gitcoin.co/explorer>Funded Issue Explorer</a> contains a handful of issues that are ready to be paid out as soon as they are turned around. Check out the developer guide at <a href=https://gitcoin.co/help/dev>https://gitcoin.co/help/dev</a>.")
        },
        {
            'q': _('I am a repo maintainer.  How do I get started?'),
            'a': _("The best way to get started is to post a funded issue on a task you need done.  Check out the repo maintainers guide at <a href=https://gitcoin.co/help/repo>https://gitcoin.co/help/repo</a>.")
        },
        {
            'q': _('What tokens does Gitcoin support?'),
            'a': _("Gitcoin supports Ether and all ERC20 tokens.  If the token you'd like to use is Ethereum based, then Gitcoin supports it.")
        },
        {
            'q': _('What kind of issues are fundable?'),
            'a': _("""

    <p class="c5"><span class="c4 c0">Gitcoin supports bug, feature, and security funded issues. &nbsp;Any issue that you need done is a good candidate for a funded issue, provided that:</span></p><ul class="c13 lst-kix_twl0y342ii52-0 start"><li class="c5 c11"><span class="c4 c0">It&rsquo;s open today.</span></li><li class="c5 c11"><span class="c4 c0">The repo README clearly enumerates how a new developer should get set up to contribute.</span></li><li class="c5 c11"><span class="c4 c0">The task is well defined.</span></li><li class="c5 c11"><span class="c4 c0">The end-state of the task is well defined.</span></li><li class="c5 c11"><span class="c4 c0">The pricing of the task reflects (market rate * complexity) of the task.</span></li><li class="c5 c11"><span class="c4 c0">The issue is on the roadmap, but does not block other work.</span></li></ul><p class="c5 c6"><span class="c4 c0"></span></p><p class="c5"><span class="c4 c0">To get started with funded issues today, it might be good to start small. &nbsp;Is there a small bug that needs fixed? &nbsp;An issue that&rsquo;s been open for a while that no one is tackling? &nbsp;An administrative task?</span></p>


            """)
        },
        {
            'q': _('Whats the difference between tips & funded issues?'),
            'a': _("""

<p>
<strong>A tip</strong> is a tool to send ether or any ethereum token to any github account.  The flow for tips looks like this:
</p><p>
> Send (party 1) => receive (party 2)
</p><p>

<strong>Funded Issues</strong> are a way to fund open source features, bugs, or security bounties.  The flow for funded issues looks like this:
</p><p>

>  Fund Issue (party 1) => claim funds  (party 2) => accept (party 1)
</p>


            """)
        },
        {
            'q': _('What kind of contributors are successful on the Gitcoin network?'),
            'a': _("""

<p>
If you have an issues board that needs triaged, read on..
</p>
<p>
If you would like to recruit engineers to help work on your repo, read on..
</p>
<p>
If you want to create value, and receive Ether tokens in return, read on..
</p>
<p>
If you are looking for a quick win, an easy buck, or to promote something, please turn around.
</p>

<p>
We value communication that is:
</p>

<ul>
<li>
    Collaborative
</li>
<li>
    Intellectual & Intellectually Honest
</li>
<li>
    Humble
</li>
<li>
    Empathetic
</li>
<li>
    Pragmatic
</li>
<li>
    Stress reducing
</li>
</ul>

<p>
Here are some of our values
</p>
<ul>
<li>
    Show, don't tell
</li>
<li>
    Give first
</li>
<li>
     Be thoughtful & direct
</li>
<li>
     Be credible
</li>
<li>
     Challenge the status quo and be willing to be challenged
</li>
<li>
     Create delightful experiences
</li>
</ul>


            """)
        },
        {
            'q': _('I received a notification about tip / funded issue, but I can\'t process it.  Help!'),
            'a': _("We'd love to help!  Please email <a href='mailto:founders@gitcoin.co'>founders@gitcoin.co</a> or join <a href=/slack>Gitcoin Community Slack</a>.")
        },
        {
            'q': _('Am I allowed to place bounties on projects I don\'t contribute to or own?'),
            'a': _("TLDR: Yes you are.  But as OSS devs ourselves, our experience has been that if you want to get the product you work on merged into the upstream, you will need to work with the contributors or owners of that repo.  If not, you can always fork a repo and run your own roadmap.")
        },
        {
            'q': _('I started work on a bounty but someone else has too.  Who gets it?'),
            'a': _("As a general rule, we tend to treat the person who 'started work' first as having precedence over the issue.  The parties involved are all welcome to work together to split the bounty or come to some other agreement, but if an agreement is uanble to be made, then the first person to start work will have first shot at the bounty.")
        },
        ],
     'General': [
        {
            'q': _('Is Gitcoin open source?'),
            'a': _("Yes, all of Gitcoin's core software systems are open source and available at "
                   "<a href=https://github.com/gitcoinco/>https://github.com/gitcoinco/</a>.  Please see the "
                   "LICENSE.txt file in each repo for more details.")
        },
        {
            'q': _('Is a token distribution event planned for Gitcoin?'),
            'a': _("""
<p>Gitcoin Core is considering doing a token distribution event (TDI), but at the time is focused first and foremost on providing value in Open Source Software&nbsp;in a lean way.</p>
<p>To find out more about a possible upcoming token distribution event,&nbsp;check out&nbsp;<a href="https://gitcoin.co/whitepaper">https://gitcoin.co/whitepaper</a></p>
<p>&nbsp;</p>            """)
        },
        {
            'q': _('What is the difference between Gitcoin and Gitcoin Core?'),
            'a': _("""
Gitcoin Core LLC is the legal entity that manages the software development of the Gitcoin Network (Gitcoin).

The Gitcoin Network is a series of smart contracts that helps Grow Open Source, but enabling developers to easily post and manage funded issues.            """)
        },
        {
            'q': _('Who is the team at Gitcoin Core?'),
            'a': _("""
<p>The founder is <a href="https://linkedin.com/in/owocki">Kevin Owocki</a>, a technologist from the Boulder Colorado tech scene. &nbsp; &nbsp;Kevin&nbsp;has a BS in Computer Science, 15 years experience in Open Source Software and Technology Startups. He is a volunteer in the Boulder Community for several community organizations, and an avid open source developer. His work has been featured in&nbsp;<a href="http://techcrunch.com/2011/02/10/group-dating-startup-ignighter-raises-3-million/">TechCrunch</a>,&nbsp;<a href="http://www.cnn.com/2011/BUSINESS/03/29/india.online.matchmaking/">CNN</a>,&nbsp;<a href="http://www.inc.com/30under30/2011/profile-adam-sachs-kevin-owocki-and-dan-osit-founders-ignighter.html">Inc Magazine</a>,&nbsp;<a href="http://www.nytimes.com/2011/02/20/business/20ignite.html?_r=4&amp;amp;pagewanted=1&amp;amp;ref=business">The New York Times</a>,&nbsp;<a href="http://boingboing.net/2011/09/24/tosamend-turn-all-online-i-agree-buttons-into-negotiations.html">BoingBoing</a>,&nbsp;<a href="http://www.wired.com/2015/12/kevin-owocki-adblock-to-bitcoin/">WIRED</a>,&nbsp;<a href="https://www.forbes.com/sites/amycastor/2017/08/31/toothpick-takes-top-prize-in-silicon-beach-ethereum-hackathon/#6bf23b7452ad">Forbes</a>, and&nbsp;<a href="http://www.techdigest.tv/2007/08/super_mario_get_1.html">TechDigest</a>.</p>
<p><strong>Gitcoin</strong>&nbsp;was borne of the community in Boulder Colorado's thriving tech scene. One of the most amazing things about the Boulder community is the #givefirst mantra. The founding team has built their careers off of advice, mentorship, and relationships in the local tech community. &nbsp;</p>

<p>We are hiring.  If you want to join the team, <a href=mailto:founders@gitcoin.co>email us</a>.

            """)
        },
        {
            'q': _('What is the mission of Gitcoin Core?'),
            'a': _("""
The mission of Gitcoin is "Grow Open Source".

            """)
        },
        {
            'q': _('How can I stay in touch with project updates?'),
            'a': _("""
The best way to stay in touch is to

<ul>
<li>
    <a href="/#mailchimp">Subscribe to the mailing list</a>
</li>
<li>
    <a href="/twitter">Follow the project on twitter</a>
</li>
<li>
    <a href="/slack">Join the slack channel</a>
</li>

</ul>

            """)
        },
     ],
     'Web3': [
        {
            'category': "Web3",
            'q': _('What is the difference between Gitcoin and centralized hiring websites?'),
            'a': gettext("""
<p>There are many successful centralized hiring resources available on the web. &nbsp;Because these platforms were an&nbsp;efficient way to source, select, and manage a global workforce , millions of dollars was&nbsp;processed through these systems every day.</p>
<p>Gitcoin takes the value that flows through these system, and makes it more efficient and fair. &nbsp;Gitcoin is a distributed network of smart contracts, based upon Ethereum, that aims to solve problems with centralized hiring resources, namely by</p>
<ul>
<li>being more open,</li>
<li>being more fair,</li>
<li>being more efficient,</li>
<li>being easier to use.</li>
<li>leveraging a global workforce,</li>
<li>cutting out the middlemen,</li>
</ul>
<p>When Sir Tim Berners-Lee first invented the World Wide Web in the late 1980s&nbsp;to make information sharing on the Internet easier, he did something very important. He specified an open protocol, the Hypertext Transfer Protocol or HTTP, that anyone could use to make information available and to access such information. &nbsp;</p>
<p>Gitcoin is similarly built on an open protocol of smart contracts.</p>
<p>By specifying a&nbsp;protocol, Tim Berners-Lee opened the way for anyone to build software, so-called web servers and browsers that would be compatible with this protocol. &nbsp; By specifying an open source protocol for Funding Issues and software development scoping &amp; payment, the Gitcoin Core team hopes to similarly inspire a generation of inventions in 21st century software.</p>
<p>
To learn more about blockchain, please checkout <a href="{}">this video about web3</a> or the <a href="https://github.com/gitcoinco/gitcoinco/issues?q=is%3Aissue+is%3Aopen+label%3Ahelp">Github Issues board</a>
</p>
            """).format(reverse('web3'))
        },
        {
            'q': _('Why do I need metamask?'),
            'a': gettext("""
<p>
You need <a href="https://metamask.io/">Metamask</a> in order to use Gitcoin.
</p>
<p>

Metamask turns google chrome into a Web3 Browser.   Web3 is powerful because it lets websites retrieve data from the blockchain, and lets users securely manage identity.
</p>
<p>

In contrast to web2 where third parties own your data, in web3 you own your data and you are always in control.  On web3, your data is secured on the blockchain, which means that no one can ever freeze your assets or censor you.
</p>
<p>

Download Metamask <a href="https://metamask.io/">here</a> today.
</p>
<p>
To learn more about Metamask, please checkout <a href="{}">this video about web3</a> or the <a href="https://github.com/gitcoinco/gitcoinco/issues?q=is%3Aissue+is%3Aopen+label%3Ahelp">Github Issues board</a>
</p>

           """).format(reverse('web3'))
        },
        {
            'q': _('Why do I need to pay gas?'),
            'a': _("""
<p>
"Gas" is the name for a special unit used in Ethereum. It measures how much "work" an action or set of actions takes to perform (for example, storing data in a smart contract).
</p>
<p>
The reason gas is important is that it helps to ensure an appropriate fee is being paid by transactions submitted to the network. By requiring that a transaction pay for each operation it performs (or causes a contract to perform), we ensure that network doesn't become bogged down with performing a lot of intensive work that isn't valuable to anyone.
</p>
<p>
Gas fees are paid to the maintainers of the Ethereum network, in return for securing all of the Ether and Ethereum-based transactions in the world.  Gas fees are not paid to Gitcoin Core directly or indirectly.
</p>
<p>
To learn more about gas, pleaes checkout the <a href="https://github.com/gitcoinco/gitcoinco/issues?q=is%3Aissue+is%3Aopen+label%3Ahelp">Github Issues board</a>
</p>
           """)
        },
        {
            'q': _('What are the advanages of Ethereum based applications?'),
            'a': gettext("""
Here are some of the advantages of Ethereum based applications:
<ul>
<li>
    Lower (or no) fees
</li>
<li>
    No middlemen
</li>
<li>
    No third party owns or can sell your data
</li>
<li>
    No international conversion fees
</li>
<li>
    Get paid in protocol, utility, or application tokens; not just cash.
</li>
</ul>
<p>
To learn more about Ethereum based apps, please checkout <a href="{}">this video about web3</a> or the <a href="https://github.com/gitcoinco/gitcoinco/issues?q=is%3Aissue+is%3Aopen+label%3Ahelp">Github Issues board</a>
</p>


           """).format(reverse('web3'))
        },
        {
            'q': _('I still dont get it.  Help!'),
            'a': _("""
We want to nerd out with you a little bit more.  <a href="/slack">Join the Gitcoin Slack Community</a> and let's talk.


""")
        },
     ],
    }

    tutorials = [{
        'img': static('v2/images/help/firehose.jpg'),
        'url': 'https://medium.com/gitcoin/tutorial-leverage-gitcoins-firehose-of-talent-to-do-more-faster-dcd39650fc5',
        'title': _('Leverage Gitcoin’s Firehose of Talent to Do More Faster'),
    }, {
        'img': static('v2/images/tools/api.jpg'),
        'url': 'https://medium.com/gitcoin/tutorial-how-to-price-work-on-gitcoin-49bafcdd201e',
        'title': _('How to Price Work on Gitcoin'),
    }, {
        'img': 'https://raw.github.com/gitcoinco/Gitcoin-Exemplars/master/helpImage.png',
        'url': 'https://github.com/gitcoinco/Gitcoin-Exemplars',
        'title': _('Exemplars for Writing A Good Bounty Description'),
    }, {
        'img': static('v2/images/help/tools.png'),
        'url': 'https://medium.com/gitcoin/tutorial-post-a-bounty-in-90-seconds-a7d1a8353f75',
        'title': _('Post a Bounty in 90 Seconds'),
    }, {
        'img': static('v2/images/tldr/tips_noborder.jpg'),
        'url': 'https://medium.com/gitcoin/tutorial-send-a-tip-to-any-github-user-in-60-seconds-2eb20a648bc8',
        'title': _('Send a Tip to any Github user in 60 seconds'),
    }, {
        'img': 'https://cdn-images-1.medium.com/max/1800/1*IShTwIlxOxbVAGYbOEfbYg.png',
        'url': 'https://medium.com/gitcoin/how-to-build-a-contributor-friendly-project-927037f528d9',
        'title': _('How To Build A Contributor Friendly Project'),
    }, {
        'img': 'https://cdn-images-1.medium.com/max/2000/1*23Zxk9znad1i422nmseCGg.png',
        'url': 'https://medium.com/gitcoin/fund-an-issue-on-gitcoin-3d7245e9b3f3',
        'title': _('Fund An Issue on Gitcoin!'),
    }, {
        'img': 'https://cdn-images-1.medium.com/max/2000/1*WSyI5qFDmy6T8nPFkrY_Cw.png',
        'url': 'https://medium.com/gitcoin/getting-started-with-gitcoin-fa7149f2461a',
        'title': _('Getting Started With Gitcoin'),
    }]

    context = {
        'active': 'help',
        'title': _('Help'),
        'faq': faq,
        'tutorials': tutorials,
    }
    return TemplateResponse(request, 'help.html', context)


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
            "Cosmic Teal",
            "#25e899",
            "37, 232, 153"
        ),
        (
            "Dark Cosmic Teal",
            "#0fce7c",
            "15, 206, 124"
        ),
        (
            "Milky Way Blue",
            "#15003e",
            "21, 0, 62"
        ),
        (
            "Stardust Yellow",
            "#FFCE08",
            "255,206, 8"
        ),
        (
            "Polaris Blue",
            "#3E00FF",
            "62, 0, 255"
        ),
        (
            "Vinus Purple",
            "#8E2ABE",
            "142, 42, 190"
        ),
        (
            "Regulus Red",
            "#F9006C",
            "249, 0, 108"
        ),
        (
            "Star White",
            "#FFFFFF",
            "23, 244, 238"
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
        'code': code
    }
    context['title'] = "Error {}".format(code)
    return_as_json = 'api' in request.path

    if return_as_json:
        return JsonResponse(context, status=500)
    return TemplateResponse(request, 'error.html', context, status=code)


def portal(request):
    return redirect('https://gitcoin.co/help')


def community(request):
    return redirect('https://github.com/gitcoinco/community')


def onboard(request):
    return redirect('https://docs.google.com/document/d/1DQvek5TwASIp1njx5VZeLKEgSxfvxm871vctx1l_33M/edit?')


def podcast(request):
    return redirect('https://itunes.apple.com/us/podcast/gitcoin-community/id1360536677')


def feedback(request):
    return redirect('https://goo.gl/forms/9rs9pNKJDnUDYEeA3')


def help_dev(request):
    return redirect('https://docs.google.com/document/d/1S8BLKJF7J5RbrfFw-mX0iYcy4VSc6-a1aQXtKT_ta0Y/edit')


def help_pilot(request):
    return redirect('https://docs.google.com/document/d/1R-qQKlIcW38d7l6GumehDlOhdmX1-6Ibab3gE06qotQ/edit')


def help_repo(request):
    return redirect('https://docs.google.com/document/d/1_U9IdDN8FIRMGAdLWCMl2BnqCTAv558QvyJiSWQfkbs/edit')


def help_faq(request):
    return redirect('https://gitcoin.co/help#faq')


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
    context = {
        'active': 'slack',
        'msg': None,
        'nav': 'home',
    }

    if request.POST:
        email = request.POST.get('email')
        context['msg'] = _('You must provide an email address')
        if email:
            context['msg'] = _('Your invite has been sent.')
            context['success'] = True
            try:
                validate_email(email)
                get_or_save_email_subscriber(email, 'slack', send_slack_invite=False)
                response = invite_to_slack(email)

                if not response.get('ok'):
                    context['msg'] = response.get('error', _('Unknown error'))
                context['success'] = False
            except ValidationError:
                context['msg'] = _('Invalid email')

    return TemplateResponse(request, 'slack.html', context)


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

def livestream(request):
    return redirect('https://calendar.google.com/calendar/r?cid=N3JxN2dhMm91YnYzdGs5M2hrNjdhZ2R2ODhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ')


def twitter(request):
    return redirect('http://twitter.com/gitcoin')


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


@cached_view_as(Token.objects.filter(network=get_default_network, approved=True))
def tokens(request):
    context = {}
    networks = ['mainnet', 'ropsten', 'rinkeby', 'unknown', 'custom']
    for network in networks:
        key = f"{network}_tokens"
        context[key] = Token.objects.filter(network=network, approved=True)
    return TemplateResponse(request, 'tokens_js.txt', context, content_type='text/javascript')


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
