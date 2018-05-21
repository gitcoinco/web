# -*- coding: utf-8 -*-
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
from __future__ import unicode_literals

import json
import math
import random

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db.models import Max
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import gettext_lazy as _

from app.utils import sync_profile
from chartit import Chart, DataPool
from dashboard.models import Bounty, Profile, Tip, UserAction
from dashboard.utils import create_user_action
from marketing.mails import new_feedback
from marketing.models import (
    EmailEvent, EmailSubscriber, GithubEvent, Keyword, LeaderboardRank, SlackPresence, SlackUser, Stat,
)
from marketing.utils import get_or_save_email_subscriber, validate_slack_integration
from retail.helpers import get_ip


def get_settings_navs():
    return [{
        'body': 'Email',
        'href': reverse('email_settings', args=('', ))
    }, {
        'body': 'Privacy',
        'href': reverse('privacy_settings'),
    }, {
        'body': 'Matching',
        'href': reverse('matching_settings'),
    }, {
        'body': 'Feedback',
        'href': reverse('feedback_settings'),
    }, {
        'body': 'Slack',
        'href': reverse('slack_settings'),
    }]


def settings_helper_get_auth(request, key=None):
    # setup
    github_handle = request.user.username if request.user.is_authenticated else False
    is_logged_in = bool(request.user.is_authenticated)
    es = EmailSubscriber.objects.none()

    # find the user info
    if not key:
        email = request.user.email if request.user.is_authenticated else None
        if not email:
            github_handle = request.user.username if request.user.is_authenticated else None
        if hasattr(request.user, 'profile'):
            if request.user.profile.email_subscriptions.exists():
                es = request.user.profile.email_subscriptions.first()
            if not es or es and not es.priv:
                es = get_or_save_email_subscriber(
                    request.user.email, 'settings', profile=request.user.profile)
    else:
        try:
            es = EmailSubscriber.objects.get(priv=key)
            email = es.email
        except EmailSubscriber.DoesNotExist:
            pass

    # lazily create profile if needed
    profiles = Profile.objects.none()
    if github_handle:
        profiles = Profile.objects.prefetch_related('alumni').filter(handle__iexact=github_handle).exclude(email='')
    profile = None if not profiles.exists() else profiles.first()
    if not profile and github_handle:
        profile = sync_profile(github_handle, user=request.user)

    # lazily create email settings if needed
    if not es:
        if request.user.is_authenticated and request.user.email:
            es = EmailSubscriber.objects.create(
                email=request.user.email,
                source='settings_page',
            )
            es.set_priv()
            es.save()

    return profile, es, request.user, is_logged_in


