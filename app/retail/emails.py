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
        'show_expires': tip.expires_date < (timezone.now() + timezone.timedelta(days=365)) and tip.expires_date,
        'is_new': is_new,
        'warning': warning,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
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
    if persona == 'fulfiller':
        accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
        github_username = " @" + accepted_fulfillments.first().fulfiller_github_username if accepted_fulfillments.exists() and accepted_fulfillments.first().fulfiller_github_username else ""
        txt = f"""
hi{github_username},

thanks for turning around this bounty.  we're hyperfocused on making gitcoin a great place for blockchain developers to hang out, learn new skills, and make a little extra ETH.

in that spirit,  i have a few questions for you.

> what would you say your average hourly rate was for this bounty? {bounty.github_url}

> what was the best thing about working on the platform?  what was the worst?

> would you use gitcoin again?

thanks again for being a member of the community.

kevin

"""
    elif persona == 'funder':
        github_username = " @" + bounty.bounty_owner_github_username if bounty.bounty_owner_github_username else ""
        if bounty.status == 'done':
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
        elif bounty.status == 'cancelled':
            txt = f"""
hi{github_username},

we saw that you cancelled this bounty.

i was sorry to see that the bounty did not get done.

i have a few questions for you.

> why did you decide to cancel the bounty?

> would you use gitcoin again?

thanks again for being a member of the community.

kevin

"""
        else:
            raise Exception('unknown bounty status')
    else:
        raise Exception('unknown persona')

    params = {
        'txt': txt,
    }
    response_html = premailer_transform(render_to_string("emails/txt.html", params))
    response_txt = txt

    return response_html, response_txt


