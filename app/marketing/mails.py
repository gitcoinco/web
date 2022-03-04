# -*- coding: utf-8 -*-
"""Define the standard marketing email logic.

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

"""
import base64
import datetime
import logging

from django.conf import settings
from django.utils import timezone, translation
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

import sendgrid
from app.utils import get_profiles_from_text
from marketing.utils import allowed_to_send_email, func_name, get_or_save_email_subscriber
from python_http_client.exceptions import HTTPError, UnauthorizedError
from retail.emails import (
    email_to_profile, get_notification_count, render_admin_contact_funder, render_bounty_changed,
    render_bounty_expire_warning, render_bounty_feedback, render_bounty_hypercharged,
    render_bounty_startwork_expire_warning, render_bounty_unintersted, render_comment, render_featured_funded_bounty,
    render_funder_payout_reminder, render_funder_stale, render_gdpr_reconsent, render_gdpr_update,
    render_grant_cancellation_email, render_grant_match_distribution_final_txn, render_grant_recontribute,
    render_grant_txn_failed, render_grant_update, render_match_distribution, render_match_email, render_mention,
    render_new_bounty, render_new_bounty_acceptance, render_new_bounty_rejection, render_new_bounty_roundup,
    render_new_contributions_email, render_new_grant_approved_email, render_new_grant_email, render_new_work_submission,
    render_no_applicant_reminder, render_pending_contribution_email, render_quarterly_stats, render_remember_your_cart,
    render_request_amount_email, render_reserved_issue, render_start_work_applicant_about_to_expire,
    render_start_work_applicant_expired, render_start_work_approved, render_start_work_new_applicant,
    render_start_work_rejected, render_subscription_terminated_email, render_successful_contribution_email,
    render_support_cancellation_email, render_tax_report, render_thank_you_for_supporting_email, render_tip_email,
    render_tribe_hackathon_prizes, render_unread_notification_email_weekly_roundup, render_wallpost,
    render_weekly_recap,
)
from sendgrid.helpers.mail import Attachment, Content, Email, Mail, Personalization
from sendgrid.helpers.stats import Category

logger = logging.getLogger(__name__)


def send_mail(from_email, _to_email, subject, body, html=False,
              from_name="Gitcoin.co", cc_emails=None, categories=None, debug_mode=False, zip_path=None, csv=None):
    """Send email via SendGrid."""
    # make sure this subscriber is saved
    if not settings.SENDGRID_API_KEY:
        logger.warning('No SendGrid API Key set. Not attempting to send email.')
        return

    if categories is None:
        categories = ['default']

    to_email = _to_email
    get_or_save_email_subscriber(to_email, 'internal')

    # setup
    from_name = str(from_name)
    subject = str(subject)
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    from_email = Email(from_email, from_name)
    to_email = Email(to_email)
    contenttype = "text/plain" if not html else "text/html"

    # build content
    content = Content(contenttype, html) if html else Content(contenttype, body)

    # TODO:  A bit of a hidden state change here.  Really confusing when doing development.
    #        Maybe this should be a variable passed into the function the value is set upstream?
    if settings.IS_DEBUG_ENV or debug_mode:
        to_email = Email(settings.CONTACT_EMAIL)  # just to be double secret sure of what were doing in dev
        subject = _("[DEBUG] ") + subject

    mail = Mail(from_email, subject, to_email, content)
    response = None

    # build personalization
    if cc_emails:
        p = Personalization()
        p.add_to(to_email)
        for cc_addr in set(cc_emails):
            cc_addr = Email(cc_addr)
            if settings.IS_DEBUG_ENV:
                cc_addr = to_email
            if cc_addr._email != to_email._email:
                p.add_to(cc_addr)
        mail.add_personalization(p)

    # categories
    for category in categories:
        mail.add_category(Category(category))

    # Zip Attachment
    if zip_path is not None:
        with open(zip_path, 'rb') as f:
            data = f.read()
            f.close()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.content = encoded
        attachment.type = 'application/zip'
        attachment.filename = 'tax_report.zip'
        attachment.disposition = 'attachment'
        mail.add_attachment(attachment)

    if csv is not None:
        with open(csv, 'rb') as f:
            data = f.read()
            f.close()
        encoded = base64.b64encode(data).decode()
        attachment = Attachment()
        attachment.content = encoded
        attachment.type = 'text/csv'
        attachment.filename = csv.replace('/tmp/', '')
        attachment.disposition = 'attachment'
        mail.add_attachment(attachment)
    # debug logs
    logger.info(f"-- Sending Mail '{subject}' to {to_email.email}")
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except UnauthorizedError as e:
        logger.debug(
            f'-- Sendgrid Mail failure - {_to_email} / {categories} - Unauthorized - Check sendgrid credentials')
        logger.debug(e)
    except HTTPError as e:
        logger.debug(f'-- Sendgrid Mail failure - {_to_email} / {categories} - {e}')

    return response


def validate_email(email):

    import re
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):
        return True
    return False

def get_bounties_for_keywords(keywords, hours_back):
    from dashboard.models import Bounty
    new_bounties_pks = []
    all_bounties_pks = []

    new_bounty_cutoff = (timezone.now() - timezone.timedelta(hours=hours_back))
    all_bounty_cutoff = (timezone.now() - timezone.timedelta(days=60))

    for keyword in keywords:
        relevant_bounties = Bounty.objects.current().filter(
            network='mainnet',
            idx_status__in=['open'],
        ).keyword(keyword).exclude(bounty_reserved_for_user__isnull=False)
        for bounty in relevant_bounties.filter(web3_created__gt=new_bounty_cutoff):
            new_bounties_pks.append(bounty.pk)
        for bounty in relevant_bounties.filter(web3_created__gt=all_bounty_cutoff):
            all_bounties_pks.append(bounty.pk)
    new_bounties = Bounty.objects.filter(pk__in=new_bounties_pks).order_by('-_val_usd_db')
    all_bounties = Bounty.objects.filter(pk__in=all_bounties_pks).exclude(pk__in=new_bounties_pks).order_by('-_val_usd_db')

    new_bounties = new_bounties.order_by('-admin_mark_as_remarket_ready')
    all_bounties = all_bounties.order_by('-admin_mark_as_remarket_ready')

    return new_bounties, all_bounties


