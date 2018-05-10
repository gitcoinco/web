from django.conf import settings
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext_lazy as _

from marketing.mails import send_mail, setup_lang
from retail.emails import premailer_transform


def mentors_match(matched_mentors, profile):
    from_email = settings.SERVER_EMAIL
    cur_language = translation.get_language()
    to_email = profile.email
    try:
        setup_lang(to_email)
        subject = _("You've got a match!")
        params = {
            'matched_mentors': [(match, profile.skills_matched(match)) for match in matched_mentors]
        }
        html = premailer_transform(render_to_string("emails/mentor_match.html", params))
        text = render_to_string("emails/mentor_match.txt", params)
        send_mail(from_email, to_email, subject, text, html)
    finally:
        translation.activate(cur_language)
