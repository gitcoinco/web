# -*- coding: utf-8 -*-
"""
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

from django.template.loader import render_to_string
from django.utils.translation import gettext as _

from retail.emails import premailer_transform


"""
    Note: "Time Tokens" used to be called "Personal Tokens". To simplify the renaming process,
    variables, classes, and contracts continue to use the old name, but user-facing text uses the
    new name. Personal tokens and Time tokens are the same thing, so you will likely see those two
    phrases used interchangeably throughout the codebase
"""


def render_ptoken_created(ptoken):
    params = {'ptoken': ptoken}

    response_html = premailer_transform(render_to_string("emails/ptoken_created.html", params))
    response_txt = render_to_string("emails/ptoken_created.txt", params)
    subject = _("🎉 Your new time token is ready 🎉")

    return response_html, response_txt, subject


def render_ptoken_redemption_request(ptoken, redeem):
    params = {'ptoken': ptoken, 'redeem': redeem}

    response_html = premailer_transform(render_to_string("emails/ptoken_redemption_requested.html", params))
    response_txt = render_to_string("emails/ptoken_redemption_requested.txt", params)
    subject = _("New redemption request")

    return response_html, response_txt, subject


def render_ptoken_redemption_accepted(ptoken, redeem):
    params = {'ptoken': ptoken, 'redeem': redeem}

    response_html = premailer_transform(render_to_string("emails/ptoken_redemption_accepted.html", params))
    response_txt = render_to_string("emails/ptoken_redemption_accepted.txt", params)
    subject = _("Redemption request accepted")

    return response_html, response_txt, subject


def render_ptoken_redemption_rejected(ptoken, redeem):
    params = {'ptoken': ptoken, 'redeem': redeem}

    response_html = premailer_transform(render_to_string("emails/ptoken_redemption_rejected.html", params))
    response_txt = render_to_string("emails/ptoken_redemption_rejected.txt", params)
    subject = _("Redemption rejected")

    return response_html, response_txt, subject


def render_ptoken_redemption_cancelled(ptoken, redeem):
    params = {'ptoken': ptoken, 'redeem': redeem}

    response_html = premailer_transform(render_to_string("emails/ptoken_redemption_cancelled.html", params))
    response_txt = render_to_string("emails/ptoken_redemption_cancelled.txt", params)
    subject = _("Redemption cancelled")

    return response_html, response_txt, subject


def render_ptoken_redemption_complete_for_requester(ptoken, redeem):
    params = {'ptoken': ptoken, 'redeem': redeem}

    response_html = premailer_transform(render_to_string("emails/ptoken_redemption_complete_for_requester.html", params))
    response_txt = render_to_string("emails/ptoken_redemption_complete_for_requester.txt", params)
    subject = _(f"🌈 Redemption complete for {redeem.reason}")

    return response_html, response_txt, subject


def render_ptoken_redemption_complete_for_owner(ptoken, redeem):
    params = {'ptoken': ptoken, 'redeem': redeem}

    response_html = premailer_transform(render_to_string("emails/ptoken_redemption_complete_for_owner.html", params))
    response_txt = render_to_string("emails/ptoken_redemption_complete_for_owner.txt", params)
    subject = _(f"🌈 Redemption complete for {redeem.reason}")

    return response_html, response_txt, subject
