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
from grants.models import Contribution, Grant, Subscription
from marketing.models import LeaderboardRank
from marketing.utils import get_or_save_email_subscriber
from premailer import Premailer
from retail.utils import strip_double_chars, strip_html

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
    ('faucet', _('Faucet Notification Emails'), _('Only when you are sent a faucet distribution')),
    ('bounty', _('Bounty Notification Emails'), _('Only when you\'re active on a bounty')),
    ('bounty_match', _('Bounty Match Emails'), _('Only when you\'ve posted a open bounty and you have a new match')),
    ('bounty_feedback', _('Bounty Feedback Emails'), _('Only after a bounty you participated in is finished.')),
    (
        'bounty_expiration', _('Bounty Expiration Warning Emails'),
        _('Only after you posted a bounty which is going to expire')
    ),
    ('featured_funded_bounty', _('Featured Funded Bounty Emails'), _('Only when you\'ve paid for a bounty to be featured')),
    ('comment', _('Comment Emails'), _('Only when you are sent a comment')),
    ('wall_post', _('Wall Post Emails'), _('Only when someone writes on your wall')),
    ('grant_updates', _('Grant Update Emails'), _('Updates from Grant Owners about grants you\'ve funded.')),
    ('grant_txn_failed', _('Grant Transaction Failed Emails'), _('Notifies Grant contributors when their contribution txn has failed.')),
]


NOTIFICATION_EMAILS = [
    ('chat', _('Chat Emails'), _('Only emails from Gitcoin Chat')),
    ('mention', _('Mentions'), _('Only when other users mention you on posts')),
]

ALL_EMAILS = MARKETING_EMAILS + TRANSACTIONAL_EMAILS + NOTIFICATION_EMAILS


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
		"email_type": "welcome_mail"
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
    subscription = Subscription.objects.last()
    response_html, __, __ = render_new_supporter_email(subscription.grant, subscription)
    return HttpResponse(response_html)


@staff_member_required
def new_grant(request):
    grant = Grant.objects.first()
    response_html, __, __ = render_new_grant_email(grant)
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
		'email_type': 'tip'
    }

    response_html = premailer_transform(render_to_string("emails/new_tip.html", params))
    response_txt = render_to_string("emails/new_tip.txt", params)

    return response_html, response_txt


def render_request_amount_email(to_email, request, is_new):

    link = f'{reverse("tip")}?request={request.id}'
    params = {
        'link': link,
        'amount': request.amount,
        'tokenName': request.token_name if request.network == 'ETH' else request.network,
        'address': request.address,
        'comments': request.comments,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'email_type': 'request',
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
    response_html = premailer_transform(render_to_string("emails/funder_payout_reminder.html", kwargs))
    response_txt = ''
    return response_html, response_txt


def render_match_distribution(mr):
    params = {
        'mr': mr,
    }
    response_html = premailer_transform(render_to_string("emails/match_distribution.html"))
    response_txt = ''
    return response_html, response_txt


def render_no_applicant_reminder(bounty):
    params = {
        'bounty': bounty,
        'directory_link': '/users?skills=' + bounty.keywords.lower()
    }
    response_html = premailer_transform(render_to_string("emails/bounty/no_applicant_reminder.html", params))
    response_txt = render_to_string("emails/bounty/no_applicant_reminder.txt", params)
    return response_html, response_txt


def render_bounty_feedback(bounty, persona='submitter', previous_bounties=[]):
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

PS - we've got some new gitcoin schwag on order. if interested, let us know and we can send you a code to order some :)

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

PS - we've got some new gitcoin schwag on order. if interested, let us know and we can send you a code to order some :)

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

alisa and frank from Gitcoin here (CC scott and vivek too) — i see you haven't funded an issue in {time_as_str}.
in the spirit of making Gitcoin better + checking in:

- have any issues which might be bounty worthy or projects you're hoping to build?
- do you have any feedback for Gitcoin Core on how we might improve the product to fit your needs?
- are you interested in joining one of <a href="https://gitcoin.co/hackathon-list/">our upcoming hackathons?</a> it's possible
we could do so at a discount, as you're a current funder on the platform

appreciate you being a part of the community + let us know if you'd like some Gitcoin schwag, we can send a link your way to order some :)

~ alisa / frank (gitcoin product team)


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
        profile = Profile.objects.filter(email__iexact=to_email).last()
    except Profile.DoesNotExist:
        pass
    return profile

def render_new_bounty(to_email, bounties, old_bounties, offset=3, quest_of_the_day={}, upcoming_grant={}, upcoming_hackathon={}, latest_activities={}, from_date=date.today(), days_ago=7, chats_count=0, featured_bounties=[]):
    from townsquare.utils import is_email_townsquare_enabled, is_there_an_action_available
    from marketing.views import upcoming_dates, email_announcements, trending_avatar
    sub = get_or_save_email_subscriber(to_email, 'internal')

    email_style = 26

    # Get notifications count from the Profile.User of to_email
    profile = email_to_profile(to_email)

    notifications_count = get_notification_count(profile, days_ago, from_date)

    upcoming_events = []
    for hackathon in upcoming_hackathon:
        upcoming_events = upcoming_events + [{
            'event': hackathon,
            'title': f"Hackathon Start: {hackathon.name}",
            'image_url': hackathon.logo.url if hackathon.logo else f'{settings.STATIC_URL}v2/images/emails/hackathons-neg.png',
            'url': hackathon.url,
            'date': hackathon.start_date.strftime("%Y-%m-%d")
        }]
    for hackathon in upcoming_hackathon:
        upcoming_events = upcoming_events + [{
            'event': hackathon,
            'title': f"Hackathon End: {hackathon.name}",
            'image_url': hackathon.logo.url if hackathon.logo else f'{settings.STATIC_URL}v2/images/emails/hackathons-neg.png',
            'url': hackathon.url,
            'date': hackathon.end_date.strftime("%Y-%m-%d")
        }]
    for ele in upcoming_dates():
        upcoming_events = upcoming_events + [{
            'event': ele,
            'title': ele.title,
            'image_url': ele.img_url,
            'url': ele.url,
            'date': ele.date.strftime("%Y-%m-%d")
        }]
    upcoming_events = sorted(upcoming_events, key=lambda ele: ele['date'])
    upcoming_events = upcoming_events[0:7]

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
        'base_url': settings.BASE_URL,
        'show_action': True,
        'quest_of_the_day': quest_of_the_day,
        'upcoming_events': upcoming_events,
        'activities': latest_activities,
        'notifications_count': notifications_count,
        'chats_count': chats_count,
        'show_action': is_email_townsquare_enabled(to_email) and is_there_an_action_available()
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
		'email_type': 'bounty'
    }
    response_html = premailer_transform(render_to_string("emails/share_bounty_email.html", params))
    response_txt = render_to_string("emails/share_bounty_email.txt", params)
    return response_html, response_txt


