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
from django.template.response import TemplateResponse
from django.shortcuts import redirect


def index(request):
    context = {
        'active': 'home',
    }
    return TemplateResponse(request, 'index.html', context)


def about(request):
    context = {
        'active': 'about',
        'title': 'About',
    }
    return TemplateResponse(request, 'about.html', context)


def help(request):
    faq = [
        {
            'q': 'Is Gitcoin open source?',
            'a': "Yes, all of Gitcoin's core software systems are open source and available at <a href=https://github.com/gitcoinco/>https://github.com/gitcoinco/</a>.  Please see the liscense.txt file in each repo for more details."
        },
        {
            'q': 'I am a developer, I want build more Open Source Software. Where can I start?',
            'a': "Check out the developer guide at <a href=https://gitcoin.co/help/dev>https://gitcoin.co/help/dev</a>."
        },
        {
            'q': 'What tokens does Gitcoin support?',
            'a': "Gitcoin supports Ether and all ERC20 tokens."
        },
        {
            'q': 'I am a repo maintainer.  How do I get started?',
            'a': "Check out the repo maintainers guide at <a href=https://gitcoin.co/help/repo>https://gitcoin.co/help/repo</a>."
        },
        {
            'q': 'What kind of issues are fundable?',
            'a': """

    <p class="c5"><span class="c4 c0">Gitcoin supports bug, feature, and security funded issues. &nbsp;Any issue that you need done is a good candidate for a funded issue, provided that:</span></p><ul class="c13 lst-kix_twl0y342ii52-0 start"><li class="c5 c11"><span class="c4 c0">It&rsquo;s open today.</span></li><li class="c5 c11"><span class="c4 c0">The repo README clearly enumerates how a new developer should get set up to contribute.</span></li><li class="c5 c11"><span class="c4 c0">The task is well defined.</span></li><li class="c5 c11"><span class="c4 c0">The end-state of the task is well defined.</span></li><li class="c5 c11"><span class="c4 c0">The pricing of the task reflects (market rate * complexity) of the task.</span></li><li class="c5 c11"><span class="c4 c0">The issue is on the roadmap, but does not block other work.</span></li></ul><p class="c5 c6"><span class="c4 c0"></span></p><p class="c5"><span class="c4 c0">To get started with funded issues today, it might be good to start small. &nbsp;Is there a small bug that needs fixed? &nbsp;An issue that&rsquo;s been open for a while that no one is tackling? &nbsp;An administrative task?</span></p>


            """
        },
        {
            'q': 'What is the difference between Gitcoin and centralized hiring websites?',
            'a': """
<p>There are many successful centralized hiring resources available on the web. &nbsp;Because these platforms were an&nbsp;efficient way to source, select, and manage a global workforce , millions of dollars was&nbsp;processed through these systems every day.</p>
<p>Gitcoin takes the value that flows through these system, and makes it more efficient and fair. &nbsp;Gitcoin is a distributed network of smart contracts, based upon Ethereum, that aims to solve problems with centralized hiring resources, namely by</p>
<ul>
<li>cutting out the middlemen,</li>
<li>being more fair,</li>
<li>being more efficient,</li>
<li>being more open,</li>
<li>being easier to use.</li>
</ul>
<p>When Sir Tim Berners-Lee first invented the World Wide Web in the late 1980s&nbsp;to make information sharing on the Internet easier, he did something very important. He specified an open protocol, the Hypertext Transfer Protocol or HTTP, that anyone could use to make information available and to access such information. &nbsp;</p>
<p>Gitcoin is similarly built on an open protocol of smart contracts.</p>
<p>By specifying a&nbsp;protocol, Tim Berners-Lee opened the way for anyone to build software, so-called web servers and browsers that would be compatible with this protocol. &nbsp; By specifying an open source protocol for Funding Issues and software development scoping &amp; payment, the Gitcoin Core team hopes to similarly inspire a generation of inventions in 21st century software.</p>
            """
        },
        {
            'q': 'Is a token distribution event planned for Gitcoin?',
            'a': """
<p>Gitcoin Core is considering doing a token distribution event (TDI), but at the time is focused first and foremost on providing value in Open Source Software&nbsp;in a lean way.</p>
<p>To find out more about a possible upcoming token distribution event,&nbsp;check out&nbsp;<a href="https://gitcoin.co/whitepaper">https://gitcoin.co/whitepaper</a></p>
<p>&nbsp;</p>            """
        },
        {
            'q': 'What is the difference between Gitcoin and Gitcoin Core?',
            'a': """
Gitcoin Core LLC is the legal entity that manages the software development of the Gitcoin Network (Gitcoin).

The Gitcoin Network is a series of smart contracts that helps Push Open Source Forward, but enabling developers to easily post and manage funded issues.            """
        },
        {
            'q': 'Who is the team at Gitcoin Core?',
            'a': """
<p>The founder is <a href="https://linkedin.com/in/owocki">Kevin Owocki</a>, a technologist from the Boulder Colorado tech scene. &nbsp; &nbsp;Kevin&nbsp;has a BS in Computer Science, 15 years experience in Open Source Software and Technology Startups. He is a volunteer in the Boulder Community for several community organizations, and an avid open source developer. His work has been featured in&nbsp;<a href="http://techcrunch.com/2011/02/10/group-dating-startup-ignighter-raises-3-million/">TechCrunch</a>,&nbsp;<a href="http://www.cnn.com/2011/BUSINESS/03/29/india.online.matchmaking/">CNN</a>,&nbsp;<a href="http://www.inc.com/30under30/2011/profile-adam-sachs-kevin-owocki-and-dan-osit-founders-ignighter.html">Inc Magazine</a>,&nbsp;<a href="http://www.nytimes.com/2011/02/20/business/20ignite.html?_r=4&amp;amp;pagewanted=1&amp;amp;ref=business">The New York Times</a>,&nbsp;<a href="http://boingboing.net/2011/09/24/tosamend-turn-all-online-i-agree-buttons-into-negotiations.html">BoingBoing</a>,&nbsp;<a href="http://www.wired.com/2015/12/kevin-owocki-adblock-to-bitcoin/">WIRED</a>,&nbsp;<a href="https://www.forbes.com/sites/amycastor/2017/08/31/toothpick-takes-top-prize-in-silicon-beach-ethereum-hackathon/#6bf23b7452ad">Forbes</a>, and&nbsp;<a href="http://www.techdigest.tv/2007/08/super_mario_get_1.html">TechDigest</a>.</p>
<p><strong>Gitcoin</strong>&nbsp;was borne of the community in Boulder Colorado's thriving tech scene. One of the most amazing things about the Boulder community is the #givefirst mantra. The founding team has built their careers off of advice, mentorship, and relationships in the local tech community. &nbsp;</p>

<p>We are hiring.  If you want to join the team, <a href=mailto:founders@gitcoin.co>email us</a>.

            """
        },
        {
            'q': 'What is the mission of Gitcoin Core?',
            'a': """
The mission of Gitcoin is "Push Open Source Forward".

            """
        },
        {
            'q': 'How can I stay in touch with project updates?',
            'a': """
The best way to stay in touch is to

<ul>
<li>
    <a href="/#mailchimp">Subscribe to the mailing list</a>
</li>
<li>
    <a href="https://twitter.com/GetGitcoin">Follow the project on twitter</a>
</li>
<li>
    <a href="/slack">Join the slack channel</a>
</li>

</ul>

            """
        },

    ]

    context = {
        'active': 'help',
        'title': 'Help',
        'faq': faq,
    }
    return TemplateResponse(request, 'help.html', context)


