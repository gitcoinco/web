'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.utils import timezone
import premailer

### RENDERERS


def render_new_tip(tip):

    params = {
        'link': tip.url,
        'amount': round(tip.amount,2),
        'tokenName': tip.tokenName,
        'comments': tip.comments,
        'tip': tip,
        'show_expires': tip.expires_date < (timezone.now() + timezone.timedelta(days=365)),
    }

    response_html = premailer.transform(render_to_string("emails/new_tip.html", params))
    response_txt = render_to_string("emails/new_tip.txt", params)

    return response_html, response_txt


def render_new_bounty(bounty):

    params = {
        'bounty': bounty,
    }

    response_html = premailer.transform(render_to_string("emails/new_bounty.html", params))
    response_txt = render_to_string("emails/new_bounty.txt", params)

    return response_html, response_txt


def render_new_bounty_claim(bounty):

    params = {
        'bounty': bounty,
    }

    response_html = premailer.transform(render_to_string("emails/new_bounty_claim.html", params))
    response_txt = render_to_string("emails/new_bounty_claim.txt", params)

    return response_html, response_txt


def render_new_bounty_acceptance(bounty):

    params = {
        'bounty': bounty,
    }

    response_html = premailer.transform(render_to_string("emails/new_bounty_acceptance.html", params))
    response_txt = render_to_string("emails/new_bounty_acceptance.txt", params)

    return response_html, response_txt


def render_new_bounty_rejection(bounty):

    params = {
        'bounty': bounty,
    }

    response_html = premailer.transform(render_to_string("emails/new_bounty_rejection.html", params))
    response_txt = render_to_string("emails/new_bounty_rejection.txt", params)

    return response_html, response_txt


def render_bounty_expire_warning(bounty):

    unit = 'days'
    num = int(round((bounty.expires_date - timezone.now()).days, 0))
    if num == 0:
        unit = 'hours'
        num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))

    params = {
        'bounty': bounty,
        'num': num,
        'unit': unit,
    }

    response_html = premailer.transform(render_to_string("emails/new_bounty_expire_warning.html", params))
    response_txt = render_to_string("emails/new_bounty_expire_warning.txt", params)

    return response_html, response_txt


def roundup_bounties(start_date, end_date):
    from dashboard.models import Bounty

    bounties = Bounty.objects.all()
    if not settings.DEBUG:
        bounties = bounties.filter(
            web3_created__gt=start_date,
            web3_created__lt=start_date,
            expires_date__gt=end_date + timezone.timedelta(days=3),
        )
    bounties = bounties.filter(
        is_open=True,
        ).order_by('-_val_usd_db')[:5]

    return bounties


def render_new_bounty_roundup(bounties):

    params = {
        'bounties': bounties,
        'override_back_color': '#0fce7c',
        'invert_footer': True,
    }

    response_html = premailer.transform(render_to_string("emails/bounty_roundup.html", params))
    response_txt = render_to_string("emails/bounty_roundup.txt", params)

    return response_html, response_txt


### DJANGO REQUESTS


@staff_member_required
def new_tip(request):
    from dashboard.models import Tip
    tip = Tip.objects.last()
    response_html, response_txt = render_new_tip(tip)

    return HttpResponse(response_html)


@staff_member_required
def new_bounty(request):
    from dashboard.models import Bounty

    response_html, response_txt = render_new_bounty(Bounty.objects.all().last())

    return HttpResponse(response_html)


@staff_member_required
def new_bounty_claim(request):
    from dashboard.models import Bounty

    response_html, response_txt = render_new_bounty_claim(Bounty.objects.all().last())

    return HttpResponse(response_html)


@staff_member_required
def new_bounty_rejection(request):
    from dashboard.models import Bounty

    response_html, response_txt = render_new_bounty_rejection(Bounty.objects.all().last())

    return HttpResponse(response_html)


@staff_member_required
def new_bounty_acceptance(request):
    from dashboard.models import Bounty

    response_html, response_txt = render_new_bounty_acceptance(Bounty.objects.all().last())

    return HttpResponse(response_html)

@staff_member_required
def bounty_expire_warning(request):
    from dashboard.models import Bounty

    response_html, response_txt = render_bounty_expire_warning(Bounty.objects.all().last())

    return HttpResponse(response_html)


@staff_member_required
def roundup(request):
    from dashboard.models import Bounty

    bounties = roundup_bounties(timezone.now()-timezone.timedelta(weeks=1), timezone.now())
    response_html, response_txt = render_new_bounty_roundup(bounties)

    return HttpResponse(response_html)
