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
from django.utils.translation import gettext as _

import cssutils
import premailer
from marketing.models import LeaderboardRank
from marketing.utils import get_or_save_email_subscriber
from retail.utils import strip_double_chars, strip_html

# RENDERERS

# key, name, frequency
MARKETING_EMAILS = [
    ('roundup', _('Roundup Emails'), _('Weekly')),
    ('new_bounty_notifications', _('New Bounty Notification Emails'), _('(up to) Daily')),
    ('important_product_updates', _('Product Update Emails'), _('Quarterly')),
]

TRANSACTIONAL_EMAILS = [
    ('tip', _('Tip Emails'), _('Only when you are sent a tip')),
    ('faucet', _('Faucet Notification Emails'), _('Only when you are sent a faucet distribution')),
    ('bounty', _('Bounty Notification Emails'), _('Only when you\'re active on a bounty')),
    ('bounty_match', _('Bounty Match Emails'), _('Only when you\'ve posted a open bounty and you have a new match')),
    ('bounty_feedback', _('Bounty Feedback Emails'), _('Only after a bounty you participated in is finished.')),
    (
        'bounty_expiration', _('Bounty Expiration Warning Emails'),
        _('Only after you posted a bounty which is going to expire')
    ),
]

ALL_EMAILS = MARKETING_EMAILS + TRANSACTIONAL_EMAILS


def premailer_transform(html):
    cssutils.log.setLevel(logging.CRITICAL)
    p = premailer.Premailer(html, base_url=settings.BASE_URL)
    return p.transform()


