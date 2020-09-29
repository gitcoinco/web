# -*- coding: utf-8 -*-
"""
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
"""

from django.conf import settings
from django.utils import translation

from marketing.mails import send_mail, setup_lang
from marketing.utils import func_name, should_suppress_notification_email
from ptokens.emails import (
    render_ptoken_created, render_ptoken_redemption_accepted, render_ptoken_redemption_cancelled,
    render_ptoken_redemption_complete_for_owner, render_ptoken_redemption_complete_for_requester,
    render_ptoken_redemption_rejected, render_ptoken_redemption_request,
)


def send_personal_token_created(profile, ptoken):
    from_email = settings.CONTACT_EMAIL
    to_email = profile.email
    cur_language = translation.get_language()

    try:
        setup_lang(to_email)
        html, text, subject = render_ptoken_created(ptoken)

        if not should_suppress_notification_email(to_email, 'personal_token_created'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def send_ptoken_redemption_request(profile, ptoken, redemption):
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
        html, text, subject = render_ptoken_redemption_request(ptoken, redemption)

        if not should_suppress_notification_email(to_email, 'personal_token_redemption'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def send_ptoken_redemption_accepted(profile, ptoken, redemption):
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
        html, text, subject = render_ptoken_redemption_accepted(ptoken, redemption)

        if not should_suppress_notification_email(to_email, 'personal_token_redemption'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def send_ptoken_redemption_rejected(profile, ptoken, redemption):
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
        html, text, subject = render_ptoken_redemption_rejected(ptoken, redemption)

        if not should_suppress_notification_email(to_email, 'personal_token_redemption'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def send_ptoken_redemption_cancelled(profile, ptoken, redemption):
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
        html, text, subject = render_ptoken_redemption_cancelled(ptoken, redemption)

        if not should_suppress_notification_email(to_email, 'personal_token_redemption'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def send_ptoken_redemption_complete_for_requester(profile, ptoken, redemption):
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
        html, text, subject = render_ptoken_redemption_complete_for_requester(ptoken, redemption)

        if not should_suppress_notification_email(to_email, 'personal_token_redemption'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)


def send_ptoken_redemption_complete_for_owner(profile, ptoken, redemption):
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
        html, text, subject = render_ptoken_redemption_complete_for_owner(ptoken, redemption)

        if not should_suppress_notification_email(to_email, 'personal_token_redemption'):
            send_mail(from_email, to_email, subject, text, html, categories=['transactional', func_name()])
    finally:
        translation.activate(cur_language)
