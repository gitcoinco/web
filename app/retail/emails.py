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
import datetime
import logging
from datetime import date, timedelta
from functools import partial

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

import cssutils
import premailer
from app.utils import get_default_network
from grants.models import Contribution, Grant, Subscription
from marketing.models import LeaderboardRank
from marketing.common.utils import get_or_save_email_subscriber
from perftools.models import StaticJsonEnv
from retail.utils import build_utm_tracking, strip_double_chars, strip_html

logger = logging.getLogger(__name__)

# RENDERERS

# key, name, frequency
MARKETING_EMAILS = [
    ('new_bounty_notifications', _('Daily Emails'), _('(up to) Daily')),
    ('welcome_mail', _('Welcome Emails'), _('First 3 days after you sign up')),
    ('roundup', _('Roundup Emails'), _('Weekly')),
    ('important_product_updates', _('Product Update Emails'), _('Quarterly')),
	('general', _('General Email Updates'), _('as it comes')),
	('quarterly', _('Quarterly Email Updates'), _('Quarterly')),
	('grant_recontribute', _('Recontribute to previously funded grants'), _('Quarterly')),
]

TRANSACTIONAL_EMAILS = [
    ('tip', _('Tip Emails'), _('Only when you are sent a tip')),
    ('bounty', _('Bounty Notification Emails'), _('Only when you\'re active on a bounty')),
    ('bounty_match', _('Bounty Match Emails'), _('Only when you\'ve posted a open bounty and you have a new match')),
    ('bounty_feedback', _('Bounty Feedback Emails'), _('Only after a bounty you participated in is finished.')),
    (
        'bounty_expiration', _('Bounty Expiration Warning Emails'),
        _('Only after you posted a bounty which is going to expire')
    ),
    ('export_data', _('Export Data Emails'), _('Only when you have exported contribution or spending data')),
    ('export_data_failed', _('Export Data Failed Emails'), _('Only when you have tried to export contribution or spending data but the process has failed.')),
    ('featured_funded_bounty', _('Featured Funded Bounty Emails'), _('Only when you\'ve paid for a bounty to be featured')),
    ('comment', _('Comment Emails'), _('Only when you are sent a comment')),
    ('wall_post', _('Wall Post Emails'), _('Only when someone writes on your wall')),
    ('grant_updates', _('Grant Update Emails'), _('Updates from Grant Owners about grants you\'ve funded.')),
    ('grant_txn_failed', _('Grant Transaction Failed Emails'), _('Notifies Grant contributors when their contribution txn has failed.')),
]


NOTIFICATION_EMAILS = [
    ('mention', _('Mentions'), _('Only when other users mention you on posts')),
]


MAUTIC_EMAILS = [
    ('marketing', _('General Marketing Emails'), _('as it comes')),
]


ALL_EMAILS = MARKETING_EMAILS + TRANSACTIONAL_EMAILS + NOTIFICATION_EMAILS + MAUTIC_EMAILS


def premailer_transform(html):
    cssutils.log.setLevel(logging.CRITICAL)
    p = premailer.Premailer(html, base_url=settings.BASE_URL)
    return p.transform()


def render_export_data_email(user_profile):
    params = {'profile': user_profile}
    response_html = premailer_transform(render_to_string("emails/export_data.html", params))
    response_txt = render_to_string("emails/export_data.txt", params)
    subject = _("Your Gitcoin CSV Download")

    return response_html, response_txt, subject


def render_export_data_email_failed(user_profile):
    params = {'profile': user_profile}
    response_html = premailer_transform(render_to_string("emails/export_data_failed.html", params))
    response_txt = render_to_string("emails/export_data_failed.txt", params)
    subject = _("Your CSV Download Has Failed")

    return response_html, response_txt, subject


def render_featured_funded_bounty(bounty):
    params = {'bounty': bounty, 'utm_tracking': build_utm_tracking('featured_funded_bounty')}
    response_html = premailer_transform(render_to_string("emails/funded_featured_bounty.html", params))
    response_txt = render_to_string("emails/funded_featured_bounty.txt", params)
    subject = _("Your bounty is now live on Gitcoin!")

    return response_html, response_txt, subject


def render_new_grant_email(grant):
    params = {'grant': grant, 'utm_tracking': build_utm_tracking('new_grant')}
    response_html = premailer_transform(render_to_string("emails/grants/new_grant.html", params))
    response_txt = render_to_string("emails/grants/new_grant.txt", params)
    subject = _("Your Gitcoin Grant")
    return response_html, response_txt, subject


def render_new_grant_approved_email(grant):
    params = {'grant': grant, 'utm_tracking': build_utm_tracking('new_grant_approved')}
    response_html = premailer_transform(render_to_string("emails/grants/new_grant_approved.html", params))
    response_txt = render_to_string("emails/grants/new_grant_approved.txt", params)
    subject = _("Your Grant on Gitcoin Grants has been approved")
    return response_html, response_txt, subject


def render_new_contributions_email(grant):
    hours_ago = 12
    network = get_default_network()
    contributions = grant.contributions.filter(
        success=True,
        tx_cleared=True,
        created_on__gt=timezone.now() - timezone.timedelta(hours=hours_ago),
        subscription__network=network
    )
    amount_raised = sum(contributions.values_list('normalized_data__amount_per_period_usdt', flat=True))
    num_of_contributors = len(set(contributions.values_list('profile_for_clr', flat=True)))

    # amount raised in L2/sidechains
    amount_raised_zksync = sum(
        contributions.filter(checkout_type='eth_zksync').values_list(
            'normalized_data__amount_per_period_usdt', flat=True
        )
    )
    amount_raised_polygon = sum(
        contributions.filter(checkout_type='eth_polygon').values_list(
            'normalized_data__amount_per_period_usdt', flat=True
        )
    )

    params = {
        'grant': grant,
        'hours_ago': hours_ago,
        'amount_raised': amount_raised,
        'amount_raised_zksync': amount_raised_zksync,
        'amount_raised_polygon': amount_raised_polygon,
        'show_zksync_amount': False if amount_raised_zksync < 1 else True,
        'show_polygon_amount': False if amount_raised_polygon < 1 else True,
        'num_of_contributors': num_of_contributors,
        'media_url': settings.MEDIA_URL,
        'contributions': contributions,
        'utm_tracking': build_utm_tracking('new_contributions'),
    }
    response_html = premailer_transform(render_to_string("emails/grants/new_contributions.html", params))
    response_txt = render_to_string("emails/grants/new_contributions.txt", params)
    subject = f"You have {contributions.count()} new Grant contributions worth ${round(amount_raised, 2)}!"

    if amount_raised < 1:
        # trigger to prevent email sending for negligible amounts
        subject = ''

    return response_html, response_txt, subject