def featured_funded_bounty(from_email, bounty):
    to_email = bounty.bounty_owner_email
    if not to_email:
        if bounty.bounty_owner_profile:
            to_email = bounty.bounty_owner_profile.email
    if not to_email:
        if bounty.bounty_owner_profile and bounty.bounty_owner_profile.user:
            to_email = bounty.bounty_owner_profile.user.email
    if not to_email:
        return

    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_featured_funded_bounty(bounty)

        if allowed_to_send_email(to_email, 'featured_funded_bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def new_grant_flag_admin(flag):
    from_email = settings.CONTACT_EMAIL
    to_email = 'new-grants@gitcoin.co'

    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        subject = _("New Grant Flag")
        body = f"{flag.comments} : {settings.BASE_URL}{flag.admin_url}"
        if allowed_to_send_email(to_email, 'new_grant_flag_admin'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def new_grant(grant, profile):
    from_email = settings.CONTACT_EMAIL
    to_email = profile.email
    if not to_email:
        if profile and profile.user:
            to_email = profile.user.email
    if not to_email:
        return

    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_new_grant_email(grant)

        if allowed_to_send_email(to_email, 'new_grant'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def new_grant_approved(grant, profile):
    from_email = settings.CONTACT_EMAIL
    to_email = profile.email
    if not to_email:
        if profile and profile.user:
            to_email = profile.user.email
    if not to_email:
        return

    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_new_grant_approved_email(grant)

        if allowed_to_send_email(to_email, 'new_grant_approved'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def new_contributions(grant):
    from_email = settings.CONTACT_EMAIL
    to_email = grant.admin_profile.email
    if not to_email:
        if grant.admin_profile:
            to_email = grant.admin_profile.email
        else:
            return
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_new_contributions_email(grant)

        if allowed_to_send_email(to_email, 'new_contributions') and subject:
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def thank_you_for_supporting(grants_with_subscription):
    positive_subscriptions = list(filter(lambda gws: not gws["subscription"].negative, grants_with_subscription))
    if len(positive_subscriptions) == 0:
        return

    from_email = settings.CONTACT_EMAIL
    to_email = positive_subscriptions[0]["subscription"].contributor_profile.email
    if not to_email:
        to_email = positive_subscriptions[0]["subscription"].contributor_profile.user.email

    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_thank_you_for_supporting_email(grants_with_subscription)

        if allowed_to_send_email(to_email, 'thank_you_for_supporting'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def support_cancellation(grant, subscription):
    if subscription and subscription.negative:
        return
    from_email = settings.CONTACT_EMAIL
    to_email = subscription.contributor_profile.email
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_support_cancellation_email(grant, subscription)

        if allowed_to_send_email(to_email, 'support_cancellation'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def grant_cancellation(grant):
    from_email = settings.CONTACT_EMAIL
    to_email = grant.admin_profile.email
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_grant_cancellation_email(grant)

        if allowed_to_send_email(to_email, 'grant_cancellation'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def grant_txn_failed(failed_contrib):
    profile, grant, tx_id = failed_contrib.subscription.contributor_profile, failed_contrib.subscription.grant, failed_contrib.tx_id

    from_email = settings.CONTACT_EMAIL
    to_email = profile.email
    if not to_email:
        to_email = profile.email
    if not to_email:
        return

    cur_language = translation.get_language()

    subject = f"Your Grant transaction failed. Wanna try again?"

    try:
        setup_lang(to_email)
        html, text = render_grant_txn_failed(failed_contrib)
        send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)

def subscription_terminated(grant, subscription):
    if subscription and subscription.negative:
        return
    from_email = settings.CONTACT_EMAIL
    to_email = subscription.contributor_profile.email
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_subscription_terminated_email(grant, subscription)

        if allowed_to_send_email(to_email, 'subscription_terminated'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def successful_contribution(grant, subscription, contribution):
    if subscription and subscription.negative:
        return
    from_email = settings.CONTACT_EMAIL
    to_email = subscription.contributor_profile.email
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_successful_contribution_email(grant, subscription, contribution)

        if allowed_to_send_email(to_email, 'successful_contribution'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def pending_contribution(contribution):
    from_email = settings.CONTACT_EMAIL
    to_email = contribution.subscription.contributor_profile.email
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_pending_contribution_email(contribution)

        if allowed_to_send_email(to_email, 'pending_contribution'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def admin_contact_funder(bounty, text, from_user):
    from_email = from_user.email
    to_email = bounty.bounty_owner_email
    if not to_email:
        if bounty.bounty_owner_profile:
            to_email = bounty.bounty_owner_profile.email
    if not to_email:
        if bounty.bounty_owner_profile and bounty.bounty_owner_profile.user:
            to_email = bounty.bounty_owner_profile.user.email
    if not to_email:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)

        subject = bounty.url
        __, text = render_admin_contact_funder(bounty, text, from_user)
        cc_emails = [from_email]
        if allowed_to_send_email(to_email, 'admin_contact_funder'):
            send_mail(
                from_email,
                to_email,
                subject,
                text,
                cc_emails=cc_emails,
                from_name=from_email,
                categories=['transactional', func_name()],
            )
    finally:
        translation.activate(cur_language)


def funder_stale(to_email, github_username, days=30, time_as_str='about a month'):
    from_email = 'product@gitcoin.co'
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)

        subject = "hey from gitcoin.co" if not github_username else f"hey @{github_username}"
        __, text = render_funder_stale(github_username, days, time_as_str)
        cc_emails = []
        if allowed_to_send_email(to_email, 'admin_contact_funder'):
            send_mail(
                from_email,
                to_email,
                subject,
                text,
                cc_emails=cc_emails,
                from_name=from_email,
                categories=['transactional', func_name()],
            )
    finally:
        translation.activate(cur_language)


def bounty_feedback(bounty, persona='fulfiller', previous_bounties=None):
    from_email = 'product@gitcoin.co'
    to_email = None
    cur_language = translation.get_language()
    if previous_bounties is None:
        previous_bounties = []

    try:
        setup_lang(to_email)
        if persona == 'fulfiller':
            accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
            to_email = accepted_fulfillments.first().fulfiller_email if accepted_fulfillments.exists() else ""
        elif persona == 'funder':
            to_email = bounty.bounty_owner_email
            if not to_email:
                if bounty.bounty_owner_profile:
                    to_email = bounty.bounty_owner_profile.email
            if not to_email:
                if bounty.bounty_owner_profile and bounty.bounty_owner_profile.user:
                    to_email = bounty.bounty_owner_profile.user.email
        if not to_email:
            return

        subject = bounty.github_url
        html, text = render_bounty_feedback(bounty, persona, previous_bounties)
        cc_emails = [from_email, 'product@gitcoin.co']
        if allowed_to_send_email(to_email, 'bounty_feedback'):
            send_mail(
                from_email,
                to_email,
                subject,
                text,
                html,
                cc_emails=cc_emails,
                from_name="Gitcoin Product Team",
                categories=['transactional', func_name()],
            )
    finally:
        translation.activate(cur_language)


def tip_email(tip, to_emails, is_new):
    round_decimals = 5
    if not tip or not tip.txid or not tip.amount or not tip.tokenName:
        return

    warning = '' if tip.network == 'mainnet' else "({})".format(tip.network)
    subject = gettext("⚡️ New Tip Worth {} {} {}").format(round(tip.amount, round_decimals), warning, tip.tokenName)
    if not is_new:
        subject = gettext("🕐 Tip Worth {} {} {} Expiring Soon").format(round(tip.amount, round_decimals), warning,
                                                                        tip.tokenName)

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_tip_email(to_email, tip, is_new)

            if allowed_to_send_email(to_email, 'tip'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def comment_email(comment):

    subject = gettext("💬 New Comment")

    cur_language = translation.get_language()
    to_emails = list(comment.activity.comments.values_list('profile__email', flat=True))
    to_emails.append(comment.activity.profile.email)
    if comment.activity.other_profile:
        to_emails.append(comment.activity.other_profile.email)
    to_emails = set([e for e in to_emails if e != comment.profile.email])
    for to_email in to_emails:
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_comment(to_email, comment)

            if allowed_to_send_email(to_email, 'comment'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            pass
    translation.activate(cur_language)
    print(f"sent comment email to {len(to_emails)}")

    emails = get_profiles_from_text(comment.comment).values_list('email', flat=True)
    mentioned_emails = set(emails)
    # Don't send emails again to users who already received a comment email
    deduped_emails = mentioned_emails.difference(to_emails)
    print(f"sent mention email to {len(deduped_emails)}")
    mention_email(comment, deduped_emails)


def mention_email(post, to_emails):
    subject = gettext("💬 @{} mentioned you in a post").format(post.profile.handle)
    cur_language = translation.get_language()

    for to_email in to_emails:
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_mention(to_email, post)

            if allowed_to_send_email(to_email, 'mention'):
                send_mail(from_email, to_email, subject, text, html, categories=['notification', func_name()])
        except Exception as e:
            logger.error('Status Update error - Error: (%s) - Handle: (%s)', e, to_email)

    translation.activate(cur_language)


def tip_comment_awarded_email(post, to_emails):
    subject = gettext("🏆 @{} has awarded you.").format(post.profile.handle)
    cur_language = translation.get_language()

    for to_email in to_emails:
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_mention(to_email, post)

            if allowed_to_send_email(to_email, 'mention'):
                send_mail(from_email, to_email, subject, text, html, categories=['notification', func_name()])
        except Exception as e:
            logger.error('Status Update error - Error: (%s) - Handle: (%s)', e, to_email)
    translation.activate(cur_language)


def wall_post_email(activity):

    to_emails = []
    what = ''
    if activity.what == 'profile':
        to_emails.append(activity.other_profile.email)
        what = f"@{activity.other_profile.handle}"
    if activity.what == 'kudos':
        what = activity.kudos.ui_name
        pass
    if activity.what == 'grant':
        what = activity.grant.title
        for tm in activity.grant.team_members.all():
            to_emails.append(tm.email)
    subject = f"💬 New Wall Post on {what}'s wall"

    cur_language = translation.get_language()
    for to_email in to_emails:
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_wallpost(to_email, activity)

            if allowed_to_send_email(to_email, 'wall_post'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            pass
    translation.activate(cur_language)

def grant_recontribute(profile, prev_round_start, prev_round_end, next_round, next_round_start, next_round_end, match_pool):
    from_email = settings.CONTACT_EMAIL
    to_email = profile.email
    if not to_email:
        if profile and profile.user:
            to_email = profile.user.email
    if not to_email:
        return

    cur_language = translation.get_language()

    subject = f"Grants CLR Round {next_round} Is Here! Fund the grants you supported last round"

    try:
        setup_lang(to_email)
        html, text = render_grant_recontribute(to_email, prev_round_start, prev_round_end, next_round, next_round_start, next_round_end, match_pool)
        send_mail(from_email, to_email, subject, text, html, categories=['marketing', func_name()])
    finally:
        translation.activate(cur_language)

def grant_update_email(activity):

    what = activity.grant.title
    subject = f"📣 Message from @{activity.profile.handle} of Gitcoin Grant: {what}"
    to_emails = list(set([profile.email for profile in activity.grant.contributors if profile.pk not in activity.grant.metadata.get('unsubscribed_profiles', [])]))
    cur_language = translation.get_language()
    for to_email in to_emails:
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_grant_update(to_email, activity)

            if allowed_to_send_email(to_email, 'grant_updates'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            pass
    translation.activate(cur_language)


def new_grant_admin(grant):
    to_emails = ['new-grants@gitcoin.co']
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    for to_email in to_emails:
        try:
            setup_lang(to_email)
            subject = _("New Grant Request")
            body_str = _("A new grant request was completed. You may respond to the request here")
            body = f"{body_str}: {settings.BASE_URL}{grant.admin_url}"
            if allowed_to_send_email(to_email, 'grant'):
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    body,
                    from_name=_("No Reply from Gitcoin.co"),
                    categories=['admin', func_name()],
                )
        finally:
            translation.activate(cur_language)


def notion_failure_email(grant):
    to_emails = ['new-grants@gitcoin.co']
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    for to_email in to_emails:
        try:
            setup_lang(to_email)
            subject = _("Failed to write grant to notions db")
            body_str = _("The following grant failed to be written to notions db, please manually add it")
            body = f'{body_str}:\n\nTitle: "{grant.title}"\nURL: "{settings.BASE_URL.rstrip("/")}{grant.url}"'
            if allowed_to_send_email(to_email, 'grant'):
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    body,
                    from_name=_("No Reply from Gitcoin.co"),
                    categories=['admin', func_name()],
                )
        finally:
            translation.activate(cur_language)


def send_user_feedback(quest, feedback, user):
    to_email = quest.creator.email
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = f"Your Gitcoin Quest \"{quest.title}\" has feedback from another user!"
        body_str = f"Your quest: {quest.title} has feedback from user {user.profile.handle}:\n\n{feedback}\n\nto edit your quest, click <a href=\"{quest.edit_url}\">here</a>"
        body = f"{body_str}"
        if allowed_to_send_email(to_email, 'quest'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=f"@{user.profile.handle} on gitcoin.co",
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def new_quest_request(quest, is_edit):
    to_email = "support@gitcoin.co"
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New Quest Request" if not is_edit else "Quest Edited")
        action = 'created' if not is_edit else 'edited'
        body_str = f"The quest '{quest.title}' has been {action}"
        body = f"{body_str}: {settings.BASE_URL}{quest.admin_url}"
        if allowed_to_send_email(to_email, 'quest'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def new_action_request(action):
    to_email = "support@gitcoin.co"
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New Action Request")
        body_str = f"The action '{action.title}' has been created"
        body = f"{body_str}: {settings.BASE_URL}{action.admin_url}"
        if allowed_to_send_email(to_email, 'action'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def new_quest_approved(quest):
    to_email = quest.creator.email
    from_email = settings.PERSONAL_CONTACT_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("Your Quest is live on Gitcoin.co/quests")
        body_str = _("Your quest has been approved and is now live at")
        body = f"{body_str}: {settings.BASE_URL}{quest.url}"
        if allowed_to_send_email(to_email, 'quest'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def new_token_request(obj):
    to_email = "support@gitcoin.co"
    from_email = obj.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New Token Request")
        body_str = _("A new token request was completed. You may fund the token request here")
        body = f"{body_str}: https://gitcoin.co/{obj.admin_url} \n\n {obj.email}"
        send_mail(
            from_email,
            to_email,
            subject,
            body,
            from_name=_("No Reply from Gitcoin.co"),
            categories=['admin', func_name()],
        )
    finally:
        translation.activate(cur_language)


def new_token_request_approved(obj):
    to_email = obj.metadata.get('email')
    from_email = 'support@gitcoin.co'
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = f"Token {obj.symbol} approved on Gitcoin"
        body = f"Token {obj.symbol} approved on Gitcoin -- You will now see it available in the (1) settings area (2) bounty posting form (3) grant funding form (4) tipping form and (5) anywhere else tokens are listed on Gitcoin. "
        send_mail(
            from_email,
            to_email,
            subject,
            body,
            from_name=_("No Reply from Gitcoin.co"),
            categories=['admin', func_name()],
        )
    finally:
        translation.activate(cur_language)


def notify_deadbeat_quest(quest):
    to_email = 'support@gitcoin.co'
    from_email = to_email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("Dead Quest Alert")
        body = f"This quest is dead ({quest.title}): https://gitcoin.co/{quest.admin_url} "
        if allowed_to_send_email(to_email, 'quest'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def notify_kudos_minted(token_request):
    to_email = token_request.profile.email
    from_email = 'support@gitcoin.co'
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("Kudos has been minted")
        body = f"Your kudos '{token_request.name}' has been minted and should be available on https://gitcoin.co/kudos/marketplace soon."
        if allowed_to_send_email(to_email, 'kudos'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def notify_kudos_rejected(token_request):
    to_email = token_request.profile.email
    from_email = 'support@gitcoin.co'
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("Kudos has been rejected")
        body = f"Your kudos '{token_request.name}', with the file {token_request.artwork_url} has been rejected.  The reason stated was '{token_request.rejection_reason}.  \n\n You can resubmit the token request at https://gitcoin.co/kudos/new "
        if allowed_to_send_email(to_email, 'kudos'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("Admin at Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def notify_deadbeat_grants(grants):
    to_email = 'support@gitcoin.co'
    from_email = to_email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = f"Dead Grants Alert {grants.count()}"
        body = "\n\n-".join([f"({grant.title}): https://gitcoin.co/{grant.admin_url} " for grant in grants])
        if allowed_to_send_email(to_email, 'sdeadbeat'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def new_kudos_request(obj):
    to_email = 'support@gitcoin.co'
    from_email = obj.profile.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New Kudos Request")
        body_str = _("A new kudos request was completed. You may approve the kudos request here")
        body = f"{body_str}: https://gitcoin.co/{obj.admin_url} \n\n {obj.profile.email}"
        if allowed_to_send_email(to_email, 'kudos'):
            send_mail(
                from_email,
                to_email,
                subject,
                body,
                from_name=_("No Reply from Gitcoin.co"),
                categories=['admin', func_name()],
            )
    finally:
        translation.activate(cur_language)


def warn_account_out_of_eth(account, balance, denomination):
    to_email = settings.PERSONAL_CONTACT_EMAIL
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = account + str(_(" is out of gas"))
        body_str = _("is down to ")
        body = f"{account} {body_str} {balance} {denomination}"
        send_mail(
            from_email,
            to_email,
            subject,
            body,
            from_name=_("No Reply from Gitcoin.co"),
            categories=['admin', func_name()],
        )
    finally:
        translation.activate(cur_language)


def new_feedback(email, feedback):
    to_email = 'product@gitcoin.co'
    from_email = settings.SERVER_EMAIL
    subject = "New Feedback"
    body = f"New feedback from {email}: {feedback}"
    send_mail(
        from_email,
        to_email,
        subject,
        body,
        from_name="No Reply from Gitcoin.co",
        categories=['admin', func_name()],
    )


def gdpr_reconsent(email):
    to_email = email
    from_email = settings.PERSONAL_CONTACT_EMAIL
    subject = "Would you still like to receive email from Gitcoin?"
    html, text = render_gdpr_reconsent(to_email)
    send_mail(
        from_email,
        to_email,
        subject,
        text,
        html,
        from_name="Kevin Owocki (Gitcoin.co)",
        categories=['marketing', func_name()],
    )


def funder_payout_reminder(to_email, bounty, github_username, live):
    from_email = "support@gitcoin.co"
    subject = "Payout reminder"
    html, text = render_funder_payout_reminder(to_email=to_email, bounty=bounty, github_username=github_username)
    if (live):
        try:
            send_mail(
                from_email,
                to_email,
                subject,
                text,
                html,
                from_name="Kevin Owocki (Gitcoin.co)",
                categories=['marketing', func_name()],
            )
        except Exception as e:
            logger.warning(e)
            return False
        return True
    else:
        return html


def grant_match_distribution_kyc(match):
    to_email = match.grant.admin_profile.email
    cc_emails = [profile.email for profile in match.grant.team_members.all()]
    from_email = 'kyc@gitcoin.co'
    cur_language = translation.get_language()
    rounded_amount = round(match.amount, 2)
    token_name = f"CLR{match.round_number}"
    try:
        setup_lang(to_email)
        subject = f"💰 (ACTION REQUIRED) Grants Round {match.round_number} Match Distribution: {rounded_amount} DAI"
        body = f"""
<pre>
Hello @{match.grant.admin_profile.handle},

This email is in regards to your Gitcoin Grants Round {match.round_number} payout of {rounded_amount} DAI for https://gitcoin.co{match.grant.get_absolute_url()}.

We are required by law to collect the following information from you.  Please respond to this email (or contact us at @gitcoin_verify on Keybase) with the following information.

For persons:
- Full Name
- Physical Address
- (Only if you’re a US Citizen) Social Security Number
- Proof of physical address (utility bill, or bank statement)
- Proof of identity (government issued ID)

For corporations:
- Corporation Legal Name
- Physical Address
- Proof of physical address (utility bill, or bank statement)
- Proof of Incorporation

Thanks,
Gitcoin Grants KYC Team
</pre>

        """
        send_mail(
            from_email,
            to_email,
            subject,
            '',
            body,
            from_name=_("Gitcoin Grants"),
            cc_emails=cc_emails,
            categories=['admin', func_name()],
        )
    finally:
        translation.activate(cur_language)


def grant_more_info_required(grant, more_info):
    to_email = grant.admin_profile.email
    cc_emails = [profile.email for profile in grant.team_members.all()]
    from_email = 'new-grants@gitcoin.co'
    cc_emails.append(from_email)
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = f"More Info Requested for {grant.url}"
        body = f"""
<pre>
Hello @{grant.admin_profile.handle},

This email is in regards to your Gitcoin Grant: {grant.url}

We require more information to approve your application. {more_info}

Thanks,
Gitcoin Grant Team
</pre>

        """
        send_mail(
            from_email,
            to_email,
            subject,
            '',
            body,
            from_name=_("Gitcoin Grants"),
            cc_emails=cc_emails,
            categories=['admin', func_name()],
        )
    finally:
        translation.activate(cur_language)


def grant_match_distribution_final_txn(match, needs_claimed=False):
    to_email = match.grant.admin_profile.email
    cc_emails = [profile.email for profile in match.grant.team_members.all()]
    from_email = 'support@gitcoin.co'
    cur_language = translation.get_language()
    rounded_amount = round(match.amount, 2)
    try:
        setup_lang(to_email)
        subject = f"🎉 Your Match Distribution of {rounded_amount} DAI has been sent! 🎉"
        if needs_claimed:
            subject = f"💰ACTION REQUIRED - Your Grants Round {match.round_number} Distribution of {rounded_amount} DAI"

        html, text = render_grant_match_distribution_final_txn(match)

        send_mail(
            from_email,
            to_email,
            subject,
            text,
            html,
            from_name=_("Gitcoin Grants"),
            cc_emails=cc_emails,
            categories=['admin', func_name()],
        )
    except Exception as e:
        logger.warning(e)
    finally:
        translation.activate(cur_language)


def match_distribution(mr):
    from_email = "support@gitcoin.co"
    to_email = mr.profile.email
    subject = f"Match Distribution of ${mr.match_total} for @{mr.profile.handle}"
    html, text = render_match_distribution(mr)
    try:
        send_mail(
            from_email,
            to_email,
            subject,
            text,
            html,
            from_name="Gitcoin",
            categories=['marketing', func_name()],
        )
    except Exception as e:
        logger.warning(e)
        return False
    return html


def no_applicant_reminder(to_email, bounty):
    from_email = settings.SERVER_EMAIL
    subject = "Get more applicants on your bounty"
    html, text = render_no_applicant_reminder(bounty=bounty)
    try:
        send_mail(
            from_email,
            to_email,
            subject,
            text,
            html,
            from_name="No Reply from Gitcoin.co",
            categories=['marketing', func_name()],
        )
    except Exception as e:
        logger.warning(e)
        return False
    return True


def share_bounty(emails, msg, profile, invite_url=None, kudos_invite=False):
    from dashboard.tasks import bounty_emails
    # attempt to delay bounty_emails task to a worker
    # long on failure to queue
    try:
        bounty_emails.delay(emails, msg, profile.handle, invite_url, kudos_invite)
    except Exception as e:
        logger.error(str(e))


def new_reserved_issue(from_email, user, bounty):
    to_email = user.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_reserved_issue(to_email, user, bounty)

        if allowed_to_send_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def new_bounty_daily(es):
    from dashboard.models import Bounty
    to_email = es.email
    keywords = es.keywords
    bounties, old_bounties = get_bounties_for_keywords(keywords, 24)
    max_bounties = 5
    if len(bounties) > max_bounties:
        bounties = bounties[0:max_bounties]

    # fallback from tag matching
    if not bounties:
        bounties = Bounty.objects.current().filter(
            network='mainnet',
            idx_status__in=['open'],
            web3_created__gt=timezone.now() - timezone.timedelta(hours=24),
        ).exclude(bounty_reserved_for_user__isnull=False).order_by('-_val_usd_db')[0:3]

    to_emails = [to_email]

    from townsquare.utils import is_email_townsquare_enabled
    from marketing.views import quest_of_the_day, upcoming_grant, get_hackathons, upcoming_dates, upcoming_dates, email_announcements
    quest = quest_of_the_day()
    grant = upcoming_grant()
    hackathons = get_hackathons()
    dates = hackathons[0] + hackathons[1] + list(upcoming_dates())
    announcements = email_announcements()
    town_square_enabled = is_email_townsquare_enabled(to_email)
    should_send = (len(bounties) > 0) or town_square_enabled
    if not should_send:
        return False

    offers = f""
    if to_emails:
        offers = ""

        profile = email_to_profile(to_emails[0])
        notifications = get_notification_count(profile, 7, timezone.now())
        if notifications:
            plural = 's' if notifications > 1 else ''
            notifications = f"💬 {notifications} Notification{plural}"
        else:
            notifications = ''

        new_bounties = ""
        if bounties:
            plural_bounties = "Bounties" if len(bounties)>1 else "Bounty"
            new_bounties = f"💰{len(bounties)} {plural_bounties}"
        elif old_bounties:
            plural_old_bounties = "Bounties" if len(old_bounties)>1 else "Bounty"
            new_bounties = f"💰{len(old_bounties)} {plural_old_bounties}"

        new_quests = ""
        if quest:
            new_quests = f"🎯1 Quest"

        new_dates = ""
        if dates:
            plural_dates = "Events" if len(dates)>1 else "Event"
            new_dates = f"🛠📆{len(dates)} {plural_dates}"

        new_announcements = ""
        if announcements:
            plural = "Announcement"
            new_announcements = f"📣 1 {plural}"

        def comma(a):
            return ", " if a and (new_bounties or new_quests or new_dates or new_announcements or notifications) else ""

        subject = f"{notifications}{comma(notifications)}{new_announcements}{comma(new_announcements)}{new_bounties}{comma(new_bounties)}{new_dates}{comma(new_dates)}{new_quests}{comma(new_quests)}{offers}"

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL

            html, text = render_new_bounty(to_email, bounties, old_bounties='', quest_of_the_day=quest, upcoming_grant=grant, hackathons=get_hackathons())

            if allowed_to_send_email(to_email, 'new_bounty_notifications'):
                send_mail(from_email, to_email, subject, text, html, categories=['marketing', func_name()])
        finally:
            translation.activate(cur_language)
    return True


def weekly_roundup(to_emails=None):
    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            html, text, subject, from_email, from_name = render_new_bounty_roundup(to_email)

            if not html:
                print("no content")
                return

            if allowed_to_send_email(to_email, 'roundup'):
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name=from_name,
                    categories=['marketing', func_name()],
                )
            else:
                print('supressed')
        finally:
            translation.activate(cur_language)


def weekly_recap(to_emails=None):
    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            html, text, subject = render_weekly_recap(to_email)
            from_email = settings.PERSONAL_CONTACT_EMAIL

            if allowed_to_send_email(to_email, 'weeklyrecap'):
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name="Kevin Owocki (Gitcoin.co)",
                    categories=['marketing', func_name()],
                )
            else:
                print('supressed')
        finally:
            translation.activate(cur_language)


def unread_notification_email_weekly_roundup(to_emails=None):
    if to_emails is None:
        to_emails = []

    cur_language = translation.get_language()
    for to_email in to_emails:
        try:
            setup_lang(to_email)
            html, text, subject = render_unread_notification_email_weekly_roundup(to_email)
            from_email = settings.PERSONAL_CONTACT_EMAIL

            if allowed_to_send_email(to_email, 'weeklyrecap'):
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name="Kevin Owocki (Gitcoin.co)",
                    categories=['marketing', func_name()],
                )
            else:
                print('supressed')
        finally:
            translation.activate(cur_language)


def gdpr_update(to_emails=None):
    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            html, text, subject = render_gdpr_update(to_email)
            from_email = settings.PERSONAL_CONTACT_EMAIL

            if allowed_to_send_email(to_email, 'roundup'):
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name="Kevin Owocki (Gitcoin.co)",
                    categories=['marketing', func_name()],
                )
        finally:
            translation.activate(cur_language)


def new_work_submission(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt_now:
        return

    if to_emails is None:
        to_emails = []

    subject = gettext("✉️ New Work Submission Inside for {} ✉️").format(bounty.title_or_desc)

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_new_work_submission(to_email, bounty)

            if allowed_to_send_email(to_email, 'bounty'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def new_bounty_rejection(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt_now:
        return

    subject = gettext("😕 Work Submission Rejected for {} 😕").format(bounty.title_or_desc)

    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_new_bounty_rejection(to_email, bounty)

            if allowed_to_send_email(to_email, 'bounty'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def new_bounty_acceptance(bounty, to_emails=None):
    from dashboard.models import Profile
    from dashboard.utils import get_unrated_bounties_count
    if not bounty or not bounty.value_in_usdt_now:
        return

    if to_emails is None:
        to_emails = []

    subject = gettext("🌈 Funds Paid for {} 🌈").format(bounty.title_or_desc)

    for to_email in to_emails:
        cur_language = translation.get_language()
        profile = Profile.objects.filter(email=to_email).first()
        unrated_count = get_unrated_bounties_count(profile)
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_new_bounty_acceptance(to_email, bounty, unrated_count)

            if allowed_to_send_email(to_email, 'bounty'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def bounty_changed(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt_now:
        return

    subject = gettext("Bounty Details Changed for {}").format(bounty.title_or_desc)

    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_bounty_changed(to_email, bounty)

            if allowed_to_send_email(to_email, 'bounty'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def bounty_hypercharged(bounty, to_emails=None):
    subject = gettext("We selected a bounty for you")

    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_bounty_hypercharged(to_email, bounty)

            if allowed_to_send_email(to_email, 'bounty'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)

def new_match(to_emails, bounty, github_username):
    subject = gettext("⚡️ {} Meet {}: {}! ").format(github_username.title(), bounty.org_name.title(), bounty.title)

    to_email = to_emails[0]
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        from_email = settings.CONTACT_EMAIL
        html, text = render_match_email(bounty, github_username)
        if allowed_to_send_email(to_email, 'bounty_match'):
            send_mail(
                from_email,
                to_email,
                subject,
                text,
                html,
                cc_emails=to_emails,
                categories=['transactional', func_name()],
            )
    finally:
        translation.activate(cur_language)


def quarterly_stats(to_emails=None, platform_wide_stats=None):
    if not platform_wide_stats:
        return

    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            then = (timezone.now() - timezone.timedelta(days=45))
            quarter = int(then.month / 3) + 1
            year = then.year
            date = f"Q{quarter} {year}"
            subject = f"Your Quarterly Gitcoin Stats ({date})"
            html, text = render_quarterly_stats(to_email, platform_wide_stats)
            from_email = settings.PERSONAL_CONTACT_EMAIL

            if allowed_to_send_email(to_email, 'roundup'):
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name="Kevin Owocki (Gitcoin.co)",
                    categories=['marketing', func_name()],
                )
        finally:
            translation.activate(cur_language)


def tax_report(to_emails=None, zip_paths=None, tax_year=None):
    if to_emails is None:
        to_emails = []
    if zip_paths is None:
        zip_paths = []
    if tax_year is None:
        # retrieve last year
        tax_year = datetime.date.today().year-1
    for idx, to_email in enumerate(to_emails):
        if to_email:
            cur_language = translation.get_language()
            try:
                setup_lang(to_email)
                subject = f"Your tax report for year ({tax_year})"
                html, text = render_tax_report(to_email, tax_year)
                from_email = settings.CONTACT_EMAIL
                send_mail(
                    from_email,
                    to_email,
                    subject,
                    text,
                    html,
                    from_name="Kevin Owocki (Gitcoin.co)",
                    categories=['marketing', func_name()],
                    zip_path=zip_paths[idx]
                )
            finally:
                translation.activate(cur_language)


def bounty_expire_warning(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt_now:
        return

    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            unit = _('day')
            num = int(round((bounty.expires_date - timezone.now()).days, 0))
            if num == 0:
                unit = _('hour')
                num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))
            unit = unit + ("s" if num != 1 else "")
            subject = gettext("😕 Your Funded Issue ({}) Expires In {} {} ... 😕").format(bounty.title_or_desc, num,
                                                                                          unit)

            from_email = settings.CONTACT_EMAIL
            html, text = render_bounty_expire_warning(to_email, bounty)

            if allowed_to_send_email(to_email, 'bounty_expiration'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days):
    if not bounty or not bounty.value_in_usdt_now:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        from_email = settings.CONTACT_EMAIL
        html, text = render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days)
        subject = gettext("Are you still working on '{}' ? ").format(bounty.title_or_desc)

        if allowed_to_send_email(to_email, 'bounty_expiration'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def bounty_startwork_expired(to_email, bounty, interest, time_delta_days):
    if not bounty or not bounty.value_in_usdt_now:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        from_email = settings.CONTACT_EMAIL
        html, text = render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days)
        subject = gettext("We've removed you from the task: '{}' ? ").format(bounty.title_or_desc)

        if allowed_to_send_email(to_email, 'bounty_expiration'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def bounty_uninterested(to_email, bounty, interest):
    from_email = settings.CONTACT_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text = render_bounty_unintersted(to_email, bounty, interest)
        subject = "Funder has removed you from the task: '{}' ? ".format(bounty.title_or_desc)

        if allowed_to_send_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_approved(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = interest.profile.email
    if not to_email:
        if interest.profile and interest.profile.user:
            to_email = interest.profile.user.email
    if not to_email:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_approved(interest, bounty)

        if allowed_to_send_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_rejected(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = interest.profile.email
    if not to_email:
        if interest.profile and interest.profile.user:
            to_email = interest.profile.user.email
    if not to_email:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_rejected(interest, bounty)

        if allowed_to_send_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_new_applicant(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = bounty.bounty_owner_email
    if not to_email:
        if bounty.bounty_owner_profile:
            to_email = bounty.bounty_owner_profile.email
    if not to_email:
        if bounty.bounty_owner_profile and bounty.bounty_owner_profile.user:
            to_email = bounty.bounty_owner_profile.user.email
    if not to_email:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_new_applicant(interest, bounty)

        if allowed_to_send_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_applicant_about_to_expire(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = bounty.bounty_owner_email
    if not to_email:
        if bounty.bounty_owner_profile:
            to_email = bounty.bounty_owner_profile.email
    if not to_email:
        if bounty.bounty_owner_profile and bounty.bounty_owner_profile.user:
            to_email = bounty.bounty_owner_profile.user.email
    if not to_email:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_applicant_about_to_expire(interest, bounty)

        if allowed_to_send_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_applicant_expired(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = bounty.bounty_owner_email
    if not to_email:
        if bounty.bounty_owner_profile:
            to_email = bounty.bounty_owner_profile.email
    if not to_email:
        if bounty.bounty_owner_profile and bounty.bounty_owner_profile.user:
            to_email = bounty.bounty_owner_profile.user.email
    if not to_email:
        return
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_applicant_expired(interest, bounty)

        if allowed_to_send_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def setup_lang(to_email):
    """Activate the User's language preferences based on their email address.

    Args:
        to_email (str): The email address to lookup language preferences for.

    """
    from django.contrib.auth.models import User
    user = None

    try:
        user = User.objects.select_related('profile').get(email=to_email)
    except User.MultipleObjectsReturned:
        user = User.objects.select_related('profile').filter(email=to_email).first()
    except User.DoesNotExist:
        print("Could not determine recipient preferred email, using default.")

    if user and hasattr(user, 'profile'):
        preferred_language = user.profile.get_profile_preferred_language()
        translation.activate(preferred_language)


def new_funding_limit_increase_request(profile, cleaned_data):
    to_email = 'support@gitcoin.co'
    from_email = profile.email or settings.SERVER_EMAIL
    cur_language = translation.get_language()
    usdt_per_tx = cleaned_data.get('usdt_per_tx', 0)
    usdt_per_week = cleaned_data.get('usdt_per_week', 0)
    comment = cleaned_data.get('comment', '')
    accept_link = f'{settings.BASE_URL}requestincrease?' \
        f'profile_pk={profile.pk}&' \
        f'usdt_per_tx={usdt_per_tx}&' \
        f'usdt_per_week={usdt_per_week}'

    try:
        setup_lang(to_email)
        subject = _('New Funding Limit Increase Request')
        body = f'New Funding Limit Request from {profile} ({profile.absolute_url}).\n\n' \
            f'New Limit in USD per Transaction: {usdt_per_tx}\n' \
            f'New Limit in USD per Week: {usdt_per_week}\n\n' \
            f'To accept the Funding Limit, visit: {accept_link}\n' \
            f'Administration Link: ({settings.BASE_URL}_administrationdashboard/profile/' \
            f'{profile.pk}/change/#id_max_tip_amount_usdt_per_tx)\n\n' \
            f'Comment:\n{comment}'

        send_mail(from_email, to_email, subject, body, from_name=_("No Reply from Gitcoin.co"))
    finally:
        translation.activate(cur_language)


def bounty_request_feedback(profile):
    from_email = 'product@gitcoin.co'
    to_email = profile.email
    if not to_email:
        if profile and profile.user:
            to_email = profile.user.email
    if not to_email:
        return
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        subject = _(f'Bounty Request Feedback, @{profile.username} <> Gitcoin')
        body = f'Howdy @{profile.username},\n\n' \
            'This is the Product Team from Gitcoin. ' \
            'We noticed you requested a bounty ' \
            'a few months ago and just wanted to check in. ' \
            'How\'d it go? Any feedback for us?\n\n' \
            'Let us know if you have any bounties in your near future ' \
            '-- we\'ll pay attention to ' \
            'Gitcoin Requests (https://gitcoin.co/requests/) ' \
            'from you as we know you\'ve suggested good things ' \
            'in the past 🙂\n\n' \
            'Best,\n\nThe Product Team'

        send_mail(
            from_email,
            to_email,
            subject,
            body,
            from_name=_('Gitcoin Product Team (Gitcoin.co)'),
        )
    finally:
        translation.activate(cur_language)


def fund_request_email(request, to_emails, is_new=False):
    token_name = request.token_name if request.network == 'ETH' else request.network
    subject = gettext("🕐 New Request funds from {} ({} {})").format(request.requester.handle,
                                                                     request.amount,
                                                                     token_name)
    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = request.requester.email
            from_name = f"@{request.requester.handle} on Gitcoin.co"
            html, text = render_request_amount_email(to_email, request, is_new)

            if allowed_to_send_email(to_email, 'tip'):
                send_mail(from_email, to_email, subject, text, html, from_name=from_name, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def remember_your_cart(profile, cart_query, grants, hours):
    to_email = profile.email
    from_email = settings.CONTACT_EMAIL

    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = f"⏱{hours} hours left 🛒 Your grant cart is waiting for you 🛒"
        html, text = render_remember_your_cart(cart_query, grants, hours)

        if allowed_to_send_email(to_email, 'grant_updates'):
            send_mail(from_email, to_email, subject, text, html, categories=['marketing', func_name()])
    finally:
        translation.activate(cur_language)

def tribe_hackathon_prizes(hackathon):
    from dashboard.models import TribeMember, Sponsor
    from marketing.utils import generate_hackathon_email_intro

    sponsors = hackathon.sponsor_profiles.all()
    tribe_members_in_sponsors = TribeMember.objects.filter(org__in=[sponsor for sponsor in sponsors]).exclude(status='rejected').exclude(profile__user=None).only('profile')

    for tribe_member in tribe_members_in_sponsors.distinct('profile'):
        # Get all records of this tribe_member for each sponsor he is a member of
        tribe_member_records = tribe_members_in_sponsors.filter(profile=tribe_member.profile)

        sponsors_prizes = []
        for sponsor in sponsors:
            if sponsor in [tribe_member_record.org for tribe_member_record in tribe_member_records]:
                prizes = hackathon.get_current_bounties.filter(bounty_owner_profile=sponsor)
                sponsor_prize = {
                    "sponsor": sponsor,
                    "prizes": prizes
                }
                sponsors_prizes.append(sponsor_prize)

        subject_begin = generate_hackathon_email_intro(sponsors_prizes)
        subject = f"{subject_begin} participating in {hackathon.name} on Gitcoin 🚀"

        try:
            html, text = render_tribe_hackathon_prizes(hackathon, sponsors_prizes, subject_begin)
        except:
            return

        profile = tribe_member.profile
        to_email = profile.email
        from_email = settings.CONTACT_EMAIL
        if not to_email:
            if profile and profile.user:
                to_email = profile.user.email
        if not to_email:
            continue

        cur_language = translation.get_language()

        try:
            setup_lang(to_email)
            send_mail(from_email, to_email, subject, text, html, categories=['marketing', func_name()])
        finally:
            translation.activate(cur_language)
