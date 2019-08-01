# -*- coding: utf-8 -*-
'''
    Copyright (C) 2019 Gitcoin Core

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
from datetime import date, timedelta
from functools import partial

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
from grants.models import Contribution, Grant, Subscription
from marketing.models import LeaderboardRank
from marketing.utils import get_or_save_email_subscriber
from retail.utils import strip_double_chars, strip_html

logger = logging.getLogger(__name__)

# RENDERERS

# key, name, frequency
MARKETING_EMAILS = [
    ('welcome_mail', _('Welcome Emails'), _('First 3 days after you sign up')),
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
    ('featured_funded_bounty', _('Featured Funded Bounty Emails'), _('Only when you\'ve paid for a bounty to be featured'))
]

ALL_EMAILS = MARKETING_EMAILS + TRANSACTIONAL_EMAILS


def premailer_transform(html):
    cssutils.log.setLevel(logging.CRITICAL)
    p = premailer.Premailer(html, base_url=settings.BASE_URL)
    return p.transform()

def render_featured_funded_bounty(bounty):
    params = {'bounty': bounty}
    response_html = premailer_transform(render_to_string("emails/funded_featured_bounty.html", params))
    response_txt = render_to_string("emails/funded_featured_bounty.txt", params)
    subject = _("Your bounty is now live on Gitcoin!")

    return response_html, response_txt, subject


def render_nth_day_email_campaign(to_email, nth, firstname):
    subject_map = {
        1: "Day 1: Growing Open Source",
        2: "Day 2: Using Gitcoin's Issue Explorer",
        3: "Learning Blockchain"
    }

    subject = subject_map[nth]

    params = {
        "firstname": firstname,
        "subscriber": get_or_save_email_subscriber(to_email, "internal"),
    }
    response_html = premailer_transform(render_to_string(f"emails/campaigns/email_campaign_day_{nth}.html", params))
    response_txt = render_to_string(f"emails/campaigns/email_campaign_day_{nth}.txt", params)

    return response_html, response_txt, subject

def render_new_grant_email(grant):
    params = {'grant': grant}
    response_html = premailer_transform(render_to_string("emails/grants/new_grant.html", params))
    response_txt = render_to_string("emails/grants/new_grant.txt", params)
    subject = _("Your Gitcoin Grant")
    return response_html, response_txt, subject


def render_change_grant_owner_request(grant):
    params = {'grant': grant}
    response_html = premailer_transform(render_to_string("emails/grants/change_owner_request.html", params))
    response_txt = render_to_string("emails/grants/change_owner_request.txt", params)
    subject = _("You've been chosen to be the owner for a Gitcoin Grant")
    return response_html, response_txt, subject


def render_change_grant_owner_accept(grant):
    params = {'grant': grant}
    response_html = premailer_transform(render_to_string("emails/grants/change_owner_accept.html", params))
    response_txt = render_to_string("emails/grants/change_owner_accept.txt", params)
    subject = _("Grant Owner has changed")
    return response_html, response_txt, subject


def render_notify_ownership_change(grant):
    params = {'grant': grant}
    response_html = premailer_transform(render_to_string("emails/grants/change_owner_notify.html", params))
    response_txt = render_to_string("emails/grants/change_owner_notify.txt", params)
    subject = _("Grant ownership has been changed")
    return response_html, response_txt, subject


def render_change_grant_owner_reject(grant):
    params = {'grant': grant}
    response_html = premailer_transform(render_to_string("emails/grants/change_owner_reject.html", params))
    response_txt = render_to_string("emails/grants/change_owner_reject.txt", params)
    subject = _("Grant has no change in ownership")
    return response_html, response_txt, subject


def render_new_supporter_email(grant, subscription):
    params = {'grant': grant, 'subscription': subscription}
    response_html = premailer_transform(render_to_string("emails/grants/new_supporter.html", params))
    response_txt = render_to_string("emails/grants/new_supporter.txt", params)
    subject = _("You have a new Grant supporter!")
    return response_html, response_txt, subject


def render_thank_you_for_supporting_email(grant, subscription):
    params = {'grant': grant, 'subscription': subscription}
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


def render_grant_cancellation_email(grant, subscription):
    params = {'grant': grant, 'subscription': subscription}
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
    params = {'grant': grant, 'subscription': subscription, "contribution": contribution}
    response_html = premailer_transform(render_to_string("emails/grants/successful_contribution.html", params))
    response_txt = render_to_string("emails/grants/successful_contribution.txt", params)
    subject = _('Your Gitcoin Grants contribution was successful!')
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
def subscription_terminated(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    response_html, __, __ = render_subscription_terminated_email(grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def grant_cancellation(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    response_html, __, __ = render_grant_cancellation_email(grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def support_cancellation(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    response_html, __, __ = render_support_cancellation_email(grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def thank_you_for_supporting(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    response_html, __, __ = render_thank_you_for_supporting_email(grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def new_supporter(request):
    grant = Grant.objects.first()
    subscription = Subscription.objects.filter(grant__pk=grant.pk).first()
    response_html, __, __ = render_new_supporter_email(grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def new_grant(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_new_grant_email(grant)
    return HttpResponse(response_html)


@staff_member_required
def change_grant_owner_request(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_change_grant_owner_request(grant)
    return HttpResponse(response_html)


@staff_member_required
def notify_ownership_change(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_notify_ownership_change(grant)
    return HttpResponse(response_html)


@staff_member_required
def change_grant_owner_accept(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_change_grant_owner_accept(grant)
    return HttpResponse(response_html)


@staff_member_required
def change_grant_owner_reject(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_change_grant_owner_reject(grant)
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
    }

    response_html = premailer_transform(render_to_string("emails/new_tip.html", params))
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


def render_funder_payout_reminder(**kwargs):
    kwargs['bounty_fulfillment'] = kwargs['bounty'].fulfillments.filter(fulfiller_github_username=kwargs['github_username']).last()
    response_html = premailer_transform(render_to_string("emails/funder_payout_reminder.html", kwargs))
    response_txt = ''
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

alisa / frank (gitcoin product team)

PS - we've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

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

alisa / frank (gitcoin product team)

PS - we've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

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

alisa / frank (gitcoin product team)

PS - we've got some new gitcoin schwag on order. send me your mailing address and your t shirt size and i'll ship you some.

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

alisa and frank from Gitcoin here (CC scott and vivek too) — i see you haven't funded an issue in {time_as_str}. in the spirit of making Gitcoin better + checking in:

- has anything been slipping on your issue board which might be bounty worthy?
- do you have any feedback for Gitcoin Core on how we might improve the product to fit your needs?

our idea is that gitcoin should be a place you come when priorities stretch long, and you need an extra set of capable hands. curious if this fits what you're looking for these days.

appreciate you being a part of the community and let me know if you'd like some Gitcoin schwag — just send over a mailing address and a t-shirt size and it'll come your way.

~ alisa / frank (gitcoin product team)


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

def render_unread_notification_email_weekly_roundup(to_email, from_date=date.today(), days_ago=7):
    subscriber = get_or_save_email_subscriber(to_email, 'internal')
    from dashboard.models import Profile
    from inbox.models import Notification
    profile = Profile.objects.filter(email__iexact=to_email).last()

    from_date = from_date + timedelta(days=1)
    to_date = from_date - timedelta(days=days_ago)

    notifications = Notification.objects.filter(to_user=profile.id, is_read=False, created_on__range=[to_date, from_date]).count()

    params = {
        'subscriber': subscriber,
        'profile': profile.handle,
        'notifications': notifications,
    }

    subject = "Your unread notifications"

    response_html = premailer_transform(render_to_string("emails/unread_notifications_roundup/unread_notification_email_weekly_roundup.html", params))
    response_txt = render_to_string("emails/unread_notifications_roundup/unread_notification_email_weekly_roundup.txt", params)

    return response_html, response_txt, subject

def render_weekly_recap(to_email, from_date=date.today(), days_back=7):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    from dashboard.models import Profile
    prof = Profile.objects.filter(email__iexact=to_email).last()
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
        'debug': activity_types
    }

    response_html = premailer_transform(render_to_string("emails/recap/weekly_founder_recap.html", params))
    response_txt = render_to_string("emails/recap/weekly_founder_recap.txt", params)

    return response_html, response_txt


def render_gdpr_reconsent(to_email):
    sub = get_or_save_email_subscriber(to_email, 'internal')
    params = {
        'subscriber': sub,
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
        'kudos_invite': kudos_invite
    }
    response_html = premailer_transform(render_to_string("emails/share_bounty_email.html", params))
    response_txt = render_to_string("emails/share_bounty_email.txt", params)
    return response_html, response_txt


def render_new_work_submission(to_email, bounty):
    params = {
        'bounty': bounty,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_work_submission.html", params))
    response_txt = render_to_string("emails/new_work_submission.txt", params)

    return response_html, response_txt


def render_new_bounty_acceptance(to_email, bounty, unrated_count=0):
    params = {
        'bounty': bounty,
        'unrated_count': unrated_count,
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


def render_reserved_issue(to_email, user, bounty):
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'user': user,
        'bounty': bounty
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

def render_new_bounty_roundup(to_email):
    from dashboard.models import Bounty
    from django.conf import settings
    subject = "Hacking, Begin! Grow Ethereum Has Started"
    new_kudos_pks = [2050, 4281, 1970]
    new_kudos_size_px = 150

    kudos_friday = f'''