def render_new_work_submission(to_email, bounty):
    params = {
        'bounty': bounty,
		'email_type': 'bounty',
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
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_acceptance.html", params))
    response_txt = render_to_string("emails/new_bounty_acceptance.txt", params)

    return response_html, response_txt


def render_new_bounty_rejection(to_email, bounty):
    params = {
        'bounty': bounty,
        'email_type': 'bounty',
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/new_bounty_rejection.html", params))
    response_txt = render_to_string("emails/new_bounty_rejection.txt", params)

    return response_html, response_txt


def render_comment(to_email, comment):
    params = {
        'comment': comment,
        'email_type': 'comment',
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
        'hide_bottom_logo': True,
    }

    response_html = premailer_transform(render_to_string("emails/grant_txn_failed.html", params))
    response_txt = render_to_string("emails/grant_txn_failed.txt", params)

    return response_html, response_txt

def render_wallpost(to_email, activity):
    params = {
        'activity': activity,
        'email_type': 'wall_post',
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
		'email_type': 'bounty',
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
		'email_type': 'faucet',
        'subscriber': get_or_save_email_subscriber(fr.email, 'internal'),
    }

    response_html = premailer_transform(render_to_string("emails/faucet_request.html", params))
    response_txt = render_to_string("emails/faucet_request.txt", params)

    return response_html, response_txt


def render_bounty_startwork_expired(to_email, bounty, interest, time_delta_days):
    params = {
        'bounty': bounty,
        'interest': interest,
		'email_type': 'bounty',
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


def render_bounty_request(to_email, model, base_url):
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'model': model,
        'base_url': base_url
    }
    subject = _("New Bounty Request")
    response_html = premailer_transform(render_to_string("emails/bounty_request.html", params))
    response_txt = render_to_string("emails/bounty_request.txt", params)
    return response_html, response_txt, subject


def render_start_work_approved(interest, bounty):
    to_email = interest.profile.email
    params = {
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'interest': interest,
        'bounty': bounty,
		'email_type': 'bounty',
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
		'email_type': 'bounty',
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
		'email_type': 'bounty',
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
def weekly_recap(request):
    response_html, _ = render_weekly_recap("mark.beacom@consensys.net")
    return HttpResponse(response_html)


@staff_member_required
def unread_notification_email_weekly_roundup(request):
    response_html, _, _ = render_unread_notification_email_weekly_roundup('sebastian.tharakan97@gmail.com')
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
    from marketing.views import quest_of_the_day, upcoming_grant, upcoming_hackathon, latest_activities
    bounties = Bounty.objects.current().order_by('-web3_created')[0:3]
    old_bounties = Bounty.objects.current().order_by('-web3_created')[0:3]
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, bounties, old_bounties='', offset=int(request.GET.get('offset', 2)), quest_of_the_day=quest_of_the_day(), upcoming_grant=upcoming_grant(), upcoming_hackathon=upcoming_hackathon(), latest_activities=latest_activities(request.user), chats_count=7)
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


def roundup(request):
    email = request.user.email if request.user.is_authenticated else 'test@123.com'
    response_html, _, _, _, _ = render_new_bounty_roundup(email)
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
