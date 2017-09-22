import sendgrid
from sendgrid.helpers.mail import *
from django.conf import settings


def send_mail(from_email, to_email, subject, body, html=False):
    sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
    from_email = Email(from_email)
    to_email = Email(to_email)
    contenttype = "text/plain" if not html else "text/html"
    content = Content(contenttype, body)
    if settings.DEBUG:
        subject="[DEBUG] " + subject
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