<h3>Happy Kudos Friday!</h3>
</p>
<p>
''' + "".join([f"<a href='https://gitcoin.co/kudos/{pk}/'><img style='max-width: {new_kudos_size_px}px; display: inline; padding-right: 10px; vertical-align:middle ' src='https://gitcoin.co/dynamic/kudos/{pk}/'></a>" for pk in new_kudos_pks]) + '''
</p>
    '''
    intro = f'''
<p>
Hey Gitcoiners,
</p>
<p>
Grow Ethereum has officially started! After weeks of hype, the hackathon is now upon us. Dozens of bounties from some of the top projects in Ethereum are now live on the Hackathon Issue Explorer. If you aren't already a member, join the Discord to find a team and then get to work! Some of the Hackathon bounties are featured in this email below, but many more are up for grabs. For more information on the prizes, and to take a look at the availabile issues, check out the hackathon homepage <a href="https://hackathons.gitcoin.co/grow-ethereum/" target="_blank">here.</a>
</p>
<p>
Who are the sponsors for Grow Ethereum? This hackathon features a wide range of projects coming from all parts of the ecosystem. Our core sponsors are <a href="https://www.adex.network/">AdEx</a>, <a href="https://bzx.network/">bZx</a>, the <a href="https://ethereum.org/">Ethereum Foundation</a>, <a href="https://www.unicef.org/innovation/blockchain">UNICEF</a>, and <a href="https://www.metacartel.org/">Metacartel</a>. Our node sponsors are <a href="https://www.portis.io/">Portis</a>, <a href="https://fluence.network/">fluence</a>, <a href="https://pegasys.tech/">PegaSys</a>, <a href="https://www.arweave.org/">Arweave</a>, and <a href="https://raiden.network/">Raiden</a>. For more information on each sponsor's bounty offerings, drop by the Discord and find their specific sponsor channel. There, bounties will be posted, and you can ask any questions you may have.
</p>
<p>
Last, we're inching closer to our announcement of the next round of CLR matching for Gitcoin Grants. If you have a project that needs funding, or are a funder that would like to help grow open source, check out the current Gitcoin Grants homepage. We are happy to answer any questions you might have. <a href="https://gitcoin.co/grants/">Grants live here.</a>
</p>
{kudos_friday}
<h3>What else is new?</h3>
    <ul>
        <li>
            The Gitcoin Livestream is back this week! Join us <a href="https://gitcoin.co/livestream"> at 2PM ET this Friday.
        </li>
        <li>
        Looking for something to watch this weekend? Gitcoin Media is about to upload a new wave of past livestreams. Take a look at the existing ones uploaded today and get ready to watch the next ones! Gitcoin Media lives <a href="https://www.youtube.com/gitcoinmedia">here.</a>
        </li>
    </ul>
