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
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.http import Http404, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from dashboard.models import Activity, Bounty
from dashboard.notifications import amount_usdt_open_work, open_bounties
from dashboard.tokens import token_by_name
from economy.models import Token
from marketing.mails import new_token_request
from marketing.models import Alumni, LeaderboardRank
from marketing.utils import get_or_save_email_subscriber, invite_to_slack
from retail.helpers import get_ip

from .utils import build_stat_results, programming_languages


def index(request):
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
        'is_outside': True,
        'slides': slides,
        'slideDurationInMs': 6000,
        'active': 'home',
        'hide_newsletter_caption': True,
        'hide_newsletter_consent': True,
        'gitcoin_description': gitcoin_description,
        'newsletter_headline': _("Get the Latest Gitcoin News! Join Our Newsletter.")
    }
    return TemplateResponse(request, 'index.html', context)


def contributor_landing(request, tech_stack):

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

    available_bounties_count = open_bounties().count()
    available_bounties_worth = amount_usdt_open_work()
    
    context = {
        'title': tech_stack.title() + str(_(" Open Source Opportunities")) if tech_stack else "Open Source Opportunities",
        'slides': slides,
        'slideDurationInMs': 6000,
        'active': 'home',
        'newsletter_headline': _("Be the first to find out about newly posted bounties."),
        'hide_newsletter_caption': True,
        'hide_newsletter_consent': True,
        'projects': projects,
        'gitcoin_description': gitcoin_description,
        'available_bounties_count': available_bounties_count,
        'available_bounties_worth': available_bounties_worth,
        'tech_stack': tech_stack,
    }

    return TemplateResponse(request, 'contributor_landing.html', context)

def how_it_works(request, work_type):
    """Show How it Works / Funder page."""
    if work_type not in ['funder', 'contributor']:
        raise Http404

    context = {
        'active': f'how_it_works_{work_type}',
    }
    return TemplateResponse(request, 'how_it_works.html', context)


def robotstxt(request):
    return TemplateResponse(request, 'robots.txt', {})


def about(request):
    core_team = [
        (
            static("v2/images/team/kevin-owocki.png"),
            "Kevin Owocki",
            "All the things",
            "owocki",
            "owocki",
            "The Community",
            "Avocado Toast"
        ),
        (
            static("v2/images/team/alisa-march.jpg"),
            "Alisa March", "User Experience Design",
            "PixelantDesign",
            "pixelant",
            "Tips",
            "Apple Cider Doughnuts"
        ),
        (
            static("v2/images/team/justin-bean.jpg"),
            "Justin Bean", "Engineering",
            "StareIntoTheBeard",
            "justinbean",
            "Issue Explorer",
            "Sushi"
        ),
        (
            static("v2/images/team/mark-beacom.jpg"),
            "Mark Beacom",
            "Engineering",
            "mbeacom",
            "mbeacom",
            "Start/Stop Work",
            "Dolsot Bibimbap"
        ),
        (
            static("v2/images/team/eric-berry.jpg"),
            "Eric Berry",
            "OSS Funding",
            "coderberry",
            "ericberry",
            "Chrome/Firefox Extension",
            "Pastel de nata"
        ),
        (
            static("v2/images/team/vivek-singh.jpg"),
            "Vivek Singh",
            "Community Buidl-er",
            "vs77bb",
            "vivek-singh-b5a4b675",
            "Gitcoin Requests",
            "Tangerine Gelato"
        ),
        (
            static("v2/images/team/aditya-anand.jpg"),
            "Aditya Anand M C",
            "Engineering",
            "thelostone-mc",
            "aditya-anand-m-c-95855b65",
            "The Community",
            "Cocktail Samosa"
        ),
        (
            static("v2/images/team/saptaks.jpg"),
            "Saptak Sengupta",
            "Engineering",
            "saptaks",
            "saptaks",
            "Everything Open Source",
            "daab chingri"
        ),
        (
            static("v2/images/team/scott.jpg"),
            "Scott Moore",
            "Biz Dev",
            "ceresstation",
            "scott-moore-a2970075",
            "Issue Explorer",
            "Teriyaki Chicken"
        ),
    ]
    exclude_community = ['kziemiane', 'owocki', 'mbeacom']
    community_members = [
    ]
    leadeboardranks = LeaderboardRank.objects.filter(active=True, leaderboard='quarterly_earners').exclude(github_username__in=exclude_community).order_by('-amount')[0: 15]
    for lr in leadeboardranks:
        package = (lr.avatar_url, lr.github_username, lr.github_username, '')
        community_members.append(package)

    alumnis = [
    ]
    for alumni in Alumni.objects.select_related('profile').filter(public=True).exclude(organization='gitcoinco'):
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
    context = {
        'is_outside': True,
        'active': 'mission',
        'title': 'Mission',
        'card_title': _('Gitcoin is a mission-driven organization.'),
        'card_desc': _('Our mission is to grow open source.'),
        'avatar_url': static('v2/images/grow_open_source.png'),
    }
    return TemplateResponse(request, 'mission.html', context)


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


