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
    ('new_bounty_notifications', _('Daily Bounty Action Emails'), _('(up to) Daily')),
    ('important_product_updates', _('Product Update Emails'), _('Quarterly')),
	('general', _('General Email Updates'), _('as it comes')),
	('quarterly', _('Quarterly Email Updates'), _('Quarterly')),
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


def render_funder_payout_reminder(**kwargs):
    kwargs['bounty_fulfillment'] = kwargs['bounty'].fulfillments.filter(fulfiller_github_username=kwargs['github_username']).last()
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


def render_new_bounty(to_email, bounties, old_bounties, offset=3, trending_quests=[]):
    from townsquare.utils import is_email_townsquare_enabled, is_there_an_action_available
    email_style = (int(timezone.now().strftime("%-j")) + offset) % 24
    sub = get_or_save_email_subscriber(to_email, 'internal')
    params = {
        'old_bounties': old_bounties,
        'bounties': bounties,
        'subscriber': sub,
        'keywords': ",".join(sub.keywords) if sub and sub.keywords else '',
        'email_style': email_style,
		'email_type': 'new_bounty_notifications',
        'base_url': settings.BASE_URL,
        'show_action': True,
        'trending_quests': trending_quests,
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

    notifications = Notification.objects.filter(to_user=profile.id, is_read=False, created_on__range=[to_date, from_date]).count()

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
    subject = args.subject
    new_kudos_pks = args.kudos_ids.split(',')
    new_kudos_size_px = 150
    if settings.DEBUG and False:
        # for debugging email styles
        email_style = 2
    else:
        offset = 2
        email_style = 27

    kudos_friday = f'''
<h3>New Kudos This Month</h3>
</p>
<p>
<a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcGuw591LiVuDWNcwacQCseM697-2FN7Cs8hLaPLvG1lqJun3dw_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DGH82LNmlW6jYFS3iDc5AR8dy7j3L7Wa3X4GSt7j-2BYqmKjQbVAXo3Ki9qBVXdpVfjj9Ri56AvRT98H6EB4t0epr6FJWLMUvP-2FYoUHNMACW7qGgCAAkW4-2FLiQO4hUuRoKbRLMw5uap9fviiF1iKCsooI23yTUqsWigzoK-2BWMkCNZAZDD5gzbZ2-2BSc5UZFLAtnyahkJqxzu2PAWz3shYV0-2FvrlpwtvhI5emrVqca0tUc8x" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcGuw591LiVuDWNcwacQCseM697-2FN7Cs8hLaPLvG1lqJun3dw_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DGH82LNmlW6jYFS3iDc5AR8dy7j3L7Wa3X4GSt7j-2BYqmKjQbVAXo3Ki9qBVXdpVfjj9Ri56AvRT98H6EB4t0epr6FJWLMUvP-2FYoUHNMACW7qGgCAAkW4-2FLiQO4hUuRoKbRLMw5uap9fviiF1iKCsooI23yTUqsWigzoK-2BWMkCNZAZDD5gzbZ2-2BSc5UZFLAtnyahkJqxzu2PAWz3shYV0-2FvrlpwtvhI5emrVqca0tUc8x&amp;source=gmail&amp;ust=1586984596249000&amp;usg=AFQjCNGi1ILCw6ktN0tYTLP_MYhdBNzv4Q"><img src="https://ci5.googleusercontent.com/proxy/BSTArez13C2mcKUDmLQGaJyiC1pibLCvQHJNAVbnP8lnae7iN-e1lH7SstdZewWKidXQEK2zLgJN_w=s0-d-e1-ft#https://gitcoin.co/dynamic/kudos/11602/" class="CToWUd"></a><a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcGuw591LiVuDWNcwacQCseOb5oHHByPrFZJRwluGnvd46djX_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DGQwCrjpdzlng9XEDT-2BRaCTRWOXMecRJWQUKtCWA8jidrCJJQvtT20KInZsf-2FnvXjk5i-2FW9J-2BuSATrPfAD3EG6djmu1F9Sd00MUaO2qfrYPp2mzB-2BkQaj0KYEYxj1zK-2BlhLlcPLxO318iHpK6evwhZcxUFTzBYJQeve0dtdQ9laE2dkwnos5KiHBIYhC83KaY6jZJRkNYSqQJ3G66soTRPtdj2Rl91C63IxwBJP4QdDc" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcGuw591LiVuDWNcwacQCseOb5oHHByPrFZJRwluGnvd46djX_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DGQwCrjpdzlng9XEDT-2BRaCTRWOXMecRJWQUKtCWA8jidrCJJQvtT20KInZsf-2FnvXjk5i-2FW9J-2BuSATrPfAD3EG6djmu1F9Sd00MUaO2qfrYPp2mzB-2BkQaj0KYEYxj1zK-2BlhLlcPLxO318iHpK6evwhZcxUFTzBYJQeve0dtdQ9laE2dkwnos5KiHBIYhC83KaY6jZJRkNYSqQJ3G66soTRPtdj2Rl91C63IxwBJP4QdDc&amp;source=gmail&amp;ust=1586984596249000&amp;usg=AFQjCNG0veChh_xAg5KKCXw-5ERrb-1xog"><img src="https://ci4.googleusercontent.com/proxy/dSvCLCzQzKLWfVImFZFwgChOOoQ38m6DuukVu_OPBSTPdhUkLRPxL8MEWe2qDeoLxkLgjrtF8dHX=s0-d-e1-ft#https://gitcoin.co/dynamic/kudos/7496/" class="CToWUd"></a><a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcGuw591LiVuDWNcwacQCseMwhgfkTLghKGS-2BI8dJQVbqDVpQ_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DAyTOt7DQ-2BZfgiN3Y6ugsZvNaNjMRMnH9xWv-2B6oSfwhcyw5ahwYcAqf2-2BZNfGK1nOdKfVHmAVMQ52-2FSPMCrisGSdYyhkRf7xdqBsYBrebXrqi-2FUmj2gwjZvpi8EZOZjZSlZqmEuacwGlmcWNSzFHTt5sbPmlMsCAwv2O806ILZA3trqtt8Jgd2aFie1VZsKRZNoQe6WYq5oh5z0LmE88xm92H1uWbmdFDXmhqlY8Ma-2Fo" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcGuw591LiVuDWNcwacQCseMwhgfkTLghKGS-2BI8dJQVbqDVpQ_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DAyTOt7DQ-2BZfgiN3Y6ugsZvNaNjMRMnH9xWv-2B6oSfwhcyw5ahwYcAqf2-2BZNfGK1nOdKfVHmAVMQ52-2FSPMCrisGSdYyhkRf7xdqBsYBrebXrqi-2FUmj2gwjZvpi8EZOZjZSlZqmEuacwGlmcWNSzFHTt5sbPmlMsCAwv2O806ILZA3trqtt8Jgd2aFie1VZsKRZNoQe6WYq5oh5z0LmE88xm92H1uWbmdFDXmhqlY8Ma-2Fo&amp;source=gmail&amp;ust=1586984596249000&amp;usg=AFQjCNFh4DGlmacZcRPxwyJvM6IGHZNtpA"><img src="https://ci3.googleusercontent.com/proxy/ovCZsoJjeRuwhwzwpmSMyXWoDb3CdXyaWsxJP-KbgwlO4jWnbmHeUN7rd23H3sol-9jlEtc_6DTv=s0-d-e1-ft#https://gitcoin.co/dynamic/kudos/1838/" class="CToWUd"></a>
</p>
    '''

    intro = intro = f'''
<p>
    Good day Gitcoiners,
    </p>
    <p>
    Well <span class="il">that</span> <span class="il">was</span> <span class="il">quick</span> - February has been a fast and crazy month. Watching the spread of the SARS-CoV-2 virus and economic uncertainty <span class="il">that</span> follows, we hope everyone in our global community is staying safe and healthy. Now more than ever it’s obvious the future of work will have to be flexible and remote. If you’re feeling isolated, come hang out in the <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcBYNnAPiaPuk3L0S0bOo-2FfWNASCSyl8eRAZTQXnlKOxSxHF9_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DDsLjx8q7mePC-2BiEm0o6bhdQxjV8c-2F-2BYH4YEPB9oTbMax4TSEFRR-2FCZ4i76wmVqwhxy9wRMHf8CXewF4CtMV1Q8-2BWPzGID3G0-2FEUfoSPw-2BNPaWokizpG8h0nGI3drivVzERQ-2BDSqpnOJYuwsIKLCKRYPjzm9pQ1Ab4Trp9bVn4bwRwaAdspzLgwoer-2FsBP55YdMH2ejTrh5NTcUt7gd4dwNd-2FXCymYTqG0Qr-2FBt8ugaY" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcBYNnAPiaPuk3L0S0bOo-2FfWNASCSyl8eRAZTQXnlKOxSxHF9_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DDsLjx8q7mePC-2BiEm0o6bhdQxjV8c-2F-2BYH4YEPB9oTbMax4TSEFRR-2FCZ4i76wmVqwhxy9wRMHf8CXewF4CtMV1Q8-2BWPzGID3G0-2FEUfoSPw-2BNPaWokizpG8h0nGI3drivVzERQ-2BDSqpnOJYuwsIKLCKRYPjzm9pQ1Ab4Trp9bVn4bwRwaAdspzLgwoer-2FsBP55YdMH2ejTrh5NTcUt7gd4dwNd-2FXCymYTqG0Qr-2FBt8ugaY&amp;source=gmail&amp;ust=1586984596247000&amp;usg=AFQjCNF8kplUBHEYBCmoUiv0AB6d_h2ebQ">Town Square</a>, we promise it’s virus free.
    </p>
    <p>
    As we leap Into March, there are plenty of new opportunities for you to earn crypto working for the open internet. First off, the <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcKov-2F6t51IcPDbdpOox2K-2BovhETabJOpFR7uVOuqIXbTphN50yca-2FAnhInshYZ9Cmg-3D-3DI2L9_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DOThImqT9xm38pdDEdsoH4DiIZNhnIUGkw3g0pitzjgkOvJjjznpXxI7VWmBQh54yBo7DXbWE0VCLnP2X7B7hRMibw6Lv7zlZTljao8h22i2pagUuYycLwJk-2BBOjPCOLHv6AOs0iZ9aO4CL3znV-2B8a02hEvlg-2FwNkJd6XosxH8rFoMQvc8uobA4scIdQtjr4wIoPoTAKpW5X2-2F68vODuclFmK1AYGPJtp6GmPUjw9jOc" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcKov-2F6t51IcPDbdpOox2K-2BovhETabJOpFR7uVOuqIXbTphN50yca-2FAnhInshYZ9Cmg-3D-3DI2L9_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DOThImqT9xm38pdDEdsoH4DiIZNhnIUGkw3g0pitzjgkOvJjjznpXxI7VWmBQh54yBo7DXbWE0VCLnP2X7B7hRMibw6Lv7zlZTljao8h22i2pagUuYycLwJk-2BBOjPCOLHv6AOs0iZ9aO4CL3znV-2B8a02hEvlg-2FwNkJd6XosxH8rFoMQvc8uobA4scIdQtjr4wIoPoTAKpW5X2-2F68vODuclFmK1AYGPJtp6GmPUjw9jOc&amp;source=gmail&amp;ust=1586984596247000&amp;usg=AFQjCNHWdzIYjJFEfBCxYA2Na61EZKw17g">Social Impact Incubator</a> is in full swing. Today is the last day to <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5Sid9St-2FexGcujYZhvlYfWiMdtbkBycygJJPbVjqLK8gpmh49b1jdJ6y42Lzk79My4g-3DOTvW_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DCQlOdaHobdzh-2BlBufhgZIIwsHeIz-2Bb7rMS8TQDsLryRwXtJfp-2BXojoDz59bHHrXhFODkYPiQ20VW2aJN3JpqoDRTS5eTgVPbocq1IJ7UKbWsm-2Ba3T-2FvgFY0G4Pp7Do2oyunEgWR76uRN9q9ZQG6CfVbEjyC3o-2BMdw3rh-2Buo00JRTx9RvI7-2F75CIHkxzEWrxCFqaJfCq42z6M6nyxRqt92pXY0Pr6KuARrKWnG7Hnliy" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5Sid9St-2FexGcujYZhvlYfWiMdtbkBycygJJPbVjqLK8gpmh49b1jdJ6y42Lzk79My4g-3DOTvW_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DCQlOdaHobdzh-2BlBufhgZIIwsHeIz-2Bb7rMS8TQDsLryRwXtJfp-2BXojoDz59bHHrXhFODkYPiQ20VW2aJN3JpqoDRTS5eTgVPbocq1IJ7UKbWsm-2Ba3T-2FvgFY0G4Pp7Do2oyunEgWR76uRN9q9ZQG6CfVbEjyC3o-2BMdw3rh-2Buo00JRTx9RvI7-2F75CIHkxzEWrxCFqaJfCq42z6M6nyxRqt92pXY0Pr6KuARrKWnG7Hnliy&amp;source=gmail&amp;ust=1586984596247000&amp;usg=AFQjCNE1RUTOLFkZ4nqm9ZEr9Imsv7gvMw">sign up</a> and find a team, now with <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5SjVag2cmwNKRXQJMSrbRTwqoDxXRzTCOk3swSb8Y1vKg7IR-2FESeU7FiwYOR-2FUu2PFk-3DQoiB_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DA8-2Be9EFY2rCsY4DDdsVIp5-2F52y2OWBHWuGkIMDBSr-2Bvadyr24VE-2B4yOiqllqcC4v9chsai-2BDXEPVX0oAIja59odD92nuLpqQXTaWbDEGxUMuWzPihVGeJZS7C4fXPw6-2BAgzbkXZeqltTqtXL0ohHwlJk24LBFyW9FZwEF9sLzZctxh-2FnI4tGW6ejiKA1BLJpc7mNtQLhw2s-2B4g1oy-2Bpc8-2Fy-2Bhnm6-2BlY-2FMF25Qw5-2BtyC" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5SjVag2cmwNKRXQJMSrbRTwqoDxXRzTCOk3swSb8Y1vKg7IR-2FESeU7FiwYOR-2FUu2PFk-3DQoiB_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DA8-2Be9EFY2rCsY4DDdsVIp5-2F52y2OWBHWuGkIMDBSr-2Bvadyr24VE-2B4yOiqllqcC4v9chsai-2BDXEPVX0oAIja59odD92nuLpqQXTaWbDEGxUMuWzPihVGeJZS7C4fXPw6-2BAgzbkXZeqltTqtXL0ohHwlJk24LBFyW9FZwEF9sLzZctxh-2FnI4tGW6ejiKA1BLJpc7mNtQLhw2s-2B4g1oy-2Bpc8-2Fy-2Bhnm6-2BlY-2FMF25Qw5-2BtyC&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNE9B7EJV3e4HZdw04CDr186GqbtgQ">$40,000</a> up for grabs.
    </p>
    <p>
    Next, the <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK60mSbiY1eiSw8bRR7-2B8XrxNgopTf34wseFqlspQjWwztkxan0qLvM49TKKeB-2FLn8E-3DZmEO_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DKjDRYAwpnenHmirEEiJNBC0Tw4Hcu5lXl4lLoAlnlnk2zluNktBOERQHzDhnKwsO2FklvyJzTPrFU6okfF5YE9-2BnjPhera0uT-2BnyjdqFnDKlane8yl1wJFKvx4UGFj5RyBTb2zxrQVQHWLZBQmvCht205fQhEn9OHR3jGKsVDdoHpdG6SsgY5wevDB0Bfg-2B2PiogB6XM0pyL-2F6i6-2BTZMzuvdcpu3mKX26FXg6o3jlSl" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK60mSbiY1eiSw8bRR7-2B8XrxNgopTf34wseFqlspQjWwztkxan0qLvM49TKKeB-2FLn8E-3DZmEO_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DKjDRYAwpnenHmirEEiJNBC0Tw4Hcu5lXl4lLoAlnlnk2zluNktBOERQHzDhnKwsO2FklvyJzTPrFU6okfF5YE9-2BnjPhera0uT-2BnyjdqFnDKlane8yl1wJFKvx4UGFj5RyBTb2zxrQVQHWLZBQmvCht205fQhEn9OHR3jGKsVDdoHpdG6SsgY5wevDB0Bfg-2B2PiogB6XM0pyL-2F6i6-2BTZMzuvdcpu3mKX26FXg6o3jlSl&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNFnYoFynmNPhRTbL6fyLV7QMXbZyw">Skynet Virtual Hackathon</a> by <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK7HXYAwJXagSrmu2RyqPA1cUYgyfQejLrnmbduRI6RliQ-3D-3D59WT_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DFfJS7CuWC475jVmzM4ILueI6AXZxinPKTnFFOvSYiY6gy7okmu3x7b1uEd-2BOXljzUakvfDzYNfTUsC1HC6PyT59ns-2BDskh-2BbOlJkkpvRsLkVuRHTW7XNGiTDPcqLbSi8TblTKvSr2hvOtpsWQmeDIKD5-2Bh4SGDaFWI4COSSTrb272GlEd2cemvWoVTFMx3TzoSTV5fBRYlKCKP0ARUGltoJjRGqXNwnud2CW2RCwzUP" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK7HXYAwJXagSrmu2RyqPA1cUYgyfQejLrnmbduRI6RliQ-3D-3D59WT_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DFfJS7CuWC475jVmzM4ILueI6AXZxinPKTnFFOvSYiY6gy7okmu3x7b1uEd-2BOXljzUakvfDzYNfTUsC1HC6PyT59ns-2BDskh-2BbOlJkkpvRsLkVuRHTW7XNGiTDPcqLbSi8TblTKvSr2hvOtpsWQmeDIKD5-2Bh4SGDaFWI4COSSTrb272GlEd2cemvWoVTFMx3TzoSTV5fBRYlKCKP0ARUGltoJjRGqXNwnud2CW2RCwzUP&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNFteO8d874pl5zBT3NSmsvP7qD8bg">Sia</a> goes live today! Check out our <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcJS-2BhPgNACVmIQe6-2BU9JhWR7yzeNqtrgMiIo-2FTKOYr7-2FtjNZvQvvOOX2vxhzkWkCeuICPUyh7OAuiHCXXchZ4eWGAwH8mt-2BDkZMx-2FwP5YjGFiZ1l_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DIyUqM95Gv2LZvO6PpAAE-2F-2Bd7-2BFWQ4XVDf7VJHXmmOeQFjmu-2BYp59cBUblwDXJVAgPRjhL6lEOQZjH4C5CaMekDUpXpp1iOd7N1WS-2FNxOgUV6UZmsvCz6ycNglXj9-2FzAApDPLCmzEKlCM0H6HhH7amftyuQk-2FD5j14pMi5zWI-2B-2BMlp5djXcM-2F5FpYFU5HQ0hBext5amPMnb9B9a8-2B5l9l1X4GJlgKZKu3VS6THsB7y02" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcJS-2BhPgNACVmIQe6-2BU9JhWR7yzeNqtrgMiIo-2FTKOYr7-2FtjNZvQvvOOX2vxhzkWkCeuICPUyh7OAuiHCXXchZ4eWGAwH8mt-2BDkZMx-2FwP5YjGFiZ1l_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DIyUqM95Gv2LZvO6PpAAE-2F-2Bd7-2BFWQ4XVDf7VJHXmmOeQFjmu-2BYp59cBUblwDXJVAgPRjhL6lEOQZjH4C5CaMekDUpXpp1iOd7N1WS-2FNxOgUV6UZmsvCz6ycNglXj9-2FzAApDPLCmzEKlCM0H6HhH7amftyuQk-2FD5j14pMi5zWI-2B-2BMlp5djXcM-2F5FpYFU5HQ0hBext5amPMnb9B9a8-2B5l9l1X4GJlgKZKu3VS6THsB7y02&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNE9pPh3vpC1W_K1r_TIAlz6e7BJ5g">blog post</a> to learn more about Skynet and the 1,750,000 SC (~$5k) in prizes. There is even a 25,000 SC consolation prize for all submissions. Join the event  <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5SiTszLX1kQ9Q2nNXd-2BEnIQzLc0a2Yq5u7mfV07dfK-2BZsw-3D-3DlDnV_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DGmHFrZHNdnNvaznByWiZFSdP977x-2F-2BCdaLa1cv08mMGpUg0xvErhZ8DBTk7HK3-2FznULDtL5sYtsmAP9ii7IY40hfwRbEpwxowlg0-2FexYshanvXBOE0ToymNeQLaGm7wA4V2FQggfqQJ08L5QzhnJykhFOrG0usXg5PnRtPRT5hWdrDVhA6TqUYonOsO5JIFqfxROcqrFOVYv-2BkESDaRnzMwkS0Rx5FNzutoDJqSbnGa" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5SiTszLX1kQ9Q2nNXd-2BEnIQzLc0a2Yq5u7mfV07dfK-2BZsw-3D-3DlDnV_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DGmHFrZHNdnNvaznByWiZFSdP977x-2F-2BCdaLa1cv08mMGpUg0xvErhZ8DBTk7HK3-2FznULDtL5sYtsmAP9ii7IY40hfwRbEpwxowlg0-2FexYshanvXBOE0ToymNeQLaGm7wA4V2FQggfqQJ08L5QzhnJykhFOrG0usXg5PnRtPRT5hWdrDVhA6TqUYonOsO5JIFqfxROcqrFOVYv-2BkESDaRnzMwkS0Rx5FNzutoDJqSbnGa&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNEzs2jD3vwvmvQOUOiOVpp7n4H88w">here</a>. If you need some hackathon inspiration, our Global Communities retro post is also live - <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcJS-2BhPgNACVmIQe6-2BU9JhWRRabWKnSa-2BVwXda71rfOHrlOkdPI19NIzY7B23W83x6yJNdLquziNeiJ0NqR4N9-2Bs-3D433c_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DC7Co9VBVNYqZLyLZshX9R2v7yxHxmmwW47q6fgu2O2ioxV0fwLEmjqoMp941Dgr0DRLQeORCNwNk7UtBVEm8Bhl-2FFX3Mc1Mr8jYIpC8WqpwbXZP71hVcV1sFLrQsnSsdRy25zZBKwS24Fa0m6zkXKhEv2TSPLX-2FMr4TmgTpysva5aK8MVbPszbMNvlGqypnIryIrZq46lWFBTPo08cHJgQ3QO9A8klidgPWH7lBO7LL" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcJS-2BhPgNACVmIQe6-2BU9JhWRRabWKnSa-2BVwXda71rfOHrlOkdPI19NIzY7B23W83x6yJNdLquziNeiJ0NqR4N9-2Bs-3D433c_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DC7Co9VBVNYqZLyLZshX9R2v7yxHxmmwW47q6fgu2O2ioxV0fwLEmjqoMp941Dgr0DRLQeORCNwNk7UtBVEm8Bhl-2FFX3Mc1Mr8jYIpC8WqpwbXZP71hVcV1sFLrQsnSsdRy25zZBKwS24Fa0m6zkXKhEv2TSPLX-2FMr4TmgTpysva5aK8MVbPszbMNvlGqypnIryIrZq46lWFBTPo08cHJgQ3QO9A8klidgPWH7lBO7LL&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNFPnoZjoVkKEqGDwB2-3w2GPq4iIg">take a gander here</a>.
    </p>
    <p>
    Finally, March 16th will kick off both the <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5SjArsq6DUbMILhZxYQrG1h2BuRMxVcVPSemONSE4h4ZFPfFuvW1hqgQ5Xe1a7aAom8-3D_33T_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DPGG42UfVW0UNNpqbfHmT8k1YZomI-2BXiqU9Dhbjnn1OacOfvBxOfIq-2F3hwCHnzI0NMuwFct3QSyF62l8aFoB9JFpNZKZsQfQ1Rqgyu8HBnJVQnzhjU2W9AzT-2BYa-2F9RGqwUxEswNkiVZb652PnTu1fPPBVVVz8MK1k-2B1aHWy2lRAZjf-2FFjLHT-2BYhQlgXRILXeSLi26jLcetOhprXbOJhKH-2B5yOSzuL6B8TwcwSQiN5EoW" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcIjV7cIS8H37spNJAopW5SjArsq6DUbMILhZxYQrG1h2BuRMxVcVPSemONSE4h4ZFPfFuvW1hqgQ5Xe1a7aAom8-3D_33T_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DPGG42UfVW0UNNpqbfHmT8k1YZomI-2BXiqU9Dhbjnn1OacOfvBxOfIq-2F3hwCHnzI0NMuwFct3QSyF62l8aFoB9JFpNZKZsQfQ1Rqgyu8HBnJVQnzhjU2W9AzT-2BYa-2F9RGqwUxEswNkiVZb652PnTu1fPPBVVVz8MK1k-2B1aHWy2lRAZjf-2FFjLHT-2BYhQlgXRILXeSLi26jLcetOhprXbOJhKH-2B5yOSzuL6B8TwcwSQiN5EoW&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNGfr6dP8nrHEn0vFZ778oTlvhH3Qg">Funding The Future</a> Virtual Hackathon, alongside <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK60mSbiY1eiSw8bRR7-2B8XrxHtEZN15kGPNtJUBO3neicdr4a-2FNXdivFVnhdmMey1y0-3DmCtC_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DOd6xD-2FmZarWzwbZZfTCp8WnknPxyRQ-2BQ8-2FscG8EFsi8ptuztN2CosQl3OoTTmrN1x6kpjPXmpOVhTE66PuroZ6t42gSHCZIpqPOSFZs5UowcwV-2BncMiU-2Bjb8QjRQ0MLvAXt6q5LlZm-2BLDOCo9k0DSZXZuN8X54V-2Fbpu44c1pp9XgaZYiPvUaCd1f7uTPxoPXigQ09yaJVxPj1Qq3IRRMVuIQix6DiMfhp-2BHtf8VsqDS" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK60mSbiY1eiSw8bRR7-2B8XrxHtEZN15kGPNtJUBO3neicdr4a-2FNXdivFVnhdmMey1y0-3DmCtC_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DOd6xD-2FmZarWzwbZZfTCp8WnknPxyRQ-2BQ8-2FscG8EFsi8ptuztN2CosQl3OoTTmrN1x6kpjPXmpOVhTE66PuroZ6t42gSHCZIpqPOSFZs5UowcwV-2BncMiU-2Bjb8QjRQ0MLvAXt6q5LlZm-2BLDOCo9k0DSZXZuN8X54V-2Fbpu44c1pp9XgaZYiPvUaCd1f7uTPxoPXigQ09yaJVxPj1Qq3IRRMVuIQix6DiMfhp-2BHtf8VsqDS&amp;source=gmail&amp;ust=1586984596248000&amp;usg=AFQjCNEzWxaaPrlqSm9fLvXDVYl0Q6bBpA">Gitcoin Grants</a> Round 5. More to come on those soon.
    </p>
         
    
    <h3>What else is new?</h3><ul><li>
            <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK62-2F27-2FcacQLUzOfGf80CA0gHzxo5VyYmezqsKncf82UYsMrAT7AVA1qbbCJU4uj4k-3D0Uid_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DFcwNWapPUWGg1r13WkD6I41suDFA4bXuUofqpk1ujkFuzWGuRGlawZbwCVG7Hkydbxc9h9e06Q7GcZeAtt4BQi027LfItA7Xnvm6HSbE-2BevcFIvVBOv5DB33T4-2BzIqLvrJ-2FaB6OukmQKSotfK-2FqkrbbViMmhCTb-2F0teTdr4ADa-2F7V4M3chAtbIAiXkKwwhZcN8Ngejx9nEM4MVQtHKghfT7BDczAdOKs3gRWC1W6g7D" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcGR85KFq5Zq28fXFF8c-2FgK62-2F27-2FcacQLUzOfGf80CA0gHzxo5VyYmezqsKncf82UYsMrAT7AVA1qbbCJU4uj4k-3D0Uid_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DFcwNWapPUWGg1r13WkD6I41suDFA4bXuUofqpk1ujkFuzWGuRGlawZbwCVG7Hkydbxc9h9e06Q7GcZeAtt4BQi027LfItA7Xnvm6HSbE-2BevcFIvVBOv5DB33T4-2BzIqLvrJ-2FaB6OukmQKSotfK-2FqkrbbViMmhCTb-2F0teTdr4ADa-2F7V4M3chAtbIAiXkKwwhZcN8Ngejx9nEM4MVQtHKghfT7BDczAdOKs3gRWC1W6g7D&amp;source=gmail&amp;ust=1586984596249000&amp;usg=AFQjCNFfPVYdQvdjoHjdtGi2up0M5exQlw">Join us</a> for the Livestream today as David Vorick, Co-Founder of Sia, speaks to us about the launch of Skynet and the Skynet Hackathon. We’ll start at 2pm ET, so join the conversation and come with questions.
            </li>
    </ul>
    
    <p>
    Back to Chillin and Shillin,
    </p>
    
        <div class="regards">
          <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcG-2BEY9nM2FrZiOy33zRJ5HEZELxdDYuBQ1P9Oj2692qHyVGu_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DOBdsUb-2BO8-2F2T0m-2BGEoueB3ALdpYtptdAGbqKPQRRABBSgwbgmwIuVYuw79uLdzuKrTQWex6ramkt3FqfvFK5or07qElumScapwLaPJYYC2bY1tPDTe1ECBnKufL9951w9FKyPGvAMJ8QPt-2B-2FhYDrrXU7U-2FTRHycI6h8z2YCTet7bij8rusc-2B14s9jeQoffEzXsRcD0nocxqIwhZ2CXH193CwB0jFeAddDK2BNI1hkqD" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcG-2BEY9nM2FrZiOy33zRJ5HEZELxdDYuBQ1P9Oj2692qHyVGu_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DOBdsUb-2BO8-2F2T0m-2BGEoueB3ALdpYtptdAGbqKPQRRABBSgwbgmwIuVYuw79uLdzuKrTQWex6ramkt3FqfvFK5or07qElumScapwLaPJYYC2bY1tPDTe1ECBnKufL9951w9FKyPGvAMJ8QPt-2B-2FhYDrrXU7U-2FTRHycI6h8z2YCTet7bij8rusc-2B14s9jeQoffEzXsRcD0nocxqIwhZ2CXH193CwB0jFeAddDK2BNI1hkqD&amp;source=gmail&amp;ust=1586984596249000&amp;usg=AFQjCNHBdYc71FAZYSAQRJV-NpOlN1CK-g">
            <img src="https://ci6.googleusercontent.com/proxy/DE_o-Hf2tXJJxX7HZJHLK6aOd0F20t194LAdJ4q8RXEiFqRCEn5ixBaES3ywaANr6zVo9xZyJ_K5F5GrtDuACm63-DoKRLC8HPJH4sphRRTv8zo0=s0-d-e1-ft#https://s.gitcoin.co/static/v2/images/connoroday.276030ba5f80.png" class="CToWUd">
            <p>
                <a href="https://u5829119.ct.sendgrid.net/ls/click?upn=JzKZkqL7BQlM7N5Fr31jcG-2BEY9nM2FrZiOy33zRJ5HEZELxdDYuBQ1P9Oj2692qHxrmr_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DIgDwnrXW6-2FuIoA2oYwqFTjziNrp9225xRYf-2BJiITFf9V6U2ZMyw5-2F4eJjNTjqF9e6ZWgnA3fjkyak6tI2BvlqFNHmrmza9DUaS5JI3niKz9hZXmGDAIZcuKGlAiUY0ECDccKbp9CDnhpeetn41CxByzcipER2wzdEAElVq5jb-2BRmf6pElfkHzjz1FjchoDTAWaLTKh-2By7eQGZfVOrJL0fYPC4lFh9vGncUZCMCMDuHw" target="_blank" data-saferedirecturl="https://www.google.com/url?q=https://u5829119.ct.sendgrid.net/ls/click?upn%3DJzKZkqL7BQlM7N5Fr31jcG-2BEY9nM2FrZiOy33zRJ5HEZELxdDYuBQ1P9Oj2692qHxrmr_5zLnBF78PFiWL6TQQilAz27oyL2C0F-2FIQb4jxFPSdKhphqySxhcrrX2kp5efAfttfl0xD2fU65of0HE9amY4DIgDwnrXW6-2FuIoA2oYwqFTjziNrp9225xRYf-2BJiITFf9V6U2ZMyw5-2F4eJjNTjqF9e6ZWgnA3fjkyak6tI2BvlqFNHmrmza9DUaS5JI3niKz9hZXmGDAIZcuKGlAiUY0ECDccKbp9CDnhpeetn41CxByzcipER2wzdEAElVq5jb-2BRmf6pElfkHzjz1FjchoDTAWaLTKh-2By7eQGZfVOrJL0fYPC4lFh9vGncUZCMCMDuHw&amp;source=gmail&amp;ust=1586984596250000&amp;usg=AFQjCNHTToZ6ajb1GffzNcrjMx1MweUGiQ">@connoroday0</a>
            </p>
          </a>
        </div></div>

'''
    highlights = [{
        'who': 'Bobface',
        'who_link': True,
        'what': 'More great work with Austin Griffith!',
        'link': 'https://gitcoin.co/issue/austintgriffith/eth.build/14/4074',
        'link_copy': 'View more',
    }, {
        'who': 'dhaileytaha',
        'who_link': True,
        'what': 'Kudos to the best Infura Community contributor',
        'link': 'https://gitcoin.co/issue/INFURA/infura/198/4066',
        'link_copy': 'View more',
    }, {
        'who': 'developerfred',
        'who_link': True,
        'what': 'Kudos to one of our most active Gitcoiners!',
        'link': 'https://gitcoin.co/issue/gitcoinco/web/6093/4068',
        'link_copy': 'View more',
    }, ]
    sponsor = {
    'name': 'CodeFund',
    'title': 'Does your project need 🦄 developers?',
    'image_url': '',
    'link': 'http://bit.ly/codefund-gitcoin-weekly',
    'cta': 'Learn More',
    'body': [
       'CodeFund is a privacy-focused ethical advertising network (by Gitcoin) that funds open source projects.',
       'We specialize in helping companies connect with talented developers and potential customers on developer-centric sites that typically do not allow ads.'
    ]
}
    bounties_spec = [{
        'url': 'https://github.com/gitcoinco/web/issues/4569',
        'primer': '(1,750,000 SC) - Gitcoin Skynet Hackathon Challenge',
    }, {
        'url': 'https://github.com/gitcoinco/web/issues/4569',
        'primer': '(1,750,000 SC) - Gitcoin Skynet Hackathon Challenge',
    }, {
        'url': 'https://github.com/gitcoinco/web/issues/4569',
        'primer': '(1,750,000 SC) - Gitcoin Skynet Hackathon Challenge',
    }]

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
        'hide_header': False,
        'highlights': highlights,
        'subscriber': get_or_save_email_subscriber(to_email, 'internal'),
        'kudos_highlights': kudos_highlights,
        'sponsor': sponsor,
		'email_type': 'roundup',
        'email_style': email_style,
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
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, bounties, old_bounties, int(request.GET.get('offset', 2)))
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


@staff_member_required
def roundup(request):
    response_html, _, _, _, _ = render_new_bounty_roundup(settings.CONTACT_EMAIL)
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
