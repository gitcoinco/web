# -*- coding: utf-8 -*-
"""Define the standard marketing email logic.

Copyright (C) 2018 Gitcoin Core

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
from django.conf import settings
from django.utils import timezone, translation
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

import sendgrid
from marketing.utils import func_name, get_or_save_email_subscriber, should_suppress_notification_email
from python_http_client.exceptions import HTTPError, UnauthorizedError
from retail.emails import (
    render_admin_contact_funder, render_bounty_changed, render_bounty_expire_warning, render_bounty_feedback,
    render_bounty_startwork_expire_warning, render_bounty_unintersted, render_faucet_rejected, render_faucet_request,
    render_funder_stale, render_gdpr_reconsent, render_gdpr_update, render_match_email, render_new_bounty,
    render_new_bounty_acceptance, render_new_bounty_rejection, render_new_bounty_roundup, render_new_work_submission,
    render_quarterly_stats, render_start_work_applicant_about_to_expire, render_start_work_applicant_expired,
    render_start_work_approved, render_start_work_new_applicant, render_start_work_rejected, render_tip_email,
)
from sendgrid.helpers.mail import Content, Email, Mail, Personalization
from sendgrid.helpers.stats import Category


def send_mail(from_email, _to_email, subject, body, html=False,
              from_name="Gitcoin.co", cc_emails=None, categories=None):
    """Send email via SendGrid."""
    # make sure this subscriber is saved
    if not settings.SENDGRID_API_KEY:
        print('No SendGrid API Key set. Not attempting to send email.')
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
    if settings.IS_DEBUG_ENV:
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

    # debug logs
    print(f"-- Sending Mail '{subject}' to {_to_email}")

    # send mails
    try:
        response = sg.client.mail.send.post(request_body=mail.get())
    except UnauthorizedError:
        print(f'-- Sendgrid Mail failure - Unauthorized - Check sendgrid credentials')
    except HTTPError as e:
        print(f'-- Sendgrid Mail failure - {e}')

    return response


def admin_contact_funder(bounty, text, from_user):
    from_email = from_user.email
    to_email = bounty.bounty_owner_email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)

        subject = bounty.url
        __, text = render_admin_contact_funder(bounty, text, from_user)
        cc_emails = [from_email]
        if not should_suppress_notification_email(to_email, 'admin_contact_funder'):
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
    from_email = settings.PERSONAL_CONTACT_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)

        subject = "hey from gitcoin.co" if not github_username else f"hey @{github_username}"
        __, text = render_funder_stale(github_username, days, time_as_str)
        cc_emails = [from_email, 'vivek.singh@consensys.net', 'scott.moore@consensys.net', 'alisa.march@consensys.net']
        if not should_suppress_notification_email(to_email, 'admin_contact_funder'):
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
    from_email = settings.PERSONAL_CONTACT_EMAIL
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

        subject = bounty.github_url
        __, text = render_bounty_feedback(bounty, persona, previous_bounties)
        cc_emails = [from_email, 'team@gitcoin.co']
        if not should_suppress_notification_email(to_email, 'bounty_feedback'):
            send_mail(
                from_email,
                to_email,
                subject,
                text,
                cc_emails=cc_emails,
                from_name="Kevin Owocki (Gitcoin.co)",
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
        subject = gettext("🕐 Tip Worth {} {} {} Expiring Soon").format(round(tip.amount, round_decimals), warning, tip.tokenName)

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_tip_email(to_email, tip, is_new)

            if not should_suppress_notification_email(to_email, 'tip'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def new_faucet_request(fr):
    to_email = settings.PERSONAL_CONTACT_EMAIL
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New Faucet Request")
        body_str = _("A new faucet request was completed. You may fund the request here")
        body = f"{body_str}: https://gitcoin.co/_administration/process_faucet_request/{fr.pk}"
        if not should_suppress_notification_email(to_email, 'faucet'):
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
    to_email = 'founders@gitcoin.co'
    from_email = obj.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New Token Request")
        body_str = _("A new token request was completed. You may fund the token request here")
        body = f"{body_str}: https://gitcoin.co/{obj.admin_url} \n\n {obj.email}"
        if not should_suppress_notification_email(to_email, 'faucet'):
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
        body = f"{account } {body_str} {balance} {denomination}"
        if not should_suppress_notification_email(to_email, 'admin'):
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
    to_email = settings.PERSONAL_CONTACT_EMAIL
    from_email = settings.SERVER_EMAIL
    subject = "New Feedback"
    body = f"New feedback from {email}: {feedback}"
    if not should_suppress_notification_email(to_email, 'admin'):
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


def new_external_bounty():
    """Send a new external bounty email notification."""
    to_email = settings.PERSONAL_CONTACT_EMAIL
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New External Bounty")
        body = f"https://gitcoin.co/_administrationexternal_bounties/externalbounty"
        if not should_suppress_notification_email(to_email, 'admin'):
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


def processed_faucet_request(fr):
    from_email = settings.SERVER_EMAIL
    subject = _("Faucet Request Processed")
    to_email = fr.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text = render_faucet_request(fr)

        if not should_suppress_notification_email(to_email, 'faucet'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def reject_faucet_request(fr):
    from_email = settings.SERVER_EMAIL
    subject = _("Faucet Request Rejected")
    to_email = fr.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text = render_faucet_rejected(fr)
        if not should_suppress_notification_email(to_email, 'faucet'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def new_bounty_daily(bounties, old_bounties, to_emails=None):
    if not bounties:
        return
    max_bounties = 10
    if len(bounties) > max_bounties:
        bounties = bounties[0:max_bounties]
    if to_emails is None:
        to_emails = []
    plural = "s" if len(bounties) != 1 else ""
    worth = round(sum([bounty.value_in_usdt for bounty in bounties if bounty.value_in_usdt]), 2)
    worth = f" worth ${worth}" if worth else ""
    subject = _(f"⚡️  {len(bounties)} New Open Funded Issue{plural}{worth} matching your profile")

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_new_bounty(to_email, bounties, old_bounties)

            if not should_suppress_notification_email(to_email, 'new_bounty_notifications'):
                send_mail(from_email, to_email, subject, text, html, categories=['marketing', func_name()])
        finally:
            translation.activate(cur_language)


def weekly_roundup(to_emails=None):
    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            html, text, subject = render_new_bounty_roundup(to_email)
            from_email = settings.PERSONAL_CONTACT_EMAIL

            if not should_suppress_notification_email(to_email, 'roundup'):
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

            if not should_suppress_notification_email(to_email, 'roundup'):
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

            if not should_suppress_notification_email(to_email, 'bounty'):
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

            if not should_suppress_notification_email(to_email, 'bounty'):
                send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
        finally:
            translation.activate(cur_language)


def new_bounty_acceptance(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt_now:
        return

    if to_emails is None:
        to_emails = []

    subject = gettext("🌈 Funds Paid for {} 🌈").format(bounty.title_or_desc)

    for to_email in to_emails:
        cur_language = translation.get_language()
        try:
            setup_lang(to_email)
            from_email = settings.CONTACT_EMAIL
            html, text = render_new_bounty_acceptance(to_email, bounty)

            if not should_suppress_notification_email(to_email, 'bounty'):
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

            if not should_suppress_notification_email(to_email, 'bounty'):
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
        if not should_suppress_notification_email(to_email, 'bounty_match'):
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

            if not should_suppress_notification_email(to_email, 'roundup'):
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
            subject = gettext("😕 Your Funded Issue ({}) Expires In {} {} ... 😕").format(bounty.title_or_desc, num, unit)

            from_email = settings.CONTACT_EMAIL
            html, text = render_bounty_expire_warning(to_email, bounty)

            if not should_suppress_notification_email(to_email, 'bounty_expiration'):
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

        if not should_suppress_notification_email(to_email, 'bounty_expiration'):
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

        if not should_suppress_notification_email(to_email, 'bounty_expiration'):
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

        if not should_suppress_notification_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_approved(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = interest.profile.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_approved(interest, bounty)

        if not should_suppress_notification_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_rejected(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = interest.profile.email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_rejected(interest, bounty)

        if not should_suppress_notification_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_new_applicant(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = bounty.bounty_owner_email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_new_applicant(interest, bounty)

        if not should_suppress_notification_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_applicant_about_to_expire(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = bounty.bounty_owner_email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_applicant_about_to_expire(interest, bounty)

        if not should_suppress_notification_email(to_email, 'bounty'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def start_work_applicant_expired(interest, bounty):
    from_email = settings.CONTACT_EMAIL
    to_email = bounty.bounty_owner_email
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        html, text, subject = render_start_work_applicant_expired(interest, bounty)

        if not should_suppress_notification_email(to_email, 'bounty'):
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


def new_bounty_request(model):
    to_email = 'vivek.singh@consensys.net'
    from_email = model.requested_by.email or settings.SERVER_EMAIL
    cur_language = translation.get_language()
    try:
        setup_lang(to_email)
        subject = _("New Bounty Request")
        body_str = _("New Bounty Request from")
        body = f"{body_str} {model.requested_by}: "\
            f"{settings.BASE_URL}_administrationbounty_requests/bountyrequest/{model.pk}/change"
        send_mail(
            from_email,
            to_email,
            subject,
            body,
            from_name=_("No Reply from Gitcoin.co"),
            categories=['admin', 'new_bounty_request'],
        )
    finally:
        translation.activate(cur_language)


def new_funding_limit_increase_request(profile, cleaned_data):
    to_email = 'founders@gitcoin.co'
    from_email = profile.email or settings.SERVER_EMAIL
    cur_language = translation.get_language()
    usdt_per_tx = cleaned_data.get('usdt_per_tx', 0)
    usdt_per_week = cleaned_data.get('usdt_per_week', 0)
    comment = cleaned_data.get('comment', '')
    accept_link = f'{settings.BASE_URL}requestincrease?'\
                  f'profile_pk={profile.pk}&'\
                  f'usdt_per_tx={usdt_per_tx}&'\
                  f'usdt_per_week={usdt_per_week}'

    try:
        setup_lang(to_email)
        subject = _('New Funding Limit Increase Request')
        body = f'New Funding Limit Request from {profile} ({profile.absolute_url}).\n\n'\
               f'New Limit in USD per Transaction: {usdt_per_tx}\n'\
               f'New Limit in USD per Week: {usdt_per_week}\n\n'\
               f'To accept the Funding Limit, visit: {accept_link}\n'\
               f'Administration Link: ({settings.BASE_URL}_administrationdashboard/profile/'\
               f'{profile.pk}/change/#id_max_tip_amount_usdt_per_tx)\n\n'\
               f'Comment:\n{comment}'

        send_mail(from_email, to_email, subject, body, from_name=_("No Reply from Gitcoin.co"))
    finally:
        translation.activate(cur_language)