def get_gitcoin(request):
    context = {
        'active': 'get',
        'title': 'Get Gitcoin',
    }
    return TemplateResponse(request, 'getgitcoin.html', context)


def handler403(request):
    return error(request, 403)


def handler404(request):
    return error(request, 404)


def handler500(request):
    return error(request, 500)


def handler400(request):
    return error(request, 400)


def error(request, code):
    context = {
        'active': 'error', 
        'code': code
    }
    context['title'] = "Error {}".format(code)
    return TemplateResponse(request, 'error.html', context)


def portal(request):
    return redirect('https://gitcoinhelp.zendesk.com/hc/en-us/')


def help_dev(request):
    return redirect('https://docs.google.com/document/d/1S8BLKJF7J5RbrfFw-mX0iYcy4VSc6-a1aQXtKT_ta0Y/edit')


def help_repo(request):
    return redirect('https://docs.google.com/document/d/1_U9IdDN8FIRMGAdLWCMl2BnqCTAv558QvyJiSWQfkbs/edit')


def help_faq(request):
    return redirect('https://gitcoinhelp.zendesk.com/hc/en-us/sections/115000415412-FAQ')


def browser_extension(request):
    return redirect('https://chrome.google.com/webstore/detail/gdocmelgnjeejhlphdnoocikeafdpaep')


def slack(request):
    return redirect('https://gitcoincommunity.herokuapp.com')


def btctalk(request):
    return redirect('https://bitcointalk.org/index.php?topic=2206663')


