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
from django.utils import timezone

import sendgrid
from economy.utils import convert_token_to_usdt
from marketing.utils import get_or_save_email_subscriber, should_suppress_notification_email
from python_http_client.exceptions import HTTPError, UnauthorizedError
from retail.emails import (
    render_bounty_expire_warning, render_bounty_feedback, render_bounty_startwork_expire_warning,
    render_bounty_unintersted, render_faucet_rejected, render_faucet_request, render_match_email, render_new_bounty,
    render_new_bounty_acceptance, render_new_bounty_rejection, render_new_bounty_roundup, render_new_work_submission,
    render_tip_email,
)
from sendgrid.helpers.mail import Content, Email, Mail, Personalization


def send_mail(from_email, _to_email, subject, body, html=False,
              from_name="Gitcoin.co", cc_emails=None):
    """Send email via SendGrid."""
    # make sure this subscriber is saved
    to_email = _to_email
    get_or_save_email_subscriber(to_email, 'internal')

    # setup
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    from_email = Email(from_email, from_name)
    to_email = Email(to_email)
    contenttype = "text/plain" if not html else "text/html"

    # build content
    content = Content(contenttype, html) if html else Content(contenttype, body)
    if settings.IS_DEBUG_ENV:
        to_email = Email(settings.CONTACT_EMAIL)  # just to be double secret sure of what were doing in dev
        subject = "[DEBUG] " + subject
    mail = Mail(from_email, subject, to_email, content)
    response = None

    # build personalization
    p = Personalization()
    p.add_to(to_email)
    if cc_emails:  # only add CCif not in prod
        for cc_addr in set(cc_emails):
            cc_addr = Email(cc_addr)
            if settings.IS_DEBUG_ENV:
                cc_addr = to_email
            if cc_addr._email != to_email._email:
                p.add_to(cc_addr)
    mail.add_personalization(p)

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


def bounty_feedback(bounty, persona='submitter', previous_bounties=[]):
    from_email = settings.PERSONAL_CONTACT_EMAIL
    to_email = bounty.bounty_owner_email
    if persona != 'submitter':
        accepted_fulfillments = bounty.fulfillments.filter(accepted=True)
        to_email = accepted_fulfillments.first().fulfiller_email if accepted_fulfillments.exists() else ""

    subject = bounty.github_url
    html, text = render_bounty_feedback(bounty, persona, previous_bounties)
    cc_emails = [from_email]
    send_mail(from_email, to_email, subject, body, cc_emails=cc_emails)


def tip_email(tip, to_emails, is_new):
    round_decimals = 5
    if not tip or not tip.url or not tip.amount or not tip.tokenName:
        return

    warning = '' if tip.network == 'mainnet' else "({})".format(tip.network)
    subject = "⚡️ New Tip Worth {} {} {}".format(round(tip.amount, round_decimals), warning, tip.tokenName)
    if not is_new:
        subject = "🕐 Tip Worth {} {} {} Expiring Soon".format(round(tip.amount, round_decimals), warning, tip.tokenName)

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_tip_email(to_email, tip, is_new)

        send_mail(from_email, to_email, subject, text, html)


def new_faucet_request(fr):
    to_email = settings.PERSONAL_CONTACT_EMAIL
    from_email = settings.SERVER_EMAIL
    subject = "New Faucet Request"
    body = f"A new faucet request was completed. You may fund the request here : https://gitcoin.co/_administration/process_faucet_request/{fr.pk}"
    send_mail(from_email, to_email, subject, body, from_name="No Reply from Gitcoin.co")


def new_external_bounty():
    """Send a new external bounty email notification."""
    to_email = settings.PERSONAL_CONTACT_EMAIL
    from_email = settings.SERVER_EMAIL
    subject = "New External Bounty"
    body = f"https://gitcoin.co/_administrationexternal_bounties/externalbounty"
    send_mail(from_email, to_email, subject, body, from_name="No Reply from Gitcoin.co")


def processed_faucet_request(fr):
    from_email = settings.SERVER_EMAIL
    subject = "Faucet Request Processed"
    html, text = render_faucet_request(fr)
    to_email = fr.email

    send_mail(from_email, to_email, subject, text, html)