def privacy_settings(request):
    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    suppress_leaderboard = profile.suppress_leaderboard if profile else False
    if not profile:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''
    if request.POST and request.POST.get('submit'):
        if profile:
            profile.suppress_leaderboard = bool(request.POST.get('suppress_leaderboard', False))
            profile.hide_profile = bool(request.POST.get('hide_profile', False))
            if profile.alumni and profile.alumni.exists():
                alumni = profile.alumni.first()
                alumni.public = bool(not request.POST.get('hide_alumni', False))
                alumni.save()

            profile.save()

    context = {
        'profile': profile,
        'nav': 'internal',
        'active': '/settings/privacy',
        'title': _('Privacy Settings'),
        'navs': get_settings_navs(),
        'is_logged_in': is_logged_in,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/privacy.html', context)


def matching_settings(request):
    """Handle viewing and updating EmailSubscriber matching settings.

    TODO:
        * Migrate this to a form and handle validation.
        * Migrate Keyword to taggit.
        * Maybe migrate keyword information to Profile instead of using ES?

    Returns:
        TemplateResponse: The populated matching template.

    """
    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''

    if request.POST and request.POST.get('submit'):
        github = request.POST.get('github', '')
        keywords = request.POST.get('keywords').split(',')
        if github:
            es.github = github
        if keywords:
            es.keywords = keywords
        ip = get_ip(request)
        if not es.metadata.get('ip', False):
            es.metadata['ip'] = [ip]
        else:
            es.metadata['ip'].append(ip)
        es.save()
        msg = _('Updated your preferences.')

    context = {
        'keywords': ",".join(es.keywords),
        'is_logged_in': is_logged_in,
        'autocomplete_keywords': json.dumps(
            [str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
        'nav': 'internal',
        'active': '/settings/matching',
        'title': _('Matching Settings'),
        'navs': get_settings_navs(),
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/matching.html', context)


def feedback_settings(request):
    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''
    if request.POST and request.POST.get('submit'):
        comments = request.POST.get('comments', '')[:255]
        has_comment_changed = comments != es.metadata.get('comments','')
        if has_comment_changed:
            new_feedback(es.email, comments)
        es.metadata['comments'] = comments
        ip = get_ip(request)
        if not es.metadata.get('ip', False):
            es.metadata['ip'] = [ip]
        else:
            es.metadata['ip'].append(ip)
        es.save()
        msg = _('We\'ve received your feedback.')

    context = {
        'nav': 'internal',
        'active': '/settings/feedback',
        'title': _('Feedback'),
        'navs': get_settings_navs(),
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/feedback.html', context)


def email_settings(request, key):
    """Display email settings.

    Args:
        key (str): The private key to lookup email subscriber data.

    TODO:
        * Remove all ES.priv_key lookups and use request.user only.
        * Remove settings_helper_get_auth usage.

    Returns:
        TemplateResponse: The email settings view populated with ES data.

    """
    profile, es, user, is_logged_in = settings_helper_get_auth(request, key)
    if not request.user.is_authenticated and (not es and key) or (request.user.is_authenticated and not hasattr(request.user, 'profile')):
        return redirect('/login/github?next=' + request.get_full_path())

    # handle 'noinput' case
    email = ''
    level = ''
    msg = ''
    pref_lang = 'en'
    if request.POST and request.POST.get('submit'):
        email = request.POST.get('email')
        level = request.POST.get('level')
        if profile:
            pref_lang = profile.get_profile_preferred_language()
        preferred_language = request.POST.get('preferred_language')
        validation_passed = True
        try:
            validate_email(email)
        except Exception as e:
            print(e)
            validation_passed = False
            msg = _('Invalid Email')
        if preferred_language:
            if preferred_language not in [i[0] for i in settings.LANGUAGES]:
                msg = _('Unknown language')
                validation_passed = False
        if level not in ['lite', 'lite1', 'regular', 'nothing']:
            validation_passed = False
            msg = _('Invalid Level')
        if validation_passed:
            if profile:
                profile.pref_lang_code = preferred_language
                profile.save()
                request.session[LANGUAGE_SESSION_KEY] = preferred_language
                translation.activate(preferred_language)
            if es:
                key = get_or_save_email_subscriber(email, 'settings')
                es.preferences['level'] = level
                es.email = email
                ip = get_ip(request)
                es.active = level != 'nothing'
                es.newsletter = level in ['regular', 'lite1']
                if not es.metadata.get('ip', False):
                    es.metadata['ip'] = [ip]
                else:
                    es.metadata['ip'].append(ip)
                es.save()
            msg = _('Updated your preferences.')
    context = {
        'nav': 'internal',
        'active': '/settings/email',
        'title': _('Email Settings'),
        'es': es,
        'msg': msg,
        'navs': get_settings_navs(),
        'preferred_language': pref_lang
    }
    return TemplateResponse(request, 'settings/email.html', context)


def slack_settings(request):
    """Displays and saves user's slack settings.

    Returns:
        TemplateResponse: The user's slack settings template response.

    """
    response = {'output': ''}
    profile, es, user, is_logged_in = settings_helper_get_auth(request)

    if not user or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    if request.POST:
        test = request.POST.get('test')
        submit = request.POST.get('submit')
        token = request.POST.get('token', '')
        repos = request.POST.get('repos', '')
        channel = request.POST.get('channel', '')

        if test and token and channel:
            response = validate_slack_integration(token, channel)

        if submit or (response and response.get('success')):
            profile.update_slack_integration(token, channel, repos)
            if not response.get('output'):
                response['output'] = _('Updated your preferences.')
            ua_type = 'added_slack_integration' if token and channel and repos else 'removed_slack_integration'
            create_user_action(user, ua_type, request, {'channel': channel, 'repos': repos})

    context = {
        'repos': profile.get_slack_repos(join=True),
        'is_logged_in': is_logged_in,
        'nav': 'internal',
        'active': '/settings/slack',
        'title': _('Slack Settings'),
        'navs': get_settings_navs(),
        'es': es,
        'profile': profile,
        'msg': response['output'],
    }
    return TemplateResponse(request, 'settings/slack.html', context)


def _leaderboard(request):
    return leaderboard(request, '')


def leaderboard(request, key=''):
    """Display the leaderboard for top earning or paying profiles.

    Args:
        key (str): The leaderboard display type. Defaults to: quarterly_earners.

    Returns:
        TemplateResponse: The leaderboard template response.

    """
    if not key:
        key = 'quarterly_earners'

    titles = {
        'quarterly_payers': _('Top Payers'),
        'quarterly_earners': _('Top Earners'),
        #        'weekly_fulfilled': 'Weekly Leaderboard: Fulfilled Funded Issues',
        #        'weekly_all': 'Weekly Leaderboard: All Funded Issues',
        #        'monthly_fulfilled': 'Monthly Leaderboard',
        #        'monthly_all': 'Monthly Leaderboard: All Funded Issues',
        #        'yearly_fulfilled': 'Yearly Leaderboard: Fulfilled Funded Issues',
        #        'yearly_all': 'Yearly Leaderboard: All Funded Issues',
        #        'all_fulfilled': 'All-Time Leaderboard: Fulfilled Funded Issues',
        #        'all_all': 'All-Time Leaderboard: All Funded Issues',
        # TODO - also include options for weekly, yearly, and all cadences of earning
    }
    if key not in titles.keys():
        raise Http404

    title = titles[key]
    leadeboardranks = LeaderboardRank.objects.filter(active=True, leaderboard=key)
    amount = leadeboardranks.values_list('amount').annotate(Max('amount')).order_by('-amount')
    items = leadeboardranks.order_by('-amount')
    top_earners = ''

    if amount:
        amount_max = amount[0][0]
        top_earners = leadeboardranks.order_by('-amount')[0:3].values_list('github_username', flat=True)
        top_earners = ['@' + username for username in top_earners]
        top_earners = f'The top earners of this period are {", ".join(top_earners)}'
    else:
        amount_max = 0

    context = {
        'items': items,
        'titles': titles,
        'selected': title,
        'title': f'Leaderboard: {title}',
        'card_title': f'Leaderboard: {title}',
        'card_desc': f'See the most valued members in the Gitcoin community this month. {top_earners}',
        'action_past_tense': 'Transacted' if 'submitted' in key else 'bountied',
        'amount_max': amount_max,
        'podium_items': items[:3] if items else []
    }
    return TemplateResponse(request, 'leaderboard.html', context)
