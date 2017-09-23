# -*- coding: utf-8 -*-
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, Personalization
from django.conf import settings
from retail.emails import *


def send_mail(from_email, to_email, subject, body, html=False):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    from_email = Email(from_email)
    to_email = Email(to_email)
    contenttype = "text/plain" if not html else "text/html"
    content = Content(contenttype, html) if html else Content(contenttype, body)
    if settings.DEBUG:
        to_email = Email(settings.CONTACT_EMAIL) #just to be double secret sure of what were doing in dev
        subject = "[DEBUG] " + subject
    mail = Mail(from_email, subject, to_email, content)
    # mail.add_header({'bcc' : settings.BCC_EMAIL}) #TODO
    response = sg.client.mail.send.post(request_body=mail.get())
    return response


def new_bounty(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "⚡️ New Bounty Worth ${}".format(bounty.value_in_usdt)

    from_email = settings.CONTACT_EMAIL
    html, text = render_new_bounty(bounty)

    for to_email in to_emails:
        send_mail(from_email, to_email, subject, text, html)


def weekly_roundup(to_emails=[]):
    start_date = timezone.now() - timezone.timedelta(weeks=1)
    end_date = timezone.now()
    bounties = roundup_bounties(start_date, end_date)

    total_value = round(sum(bounties.values_list('_val_usd_db', flat=True)),2)

    subject = "⚡️ ${} of Bounties! Roundup for Week Ending {}".format(total_value, end_date.strftime('%Y-%m-%d'))

    html, text = render_new_bounty_roundup(bounties)
    from_email = settings.CONTACT_EMAIL

    for to_email in to_emails:
        send_mail(from_email, to_email, subject, text, html)


def new_bounty_claim(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "✉️ New Bounty Claim Inside ✉️"

    from_email = settings.CONTACT_EMAIL
    html, text = render_new_bounty_claim(bounty)

    for to_email in to_emails:
        send_mail(from_email, to_email, subject, text, html)


def new_bounty_rejection(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "😕 Bounty Claim Rejected 😕"

    from_email = settings.CONTACT_EMAIL
    html, text = render_new_bounty_rejection(bounty)

    for to_email in to_emails:
        send_mail(from_email, to_email, subject, text, html)


def new_bounty_acceptance(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "🌈 Bounty Paid! 🌈"

    from_email = settings.CONTACT_EMAIL
    html, text = render_new_bounty_acceptance(bounty)

    for to_email in to_emails:
        send_mail(from_email, to_email, subject, text, html)


def bounty_expire_warning(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    unit = 'days'
    num = int(round((bounty.expires_date - timezone.now()).days, 0))
    if num == 0:
        unit = 'hours'
        num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))
    subject = "😕 Your Bounty Expires In {} {} ... 😕".format(days, unit)

    from_email = settings.CONTACT_EMAIL
    html, text = render_bounty_expire_warning(bounty)

    for to_email in to_emails:
        send_mail(from_email, to_email, subject, text, html)