</p>
<p>
Back to shipping,
</p>
'''
    highlights = [{
        'who': 'KapsonLabs',
        'who_link': True,
        'what': 'Pay Practitioner Implemented!',
        'link': 'https://gitcoin.co/issue/RibbonBlockchain/IncentivesMVP/16/3282',
        'link_copy': 'View more',
    }, {
        'who': 'samsparsky',
        'who_link': True,
        'what': 'Token Buyback for Gnosis.',
        'link': 'https://gitcoin.co/issue/GnosisEcosystemFund/Gnosis-Bounties-/3/1626',
        'link_copy': 'View more',
    }, {
        'who': 'PierrickGT',
        'who_link': True,
        'what': 'The edit button now works.',
        'link': 'https://gitcoin.co/issue/gitcoinco/web/4786/3227',
        'link_copy': 'View more',
    }, ]

    sponsor = {
        'name': 'Quantstamp',
        'title': 'Scan your smart contract with the Quantstamp Security Network V2 today.',
        'image_url': 'https://s3.us-west-2.amazonaws.com/gitcoin-static/jDSk7ZTfpY19PWdwwsk8puNd.png',
        'link': 'http://bit.ly/QStamp',
        'cta': 'Scan now',
        'body': [
            'Reentrancy bu🐜s are easy to miss. Have confidence in your code and integrate security checks as part of your development workflow.🛡'
        ]
    }

    bounties_spec = [{
        'url': 'https://github.com/fluencelabs/Bounties/issues/1',
        'primer': 'Help Build The Real Decentralized Web',
    }, {
        'url': 'https://gitcoin.co/issue/PegaSysEng/BountiedWork/20/3281',
        'primer': 'Stratum Implementation for Pantheon',
    }, {
        'url': 'https://gitcoin.co/issue/fluencelabs/Bounties/2/3291',
        'primer': 'Building REPL to Enable Customizable Decentralized Backends',
}, ]
    
    
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

    from kudos.models import KudosTransfer
    if highlight_kudos_ids:
        kudos_highlights = KudosTransfer.objects.filter(id__in=highlight_kudos_ids)
    else:
        kudos_highlights = KudosTransfer.objects.exclude(network='mainnet', txid='').order_by('-created_on')[:num_kudos_to_show]

    for key, __ in leaderboard.items():
        leaderboard[key]['items'] = LeaderboardRank.objects.active() \
            .filter(leaderboard=key).order_by('rank')[0:num_leadboard_items]
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
        'hide_header': False,
        'highlights': highlights,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'kudos_highlights': kudos_highlights,
        'sponsor': sponsor,
    }

    response_html = premailer_transform(render_to_string("emails/bounty_roundup.html", params))
    response_txt = render_to_string("emails/bounty_roundup.txt", params)

    return response_html, response_txt, subject



# DJANGO REQUESTS


@staff_member_required
def weekly_recap(request):
    response_html, _ = render_weekly_recap("mark.beacom@consensys.net")
    return HttpResponse(response_html)


@staff_member_required
def unread_notification_email_weekly_roundup(request):
    response_html, _ = render_unread_notification_email_weekly_roundup('mark.beacom@consensys.net')
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
def start_work_applicant_expired(request):
    from dashboard.models import Interest, Bounty
    interest = Interest.objects.last()
    bounty = Bounty.objects.last()
    response_html, _, _ = render_start_work_applicant_expired(interest, bounty)
    return HttpResponse(response_html)
