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
from django.conf import settings
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from marketing.utils import get_or_save_email_subscriber, invite_to_slack
from slackclient import SlackClient


def index(request):
    slides = [
        ("Kevin Owocki","/static/v2/images/avatar.png", "This could be the next freelance boom."),
        ("Aditya Anand","/static/v2/images/avatar.png", "I feel it is so awesome to have the opportunity through Gitcoin to do what I love and get paid for it, and to have reasonable freedom about the way I work, that it already seems too good to be true."),
        ("Kevin Owocki","/static/v2/images/avatar.png", "Staying lean, building the community, iterating... The way to go vs many projects that are just looking for the money grab immediately.")
    ]
    context = {
        'slides': slides,
        'slideDuration': 6000,
        'active': 'home',
    }
    return TemplateResponse(request, 'index.html', context)


def robotstxt(request):
    context = {
    }
    return TemplateResponse(request, 'robots.txt', context)


def about(request):
    context = {
        'active': 'about',
        'title': 'About',
    }
    return TemplateResponse(request, 'about.html', context)


def help(request):
    faq = [
        {
            'category': "Product",
            'q': 'I am a developer, I want build more Open Source Software. Where can I start?',
            'a': "The <a href=https://gitcoin.co/explorer>Funded Issue Explorer</a> contains a handful of issues that are ready to be paid out as soon as they are turned around. Check out the developer guide at <a href=https://gitcoin.co/help/dev>https://gitcoin.co/help/dev</a>."
        },
        {
            'q': 'I am a repo maintainer.  How do I get started?',
            'a': "The best way to get started is to post a funded issue on a task you need done.  Check out the repo maintainers guide at <a href=https://gitcoin.co/help/repo>https://gitcoin.co/help/repo</a>."
        },
        {
            'q': 'What tokens does Gitcoin support?',
            'a': "Gitcoin supports Ether and all ERC20 tokens.  If the token you'd like to use is Ethereum based, then Gitcoin supports it."
        },
        {
            'q': 'What kind of issues are fundable?',
            'a': """

    <p class="c5"><span class="c4 c0">Gitcoin supports bug, feature, and security funded issues. &nbsp;Any issue that you need done is a good candidate for a funded issue, provided that:</span></p><ul class="c13 lst-kix_twl0y342ii52-0 start"><li class="c5 c11"><span class="c4 c0">It&rsquo;s open today.</span></li><li class="c5 c11"><span class="c4 c0">The repo README clearly enumerates how a new developer should get set up to contribute.</span></li><li class="c5 c11"><span class="c4 c0">The task is well defined.</span></li><li class="c5 c11"><span class="c4 c0">The end-state of the task is well defined.</span></li><li class="c5 c11"><span class="c4 c0">The pricing of the task reflects (market rate * complexity) of the task.</span></li><li class="c5 c11"><span class="c4 c0">The issue is on the roadmap, but does not block other work.</span></li></ul><p class="c5 c6"><span class="c4 c0"></span></p><p class="c5"><span class="c4 c0">To get started with funded issues today, it might be good to start small. &nbsp;Is there a small bug that needs fixed? &nbsp;An issue that&rsquo;s been open for a while that no one is tackling? &nbsp;An administrative task?</span></p>


            """
        },
        {
            'q': 'Whats the difference between tips & funded issues?',
            'a': """

<p>
<strong>A tip</strong> is a tool to send ether or any ethereum token to any github account.  The flow for tips looks like this:
</p><p>
> Send (party 1) => receive (party 2)
</p><p>

<strong>Funded Issues</strong> are a way to fund open source features, bugs, or security bounties.  The flow for funded issues looks like this:
</p><p>

>  Fund Issue (party 1) => claim funds  (party 2) => accept (party 1)
</p>


            """
        },
        {
            'q': 'What kind of contributors are successful on the Gitcoin network?',
            'a': """

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


            """
        },
        {
            'q': 'I received a notification about tip / funded issue, but I can\'t process it.  Help!',
            'a': "We'd love to help!  Please email <a href='mailto:founders@gitcoin.co'>founders@gitcoin.co</a> or join <a href=/slack>Gitcoin Community Slack</a>."
        },
        {
            'category': "General",
            'q': 'Is Gitcoin open source?',
            'a': "Yes, all of Gitcoin's core software systems are open source and available at <a href=https://github.com/gitcoinco/>https://github.com/gitcoinco/</a>.  Please see the liscense.txt file in each repo for more details."
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
    <a href="/twitter">Follow the project on twitter</a>
</li>
<li>
    <a href="/slack">Join the slack channel</a>
</li>

</ul>

            """
        },
        {
            'category': "Web3",
            'q': 'What is the difference between Gitcoin and centralized hiring websites?',
            'a': """
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
            """
        },
        {
            'q': 'Why do I need metamask?',
            'a': """
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

           """
        },
        {
            'q': 'Why do I need to pay gas?',
            'a': """
<p>
"Gas" is the name for a special unit used in Ethereum. It measures how much "work" an action or set of actions takes to perform (for example, storing data in a smart contract).
</p>
<p>
The reason gas is important is that it helps to ensure an appropriate fee is being paid by transactions submitted to the network. By requiring that a transaction pay for each operation it performs (or causes a contract to perform), we ensure that network doesn't become bogged down with performing a lot of intensive work that isn't valuable to anyone.
</p>
<p>
Gas fees are paid to the maintainers of the Ethereum network, in return for securing all of the Ether and Ethereum-based transactions in the world.  Gas fees are not paid to Gitcoin Core directly or indirectly.
</p>
           """
        },
        {
            'q': 'What are the advanages of Ethereum based applications?',
            'a': """
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


           """
        },
        {
            'q': 'I still dont get it.  Help!',
            'a': """
We want to nerd out with you a little bit more.  <a href="/slack">Join the Gitcoin Slack Community</a> and let's talk.


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
        'title': 'Get Started',
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
    return_as_json = 'api' in request.path

    if return_as_json:
        return JsonResponse(context, status=500)
    else:
        return TemplateResponse(request, 'error.html', context)


def portal(request):
    return redirect('https://gitcoinhelp.zendesk.com/hc/en-us/')


def feedback(request):
    return redirect('https://goo.gl/forms/9rs9pNKJDnUDYEeA3')


def help_dev(request):
    return redirect('https://docs.google.com/document/d/1S8BLKJF7J5RbrfFw-mX0iYcy4VSc6-a1aQXtKT_ta0Y/edit')


def help_dev(request):
    return redirect('https://docs.google.com/document/d/1S8BLKJF7J5RbrfFw-mX0iYcy4VSc6-a1aQXtKT_ta0Y/edit')


def help_pilot(request):
    return redirect('https://docs.google.com/document/d/1R-qQKlIcW38d7l6GumehDlOhdmX1-6Ibab3gE06qotQ/edit')


def help_repo(request):
    return redirect('https://docs.google.com/document/d/1_U9IdDN8FIRMGAdLWCMl2BnqCTAv558QvyJiSWQfkbs/edit')


def help_faq(request):
    return redirect('https://gitcoin.co/help#faq')


def browser_extension(request):
    return redirect('https://chrome.google.com/webstore/detail/gdocmelgnjeejhlphdnoocikeafdpaep')


def slack(request):
    context = {

    }

    if request.POST.get('email', False):
        email = request.POST['email']
        valid_email = True
        try:
            validate_email(request.POST.get('email', False))
        except Exception as e:
            valid_email = False

        if valid_email:
            get_or_save_email_subscriber(email, 'slack')
            response = invite_to_slack(email)
            if response['ok']:
                context['msg'] = "Your invite has been sent. "
            else:
                context['msg'] = response['error']
        else:
            context['msg'] = "Invalid email"

    return TemplateResponse(request, 'slack.html', context)



def btctalk(request):
    return redirect('https://bitcointalk.org/index.php?topic=2206663')


def reddit(request):
    return redirect('https://www.reddit.com/r/gitcoincommunity/')


def twitter(request):
    return redirect('http://twitter.com/getgitcoin')


def fb(request):
    return redirect('https://www.facebook.com/GetGitcoin/')


def medium(request):
    return redirect('https://medium.com/gitcoin')


def gitter(request):
    return redirect('https://gitter.im/gitcoinco/Lobby')


def github(request):
    return redirect('https://github.com/gitcoinco/')


def youtube(request):
    return redirect('https://www.youtube.com/watch?v=DJartWzDn0E')