def results(request, keyword=None):
    """Render the Results response."""
    if keyword and keyword not in programming_languages:
        raise Http404
    context = build_stat_results(keyword)
    context['is_outside'] = True
    return TemplateResponse(request, 'results.html', context)


def activity(request):
    """Render the Activity response."""
    icons = {
        'title': 'Activity',
        'new_tip': 'fa-thumbs-up',
        'start_work': 'fa-lightbulb',
        'new_bounty': 'fa-money-bill-alt',
        'work_done': 'fa-check-circle',
    }


    def add_view_props(activity):
        activity.icon = icons.get(activity.activity_type, 'fa-check-circle')
        obj = activity.metadata
        if 'new_bounty' in activity.metadata:
            obj = activity.metadata['new_bounty']
        activity.title = obj.get('title', '')
        if 'id' in obj:
            activity.bounty_url = Bounty.objects.get(pk=obj['id']).get_relative_url()
            if activity.title:
                activity.urled_title = f'<a href="{activity.bounty_url}">{activity.title}</a>'
            else:
                activity.urled_title = activity.title
        if 'value_in_usdt_now' in obj:
            activity.value_in_usdt_now = obj['value_in_usdt_now']
        if 'token_name' in obj:
            activity.token = token_by_name(obj['token_name'])
            if 'value_in_token' in obj and activity.token:
                activity.value_in_token_disp = round((float(obj['value_in_token']) /
                                                      10 ** activity.token['decimals']) * 1000) / 1000
        return activity

    activities = Activity.objects.all().order_by('-created')
    p = Paginator(activities, 300)
    page = request.GET.get('page', 1)

    context = {
        'p': p,
        'page': p.get_page(page),
        'title': 'Activity Feed',
    }
    context["activities"] = [add_view_props(a) for a in p.get_page(page)]

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
            'a': _("Yes, all of Gitcoin's core software systems are open source and available at <a href=https://github.com/gitcoinco/>https://github.com/gitcoinco/</a>.  Please see the liscense.txt file in each repo for more details.")
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
        'img': static('v2/images/help/tools.png'),
        'url': 'https://medium.com/gitcoin/tutorial-post-a-bounty-in-90-seconds-a7d1a8353f75',
        'title': _('Post a Bounty in 90 Seconds'),
    }, {
        'img': static('v2/images/tldr/tips_noborder.jpg'),
        'url': 'https://medium.com/gitcoin/tutorial-send-a-tip-to-any-github-user-in-60-seconds-2eb20a648bc8',
        'title': _('Send a Tip to any Github user in 60 seconds'),
    }]

    context = {
        'active': 'help',
        'title': _('Help'),
        'faq': faq,
        'tutorials': tutorials,
    }
    return TemplateResponse(request, 'help.html', context)


def get_gitcoin(request):
    context = {
        'active': 'get',
        'title': _('Get Started'),
    }
    return TemplateResponse(request, 'getgitcoin.html', context)


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
    return TemplateResponse(request, 'error.html', context)


def portal(request):
    return redirect('https://gitcoin.co/help')


def community(request):
    return redirect('https://github.com/gitcoinco/community')


def onboard(request):
    return redirect('https://docs.google.com/document/d/1DQvek5TwASIp1njx5VZeLKEgSxfvxm871vctx1l_33M/edit?')


def podcast(request):
    return redirect('https://itunes.apple.com/us/podcast/gitcoin-community/id1360536677')


def presskit(request):
    return redirect('https://www.dropbox.com/sh/bsjzbu0li2z0kr1/AACKgnQC3g6m52huYI3Gx3Ega?dl=0')


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


def ios(request):

    context = {
        'active': 'ios',
        'title': 'iOS app',
        'card_title': 'Gitcoin has an iOS app!',
        'card_desc': 'Gitcoin aims to make it easier to grow open source from anywhere in the world,\
            anytime.  We’re proud to announce our iOS app, which brings us a step closer to this north star!\
            Browse open bounties on the go, express interest, and coordinate your work on the move.',
    }
    return TemplateResponse(request, 'ios.html', context)


def iosfeedback(request):
    return redirect('https://goo.gl/forms/UqegoAMh7HVibfuF3')


def casestudy(request):
    return redirect('https://docs.google.com/document/d/1M8-5xCGoJ8u-k0C0ncx_dr9LtHwZ32Ccn3KMFtEnsBA/edit')


def schwag(request):
    return redirect('https://goo.gl/forms/X3jAtOVUUNAumo072')


def slack(request):
    context = {
        'active': 'slack',
        'msg': None,
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
            ip = get_ip(request)
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


def livestream(request):
    return redirect('https://calendar.google.com/calendar/r?cid=N3JxN2dhMm91YnYzdGs5M2hrNjdhZ2R2ODhAZ3JvdXAuY2FsZW5kYXIuZ29vZ2xlLmNvbQ')


def twitter(request):
    return redirect('http://twitter.com/getgitcoin')


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


def tokens(request):
    context = {}
    networks = ['mainnet', 'ropsten', 'rinkeby', 'unknown', 'custom']
    for network in networks:
        key = f"{network}_tokens"
        context[key] = Token.objects.filter(network=network, approved=True)
    return TemplateResponse(request, 'tokens_js.txt', context, content_type='text/javascript')
