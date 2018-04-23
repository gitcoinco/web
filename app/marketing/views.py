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

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.db.models import Max
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.utils import sync_profile
from chartit import Chart, DataPool
from dashboard.models import Bounty, Profile, Tip, UserAction
from marketing.mails import new_feedback
from marketing.models import (
    EmailEvent, EmailSubscriber, GithubEvent, Keyword, LeaderboardRank, SlackPresence, SlackUser, Stat,
)
from marketing.utils import get_or_save_email_subscriber
from retail.helpers import get_ip

settings_navs = [
    {
        'body': 'Email',
        'href': '/settings/email',
    },
    {
        'body': 'Privacy',
        'href': '/settings/privacy',
    },
    {
        'body': 'Matching',
        'href': '/settings/matching',
    },
    {
        'body': 'Feedback',
        'href': '/settings/feedback',
    },
]


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
            level = es.preferences.get('level', False)
        except EmailSubscriber.DoesNotExist:
            pass

    # lazily create profile if needed
    profiles = Profile.objects.filter(handle__iexact=github_handle).exclude(email='') if github_handle else Profile.objects.none()
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
            suppress_leaderboard = profile.suppress_leaderboard
            profile.save()

    context = {
        'suppress_leaderboard': suppress_leaderboard,
        'nav': 'internal',
        'active': '/settings/privacy',
        'title': _('Privacy Settings'),
        'navs': settings_navs,
        'is_logged_in': is_logged_in,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/privacy.html', context)


def matching_settings(request):

    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''

    if request.POST and request.POST.get('submit'):
        github = request.POST.get('github', '')
        keywords = request.POST.get('keywords').split(',')
        es.github = github
        es.keywords = keywords
        ip = get_ip(request)
        if not es.metadata.get('ip', False):
            es.metadata['ip'] = [ip]
        else:
            es.metadata['ip'].append(ip)
        es.save()
        msg = "Updated your preferences.  "

    context = {
        'keywords': ",".join(es.keywords),
        'is_logged_in': is_logged_in,
        'autocomplete_keywords': json.dumps(
            [str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
        'nav': 'internal',
        'active': '/settings/matching',
        'title': _('Matching Settings'),
        'navs': settings_navs,
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
        msg = "We've received your feedback. "

    context = {
        'nav': 'internal',
        'active': '/settings/feedback',
        'title': _('Feedback'),
        'navs': settings_navs,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/feedback.html', context)


def email_settings(request, key):

    # setup
    profile, es, user, is_logged_in = settings_helper_get_auth(request, key)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    # handle 'noinput' case
    suppress_leaderboard = False
    email = ''
    level = ''
    msg = ''

    if request.POST and request.POST.get('submit'):
        email = request.POST.get('email')
        level = request.POST.get('level')
        validation_passed = True
        try:
            validate_email(email)
        except Exception as e:
            print(e)
            validation_passed = False
            msg = _('Invalid Email')

        if level not in ['lite', 'lite1', 'regular', 'nothing']:
            validation_passed = False
            msg = _('Invalid Level')
        if validation_passed:
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
            msg = "Updated your preferences.  "
    context = {
        'nav': 'internal',
        'active': '/settings/email',
        'title': _('Email Settings'),
        'es': es,
        'msg': msg,
        'navs': settings_navs,
    }
    return TemplateResponse(request, 'settings/email.html', context)


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
