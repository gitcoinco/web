# -*- coding: utf-8 -*-
"""Define the marketing views.

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
from __future__ import unicode_literals

import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.validators import validate_email
from django.db.models import Max
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import gettext_lazy as _

from app.utils import sync_profile
from cacheops import cached_view
from dashboard.models import Profile, TokenApproval
from dashboard.utils import create_user_action
from enssubdomain.models import ENSSubdomainRegistration
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from marketing.mails import new_feedback
from marketing.models import AccountDeletionRequest, EmailSubscriber, Keyword, LeaderboardRank
from marketing.utils import (
    delete_user_from_mailchimp, get_or_save_email_subscriber, validate_discord_integration, validate_slack_integration,
)
from retail.emails import ALL_EMAILS, render_nth_day_email_campaign
from retail.helpers import get_ip

logger = logging.getLogger(__name__)


def get_settings_navs(request):
    return [{
        'body': _('Email'),
        'href': reverse('email_settings', args=('', ))
    }, {
        'body': _('Privacy'),
        'href': reverse('privacy_settings')
    }, {
        'body': _('Matching'),
        'href': reverse('matching_settings')
    }, {
        'body': _('Feedback'),
        'href': reverse('feedback_settings')
    }, {
        'body': 'Slack',
        'href': reverse('slack_settings'),
    }, {
        'body': 'Discord',
        'href': reverse('discord_settings')
    }, {
        'body': 'ENS',
        'href': reverse('ens_settings')
    }, {
        'body': _('Account'),
        'href': reverse('account_settings'),
    }, {
        'body': _('Token'),
        'href': reverse('token_settings'),
    }, {
        'body': _('Job Status'),
        'href': reverse('job_settings'),
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
        profiles = Profile.objects.prefetch_related('alumni').filter(handle__iexact=github_handle)
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
    profile, __, __, is_logged_in = settings_helper_get_auth(request)
    if not profile:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''
    if request.POST and request.POST.get('submit'):
        if profile:
            profile.suppress_leaderboard = bool(request.POST.get('suppress_leaderboard', False))
            profile.hide_profile = bool(request.POST.get('hide_profile', False))
            profile = record_form_submission(request, profile, 'privacy')
            if profile.alumni and profile.alumni.exists():
                alumni = profile.alumni.first()
                alumni.public = bool(not request.POST.get('hide_alumni', False))
                alumni.save()

            profile.save()

    context = {
        'profile': profile,
        'nav': 'home',
        'active': '/settings/privacy',
        'title': _('Privacy Settings'),
        'navs': get_settings_navs(request),
        'is_logged_in': is_logged_in,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/privacy.html', context)


def record_form_submission(request, obj, submission_type):
    obj.form_submission_records.append({
        'ip': get_ip(request),
        'timestamp': int(timezone.now().timestamp()),
        'type': submission_type,
        })
    return obj


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
    __, es, __, is_logged_in = settings_helper_get_auth(request)
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
        es = record_form_submission(request, es, 'match')
        es.save()
        msg = _('Updated your preferences.')

    context = {
        'keywords': ",".join(es.keywords),
        'is_logged_in': is_logged_in,
        'autocomplete_keywords': json.dumps(
            [str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
        'nav': 'home',
        'active': '/settings/matching',
        'title': _('Matching Settings'),
        'navs': get_settings_navs(request),
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/matching.html', context)


def feedback_settings(request):
    # setup
    __, es, __, __ = settings_helper_get_auth(request)
    if not es:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    msg = ''
    if request.POST and request.POST.get('submit'):
        comments = request.POST.get('comments', '')[:255]
        has_comment_changed = comments != es.metadata.get('comments', '')
        if has_comment_changed:
            new_feedback(es.email, comments)
        es.metadata['comments'] = comments
        es = record_form_submission(request, es, 'feedback')
        es.save()
        msg = _('We\'ve received your feedback.')

    context = {
        'nav': 'home',
        'active': '/settings/feedback',
        'title': _('Feedback'),
        'navs': get_settings_navs(request),
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
    profile, es, __, __ = settings_helper_get_auth(request, key)
    if not request.user.is_authenticated and (not es and key) or (
        request.user.is_authenticated and not hasattr(request.user, 'profile')
    ):
        return redirect('/login/github?next=' + request.get_full_path())

    # handle 'noinput' case
    email = ''
    level = ''
    msg = ''
    if request.POST and request.POST.get('submit'):
        email = request.POST.get('email')
        level = request.POST.get('level')
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
                form = dict(request.POST)
                # form was not sending falses, so default them if not there
                for email_tuple in ALL_EMAILS:
                    key = email_tuple[0]
                    if key not in form.keys():
                        form[key] = False
                es.build_email_preferences(form)
                es = record_form_submission(request, es, 'email')
                ip = get_ip(request)
                es.active = level != 'nothing'
                es.newsletter = level in ['regular', 'lite1']
                if not es.metadata.get('ip', False):
                    es.metadata['ip'] = [ip]
                else:
                    es.metadata['ip'].append(ip)
                es.save()
            msg = _('Updated your preferences.')
    pref_lang = 'en' if not profile else profile.get_profile_preferred_language()
    context = {
        'nav': 'home',
        'active': '/settings/email',
        'title': _('Email Settings'),
        'es': es,
        'nav': 'home',
        'suppression_preferences': json.dumps(es.preferences.get('suppression_preferences', {}) if es else {}),
        'msg': msg,
        'email_types': ALL_EMAILS,
        'navs': get_settings_navs(request),
        'preferred_language': pref_lang
    }
    return TemplateResponse(request, 'settings/email.html', context)


def slack_settings(request):
    """Display and save user's slack settings.

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
            profile = record_form_submission(request, profile, 'slack')
            if not response.get('output'):
                response['output'] = _('Updated your preferences.')
            ua_type = 'added_slack_integration' if token and channel and repos else 'removed_slack_integration'
            create_user_action(user, ua_type, request, {'channel': channel, 'repos': repos})

    context = {
        'repos': profile.get_slack_repos(join=True) if profile else [],
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'active': '/settings/slack',
        'title': _('Slack Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'profile': profile,
        'msg': response['output'],
    }
    return TemplateResponse(request, 'settings/slack.html', context)


def discord_settings(request):
    """Display and save user's Discord settings.

    Returns:
        TemplateResponse: The user's Discord settings template response.

    """
    response = {'output': ''}
    profile, es, user, is_logged_in = settings_helper_get_auth(request)

    if not user or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    if request.POST:
        test = request.POST.get('test')
        submit = request.POST.get('submit')
        webhook_url = request.POST.get('webhook_url', '')
        repos = request.POST.get('repos', '')

        if test and webhook_url:
            response = validate_discord_integration(webhook_url)

        if submit or (response and response.get('success')):
            profile.update_discord_integration(webhook_url, repos)
            profile = record_form_submission(request, profile, 'discord')
            if not response.get('output'):
                response['output'] = _('Updated your preferences.')
            ua_type = 'added_discord_integration' if webhook_url and repos else 'removed_discord_integration'
            create_user_action(user, ua_type, request, {'webhook_url': webhook_url, 'repos': repos})

    context = {
        'repos': profile.get_discord_repos(join=True) if profile else [],
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'active': '/settings/discord',
        'title': _('Discord Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'profile': profile,
        'msg': response['output'],
    }
    return TemplateResponse(request, 'settings/discord.html', context)


def token_settings(request):
    """Display and save user's token settings.

    Returns:
        TemplateResponse: The user's token settings template response.

    """
    msg = ""
    profile, es, user, is_logged_in = settings_helper_get_auth(request)

    if not user or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    if request.POST:
        coinbase = request.POST.get('coinbase')
        approved_name = request.POST.get('contract_name')
        approved_address = request.POST.get('contract_address')
        token_address = request.POST.get('token_address')
        token_name = request.POST.get('token_name')
        txid = request.POST.get('txid')
        network = request.POST.get('network')

        TokenApproval.objects.create(
            profile=profile,
            coinbase=coinbase,
            token_name=token_name,
            token_address=token_address,
            approved_address=approved_address,
            approved_name=approved_name,
            tx=txid,
            network=network,
            )
        msg = "Token approval completed"

    context = {
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'active': '/settings/tokens',
        'title': _('Token Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'profile': profile,
        'msg': msg,
        'gas_price': round(recommend_min_gas_price_to_confirm_in_time(1), 1),
    }
    return TemplateResponse(request, 'settings/tokens.html', context)


def ens_settings(request):
    """Display and save user's ENS settings.

    Returns:
        TemplateResponse: The user's ENS settings template response.

    """
    response = {'output': ''}
    profile, es, user, is_logged_in = settings_helper_get_auth(request)

    if not user or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    ens_subdomains = ENSSubdomainRegistration.objects.filter(profile=profile).order_by('-pk')
    ens_subdomain = ens_subdomains.first() if ens_subdomains.exists() else None

    context = {
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'ens_subdomain': ens_subdomain,
        'active': '/settings/ens',
        'title': _('ENS Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'profile': profile,
        'msg': response['output'],
    }
    return TemplateResponse(request, 'settings/ens.html', context)


def account_settings(request):
    """Display and save user's Account settings.

    Returns:
        TemplateResponse: The user's Account settings template response.

    """
    msg = ''
    profile, es, user, is_logged_in = settings_helper_get_auth(request)

    if not user or not profile or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    if request.POST:
        if 'persona_is_funder' or 'persona_is_hunter' in request.POST.keys():
            profile.persona_is_funder = bool(request.POST.get('persona_is_funder', False))
            profile.persona_is_hunter = bool(request.POST.get('persona_is_hunter', False))
            profile.save()

        if 'preferred_payout_address' in request.POST.keys():
            profile.preferred_payout_address = request.POST.get('preferred_payout_address', '')
            profile.save()
            msg = _('Updated your Address')
        elif request.POST.get('disconnect', False):
            profile.github_access_token = ''
            profile = record_form_submission(request, profile, 'account-disconnect')
            profile.email = ''
            profile.save()
            create_user_action(profile.user, 'account_disconnected', request)
            messages.success(request, _('Your account has been disconnected from Github'))
            logout_redirect = redirect(reverse('logout') + '?next=/')
            return logout_redirect
        elif request.POST.get('delete', False):

            # remove profile
            profile.hide_profile = True
            profile = record_form_submission(request, profile, 'account-delete')
            profile.email = ''
            profile.save()

            # remove email
            delete_user_from_mailchimp(es.email)

            if es:
                es.delete()
            request.user.delete()
            AccountDeletionRequest.objects.create(
                handle=profile.handle,
                profile={
                        'ip': get_ip(request),
                    }
                )
            profile.avatar_baseavatar_related.all().delete()
            try:
                profile.delete()
            except:
                profile.github_access_token = ''
                profile.user = None
                profile.hide_profile = True
                profile.save()
            messages.success(request, _('Your account has been deleted.'))
            logout_redirect = redirect(reverse('logout') + '?next=/')
            return logout_redirect
        else:
            msg = _('Error: did not understand your request')

    context = {
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'active': '/settings/account',
        'title': _('Account Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'profile': profile,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/account.html', context)


def job_settings(request):
    """Display and save user's Account settings.

    Returns:
        TemplateResponse: The user's Account settings template response.

    """
    msg = ''
    profile, es, user, is_logged_in = settings_helper_get_auth(request)

    if not user or not profile or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    if request.POST:

        if 'preferred_payout_address' in request.POST.keys():
            profile.preferred_payout_address = request.POST.get('preferred_payout_address', '')
            profile.save()
            msg = _('Updated your Address')
        elif request.POST.get('disconnect', False):
            profile.github_access_token = ''
            profile = record_form_submission(request, profile, 'account-disconnect')
            profile.email = ''
            profile.save()
            create_user_action(profile.user, 'account_disconnected', request)
            messages.success(request, _('Your account has been disconnected from Github'))
            logout_redirect = redirect(reverse('logout') + '?next=/')
            return logout_redirect
        elif request.POST.get('delete', False):

            # remove profile
            profile.hide_profile = True
            profile = record_form_submission(request, profile, 'account-delete')
            profile.email = ''
            profile.save()

            # remove email
            delete_user_from_mailchimp(es.email)

            if es:
                es.delete()
            request.user.delete()
            AccountDeletionRequest.objects.create(
                handle=profile.handle,
                profile={
                        'ip': get_ip(request),
                    }
                )
            profile.delete()
            messages.success(request, _('Your account has been deleted.'))
            logout_redirect = redirect(reverse('logout') + '?next=/')
            return logout_redirect
        else:
            msg = _('Error: did not understand your request')

    context = {
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'active': '/settings/job',
        'title': _('Job Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'profile': profile,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/job.html', context)


def _leaderboard(request):
    """Display the leaderboard for top earning or paying profiles.

    Returns:
        TemplateResponse: The leaderboard template response.

    """
    context = {
        'active': 'leaderboard',
    }
    return leaderboard(request, '')


def leaderboard(request, key=''):
    """Display the leaderboard for top earning or paying profiles.

    Args:
        key (str): The leaderboard display type. Defaults to: quarterly_earners.

    Returns:
        TemplateResponse: The leaderboard template response.

    """
    cadences = ['all', 'weekly', 'monthly', 'quarterly', 'yearly']


    keyword_search = request.GET.get('keyword', '')
    keyword_search = '' if keyword_search == 'all' else keyword_search
    limit = request.GET.get('limit', 50)
    cadence = request.GET.get('cadence', 'quarterly')

    # backwards compatibility fix for old inbound links
    for ele in cadences:
        key = key.replace(f"{ele}_", '')

    titles = {
        f'payers': _('Top Funders'),
        f'earners': _('Top Coders'),
        f'orgs': _('Top Orgs'),
        f'tokens': _('Top Tokens'),
        f'keywords': _('Top Keywords'),
        f'kudos': _('Top Kudos'),
        f'cities': _('Top Cities'),
        f'countries': _('Top Countries'),
        f'continents': _('Top Continents'),
    }

    if not key:
        key = f'earners'

    if key not in titles.keys():
        raise Http404

    title = titles[key]
    which_leaderboard = f"{cadence}_{key}"
    ranks = LeaderboardRank.objects.filter(active=True, leaderboard=which_leaderboard)
    if keyword_search:
        ranks = ranks.filter(tech_keywords__icontains=keyword_search)

    amount = ranks.values_list('amount').annotate(Max('amount')).order_by('-amount')
    items = ranks.order_by('-amount')

    top_earners = ''
    technologies = set()
    for profile_keywords in ranks.values_list('tech_keywords'):
        for techs in profile_keywords:
            for tech in techs:
                technologies.add(tech)

    if amount:
        amount_max = amount[0][0]
        top_earners = ranks.order_by('-amount')[0:5].values_list('github_username', flat=True)
        top_earners = ['@' + username for username in top_earners]
        top_earners = f'The top earners of this period are {", ".join(top_earners)}'
    else:
        amount_max = 0

    profile_keys = ['tokens', 'keywords', 'cities', 'countries', 'continents']
    is_linked_to_profile = any(sub in key for sub in profile_keys)

    cadence_ui = cadence if cadence != 'all' else 'All-Time'
    page_title = f'{cadence_ui.title()} {keyword_search.title()} Leaderboard: {title.title()}'
    context = {
        'items': items[0:limit],
        'nav': 'home',
        'titles': titles,
        'cadence': cadence,
        'selected': title,
        'is_linked_to_profile': is_linked_to_profile,
        'title': page_title,
        'card_title': page_title,
        'card_desc': f'See the most valued members in the Gitcoin community recently . {top_earners}',
        'action_past_tense': 'Transacted' if 'submitted' in key else 'bountied',
        'amount_max': amount_max,
        'podium_items': items[:5] if items else [],
        'technologies': technologies,
        'active': 'leaderboard',
        'keyword_search': keyword_search,
        'cadences': cadences,
    }

    return TemplateResponse(request, 'leaderboard.html', context)

@staff_member_required
def day_email_campaign(request, day):
    if day not in list(range(1, 3)):
        raise Http404
    response_html, _, _, = render_nth_day_email_campaign('foo@bar.com', day, 'staff member')
    return HttpResponse(response_html)