def render_thank_you_for_supporting_email(grants_with_subscription):
    totals = {}
    total_match_amount = 0
    match_token = 'DAI'
    for gws in grants_with_subscription:
        key = gws['subscription'].token_symbol
        val = float(gws['subscription'].amount_per_period)
        if key not in totals.keys():
            totals[key] = 0
        totals[key] += float(val)
        match_amount = float(gws.normalized_data['match_amount_when_contributed'])
        total_match_amount += match_amount if match_amount else float(gws['subscription'].match_amount)
        match_token = gws['subscription'].match_amount_token

    params = {
        'grants_with_subscription': grants_with_subscription,
        "totals": totals,
        'total_match_amount': total_match_amount,
        'match_token': match_token,
        'utm_tracking': build_utm_tracking('thank_you_for_supporting_email'),
    }
    response_html = premailer_transform(render_to_string("emails/grants/thank_you_for_supporting.html", params))
    response_txt = render_to_string("emails/grants/thank_you_for_supporting.txt", params)
    subject = _("Thank you for supporting Grants on Gitcoin!")
    return response_html, response_txt, subject


def render_support_cancellation_email(grant, subscription):
    params = {'grant': grant, 'subscription': subscription}
    response_html = premailer_transform(render_to_string("emails/grants/support_cancellation.html", params))
    response_txt = render_to_string("emails/grants/support_cancellation.txt", params)
    subject = _("Your subscription on Gitcoin Grants has been cancelled")

    return response_html, response_txt, subject


def render_grant_cancellation_email(grant):
    params = {'grant': grant, 'utm_tracking': build_utm_tracking('grant_cancellation'),}
    response_html = premailer_transform(render_to_string("emails/grants/grant_cancellation.html", params))
    response_txt = render_to_string("emails/grants/grant_cancellation.txt", params)
    subject = _("Your Grant on Gitcoin Grants has been cancelled")
    return response_html, response_txt, subject


def render_subscription_terminated_email(grant, subscription):
    params = {'grant': grant, 'subscription': subscription}
    response_html = premailer_transform(render_to_string("emails/grants/subscription_terminated.html", params))
    response_txt = render_to_string("emails/grants/subscription_terminated.txt", params)
    subject = _("Your subscription on Gitcoin Grants has been cancelled by the Grant Creator")
    return response_html, response_txt, subject


def render_successful_contribution_email(grant, subscription, contribution):
    params = {
        'grant': grant,
        'subscription': subscription,
        'utm_tracking': build_utm_tracking('successful_contribution_email'),
        'contribution': contribution,
    }
    response_html = premailer_transform(render_to_string("emails/grants/successful_contribution.html", params))
    response_txt = render_to_string("emails/grants/successful_contribution.txt", params)
    subject = _('Your Gitcoin Grants contribution was successful!')
    return response_html, response_txt, subject


def render_pending_contribution_email(contribution):
    params = {
        'contribution': contribution,
        'hide_bottom_logo': True,
        'email_style': 'grants',
        'utm_tracking': build_utm_tracking('pending_contributions'),
    }
    response_html = premailer_transform(render_to_string("emails/grants/reminder_pending_contribution.html", params))
    response_txt = render_to_string("emails/grants/reminder_pending_contribution.html", params)
    subject = _('Complete Grant Contribution Checkout')
    return response_html, response_txt, subject


def featured_funded_bounty(request):
    from dashboard.models import Bounty
    bounty = Bounty.objects.first()
    response_html, __, __ = render_featured_funded_bounty(bounty)
    return HttpResponse(response_html)