def render_tip_email(to_email, tip, is_new):
    warning = tip.network if tip.network != 'mainnet' else ""
    already_redeemed = bool(tip.receive_txid)
    link = tip.url
    if tip.web3_type != 'v2':
        link = tip.receive_url
    elif tip.web3_type != 'v3':
        link = tip.receive_url_for_recipient
    params = {
        'link': link,
        'amount': round(tip.amount, 5),
        'tokenName': tip.tokenName,
        'comments_priv': tip.comments_priv,
        'comments_public': tip.comments_public,
        'tip': tip,
        'already_redeemed': already_redeemed,
        'show_expires': not already_redeemed and tip.expires_date < (timezone.now() + timezone.timedelta(days=365)) and tip.expires_date,
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


def render_quarterly_stats(to_email, platform_wide_stats):
    from dashboard.models import Profile
    profile = Profile.objects.filter(email=to_email).first()
    quarterly_stats = profile.get_quarterly_stats
    params = {**quarterly_stats, **platform_wide_stats}
    params['profile'] = profile
    params['subscriber'] = get_or_save_email_subscriber(to_email, 'internal'),
    print(params)
    response_html = premailer_transform(render_to_string("emails/quarterly_stats.html", params))
    response_txt = render_to_string("emails/quarterly_stats.txt", params)

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

PS - i've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

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

PS - i've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

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

PS - i've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

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


def render_admin_contact_funder(bounty, text, from_user):
    txt = f"""
{bounty.url}

{text}

{from_user}

"""
    params = {
        'txt': txt,
    }
    response_html = premailer_transform(render_to_string("emails/txt.html", params))
    response_txt = txt

    return response_html, response_txt


def render_funder_stale(github_username, days=30, time_as_str='about a month'):
    """Render the stale funder email template.

    Args:
        github_username (str): The Github username to be referenced in the email.
        days (int): The number of days back to reference.
        time_as_str (str): The human readable length of time to reference.

    Returns:
        str: The rendered response as a string.

    """
    github_username = f"@{github_username}" if github_username else "there"
    response_txt = f"""
hi {github_username},

kevin from Gitcoin here (CC scott and vivek too) — i see you haven't funded an issue in {time_as_str}. in the spirit of making Gitcoin better + checking in:

- has anything been slipping on your issue board which might be bounty worthy?
- do you have any feedback for Gitcoin Core on how we might improve the product to fit your needs?

our idea is that gitcoin should be a place you come when priorities stretch long, and you need an extra set of capable hands. curious if this fits what you're looking for these days.

appreciate you being a part of the community and let me know if you'd like some Gitcoin schwag — just send over a mailing address and a t-shirt size and it'll come your way.

~ kevin

"""

    params = {'txt': response_txt}
    response_html = premailer_transform(render_to_string("emails/txt.html", params))
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


def render_gdpr_reconsent(to_email):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    params = {
        'subscriber': sub,
    }

    response_html = premailer_transform(render_to_string("emails/gdpr_reconsent.html", params))
    response_txt = render_to_string("emails/gdpr_reconsent.txt", params)

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


def render_bounty_changed(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_changed.html", params))
    response_txt = render_to_string("emails/bounty_changed.txt", params)

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
        'subscriber': get_or_save_email_subscriber(interest.profile.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/render_bounty_startwork_expired.html", params))
    response_txt = render_to_string("emails/render_bounty_startwork_expired.txt", params)

    return response_html, response_txt


def render_gdpr_update(to_email):
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'terms_of_use_link': 'https://gitcoin.co/legal/terms',
        'privacy_policy_link': 'https://gitcoin.co/legal/privacy',
        'cookie_policy_link': 'https://gitcoin.co/legal/cookie',
    }

    subject = "Gitcoin: Updated Terms & Policies"
    response_html = premailer_transform(render_to_string("emails/gdpr_update.html", params))
    response_txt = render_to_string("emails/gdpr_update.txt", params)

    return response_html, response_txt, subject


def render_start_work_approved(interest, bounty):
    to_email = interest.profile.email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "Request Accepted "
    response_html = premailer_transform(render_to_string("emails/start_work_approved.html", params))
    response_txt = render_to_string("emails/start_work_approved.txt", params)

    return response_html, response_txt, subject


def render_start_work_rejected(interest, bounty):
    to_email = interest.profile.email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "Work Request Denied"
    response_html = premailer_transform(render_to_string("emails/start_work_rejected.html", params))
    response_txt = render_to_string("emails/start_work_rejected.txt", params)

    return response_html, response_txt, subject


def render_start_work_new_applicant(interest, bounty):
    to_email = bounty.bounty_owner_email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "A new request to work on your bounty"
    response_html = premailer_transform(render_to_string("emails/start_work_new_applicant.html", params))
    response_txt = render_to_string("emails/start_work_new_applicant.txt", params)

    return response_html, response_txt, subject


def render_start_work_applicant_about_to_expire(interest, bounty):
    to_email = bounty.bounty_owner_email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "24 Hrs to Approve"
    response_html = premailer_transform(render_to_string("emails/start_work_applicant_about_to_expire.html", params))
    response_txt = render_to_string("emails/start_work_applicant_about_to_expire.txt", params)

    return response_html, response_txt, subject


def render_start_work_applicant_expired(interest, bounty):
    to_email = bounty.bounty_owner_email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "A Worker was Auto Approved"
    response_html = premailer_transform(render_to_string("emails/start_work_applicant_expired.html", params))
    response_txt = render_to_string("emails/start_work_applicant_expired.txt", params)

    return response_html, response_txt, subject


# ROUNDUP_EMAIL
def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty
    from external_bounties.models import ExternalBounty
    subject = "Gitcoin's Summer Results & Holiday Plans"

    intro = '''

<p>
Hi there,
</p>
<p>
This week, we wrote more about our Q3 Results and Q4 Goals in <a href="https://medium.com/gitcoin/gitcoins-sprint-to-the-holidays-6d4103ad9ea4">Gitcoin's Sprint To The Holiday's</a>. We're excited about
the $350K in work already on the Gitcoin platform, and even more excited about a few things to come this winter. More to come!
</p>
<p>
Perhaps more importantly, we're in swag giveaway mode! If you ever wanted a funky Gitcoin shirt, now's the time to act.
Make a <a href="https://gitcoin.co/requests/">Gitcoin Request</a> on any open source Github issue and you'll be eligible.
</p>
<p>
We're on the move! If you'll be at Github Universe (Oct 16-17), Web 3 Summit (Oct 22 - 24), Sustain OSS (Oct 25) or Devcon 4, give us a shout!
</p>
<h3>What else is new?</h3>
    <ul>
        <li>
        We clarified <a href="https://medium.com/gitcoin/setting-your-oss-repos-monetary-policy-9c493118cd34">Gitcoin's Monetary policy</a> this week - explaining when we provide tips / bounties to contributors.
        We hope this serves as an example for other open source projects who pay fairly for help!
        </li>
        <li>
        The Gitcoin Livestream is back as regularly scheduled this week. <a href="https://gitcoin.co/livestream">Join us at 5PM ET</a>!
        </li>
    </ul>
</p>
<p>
Back to BUIDLing,
</p>
'''
    highlights = [{
        'who': 'Dan-Nolan',
        'who_link': True,
        'what': 'Received an ETHPrize Bounty via Gitcoin!',
        'link': 'https://gitcoin.co/issue/ChainshotDapps/content/1/1347',
        'link_copy': 'View more',
    }, {
        'who': 'adamskrodzki',
        'who_link': True,
        'what': 'Added tests for Winding Tree vesting contract!',
        'link': 'https://gitcoin.co/issue/windingtree/vesting-contract/1/1375',
        'link_copy': 'View more',
    }, {
        'who': 'barrasso',
        'who_link': True,
        'what': 'Won an ETH SF Bounty from Bloqboard!',
        'link': 'https://gitcoin.co/issue/ethglobal/ethsanfrancisco-bounties/9/1373',
        'link_copy': 'View more',
    }, ]

    bounties_spec = [{
        'url': 'https://github.com/prysmaticlabs/prysm/issues/569',
        'primer': 'Work with Prysmatic Labs on Sharding.',
    }, {
        'url': 'https://github.com/trailofbits/echidna/issues/15',
        'primer': 'Trail Of Bits bounty via Ethereum Community Fund.',
    }, {
        'url': 'https://github.com/Bounties-Network/Explorer/issues/237',
        'primer': 'Know anything about encryption? Bounties Network wants to know.'
    }, ]

    num_leadboard_items = 5
    #### don't need to edit anything below this line
    leaderboard = {
        'quarterly_payers': {
            'title': _('Top Payers'),
            'items': [],
        },
        'quarterly_earners': {
            'title': _('Top Earners'),
            'items': [],
        },
        'quarterly_orgs': {
            'title': _('Top Orgs'),
            'items': [],
        },
    }
    for key, __ in leaderboard.items():
        leaderboard[key]['items'] = LeaderboardRank.objects.active() \
            .filter(leaderboard=key).order_by('rank')[0:num_leadboard_items]

    bounties = []
    for nb in bounties_spec:
        try:
            bounty = Bounty.objects.current().filter(
                github_url__iexact=nb['url'],
            ).order_by('-web3_created').first()
            if bounty:
                bounties.append({
                    'obj': bounty,
                    'primer': nb['primer']
                })
        except Exception as e:
            print(e)

    ecosystem_bounties = ExternalBounty.objects.filter(created_on__gt=timezone.now() - timezone.timedelta(weeks=1)).order_by('?')[0:5]

    params = {
        'intro': intro,
        'intro_txt': strip_double_chars(strip_double_chars(strip_double_chars(strip_html(intro), ' '), "\n"), "\n "),
        'bounties': bounties,
        'leaderboard': leaderboard,
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
    bounties = Bounty.objects.current().order_by('-web3_created')[0:3]
    old_bounties = Bounty.objects.current().order_by('-web3_created')[0:3]
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, bounties, old_bounties)
    return HttpResponse(response_html)


@staff_member_required
def new_work_submission(request):
    from dashboard.models import Bounty
    bounty = Bounty.objects.current().filter(idx_status='submitted').last()
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
    response_html, _ = render_bounty_feedback(Bounty.objects.current().filter(idx_status='done').last(), 'foo')
    return HttpResponse(response_html)


@staff_member_required
def funder_stale(request):
    """Display the stale funder email template.

    Params:
        limit (int): The number of days to limit the scope of the email to.
        duration_copy (str): The copy to use for associated duration text.
        username (str): The Github username to reference in the email.

    Returns:
        HttpResponse: The HTML version of the templated HTTP response.

    """
    limit = int(request.GET.get('limit', 30))
    duration_copy = request.GET.get('duration_copy', 'about a month')
    username = request.GET.get('username', '@foo')
    response_html, _ = render_funder_stale(username, limit, duration_copy)
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


@staff_member_required
def quarterly_roundup(request):
    from marketing.utils import get_platform_wide_stats
    from dashboard.models import Profile
    platform_wide_stats = get_platform_wide_stats()
    email = settings.CONTACT_EMAIL
    handle = request.GET.get('handle')
    if handle:
        profile = Profile.objects.filter(handle=handle).first()
        email = profile.email
    response_html, _ = render_quarterly_stats(email, platform_wide_stats)
    return HttpResponse(response_html)


@staff_member_required
def gdpr_reconsent(request):
    response_html, _ = render_gdpr_reconsent(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)


@staff_member_required
def start_work_approved(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_approved(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_rejected(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_rejected(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_new_applicant(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_new_applicant(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_applicant_about_to_expire(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_applicant_about_to_expire(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def start_work_applicant_expired(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_applicant_expired(interest, bounty)
    return HttpResponse(response_html)
