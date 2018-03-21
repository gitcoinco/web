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
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone

import cssutils
import premailer
from marketing.utils import get_or_save_email_subscriber
from retail.utils import strip_double_chars, strip_html

# RENDERERS


def premailer_transform(html):
    cssutils.log.setLevel(logging.CRITICAL)
    return premailer.transform(html)


def render_tip_email(to_email, tip, is_new):
    warning = tip.network if tip.network != 'mainnet' else ""
    params = {
        'link': tip.url,
        'amount': round(tip.amount, 5),
        'tokenName': tip.tokenName,
        'comments_priv': tip.comments_priv,
        'comments_public': tip.comments_public,
        'tip': tip,
        'show_expires': tip.expires_date < (timezone.now() + timezone.timedelta(days=365)),
        'is_new': is_new,
        'warning': warning,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
        'is_sender': to_email not in tip.emails,
        'is_receiver': to_email in tip.emails,
    }

    response_html = premailer_transform(render_to_string("emails/new_tip.html", params))
    response_txt = render_to_string("emails/new_tip.txt", params)

    return response_html, response_txt


def render_match_email(bounty, github_username):
    params = {
        'bounty': bounty,
        'github_username': github_username,
    }
    response_html = premailer_transform(render_to_string("emails/new_match.html", params))
    response_txt = render_to_string("emails/new_match.txt", params)

    return response_html, response_txt


def render_bounty_feedback(bounty, persona='submitter', previous_bounties=[]):
    previous_bounties_str = ", ".join([bounty.github_url for bounty in previous_bounties])
    if persona != 'submitter':
        accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
        github_username = " @" + accepted_fulfillments.first().fulfiller_github_username if accepted_fulfillments.exists() else ""
        txt = f"""
hi{github_username},

thanks for turning around this bounty.  we're hyperfocused on making gitcoin a great place for blockchain developers to hang out, learn new skills, and make a little extra ETH. 

in that spirit,  i have a few questions for you.

> what would you say your blended hourly rate was for this bounty? {bounty.github_url}

> what was the best thing about working on the platform?  what was the worst?

> would you use gitcoin again?

thanks again for being a member of the community.
kevin

"""
    else:
        github_username = " @" + bounty.bounty_owner_github_username if bounty.bounty_owner_github_username else ""
        txt = f"""

hi{github_username},

thanks for putting this bounty ({bounty.github_url}) on gitcoin.  i'm glad to see it was turned around.

we're hyperfocused on making gitcoin a great place for blockchain developers to hang out, learn new skills, and make a little extra ETH. 

in that spirit,  i have a few questions for you:

> how much coaching/communication did it take the counterparty to turn around the issue?  was this burdensome?

> what was the best thing about working on the platform?  what was the worst?

> would you use gitcoin again?

thanks for being a member of the community.
kevin
"""

    params = {
        'txt': txt,
    }
    response_html = premailer_transform(render_to_string("emails/txt.html", params))
    response_txt = render_to_string("emails/txt.txt", params)

    return response_html, response_txt


