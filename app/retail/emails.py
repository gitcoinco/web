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
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.utils import timezone

import premailer
from marketing.utils import get_or_save_email_subscriber

### RENDERERS


def premailer_transform(html):
    import logging
    import cssutils
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


def render_new_bounty(to_email, bounty):

    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty.html", params))
    response_txt = render_to_string("emails/new_bounty.txt", params)

    return response_html, response_txt


def render_new_bounty_claim(to_email, bounty):

    params = {
        'bounty': bounty,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_claim.html", params))
    response_txt = render_to_string("emails/new_bounty_claim.txt", params)

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

    unit = 'days'
    num = int(round((bounty.expires_date - timezone.now()).days, 0))
    if num == 0:
        unit = 'hours'
        num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))

    params = {
        'bounty': bounty,
        'num': num,
        'unit': unit,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
        'is_claimee': (bounty.claimee_email if bounty.claimee_email else "").lower() == to_email.lower(),
        'is_owner': bounty.bounty_owner_email.lower() == to_email.lower(),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_expire_warning.html", params))
    response_txt = render_to_string("emails/new_bounty_expire_warning.txt", params)

    return response_html, response_txt


def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty

    bounties = [
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/ethereum/web3.py/issues/549'),
            'primer': 'This is a python issue for the Ethereum Foundation... 💯 ~ @owocki',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/gitcoinco/web/issues/208'),
            'primer': 'Want to help build Gitcoin?  Here\'s an opppy to do just that 👇\' ~ @owocki',
        },
        {
            'obj': Bounty.objects.get(current_bounty=True, github_url='https://github.com/btcsuite/btcd/issues/1089'),
            'primer': 'Into Bitcoin and distributed programming?  This issue could be for you..  ~ @owocki',
        },
    ]

    params = {
        'bounties': bounties,
        'override_back_color': '#15003e',
        'invert_footer': True,
        'hide_header': True,
        'subscriber_id': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_roundup.html", params))
    response_txt = render_to_string("emails/bounty_roundup.txt", params)

    return response_html, response_txt


### DJANGO REQUESTS


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
    from django.contrib import messages
    from django.shortcuts import redirect

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

    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_claim(request):
    from dashboard.models import Bounty

    bounty = Bounty.objects.filter(idx_status='fulfilled').last()
    response_html, _ = render_new_bounty_claim(settings.CONTACT_EMAIL, bounty)
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_rejection(request):
    from dashboard.models import Bounty

    response_html, _ = render_new_bounty_rejection(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_acceptance(request):
    from dashboard.models import Bounty

    response_html, _ = render_new_bounty_acceptance(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)

@staff_member_required
def bounty_expire_warning(request):
    from dashboard.models import Bounty

    response_html, _ = render_bounty_expire_warning(settings.CONTACT_EMAIL, Bounty.objects.all().last())
    return HttpResponse(response_html)


@staff_member_required
def roundup(request):
    response_html, _ = render_new_bounty_roundup(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)