@staff_member_required
def successful_contribution(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    contribution = Contribution.objects.filter(subscription__pk=subscription.pk).first()
    response_html, __, __ = render_successful_contribution_email(grant, subscription, contribution)
    return HttpResponse(response_html)


@staff_member_required
def pending_contribution(request):
    contribution = Contribution.objects.filter(validator_comment__contains="User may not be aware so send them email reminders").first()
    response_html, __, __ = render_pending_contribution_email(contribution)
    return HttpResponse(response_html)


@staff_member_required
def subscription_terminated(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    response_html, __, __ = render_subscription_terminated_email(grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def grant_cancellation(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_grant_cancellation_email(grant)
    return HttpResponse(response_html)


@staff_member_required
def support_cancellation(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    response_html, __, __ = render_support_cancellation_email(grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def thank_you_for_supporting(request):
    grant_with_subscription = []
    for i in range(0, 10):
        grant = Grant.objects.order_by('?').first()
        subscription = Subscription.objects.filter(grant__pk=grant.pk).last()
        if subscription:
            grant_with_subscription.append({
                'grant': grant,
                'subscription': subscription
            })
    response_html, __, __ = render_thank_you_for_supporting_email(grant_with_subscription)
    return HttpResponse(response_html)



@staff_member_required
def new_contributions(request):
    subscription = Subscription.objects.last()
    response_html, __, __ = render_new_contributions_email(subscription.grant)
    return HttpResponse(response_html)


@staff_member_required
def new_grant(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_new_grant_email(grant)
    return HttpResponse(response_html)


@staff_member_required
def new_grant_approved(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_new_grant_approved_email(grant)
    return HttpResponse(response_html)


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
		'email_type': 'tip',
        'utm_tracking': build_utm_tracking('new_tip'),
    }

    response_html = premailer_transform(render_to_string("emails/new_tip.html", params))
    response_txt = render_to_string("emails/new_tip.txt", params)

    return response_html, response_txt


def render_tribe_hackathon_prizes(hackathon, sponsors_prizes, intro_begin):
    email_style = 'hackathon'

    hackathon = {
        'hackathon': hackathon,
        'name': hackathon.name,
        'image_url': hackathon.logo.url if hackathon.logo else f'{settings.STATIC_URL}v2/images/emails/hackathons-neg.png',
        'url': hackathon.url,
    }

    for sponsor_prize in sponsors_prizes:
        sponsor_prize['name'] = sponsor_prize['sponsor'].name
        sponsor_prize['image_url'] = sponsor_prize['sponsor'].avatar_url or f'{settings.STATIC_URL}v2/images/emails/hackathons-neg.png'

    intro = f"{intro_begin} participating on a new hackathon on Gitcoin: "

    params = {
        'hackathon': hackathon,
        'sponsors_prizes': sponsors_prizes,
        'intro': intro,
        'email_style': email_style,
        'utm_tracking': build_utm_tracking('tribe_hackathon_prizes'),
        'hide_bottom_logo': True,
    }

    response_html = premailer_transform(render_to_string("emails/tribe_hackathon_prizes.html", params))
    response_txt = render_to_string("emails/tribe_hackathon_prizes.txt", params)

    return response_html, response_txt


def render_request_amount_email(to_email, request, is_new):

    link = f'{reverse("tip")}?request={request.id}'
    params = {
        'link': link,
        'amount': request.amount,
        'tokenName': request.token_name,
        'address': request.address,
        'comments': request.comments,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'email_type': 'request',
        'utm_tracking': build_utm_tracking('request_amount_email'),
        'request': request,
        'already_received': request.tip
    }

    response_html = premailer_transform(render_to_string("emails/request_funds.html", params))
    response_txt = render_to_string("emails/new_tip.txt", params)

    return response_html, response_txt


def render_kudos_email(to_email, kudos_transfer, is_new, html_template, text_template=None):
    """Summary

    Args:
        to_emails (list): An array of email addresses to send the email to.
        kudos_transfer (model): An instance of the `kudos.model.KudosTransfer` object.  This contains the information about the kudos that will be cloned.
        is_new (TYPE): Description

    Returns:
        tup: response_html, response_txt
    """
    warning = kudos_transfer.network if kudos_transfer.network != 'mainnet' else ""
    already_redeemed = bool(kudos_transfer.receive_txid)
    link = kudos_transfer.receive_url_for_recipient
    params = {
        'link': link,
        'amount': round(kudos_transfer.amount, 5),
        'token_elem': kudos_transfer.kudos_token or kudos_transfer.kudos_token_cloned_from,
        'kudos_token:': kudos_transfer.kudos_token,
        'comments_public': kudos_transfer.comments_public,
        'kudos_transfer': kudos_transfer,
        'already_redeemed': already_redeemed,
        'is_new': is_new,
        'warning': warning,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'is_sender': to_email not in kudos_transfer.emails,
        'is_receiver': to_email in kudos_transfer.emails,
        'utm_tracking': build_utm_tracking('new_kudos'),
    }

    response_html = premailer_transform(render_to_string(html_template, params))
    response_txt = render_to_string(text_template, params) if text_template else None

    return response_html, response_txt


render_new_kudos_email = partial(render_kudos_email, html_template='emails/new_kudos.html', text_template='emails/new_kudos.txt')
render_sent_kudos_email = partial(render_kudos_email, html_template='emails/new_kudos.html', text_template='emails/new_kudos.txt')
render_kudos_accepted_email = partial(render_kudos_email, html_template='emails/new_kudos.html', text_template='emails/new_kudos.txt')
render_kudos_mint_email = partial(render_kudos_email, html_template='emails/kudos_mint.html', text_template=None)
render_kudos_mkt_email = partial(render_kudos_email, html_template='emails/kudos_mkt.html', text_template=None)


def render_match_email(bounty, github_username):
    params = {
        'bounty': bounty,
        'github_username': github_username,
		'email_type': 'bounty_match'
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
    params['email_type'] = 'quarterly'
    response_html = premailer_transform(render_to_string("emails/quarterly_stats.html", params))
    response_txt = render_to_string("emails/quarterly_stats.txt", params)

    return response_html, response_txt


def render_tax_report(to_email, tax_year):
    from dashboard.models import Profile
    profile = Profile.objects.filter(email=to_email).first()
    params = {}
    params['user'] = profile
    params['tax_year'] = tax_year
    params['email_type'] = 'tax_report'
    response_html = premailer_transform(render_to_string("emails/tax_report.html", params))
    response_text = render_to_string("emails/tax_report.txt", params)

    return response_html, response_text


def render_funder_payout_reminder(**kwargs):
    kwargs['bounty_fulfillment'] = kwargs['bounty'].fulfillments.filter(profile__handle=kwargs['github_username']).last()
    kwargs['utm_tracking'] = build_utm_tracking('funder_payout_reminder')
    response_html = premailer_transform(render_to_string("emails/funder_payout_reminder.html", kwargs))
    response_txt = ''
    return response_html, response_txt


def render_grant_match_distribution_final_txn(match):
    CLR_ROUND_DATA = StaticJsonEnv.objects.get(key='CLR_ROUND').data
    claim_end_date = CLR_ROUND_DATA.get('claim_end_date')

    # timezones are in UTC (format example: 2021-06-16:15.00.00)
    claim_end_date = datetime.datetime.strptime(claim_end_date, '%Y-%m-%d:%H.%M.%S')
    params = {
        'round_number': match.round_number,
        'rounded_amount': round(match.amount, 2),
        'profile_handle': match.grant.admin_profile.handle,
        'grant_url': f'https://gitcoin.co{match.grant.get_absolute_url()}',
        'grant': match.grant,
        'claim_end_date': claim_end_date,
        'utm_tracking': build_utm_tracking('clr_match_claim'),
    }
    response_html = premailer_transform(render_to_string("emails/grants/clr_match_claim.html", params))
    response_txt = render_to_string("emails/grants/clr_match_claim.txt", params)
    return response_html, response_txt


def render_match_distribution(mr):
    params = {
        'mr': mr,
        'utm_tracking': build_utm_tracking('match_distribution'),
    }
    response_html = premailer_transform(render_to_string("emails/match_distribution.html"))
    response_txt = ''
    return response_html, response_txt


def render_no_applicant_reminder(bounty):
    params = {
        'bounty': bounty,
        'utm_tracking': build_utm_tracking('no_applicant_reminder'),
        'directory_link': '/users?skills=' + bounty.keywords.lower()
    }
    response_html = premailer_transform(render_to_string("emails/no_applicant_reminder.html", params))
    response_txt = render_to_string("emails/no_applicant_reminder.txt", params)
    return response_html, response_txt


def render_bounty_feedback(bounty, persona='submitter', previous_bounties=[]):
    if persona == 'fulfiller':
        accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
        github_username = " @" + accepted_fulfillments.first().fulfiller_github_username if accepted_fulfillments.exists() and accepted_fulfillments.first().fulfiller_github_username else ""
        txt = f"""
hi{github_username},

thanks for turning around this bounty. we're hyperfocused on making Gitcoin a great place for blockchain developers to hang out, learn new skills, and git coins.

in that spirit, we have a few questions for you.

> what would you say your average hourly rate was for this bounty? {bounty.github_url}

> what was the best thing about working on the platform? what was the worst?

> would you use Gitcoin again?

thanks again for being a member of the community.

kyle, frank & alisa (gitcoin product team)

PS - we've got some new gitcoin schwag on order. if you are intersted, you can use discount code product-feedback-is-a-gift for 50% off your order :).

"""
    elif persona == 'funder':
        github_username = " @" + bounty.bounty_owner_github_username if bounty.bounty_owner_github_username else ""
        if bounty.status == 'done':
            txt = f"""

hi{github_username},

thanks for putting this bounty ({bounty.github_url}) on Gitcoin.  i'm glad to see it was turned around.

we're hyperfocused on making Gitcoin a great place for blockchain developers to hang out, learn new skills, and git some coins.

in that spirit, we have a few questions for you:

> how much coaching/communication did it take the counterparty to turn around the issue? was this burdensome?

> what was the best thing about working on the platform? what was the worst?

> would you use gitcoin again?

thanks for being a member of the community.

kyle, frank & alisa (gitcoin product team)

PS - we've got some new gitcoin schwag on order. if you are intersted, you can use discount code product-feedback-is-a-gift for 50% off your order :)

"""
        elif bounty.status == 'cancelled':
            txt = f"""
hi{github_username},

we saw that you cancelled this bounty.

we are sorry to see that the bounty did not get done.

we have a few questions for you.

> why did you decide to cancel the bounty?

> would you use gitcoin again?

thanks again for being a member of the community.

kyle, frank & alisa (gitcoin product team)

PS - we've got some new gitcoin schwag on order. if you are intersted, you can use discount code product-feedback-is-a-gift for 50% off your order :)

"""
        else:
            raise Exception('unknown bounty status')
    else:
        raise Exception('unknown persona')

    params = {
        'txt': txt,
		'email_type': 'bounty_feedback'
    }
    response_txt = premailer_transform(render_to_string("emails/txt.html", params))
    response_html = f"<pre>{response_txt}</pre>"

    return response_html, response_txt


def render_admin_contact_funder(bounty, text, from_user):
    txt = f"""
{bounty.url}

{text}

{from_user}

"""
    params = {
        'txt': txt,
		'email_type': 'admin_contact_funder'
    }
    response_html = premailer_transform(render_to_string("emails/txt.html", params))
    response_txt = txt

    return response_html, response_txt


def render_funder_stale(github_username, days=60, time_as_str='a couple months'):
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

kyle, frank, and alisa from Gitcoin here — i see you haven't funded an issue in {time_as_str}.

in the spirit of making Gitcoin better + checking in:

> do you have any issues which might be bounty worthy or projects you're hoping to build?

> do you have any feedback for us on how we might improve the product to fit your needs?

> are you interested in hosting or partnering in one of our upcoming hackathons? this is often teh best way to get top talent working on your issues.

appreciate you being a part of the community + if you are intersted, you can use discount code product-feedback-is-a-gift for 50% off your order :)

~ kyle, frank & alisa (gitcoin product team)


"""

    params = {'txt': response_txt}
    response_html = premailer_transform(render_to_string("emails/txt.html", params))
    return response_html, response_txt


def get_notification_count(profile, days_ago, from_date):
    from_date = from_date + timedelta(days=1)
    to_date = from_date - timedelta(days=days_ago)

    notifications_count = 0
    from inbox.models import Notification
    try:
        notifications_count = Notification.objects.filter(to_user=profile.user.id, is_read=False, created_on__range=[to_date, from_date]).count()
    except Notification.DoesNotExist:
        pass
    except AttributeError:
        pass
    return notifications_count


def email_to_profile(to_email):
    from dashboard.models import Profile
    try:
        profile = Profile.objects.filter(email_index=to_email.lower()).last()
    except Profile.DoesNotExist:
        pass
    return profile


def render_new_bounty(to_email, bounties, old_bounties, offset=3, quest_of_the_day={}, upcoming_grant={}, hackathons=(), from_date=date.today(), days_ago=7, chats_count=0, featured_bounties=[]):
    from dateutil.parser import parse
    from marketing.views import email_announcements, trending_avatar

    sub = get_or_save_email_subscriber(to_email, 'internal')
    counter = 0
    import time
    counter += 1
    print(counter, time.time())
    email_style = 26

    # Get notifications count from the Profile.User of to_email
    profile = email_to_profile(to_email)

    notifications_count = get_notification_count(profile, days_ago, from_date)

    counter += 1
    print(counter, time.time())

    current_hackathons = sorted(hackathons[0], key=lambda ele: parse(ele['start_date']))
    upcoming_hackathons = sorted(hackathons[1], key=lambda ele: parse(ele['start_date']))

    current_hackathons = current_hackathons[0:7]
    upcoming_hackathons = upcoming_hackathons[0:7]

    counter += 1
    print(counter, time.time())
    params = {
        'old_bounties': old_bounties,
        'bounties': bounties,
        'featured_bounties': featured_bounties,
        'trending_avatar': trending_avatar(),
        'email_announcements': email_announcements(),
        'subscriber': sub,
        'keywords': ",".join(sub.keywords) if sub and sub.keywords else '',
        'email_style': email_style,
		'email_type': 'new_bounty_notifications',
        'utm_tracking': build_utm_tracking('new_bounty_daily'),
        'base_url': settings.BASE_URL,
        'media_url': settings.MEDIA_URL,
        'quest_of_the_day': quest_of_the_day,
        'current_hackathons': current_hackathons,
        'upcoming_hackathons': upcoming_hackathons,
        'notifications_count': notifications_count,
        'chats_count': chats_count,
    }
    counter += 1
    print(counter, time.time())
    foo = render_to_string("emails/new_bounty.html", params)

    print(counter, time.time())
    response_html = premailer_transform(foo)
    print(counter, time.time())
    response_txt = render_to_string("emails/new_bounty.txt", params)
    counter += 1
    print(counter, time.time())

    return response_html, response_txt


def render_unread_notification_email_weekly_roundup(to_email, from_date=date.today(), days_ago=7):
    subscriber = get_or_save_email_subscriber(to_email, 'internal')
    from dashboard.models import Profile
    from inbox.models import Notification
    profile = Profile.objects.filter(email_index=to_email.lower()).last()

    from_date = from_date + timedelta(days=1)
    to_date = from_date - timedelta(days=days_ago)

    notifications = Notification.objects.filter(to_user=profile.user.id, is_read=False, created_on__range=[to_date, from_date]).count()

    params = {
        'subscriber': subscriber,
        'profile': profile.handle,
        'notifications': notifications,
		'email_type': 'roundup'
    }

    subject = "Your unread notifications"

    response_html = premailer_transform(render_to_string("emails/unread_notifications_roundup/unread_notification_email_weekly_roundup.html", params))
    response_txt = render_to_string("emails/unread_notifications_roundup/unread_notification_email_weekly_roundup.txt", params)

    return response_html, response_txt, subject


def render_weekly_recap(to_email, from_date=date.today(), days_back=7):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    from dashboard.models import Profile
    prof = Profile.objects.filter(email_index=to_email.lower()).last()
    bounties = prof.bounties.all()
    from_date = from_date + timedelta(days=1)
    to_date = from_date - timedelta(days=days_back)

    activity_types = {}
    _sections = []
    activity_types_def = {
        "start_work": {
          "css-class": "status-open",
          "text": "Started work"
        },
        "stop_work": {
          "css-class": "status-cancelled",
          "text": "Work stopped"
        },
        "worker_approved": {
          "css-class": "status-open",
          "text": "Worker got approved"
        },
        "worker_applied": {
          "css-class": "status-submitted",
          "text": "Worker applied"
        },
        "new_bounty": {
          "css-class": "status-open",
          "text": "New created bounties"
        },
        "work_submitted": {
          "css-class": "status-submitted",
          "text": "Work got submitted"
        },
    }

    for bounty in bounties:
        for activity in bounty.activities.filter(created__range=[to_date, from_date]):
            if activity_types.get(activity.activity_type) is None:
                activity_types[activity.activity_type] = []

            avatar_url = "about:blank"
            if activity.profile:
                avatar_url = activity.profile.avatar_url

            item = {
                'bounty_image_url': avatar_url,
                'bounty_action_user': activity.profile.handle,
                'bounty_action_date': activity.created,
                'bounty_action': activity.activity_type,
                'bounty_name': f'{bounty.title}',
                'bounty_link': bounty.get_absolute_url()
            }
            activity_types[activity.activity_type].append(item)

    # TODO: Activities
    # TODO: Fulfillment
    # TODO: Interest

    for act_type in activity_types:
        if activity_types_def.get(act_type):
            section = {
              'items': activity_types[act_type],
              'header_name': activity_types_def[act_type]["text"],
              'header_css': activity_types_def[act_type]["css-class"],
            }
            _sections.append(section)

    params = {
        'subscriber': sub,
        'sections': _sections,
        'profile': prof,
        'override_back_color': '#f2f6f9',
        'select_params': {
          'from': from_date,
          'to': to_date
        },
        'debug': activity_types,
		'email_type': 'roundup'
    }

    response_html = premailer_transform(render_to_string("emails/recap/weekly_founder_recap.html", params))
    response_txt = render_to_string("emails/recap/weekly_founder_recap.txt", params)

    return response_html, response_txt


def render_gdpr_reconsent(to_email):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    params = {
        'subscriber': sub,
		'email_type': 'roundup'
    }

    response_html = premailer_transform(render_to_string("emails/gdpr_reconsent.html", params))
    response_txt = render_to_string("emails/gdpr_reconsent.txt", params)

    return response_html, response_txt


def render_share_bounty(to_email, msg, from_profile, invite_url=None, kudos_invite=False):
    """Render the share bounty email template.

    Args:
        to_email: user to send the email to.
        msg: the message sent in the email.

    Returns:
        str: The rendered response as a string.

    """
    params = {
        'msg': msg,
        'from_profile': from_profile,
        'to_email': to_email,
        'invite_url': invite_url,
        'kudos_invite': kudos_invite,
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('share_bounty'),
    }
    response_html = premailer_transform(render_to_string("emails/share_bounty_email.html", params))
    response_txt = render_to_string("emails/share_bounty_email.txt", params)
    return response_html, response_txt


def render_new_work_submission(to_email, bounty):
    params = {
        'bounty': bounty,
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('new_work_submission'),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_work_submission.html", params))
    response_txt = render_to_string("emails/new_work_submission.txt", params)

    return response_html, response_txt


def render_new_bounty_acceptance(to_email, bounty, unrated_count=0):
    params = {
        'bounty': bounty,
        'unrated_count': unrated_count,
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('new_bounty_acceptance'),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_acceptance.html", params))
    response_txt = render_to_string("emails/new_bounty_acceptance.txt", params)

    return response_html, response_txt


def render_new_bounty_rejection(to_email, bounty):
    params = {
        'bounty': bounty,
        'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('new_bounty_rejection'),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_rejection.html", params))
    response_txt = render_to_string("emails/new_bounty_rejection.txt", params)

    return response_html, response_txt


def render_comment(to_email, comment):
    params = {
        'comment': comment,
        'email_type': 'comment',
        'utm_tracking': build_utm_tracking('comment'),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/comment.html", params))
    response_txt = render_to_string("emails/comment.txt", params)

    return response_html, response_txt


def render_mention(to_email, post):
    from dashboard.models import Activity
    params = {
        'post': post,
        'email_type': 'mention',
        'utm_tracking': build_utm_tracking('mention'),
        'is_activity': isinstance(post, Activity),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/mention.html", params))
    response_txt = render_to_string("emails/mention.txt", params)

    return response_html, response_txt


def render_grant_update(to_email, activity):
    params = {
        'activity': activity,
        'email_type': 'grant_updates',
        'utm_tracking': build_utm_tracking('grant_update'),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/grant_update.html", params))
    response_txt = render_to_string("emails/grant_update.txt", params)

    return response_html, response_txt

def render_grant_recontribute(to_email, prev_round_start=(2020, 3, 23), prev_round_end=(2020, 4, 7), next_round=6, next_round_start=(2020, 6, 15), next_round_end=(2020, 6, 29), match_pool='175k'): # Round 5: 3/23/2020 — 4/7/2020; Round 6: 6/15/2020 — 6/29/2020 175k
    email_style = 27

    next_round_start = datetime.datetime(*next_round_start).strftime("%B %dth")
    next_round_end = datetime.datetime(*next_round_end).strftime("%B %dth %Y")

    prev_grants = []
    profile = email_to_profile(to_email)
    subscriptions = profile.grant_contributor.all()
    for subscription in subscriptions:
        grant = subscription.grant
        total_contribution_to_grant = 0
        contributions_count = subscription.subscription_contribution.filter(success=True, created_on__gte=datetime.datetime(*prev_round_start), created_on__lte=datetime.datetime(*prev_round_end)).count()
        total_contribution_to_grant = subscription.amount_per_period * contributions_count

        if total_contribution_to_grant:
            prev_grants.append({
                'id': grant.id,
                'url': grant.url[1:],
                'title': grant.title,
                'image_url': grant.logo.url if grant.logo else f'{settings.STATIC_URL}v2/images/emails/grants-symbol-pos.png',
                'amount': format(total_contribution_to_grant, '.3f'),
                'token_symbol': subscription.token_symbol
            })

    params = {
        'next_round': next_round,
        'next_round_start': next_round_start,
        'next_round_end': next_round_end,
        'match_pool': match_pool,
        'email_style': email_style,
        'utm_tracking': build_utm_tracking('grant_recontribute'),
        'prev_grants': prev_grants,
        'base_url': settings.BASE_URL,
        'bulk_add_url': "https://gitcoin.co/grants/cart/bulk-add/"+','.join(str(grant['id']) for grant in prev_grants),
        'hide_bottom_logo': True,
    }

    response_html = premailer_transform(render_to_string("emails/grant_recontribute.html", params))
    response_txt = render_to_string("emails/grant_recontribute.txt", params)

    return response_html, response_txt


def render_grant_txn_failed(contribution):
    email_style = 27
    contributions = Contribution.objects.none()
    tx_id = contribution.tx_id
    if contribution.tx_id:
        contributions = Contribution.objects.filter(tx_id=contribution.tx_id)
    elif contribution.split_tx_id:
        tx_id = contribution.split_tx_id
        contributions = Contribution.objects.filter(split_tx_id=contribution.split_tx_id)

    grants = [ele.subscription.grant for ele in contributions if ele.subscription]
    params = {
        'grants': grants,
        'tx_id': tx_id,
        'tx_url': "https://etherscan.io/tx/"+tx_id,
        'bulk_add_url': "https://gitcoin.co/grants/cart/bulk-add/" + ",".join([str(ele.id) for ele in grants]),
        'email_style': email_style,
        'utm_tracking': build_utm_tracking('grant_txn_failed'),
        'hide_bottom_logo': True,
    }

    response_html = premailer_transform(render_to_string("emails/grant_txn_failed.html", params))
    response_txt = render_to_string("emails/grant_txn_failed.txt", params)

    return response_html, response_txt

def render_wallpost(to_email, activity):
    params = {
        'activity': activity,
        'email_type': 'wall_post',
        'utm_tracking': build_utm_tracking('wallpost'),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'what': activity.what,
    }

    response_html = premailer_transform(render_to_string("emails/wall_post.html", params))
    response_txt = render_to_string("emails/wall_post.txt", params)

    return response_html, response_txt


def render_bounty_changed(to_email, bounty):
    params = {
        'bounty': bounty,
		'email_type': 'bounty',
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_changed.html", params))
    response_txt = render_to_string("emails/bounty_changed.txt", params)

    return response_html, response_txt


def render_bounty_hypercharged(to_email, bounty):
    params = {
        'bounty': bounty,
		'email_type': 'bounty',
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_hypercharged.html", params))
    response_txt = render_to_string("emails/bounty_hypercharged.txt", params)

    return response_html, response_txt


def render_bounty_changed(to_email, bounty):
    params = {
        'bounty': bounty,
		'email_type': 'bounty',
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_changed.html", params))
    response_txt = render_to_string("emails/bounty_changed.txt", params)

    return response_html, response_txt


def render_bounty_expire_warning(to_email, bounty):
    unit = 'days'
    num = int(round((bounty.expires_date - timezone.now()).days, 0))
    if num == 0:
        unit = 'hours'
        num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))

    fulfiller_emails = [fulfiller.profile.email.lower() for fulfiller in bounty.fulfillments.all()]

    params = {
        'bounty': bounty,
        'num': num,
        'unit': unit,
        'is_claimee': (to_email.lower() in fulfiller_emails),
        'is_owner': bounty.bounty_owner_email.lower() == to_email.lower(),
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('bounty_expire_warning'),
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
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('bounty_startwork_expire_warning'),
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_startwork_expire_warning.html", params))
    response_txt = render_to_string("emails/bounty_startwork_expire_warning.txt", params)

    return response_html, response_txt


def render_bounty_unintersted(to_email, bounty, interest):
    params = {
        'bounty': bounty,
        'interest': interest,
		'email_type': 'bounty',
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/bounty_uninterested.html", params))
    response_txt = render_to_string("emails/bounty_uninterested.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expired(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('bounty_startwork_expired'),
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
		'email_type': 'general'
    }

    subject = "Gitcoin: Updated Terms & Policies"
    response_html = premailer_transform(render_to_string("emails/gdpr_update.html", params))
    response_txt = render_to_string("emails/gdpr_update.txt", params)

    return response_html, response_txt, subject


def render_reserved_issue(to_email, user, bounty):
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'user': user,
        'bounty': bounty,
		'email_type': 'bounty'
    }
    subject = "Reserved Issue"
    response_html = premailer_transform(render_to_string("emails/reserved_issue.html", params))
    response_txt = render_to_string("emails/reserved_issue.txt", params)
    return response_html, response_txt, subject


def render_start_work_approved(interest, bounty):
    to_email = interest.profile.email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('start_work_approved'),
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
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('start_work_rejected'),
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
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('start_work_new_applicant'),
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
        'reject_worker_url': bounty.reject_worker_url(interest.profile.handle),
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
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('start_work_applicant_about_to_expire'),
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
        'reject_worker_url': bounty.reject_worker_url(interest.profile.handle),
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
		'email_type': 'bounty',
        'utm_tracking': build_utm_tracking('start_work_applicant_expired'),
        'approve_worker_url': bounty.approve_worker_url(interest.profile.handle),
    }

    subject = "A Worker was Auto Approved"
    response_html = premailer_transform(render_to_string("emails/start_work_applicant_expired.html", params))
    response_txt = render_to_string("emails/start_work_applicant_expired.txt", params)

    return response_html, response_txt, subject


def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty
    from django.conf import settings
    from marketing.models import RoundupEmail
    args = RoundupEmail.objects.order_by('created_on').last()
    hide_dynamic = args.hide_dynamic
    new_kudos_size_px = '300'

    subject = args.subject
    if settings.DEBUG and False:
        # for debugging email styles
        email_style = 2
    else:
        offset = 2
        email_style = (int(timezone.now().strftime("%V")) + offset) % 7

    intro = args.body
    highlights = args.highlights
    sponsor = args.sponsor
    bounties_spec = args.bounties_spec

    num_leadboard_items = 5
    highlight_kudos_ids = []
    num_kudos_to_show = 15

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


    from kudos.models import KudosTransfer, Token
    if highlight_kudos_ids:
        kudos_highlights = KudosTransfer.objects.filter(id__in=highlight_kudos_ids)
    else:
        kudos_highlights = KudosTransfer.objects.exclude(network='mainnet', txid='').order_by('-created_on')[:num_kudos_to_show]

    new_kudos = []
    if args.kudos:
        for requested_kudos in args.kudos:
            try:
                kudos = Token.objects.get(id=requested_kudos['id'])
                kudos.airdrop = requested_kudos.get('airdrop', f'https://gitcoin.co/kudos/{kudos.pk}/')
                new_kudos.append(kudos)
            except Token.DoesNotExist:
                pass


    for key, __ in leaderboard.items():
        leaderboard[key]['items'] = LeaderboardRank.objects.active() \
            .filter(leaderboard=key, product='all').order_by('rank')[0:num_leadboard_items]
    if not len(leaderboard['quarterly_payers']['items']):
        leaderboard = []

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

    params = {
        'intro': intro,
        'intro_txt': strip_double_chars(strip_double_chars(strip_double_chars(strip_html(intro), ' '), "\n"), "\n "),
        'bounties': bounties,
        'leaderboard': leaderboard,
        'invert_footer': False,
        'hide_header': True,
        'highlights': highlights,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'kudos_highlights': kudos_highlights,
        'sponsor': sponsor,
		'email_type': 'roundup',
        'email_style': email_style,
        'hide_dynamic': hide_dynamic,
        'hide_bottom_logo': True,
        'new_kudos': new_kudos,
        'new_kudos_size_px': new_kudos_size_px,
        'videos': args.videos,
        'news': args.news,
        'updates': args.updates,
        'issue': args.issue,
        'release_date': args.release_date
    }

    response_html = premailer_transform(render_to_string("emails/bounty_roundup.html", params))
    response_txt = render_to_string("emails/bounty_roundup.txt", params)

    return response_html, response_txt, subject, args.from_email, args.from_name


# DJANGO REQUESTS

@staff_member_required
def export_data(request):
    from dashboard.models import Profile

    handle = request.GET.get('handle')
    profile = Profile.objects.filter(handle=handle).first()

    response_html, _, _ = render_export_data_email(profile)
    return HttpResponse(response_html)

def export_data_failed(request):
    from dashboard.models import Profile

    handle = request.GET.get('handle')
    profile = Profile.objects.filter(handle=handle).first()

    response_html, _, _ = render_export_data_email_failed(profile)
    return HttpResponse(response_html)


@staff_member_required
def weekly_recap(request):
    response_html, _ = render_weekly_recap("product@gitcoin.co")
    return HttpResponse(response_html)


@staff_member_required
def unread_notification_email_weekly_roundup(request):
    response_html, _, _ = render_unread_notification_email_weekly_roundup('product@gitcoin.co')
    return HttpResponse(response_html)

@staff_member_required
def new_tip(request):
    from dashboard.models import Tip
    tip = Tip.objects.last()
    response_html, _ = render_tip_email(settings.CONTACT_EMAIL, tip, True)

    return HttpResponse(response_html)


@staff_member_required
def new_kudos(request):
    from kudos.models import KudosTransfer
    kudos_transfer = KudosTransfer.objects.first()
    response_html, _ = render_new_kudos_email(settings.CONTACT_EMAIL, kudos_transfer, True)

    return HttpResponse(response_html)


@staff_member_required
def kudos_mint(request):
    from kudos.models import KudosTransfer
    kudos_transfer = KudosTransfer.objects.last()
    response_html, _ = render_kudos_mint_email(settings.CONTACT_EMAIL, kudos_transfer, True)

    return HttpResponse(response_html)


@staff_member_required
def kudos_mkt(request):
    from kudos.models import KudosTransfer
    kudos_transfer = KudosTransfer.objects.last()
    response_html, _ = render_kudos_mkt_email(settings.CONTACT_EMAIL, kudos_transfer, True)

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
        'utm_tracking': build_utm_tracking('resend_tip'),
    }

    if request.POST.get('pk'):
        email = request.POST.get('email')

        if not pk or not email:
            messages.error(request, 'Not sent.  Invalid args.')
            return redirect('/_administration')

        tip = Tip.objects.get(pk=pk)
        try:
            tip.emails = tip.emails + [email]
        except:
            pass
        tip_email(tip, [email], True)
        tip.save()

        messages.success(request, 'Resend sent')

        return redirect('/_administration')

    return TemplateResponse(request, 'resend_tip.html', params)


@staff_member_required
def new_bounty(request):
    from dashboard.models import Bounty
    from marketing.views import quest_of_the_day, upcoming_grant, get_hackathons
    bounties = Bounty.objects.current().order_by('-web3_created')[0:3]
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, bounties, old_bounties='', offset=int(request.GET.get('offset', 2)), quest_of_the_day=quest_of_the_day(), upcoming_grant=upcoming_grant(), hackathons=get_hackathons(), chats_count=7)
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
def comment(request):
    from townsquare.models import Comment
    response_html, _ = render_comment(settings.CONTACT_EMAIL, Comment.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def mention(request):
    from dashboard.models import Activity
    response_html, _ = render_mention(settings.CONTACT_EMAIL, Activity.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def grant_update(request):
    from dashboard.models import Activity
    response_html, _ = render_grant_update(settings.CONTACT_EMAIL, Activity.objects.filter(activity_type='wall_post', grant__isnull=False).last())
    return HttpResponse(response_html)


@staff_member_required
def grant_recontribute(request):
    response_html, _ = render_grant_recontribute(settings.CONTACT_EMAIL)
    return HttpResponse(response_html)


def grant_txn_failed(request):
    failed_contrib = Contribution.objects.filter(subscription__contributor_profile__user__email=settings.CONTACT_EMAIL).exclude(validator_passed=True).first()
    response_html, _ = render_grant_txn_failed(failed_contrib)
    return HttpResponse(response_html)


@staff_member_required
def wallpost(request):
    from dashboard.models import Activity
    response_html, _ = render_wallpost(settings.CONTACT_EMAIL, Activity.objects.filter(activity_type='wall_post').last())
    return HttpResponse(response_html)


@staff_member_required
def new_bounty_acceptance(request):
    from dashboard.models import Bounty
    response_html, _ = render_new_bounty_acceptance(settings.CONTACT_EMAIL, Bounty.objects.last())
    return HttpResponse(response_html)


@staff_member_required
def bounty_feedback(request):
    from dashboard.models import Bounty
    from marketing.common.utils import handle_bounty_feedback

    bounty = Bounty.objects.current().filter(idx_status='done').last()

    (to_fulfiller, to_funder, fulfiller_previous_bounties, funder_previous_bounties) = handle_bounty_feedback(bounty)

    if to_fulfiller:
        response_html, _ = render_bounty_feedback(bounty, 'fulfiller', fulfiller_previous_bounties)
        return HttpResponse(response_html)

    if to_funder:
        response_html, _ = render_bounty_feedback(bounty, 'funder', funder_previous_bounties)
        return HttpResponse(response_html)


@staff_member_required
def funder_payout_reminder(request):
    """Display the funder payment reminder email template.

    Params:
        username (str): The Github username to reference in the email.

    Returns:
        HttpResponse: The HTML version of the templated HTTP response.

    """
    from dashboard.models import Bounty
    bounty = Bounty.objects.filter(fulfillment_submitted_on__isnull=False).first()
    github_username = request.GET.get('username', '@foo')
    response_html, _ = render_funder_payout_reminder(bounty=bounty, github_username=github_username)
    return HttpResponse(response_html)


@staff_member_required
def no_applicant_reminder(request):
    """Display the no applicant for bounty reminder email template.

    Params:
        username (str): The Github username to reference in the email.

    Returns:
        HttpResponse: The HTML version of the templated HTTP response.

    """
    from dashboard.models import Bounty
    bounty = Bounty.objects.filter(
        idx_status='open', current_bounty=True, interested__isnull=True
    ).first()
    response_html, _ = render_no_applicant_reminder(bounty=bounty)
    return HttpResponse(response_html)


@staff_member_required
def grant_match_distribution_final_txn(request):
    from grants.models import CLRMatch
    match = CLRMatch.objects.last()
    response_html, _ = render_grant_match_distribution_final_txn(match)
    return HttpResponse(response_html)


@staff_member_required
def match_distribution(request):
    from townsquare.models import MatchRanking
    mr = MatchRanking.objects.last()
    response_html, _ = render_match_distribution(mr)
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
    username = request.GET.get('username', 'foo')
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


def roundup(request):
    email = request.user.email if request.user.is_authenticated else 'test@123.com'
    response_html, _, _, _, _ = render_new_bounty_roundup(email)
    return HttpResponse(response_html)


@staff_member_required
def quarterly_roundup(request):
    from marketing.common.utils import get_platform_wide_stats
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
def share_bounty(request):
    from dashboard.models import Profile
    handle = request.GET.get('handle')
    profile = Profile.objects.filter(handle=handle).first()
    response_html, _ = render_share_bounty(settings.CONTACT_EMAIL, 'This is a sample message', profile)
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
def request_amount_email(request):
    from dashboard.models import FundRequest
    fr = FundRequest.objects.first()
    response_html, _ = render_request_amount_email('kevin@gitcoin.co', fr, True)
    return HttpResponse(response_html)


@staff_member_required
def start_work_applicant_expired(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_applicant_expired(interest, bounty)
    return HttpResponse(response_html)


@staff_member_required
def tribe_hackathon_prizes(request):
    from dashboard.models import HackathonEvent, Bounty
    from marketing.common.utils import generate_hackathon_email_intro

    hackathon = HackathonEvent.objects.filter(start_date__date=(timezone.now()+timezone.timedelta(days=3))).first()

    if not hackathon:
        return HttpResponse("no upcoming hackathon event in the next 3 days", status=404)

    sponsors_prizes = []
    for sponsor in hackathon.sponsor_profiles.all()[:3]:
        prizes = hackathon.get_current_bounties.filter(bounty_owner_profile=sponsor)
        sponsor_prize = {
            "sponsor": sponsor,
            "prizes": prizes
        }
        sponsors_prizes.append(sponsor_prize)

    intro_begin = generate_hackathon_email_intro(sponsors_prizes)

    response_html, _ = render_tribe_hackathon_prizes(hackathon,sponsors_prizes, intro_begin)
    return HttpResponse(response_html)


def render_remember_your_cart(grants_query, grants, hours):
    params = {
        'base_url': settings.BASE_URL,
        'desc': f'Only left {hours} hours until the end of the match round and seems you have some grants on your cart',
        'cart_query': grants_query,
        'grants': grants
    }

    response_html = premailer_transform(render_to_string("emails/cart.html", params))
    response_txt = render_to_string("emails/cart.txt", params)

    return response_html, response_txt