def reject_faucet_request(fr):
    from_email = settings.SERVER_EMAIL
    subject = "Faucet Request Rejected"
    html, text = render_faucet_rejected(fr)
    to_email = fr.email

    send_mail(from_email, to_email, subject, text, html)


def new_bounty(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt:
        return

    if to_emails is None:
        to_emails = []

    subject = f"⚡️ New Funded Issue Match worth {bounty.value_in_usdt} USD @ " \
              f"${convert_token_to_usdt(bounty.token_name)}/{bounty.token_name} {bounty.keywords})"

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_bounty(to_email, bounty)

        if not should_suppress_notification_email(to_email):
            send_mail(from_email, to_email, subject, text, html)


def weekly_roundup(to_emails=None):
    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        html, text, subject = render_new_bounty_roundup(to_email)
        from_email = settings.PERSONAL_CONTACT_EMAIL

        if not should_suppress_notification_email(to_email):
            send_mail(from_email, to_email, subject, text, html, from_name="Kevin Owocki (Gitcoin.co)")


def new_work_submission(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt:
        return

    if to_emails is None:
        to_emails = []

    subject = "✉️ New Work Submission Inside for {} ✉️".format(bounty.title_or_desc)

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_work_submission(to_email, bounty)

        if not should_suppress_notification_email(to_email):
            send_mail(from_email, to_email, subject, text, html)


def new_bounty_rejection(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "😕 Work Submission Rejected for {} 😕".format(bounty.title_or_desc)

    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_bounty_rejection(to_email, bounty)

        if not should_suppress_notification_email(to_email):
            send_mail(from_email, to_email, subject, text, html)


def new_bounty_acceptance(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt:
        return

    if to_emails is None:
        to_emails = []

    subject = "🌈 Funds Paid for {} 🌈".format(bounty.title_or_desc)

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_bounty_acceptance(to_email, bounty)

        if not should_suppress_notification_email(to_email):
            send_mail(from_email, to_email, subject, text, html)


def new_match(to_emails, bounty, github_username):

    subject = "⚡️ {} Meet {}: {}! ".format(github_username.title(), bounty.org_name.title(), bounty.title)

    to_email = to_emails[0]
    from_email = settings.CONTACT_EMAIL
    html, text = render_match_email(bounty, github_username)
    send_mail(from_email, to_email, subject, text, html, cc_emails=to_emails)


def bounty_expire_warning(bounty, to_emails=None):
    if not bounty or not bounty.value_in_usdt:
        return

    if to_emails is None:
        to_emails = []

    for to_email in to_emails:
        unit = 'day'
        num = int(round((bounty.expires_date - timezone.now()).days, 0))
        if num == 0:
            unit = 'hour'
            num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))
        unit = unit + ("s" if num != 1 else "")
        subject = "😕 Your Funded Issue ({}) Expires In {} {} ... 😕".format(bounty.title_or_desc, num, unit)

        from_email = settings.CONTACT_EMAIL
        html, text = render_bounty_expire_warning(to_email, bounty)

        if not should_suppress_notification_email(to_email):
            send_mail(from_email, to_email, subject, text, html)


def bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days):
    if not bounty or not bounty.value_in_usdt:
        return

    from_email = settings.CONTACT_EMAIL
    html, text = render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days)
    subject = "Are you still working on '{}' ? ".format(bounty.title_or_desc)

    if not should_suppress_notification_email(to_email):
        send_mail(from_email, to_email, subject, text, html)


def bounty_startwork_expired(to_email, bounty, interest, time_delta_days):
    if not bounty or not bounty.value_in_usdt:
        return

    from_email = settings.CONTACT_EMAIL
    html, text = render_bounty_startwork_expire_warning(to_email, bounty, interest, time_delta_days)
    subject = "We've removed you from the task: '{}' ? ".format(bounty.title_or_desc)

    if not should_suppress_notification_email(to_email):
        send_mail(from_email, to_email, subject, text, html)

def bounty_uninterested(to_email, bounty, interest):
    from_email = settings.CONTACT_EMAIL
    html, text = render_bounty_unintersted(to_email, bounty, interest)
    subject = "Funder has removed you from the task: '{}' ? ".format(bounty.title_or_desc)

    if not should_suppress_notification_email(to_email):
        send_mail(from_email, to_email, subject, text, html)