def render_new_bounty(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty.html", params))
    response_txt = render_to_string("emails/new_bounty.txt", params)

    return response_html, response_txt


def render_new_work_submission(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_work_submission.html", params))
    response_txt = render_to_string("emails/new_work_submission.txt", params)

    return response_html, response_txt


def render_new_bounty_acceptance(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_acceptance.html", params))
    response_txt = render_to_string("emails/new_bounty_acceptance.txt", params)

    return response_html, response_txt


def render_new_bounty_rejection(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_rejection.html", params))
    response_txt = render_to_string("emails/new_bounty_rejection.txt", params)

    return response_html, response_txt


def render_bounty_expire_warning(to_email, bounty):
    from django.db.models.functions import Lower

    unit = 'days'
    num = int(round((bounty.expires_date - timezone.now()).days, 0))
    if num == 0:
        unit = 'hours'
        num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))

    fulfiller_emails = list(bounty.fulfillments.annotate(lower_email=Lower('fulfiller_email')).values_list('lower_email'))

    params = {
        'bounty': bounty,
        'num': num,
        'unit': unit,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
        'is_claimee': (to_email.lower() in fulfiller_emails),
        'is_owner': bounty.bounty_owner_email.lower() == to_email.lower(),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_expire_warning.html", params))
    response_txt = render_to_string("emails/new_bounty_expire_warning.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
    }

    response_html = premailer_transform(render_to_string("emails/bounty_startwork_expire_warning.html", params))
    response_txt = render_to_string("emails/bounty_startwork_expire_warning.txt", params)

    return response_html, response_txt

def render_bounty_unintersted(to_email, bounty, interest):
    params = {
        'bounty': bounty,
        'interest': interest,
    }

    response_html = premailer_transform(render_to_string("emails/bounty_uninterested.html", params))
    response_txt = render_to_string("emails/bounty_uninterested.txt", params)

    return response_html, response_txt

def render_faucet_rejected(fr):

    params = {
        'fr': fr,
        'amount': settings.FAUCET_AMOUNT,
    }

    response_html = premailer_transform(render_to_string("emails/faucet_request_rejected.html", params))
    response_txt = render_to_string("emails/faucet_request_rejected.txt", params)

    return response_html, response_txt


def render_faucet_request(fr):

    params = {
        'fr': fr,
        'amount': settings.FAUCET_AMOUNT,
    }

    response_html = premailer_transform(render_to_string("emails/faucet_request.html", params))
    response_txt = render_to_string("emails/faucet_request.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expired(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
    }

    response_html = premailer_transform(render_to_string("emails/render_bounty_startwork_expired.html", params))
    response_txt = render_to_string("emails/render_bounty_startwork_expired.txt", params)

    return response_html, response_txt


# ROUNDUP_EMAIL
def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty
    subject = "MetaMask Internationalization | From a Gitcoin Bounty to an Epic "

    intro = '''

<p>
    Hi there 👋
</p>
<p>
    Last week, we saw a bounty on MetaMask snowball into an epic -- all set to be built with Gitcoin bounties. <a href="https://medium.com/gitcoin/metamask-internationalizes-via-gitcoin-bf1390c0301c">Read more</a> on how MetaMask’s internationalization strategy started with a contribution from one Gitcoiner, @mapmeld. 
</p>
<p>
    The <a href="http://gitcoin.co/faucet">Gitcoin Faucet</a> is live for those interested in a small ETH distribution to interact with Ethereum's mainnet for the first time. The first batch of distributions have been made! Want to use your distribution on Gitcoin?  The <a href="https://gitcoin.co/explorer">open issues page</a> is the best place to start. 
<p>
    What else is new?
    <ul>
        <li>
Which blockchain based, open-source projects would you like to see on Gitcoin? <a href="https://docs.google.com/forms/d/e/1FAIpQLSfUDnLRXu03eGldeb3twlgdccg4xvRI22XwRo7pm60pemDEpw/viewform">We’re offering a 15% finders fee</a> if an intro you make leads to a funded issue!
        </li>
        <li>
Revamped <a href="https://gitcoin.co/tools">Tools Page</a> is Up! We just launched an <a href="https://gitcoin.co/universe">Offchain Bounties tool in alpha</a>.
        </li>
        <li>
Looking for the next ETH Hackathon? Check out <a href="http://hackital.io/">Hackital</a>, in Washington DC on April 27- April 29th.
        </li>
        <li>
A <a href="https://github.com/gitcoinco/web/blob/master/readme_widget.md">wild Gitcoin Widget</a> appears for your Github read-me! Looking to get more OSS contributors to your repo? This will quickly show any Gitcoin issues you have open. 
        </li>
    </ul>
</p>
<p>
    I hope to see you <a href="https://gitcoin.co/slack">on slack</a>, or on the community livestream TODAY at 3pm MST ! Agenda items for this week: demo’s from @coderberry at Code Sponsor and 8trac, SXSW Hackathon  winner, as well as more simulation theory conversations, as always 🤖
</p>

'''
    highlights = [
        {
            'who': 'murduk',
            'who_link': True,
            'what': 'On last week’s newsletter, this was an open bounty. Now, it is in the Ethereum Foundation’s py-evm. Great work!',
            'link': 'https://gitcoin.co/issue/ethereum/py-evm/362',
            'link_copy': 'See more',
        },
        {
            'who': 'maektwain',
            'who_link': True,
            'what': 'Allowed any ERC20 token to be displayed on MARKET Protocol’s dApp',
            'link': 'https://gitcoin.co/issue/MARKETProtocol/Dapp/71',
            'link_copy': 'View more',
        },
        {
            'who': 'michelgotta',
            'who_link': True,
            'what': 'built the beautiful Gitcoin widget headlined above. Appreciate your effforts!',
            'link': 'https://gitcoin.co/issue/gitcoinco/web/594',
            'link_copy': 'See more',
        },
    ]

    bounties = [
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/ipld/js-cid/issues/38'),
            'primer': 'We want more projects on Gitcoin. Gitcoin Requests is one hypothesis on how to get there. Earn .3ETH along the way!  ',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/ethereum/web3.py/issues/666'),
            'primer': 'The Ethereum Foundation’s web3py needs help with Constructor Functions. Any ideas? 0.4 ETH available upon merge. ',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/gitcoinco/web/issues/671'),
            'primer': 'Have Webpack experience? IPLD is working on linked data and could use a hand.',
        },
    ]

    params = {
        'intro': intro,
        'intro_txt': strip_double_chars(strip_double_chars(strip_double_chars(strip_html(intro), ' '), "\n"), "\n "),
        'bounties': bounties,
        'override_back_color': '#15003e',
        'invert_footer': True,
        'hide_header': True,
        'highlights': highlights,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_roundup.html", params))
    response_txt = render_to_string("emails/bounty_roundup.txt", params)

    return response_html, response_txt, subject


# DJANGO REQUESTS


@staff_member_required
def new_tip(request):
    from dashboard.models import Tip
    tip = Tip.objects.last()
    response_html, _ = render_tip_email(settings.CONTACT_EMAIL, tip, True)

    return HttpResponse(response_html)


@staff_member_required
def new_match(request):
    from dashboard.models import Bounty
    response_html, _ = render_match_email(Bounty.objects.exclude(title='').last(), 'owocki')

    return HttpResponse(response_html)


@staff_member_required
def resend_new_tip(request):
    from dashboard.models import Tip
    from marketing.mails import tip_email
    pk = request.POST.get('pk', request.GET.get('pk'))
    params = {
        'pk': pk,
    }

    if request.POST.get('pk'):
        email = request.POST.get('email')

        if not pk or not email:
            messages.error(request, 'Not sent.  Invalid args.')
            return redirect('/_administration')

        tip = Tip.objects.get(pk=pk)
        tip.emails = tip.emails + [email]
        tip_email(tip, [email], True)
        tip.save()

        messages.success(request, 'Resend sent')

        return redirect('/_administration')

    return TemplateResponse(request, 'resend_tip.html', params)


@staff_member_required
def new_bounty(request):
    from dashboard.models import Bounty
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def new_work_submission(request):
    from dashboard.models import Bounty
    bounty = Bounty.objects.filter(idx_status='submitted', current_bounty=True).last()
    response_html, _ = render_new_work_submission(settings.CONTACT_EMAIL, bounty)
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_rejection(request):
    from dashboard.models import Bounty
    response_html, _ = render_new_bounty_rejection(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_acceptance(request):
    from dashboard.models import Bounty
    response_html, _ = render_new_bounty_acceptance(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def bounty_feedback(request):
    from dashboard.models import Bounty
    response_html, _ = render_bounty_feedback(Bounty.objects.filter(idx_status='done', current_bounty=True).last(), 'foo')
    return HttpResponse(response_html)


@staff_member_required
def bounty_expire_warning(request):
    from dashboard.models import Bounty
    response_html, _ = render_bounty_expire_warning(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def start_work_expired(request):
    from dashboard.models import Bounty, Interest
    response_html, _ = render_bounty_startwork_expired(settings.CONTACT_EMAIL, Bounty.objects.last(), Interest.objects.all().last(), 5)
    return HttpResponse(response_html)


@staff_member_required
def start_work_expire_warning(request):
    from dashboard.models import Bounty, Interest
    response_html, _ = render_bounty_startwork_expire_warning(settings.CONTACT_EMAIL, Bounty.objects.last(), Interest.objects.all().last(), 5)
    return HttpResponse(response_html)


@staff_member_required
def faucet(request):
    from faucet.models import FaucetRequest
    fr = FaucetRequest.objects.last()
    response_html, txt = render_faucet_request(fr)
    return HttpResponse(response_html)


@staff_member_required
def faucet_rejected(request):
    from faucet.models import FaucetRequest
    fr = FaucetRequest.objects.last()
    response_html, txt = render_faucet_rejected(fr)
    return HttpResponse(response_html)


@staff_member_required
def roundup(request):
    response_html, _, _ = render_new_bounty_roundup(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)
