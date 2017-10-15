# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
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
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail, Personalization
from django.conf import settings
from retail.emails import *
from marketing.utils import get_or_save_email_subscriber


def send_mail(from_email, to_email, subject, body, html=False, bcc_gitcoin_core=True, from_name="Gitcoin.co"):
    if(bcc_gitcoin_core):
        prepend_str = "Sent to {}\n".format(to_email)
        _body = prepend_str + str(body)
        if html:
            _html = prepend_str + str(html)
        else:
            _html = False
        _to_email = 'email_logger@gitcoin.co'
        send_mail(from_email, _to_email, subject, _body, _html, bcc_gitcoin_core=False, from_name=from_name)

    get_or_save_email_subscriber(to_email, 'internal')
    print("-- Sending Mail '{}' to {}".format(subject, to_email))
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    from_email = Email(from_email, from_name)
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


def tip_email(tip, to_emails, is_new):
    if not tip or not tip.url or not tip.amount or not tip.tokenName:
        return

    subject = "⚡️ New Tip Worth {} {}".format(round(tip.amount,2), tip.tokenName)
    if not is_new:
        subject = "🕐 New Tip Worth {} {} Expiring Soon".format(round(tip.amount,2), tip.tokenName)

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_tip_email(to_email, tip, is_new)

        send_mail(from_email, to_email, subject, text, html)


def new_bounty(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "⚡️ New Funded Issue Worth ${}".format(bounty.value_in_usdt)

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_bounty(to_email, bounty)

        send_mail(from_email, to_email, subject, text, html)


def weekly_roundup(to_emails=[]):

    subject = "🍃Gitcoin Weekly | Pumpkin Spice Lattes, Pilot Programs, Devcon3, New Funded Issue Detail Page "
    for to_email in to_emails:
        html, text = render_new_bounty_roundup(to_email)
        from_email = settings.PERSONAL_CONTACT_EMAIL

        send_mail(from_email, to_email, subject, text, html, from_name="Kevin Owocki (Gitcoin.co)")


def new_bounty_claim(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "✉️ New Claim Inside ✉️"

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_bounty_claim(to_email, bounty)

        send_mail(from_email, to_email, subject, text, html)


def new_bounty_rejection(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "😕 Claim Rejected 😕"

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_bounty_rejection(to_email, bounty)

        send_mail(from_email, to_email, subject, text, html)


def new_bounty_acceptance(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    subject = "🌈 Funds Paid! 🌈"

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_bounty_acceptance(to_email, bounty)

        send_mail(from_email, to_email, subject, text, html)


def new_match(to_emails=[]):

    subject = "🌈 New Match, Kevin meet Metamask! 🌈"

    for to_email in to_emails:
        from_email = settings.CONTACT_EMAIL
        html, text = render_new_match(to_email, bounty)

        send_mail(from_email, to_email, subject, text, html)




def bounty_expire_warning(bounty, to_emails=[]):
    if not bounty or not bounty.value_in_usdt:
        return

    for to_email in to_emails:
        unit = 'days'
        num = int(round((bounty.expires_date - timezone.now()).days, 0))
        if num == 0:
            unit = 'hours'
            num = int(round((bounty.expires_date - timezone.now()).seconds / 3600 / 24, 0))
        subject = "😕 Your Funded Issue Expires In {} {} ... 😕".format(days, unit)

        from_email = settings.CONTACT_EMAIL
        html, text = render_bounty_expire_warning(to_email, bounty)

        send_mail(from_email, to_email, subject, text, html)