def render_new_bounty(to_email, bounties, old_bounties):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    params = {
        'old_bounties': old_bounties,
        'bounties': bounties,
        'subscriber': sub,
        'keywords': ",".join(sub.keywords),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty.html", params))
    response_txt = render_to_string("emails/new_bounty.txt", params)

    return response_html, response_txt


def render_new_work_submission(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_work_submission.html", params))
    response_txt = render_to_string("emails/new_work_submission.txt", params)

    return response_html, response_txt


def render_new_bounty_acceptance(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_acceptance.html", params))
    response_txt = render_to_string("emails/new_bounty_acceptance.txt", params)

    return response_html, response_txt


def render_new_bounty_rejection(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
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
        'is_claimee': (to_email.lower() in fulfiller_emails),
        'is_owner': bounty.bounty_owner_email.lower() == to_email.lower(),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_expire_warning.html", params))
    response_txt = render_to_string("emails/new_bounty_expire_warning.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_startwork_expire_warning.html", params))
    response_txt = render_to_string("emails/bounty_startwork_expire_warning.txt", params)

    return response_html, response_txt

def render_bounty_unintersted(to_email, bounty, interest):
    params = {
        'bounty': bounty,
        'interest': interest,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_uninterested.html", params))
    response_txt = render_to_string("emails/bounty_uninterested.txt", params)

    return response_html, response_txt

def render_faucet_rejected(fr):

    params = {
        'fr': fr,
        'amount': settings.FAUCET_AMOUNT,
        'subscriber': get_or_save_email_subscriber(fr.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/faucet_request_rejected.html", params))
    response_txt = render_to_string("emails/faucet_request_rejected.txt", params)

    return response_html, response_txt


def render_faucet_request(fr):

    params = {
        'fr': fr,
        'amount': settings.FAUCET_AMOUNT,
        'subscriber': get_or_save_email_subscriber(fr.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/faucet_request.html", params))
    response_txt = render_to_string("emails/faucet_request.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expired(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
        'time_delta_days': time_delta_days,
        'subscriber': get_or_save_email_subscriber(fr.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/render_bounty_startwork_expired.html", params))
    response_txt = render_to_string("emails/render_bounty_startwork_expired.txt", params)

    return response_html, response_txt


# ROUNDUP_EMAIL
def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty
    from external_bounties.models import ExternalBounty
    subject = "$10,000 of Dai-based Gitcoin Bounties! "

    intro = '''

<p>
    Hi there
</p>
<p>
We announced <a href="https://medium.com/gitcoin/grow-open-source-gitcoin-makerdao-4f9df702afea">a partnership with MakerDAO this week</a> to provide $10,000 worth of bounties, denominated in Dai! We will start by allocation ~$2,000 to Ethereum Foundation repo’s. From here, we are open to suggestions on open source projects which may be interested in support through bounties. Please let us know <a href="https://gitcoin.co/slack">on Slack</a> or on <a href="https://twitter.com/MakerDAO/status/989641464001904641">Twitter</a>.
</p>
<h3>What else is new?</h3>
    <ul>
        <li>
Have you used <a href="https://medium.com/gitcoin/tutorial-send-a-tip-to-any-github-user-in-60-seconds-2eb20a648bc8">Gitcoin Tips</a> before? Tips are a great way to show appreciation for contributions while growing an open source community - in 60 seconds or less! 
        </li>
        <li>
Want to be the first to know when new open issues are added? <a href="http://twitter.com/gitcoinfeed">@gitcoinfeed</a> on Twitter which provides updates on all new activity on Gitcoin.
        </li>
    </ul>
</p>
<p>
On today’s <a href="http://gitcoin.co/livestream">Gitcoin Livestream</a>, we’re excited to host 1)  <a href="https://publisher.adchain.com/">AdChain</a>, a live TCR-based project, 2) <a href="https://www.uport.me/">uPort</a>, who will tell the group about their Gitcoin Bounty program, and 3) <a href="http://airswap.io/">Airswap</a>, who launched their decentralized exchange to mainnet today . <a href="https://gitcoin.co/livestream">Add it to your Google Calendar</a> and come hang out! 
</p>
<p>
I hope to see you on <a href="https://gitcoin.co/slack">Slack</a> or on <a href="https://github.com/gitcoinco/web">Github</a>. If you’re interested in growing open source and have some extra time, come by. We’re working to make Gitcoin is the best place on the internet to do so.

</p>

'''
    highlights = [
        {
            'who': 'justpixel',
            'who_link': True,
            'what': 'Worked with Bounties Network to draw up a new ‘Getting Started’ page.',
            'link': 'https://gitcoin.co/issue/Bounties-Network/bounties.network/2/309',
            'link_copy': 'See more',
        },
        {
            'who': 'agni21',
            'who_link': True,
            'what': 'Helped Tim van Mourik out on the Giraffe Tools repo.',
            'link': 'https://gitcoin.co/issue/TimVanMourik/GiraffeTools/16/262',
            'link_copy': 'View more',
        },
        {
            'who': 'netrunnerX',
            'who_link': True,
            'what': 'Made his first submission on Ethereum’s Solidity repo!',
            'link': 'https://gitcoin.co/issue/ethereum/solidity/3750/216',
            'link_copy': 'See more',
        },
    ]

    bounties = [
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url__iexact='https://github.com/PolymathNetwork/polymath-core/issues/87'),
            'primer': 'Polymath released a Bug Bounty which pays up to 10ETH for critical issues. ',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url__iexact='https://github.com/gitcoinco/web/issues/865'),
            'primer': 'ETHAvatar is a project aiming at improving blockchain UX holistically. Interested in building out the web app?',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url__iexact='https://github.com/uport-project/buidlbox/issues/3'),
            'primer': 'uPort is searching for ideas for applications which can be built on top of their platform! ',
        },
    ]

    ecosystem_bounties = ExternalBounty.objects.filter(created_on__gt=timezone.now() - timezone.timedelta(weeks=1)).order_by('?')[0:5]

    params = {
        'intro': intro,
        'intro_txt': strip_double_chars(strip_double_chars(strip_double_chars(strip_html(intro), ' '), "\n"), "\n "),
        'bounties': bounties,
        'ecosystem_bounties': ecosystem_bounties,
        'invert_footer': False,
        'hide_header': False,
        'highlights': highlights,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
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
    bounties = Bounty.objects.filter(current_bounty=True).order_by('-web3_created')[0:3]
    old_bounties = Bounty.objects.filter(current_bounty=True).order_by('-web3_created')[0:3]
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, bounties, old_bounties)
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
    response_html, _ = render_faucet_request(fr)
    return HttpResponse(response_html)


@staff_member_required
def faucet_rejected(request):
    from faucet.models import FaucetRequest
    fr = FaucetRequest.objects.exclude(comment_admin='').last()
    response_html, _ = render_faucet_rejected(fr)
    return HttpResponse(response_html)


@staff_member_required
def roundup(request):
    response_html, _, _ = render_new_bounty_roundup(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)
