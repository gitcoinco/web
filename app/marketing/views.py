# -*- coding: utf-8 -*-
"""Define the marketing views.

Copyright (C) 2020 Gitcoin Core

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

import csv
import json
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.db.models import Avg, Count, Max, Q
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.translation import LANGUAGE_SESSION_KEY
from django.utils.translation import gettext_lazy as _

from app.utils import sync_profile
from cacheops import cached_view
from chartit import PivotChart, PivotDataPool
from chat.tasks import update_chat_notifications
from dashboard.models import Activity, HackathonEvent, Profile, TokenApproval
from dashboard.utils import create_user_action, get_orgs_perms, is_valid_eth_address
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from grants.models import Grant
from marketing.country_codes import COUNTRY_CODES, COUNTRY_NAMES, FLAG_API_LINK, FLAG_ERR_MSG, FLAG_SIZE, FLAG_STYLE
from marketing.mails import new_feedback
from marketing.models import AccountDeletionRequest, EmailSubscriber, Keyword, LeaderboardRank, UpcomingDate
from marketing.utils import delete_user_from_mailchimp, get_or_save_email_subscriber, validate_slack_integration
from quests.models import Quest
from retail.emails import ALL_EMAILS, render_new_bounty, render_nth_day_email_campaign
from retail.helpers import get_ip
from townsquare.models import Announcement

logger = logging.getLogger(__name__)


def get_settings_navs(request):
    tabs = [{
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
    },{
        'body': _('Account'),
        'href': reverse('account_settings'),
    }, {
        'body': _('Token'),
        'href': reverse('token_settings'),
    }, {
        'body': _('Job Status'),
        'href': reverse('job_settings'),
    }, {
        'body': _('Tax'),
        'href': reverse('tax_settings'),
    }]

    if request.user.is_staff:
        tabs.append({
            'body': _('Organizations'),
            'href': reverse('org_settings'),
        })

    return tabs

def upcoming_dates():
    return UpcomingDate.objects.filter(date__gt=timezone.now()).order_by('date')

def email_announcements():
    return Announcement.objects.filter(key='founders_note_daily_email', valid_from__lt=timezone.now(), valid_to__gt=timezone.now()).order_by('valid_to').first()

def settings_helper_get_auth(request, key=None):
    # setup
    github_handle = request.user.username if request.user.is_authenticated else False
    is_logged_in = bool(request.user.is_authenticated)
    es = EmailSubscriber.objects.none()

    # find the user info
    if key is None or not EmailSubscriber.objects.filter(priv=key).exists():
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
        profiles = Profile.objects.prefetch_related('alumni').filter(handle=github_handle.lower())
    profile = None if not profiles.exists() else profiles.first()
    if not profile and github_handle:
        profile = sync_profile(github_handle, user=request.user)

    # lazily create email settings if needed
    if not es:
        if request.user.is_authenticated and request.user.email:
            es = EmailSubscriber.objects.create(
                email=request.user.email,
                source='settings_page',
                profile=request.user.profile,
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
            profile.dont_autofollow_earnings = bool(request.POST.get('dont_autofollow_earnings', False))
            profile.suppress_leaderboard = bool(request.POST.get('suppress_leaderboard', False))
            profile.hide_profile = bool(request.POST.get('hide_profile', False))
            profile.pref_do_not_track = bool(request.POST.get('pref_do_not_track', False))
            profile.hide_wallet_address = bool(request.POST.get('hide_wallet_address', False))
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
    profile, es, __, is_logged_in = settings_helper_get_auth(request)
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
            profile.keywords = keywords
            profile.save()
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
    email_types = {}
    from retail.emails import ALL_EMAILS
    for em in ALL_EMAILS:
        email_types[em[0]] = str(em[1])
    email_type = request.GET.get('type')
    if email_type in email_types:
        email = es.email
        if es:
            key = get_or_save_email_subscriber(email, 'settings')
            es.email = email
            unsubscribed_email_type = {}
            unsubscribed_email_type[email_type] = True
            if email_type == 'chat' and profile:
                update_chat_notifications(profile, 'email', False)
            es.build_email_preferences(unsubscribed_email_type)
            es = record_form_submission(request, es, 'email')
            ip = get_ip(request)
            if not es.metadata.get('ip', False):
        	    es.metadata['ip'] = [ip]
            else:
                es.metadata['ip'].append(ip)
            es.save()
        context = {
            'title': _('Email unsubscription successful'),
            'type': email_types[email_type]
        }
        return TemplateResponse(request, 'email_unsubscribed.html', context)
    if request.POST and request.POST.get('submit'):
        email = request.POST.get('email')
        level = request.POST.get('level')
        validation_passed = True
        try:
            email_in_use = User.objects.filter(email=email) | User.objects.filter(profile__email=email)
            email_used_marketing = EmailSubscriber.objects.filter(email=email).select_related('profile')
            logged_in = request.user.is_authenticated
            email_already_used = (email_in_use or email_used_marketing)
            user = request.user if logged_in else None
            email_used_by_me = (user and (user.email == email or user.profile.email == email))
            email_changed = es.email != email

            if email_changed and email_already_used and not email_used_by_me:
                raise ValueError(f'{request.user} attempting to use an email which is already in use on the platform')
            validate_email(email)
        except Exception as e:
            print(e)
            validation_passed = False
            msg = str(e)
        if validation_passed:
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

                if form['chat'] and profile:
                    update_chat_notifications(profile, 'email', False)

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
        'active': '/settings/email/',
        'title': _('Email Settings'),
        'es': es,
        'nav': 'home',
        'suppression_preferences': json.dumps(es.preferences.get('suppression_preferences', {}) if es else {}),
        'msg': msg,
        'profile': request.user.profile if request.user.is_authenticated else None,
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
            eth_address = request.POST.get('preferred_payout_address', '')
            if not is_valid_eth_address(eth_address):
                eth_address = profile.preferred_payout_address
            profile.preferred_payout_address = eth_address
            profile.save()
            msg = _('Updated your Address')
        elif request.POST.get('export', False):
            export_type = request.POST.get('export_type', False)

            response = HttpResponse(content_type='text/csv')
            name = f"gitcoin_{export_type}_{timezone.now().strftime('%Y_%m_%dT%H_00_00')}"
            response['Content-Disposition'] = f'attachment; filename="{name}.csv"'

            writer = csv.writer(response)
            writer.writerow(['id', 'date', 'From', 'From Location', 'To', 'To Location', 'Type', 'Value In USD', 'url', 'txid', 'token_name', 'token_value'])
            profile = request.user.profile
            earnings = profile.earnings if export_type == 'earnings' else profile.sent_earnings
            earnings = earnings.filter(network='mainnet').order_by('-created_on')
            for earning in earnings:
                writer.writerow([earning.pk,
                    earning.created_on.strftime("%Y-%m-%dT%H:00:00"), 
                    earning.from_profile.handle if earning.from_profile else '*',
                    earning.from_profile.data.get('location', 'Unknown') if earning.from_profile else 'Unknown',
                    earning.to_profile.handle if earning.to_profile else '*',
                    earning.to_profile.data.get('location', 'Unknown') if earning.to_profile else 'Unknown',
                    earning.source_type.model_class(),
                    earning.value_usd,
                    earning.txid,
                    earning.token_name,
                    earning.token_value,
                    earning.url,
                    ])

            return response
        elif request.POST.get('disconnect', False):
            profile.github_access_token = ''
            profile = record_form_submission(request, profile, 'account-disconnect')
            profile.email = ''
            profile.save()
            create_user_action(profile.user, 'account_disconnected', request)
            redirect_url = f'https://www.github.com/settings/connections/applications/{settings.GITHUB_CLIENT_ID}'
            logout(request)
            logout_redirect = redirect(redirect_url)
            logout_redirect['Cache-Control'] = 'max-age=0 no-cache no-store must-revalidate'
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
                handle=profile.handle.lower(),
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
            eth_address = request.POST.get('preferred_payout_address', '')
            if not is_valid_eth_address(eth_address):
                eth_address = profile.preferred_payout_address
            profile.preferred_payout_address = eth_address
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
                handle=profile.handle.lower(),
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


@staff_member_required
def org_settings(request):
    """Display and save user's Account settings.

    Returns:
        TemplateResponse: The user's Account settings template response.
    """
    msg = ''
    profile, es, user, is_logged_in = settings_helper_get_auth(request)
    current_scopes = []

    if not user or not profile or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect

    social_auth = user.social_auth.first()
    if social_auth and social_auth.extra_data:
        current_scopes = social_auth.extra_data.get('scope').split(',')
    orgs = get_orgs_perms(profile)
    context = {
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'active': '/settings/organizations',
        'title': _('Organizations Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'orgs': orgs,
        'profile': profile,
        'msg': msg,
        'current_scopes': current_scopes,
    }
    return TemplateResponse(request, 'settings/organizations.html', context)


def tax_settings(request):
    """Display and save user's Tax settings.

    Returns:
        TemplateResponse: The user's Tax settings template response.

    """
    msg = ''
    profile, es, user, is_logged_in = settings_helper_get_auth(request)

    if not user or not profile or not is_logged_in:
        login_redirect = redirect('/login/github?next=' + request.get_full_path())
        return login_redirect
        
    # location  dict is not empty
    location = ''
    if profile.location:
        location_components = json.loads(profile.location)
        if 'locality' in location_components:
            location += location_components['locality']
        if 'country' in location_components:
            country = location_components['country']
            if location:
                location += ', ' + country
            else:
                location += country
        if 'code' in location_components:
            code = location_components['code']
            if location:
                location += ', ' + code
            else:
                location += code
    # location dict is empty
    else:
        # set it to the last location registered for the user
        location_components = profile.locations[-1]
        if 'city' in location_components:
            if location_components['city']:
                location += location_components['city']
        if 'country_name' in location_components:
            if location_components['country_name']:
                country_name = location_components['country_name']
                if location:
                    location += ', ' + country_name
                else:
                    location += country_name
        if 'country_code' in location_components:
            if location_components['country_code']:
                country_code = location_components['country_code']
                if location:
                    location += ', ' + country_code
                else:
                    location += country_code
    
    #address is not empty
    if profile.address:
        address = profile.address   
    else:
        address = ''
    
    g_maps_api_key = "AIzaSyBaJ6gEXMqjw0Y7d5Ps9VvelzOOvfV6BvQ"
        
    context = {
        'is_logged_in': is_logged_in,
        'nav': 'home',
        'active': '/settings/tax',
        'title': _('Tax Settings'),
        'navs': get_settings_navs(request),
        'es': es,
        'profile': profile,
        'location': location,
        'address': address,
        'api_key': g_maps_api_key,
        'msg': msg,
    }
    return TemplateResponse(request, 'settings/tax.html', context)


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


    product = request.GET.get('product', 'all')
    keyword_search = request.GET.get('keyword', '')
    keyword_search = '' if keyword_search == 'all' else keyword_search
    limit = int(request.GET.get('limit', 50))
    cadence = request.GET.get('cadence', 'weekly')

    # backwards compatibility fix for old inbound links
    for ele in cadences:
        key = key.replace(f"{ele}_", '')

    titles = {
        f'payers': _('Top Funders'),
        f'earners': _('Top Earners'),
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
    all_ranks = LeaderboardRank.objects.filter(leaderboard=which_leaderboard, product=product)
    if keyword_search:
        all_ranks = all_ranks.filter(tech_keywords__icontains=keyword_search)

    amount = all_ranks.values_list('amount').annotate(Max('amount')).order_by('-amount')
    ranks = all_ranks.filter(active=True)
    items = ranks.order_by('-amount')

    top_earners = ''
    technologies = set()
    for profile_keywords in ranks.values_list('tech_keywords'):
        for techs in profile_keywords:
            for tech in techs:
                technologies.add(tech)

    flags = []
    if key == 'countries':
        for item in items[0:limit]:
            country = item.at_ify_username
            code = 'us'
            try:
                country_index = COUNTRY_NAMES.index(country)
                code = COUNTRY_CODES[country_index]
            except:
                print(f'Error: {FLAG_ERR_MSG}')
            flags.append(f'{FLAG_API_LINK}/{code}/{FLAG_STYLE}/{FLAG_SIZE}.png')

    if amount:
        amount_max = amount[0][0]
        top_earners = ranks.order_by('-amount')[0:5].values_list('github_username', flat=True)
        top_earners = ['@' + username for username in top_earners]
        top_earners = f'The top earners of this period are {", ".join(top_earners)}'
    else:
        amount_max = 0

    profile_keys = ['tokens', 'keywords', 'cities', 'countries', 'continents']
    is_linked_to_profile = any(sub in key for sub in profile_keys)

    rankdata = \
        PivotDataPool(
           series=
            [{'options': {
               'source': all_ranks,
                'legend_by': 'github_username',
                'categories': ['created_on'],
                'top_n_per_cat': 10,
                },
              'terms': {
                'amount': Avg('amount'),
                }}
             ])

    #Step 2: Create the Chart object
    cht = PivotChart(
            datasource = rankdata,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False
                  },
                'terms': 
                    ['amount']
                
            }],
            chart_options =
              {'legend': {
                   'enabled': False},
               'title': {
                   'text': 'Leaderboard'},
               'xAxis': {
                    'title': {
                       'text': 'Time'
                       },
                    'labels': {
                       'enabled': False
                       }
                    },
                }
            )

    cadence_ui = cadence if cadence != 'all' else 'All-Time'
    product_ui = product.capitalize() if product != 'all' else ''
    page_title = f'{cadence_ui.title()} {keyword_search.title()} {product_ui} Leaderboard: {title.title()}'
    last_update = items[0].created_on if len(items) else None
    next_update = last_update + timezone.timedelta(days=7) if last_update else None
    if next_update and next_update < timezone.now():
        next_update = timezone.now() + timezone.timedelta(days=1)

    context = {
        'key': key,
        'items': items[0:limit],
        'dual_list': zip(items[0:limit], flags),
        'nav': 'home',
        'cht': cht,
        'titles': titles,
        'cadence': cadence,
        'last_update': last_update,
        'next_update': next_update,
        'product': product,
        'products': ['kudos', 'grants', 'bounties', 'tips', 'all'],
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

def trending_quests():
    from quests.models import QuestAttempt
    cutoff_date = timezone.now() - timezone.timedelta(days=7)
    quests = [ele.quest for ele in QuestAttempt.objects.order_by('?').all()[0:10]]
    return quests

def trending_avatar():
    from avatar.models import AvatarTheme
    cutoff_date = timezone.now() - timezone.timedelta(days=45)
    avatar = AvatarTheme.objects.order_by("?")
    return avatar.first()

def quest_of_the_day():
    quest = trending_quests()[0]
    return quest

def upcoming_grant():
    grant = Grant.objects.order_by('-weighted_shuffle').first()
    return grant

def upcoming_hackathon():
    try:
        return HackathonEvent.objects.filter(end_date__gt=timezone.now(), visible=True).order_by('-start_date')
    except HackathonEvent.DoesNotExist:
        try:
            return [HackathonEvent.objects.filter(start_date__gte=timezone.now(), visible=True).order_by('start_date').first()]
        except HackathonEvent.DoesNotExist:
            return None

def latest_activities(user):
    from retail.views import get_specific_activities
    from townsquare.tasks import increment_view_counts
    cutoff_date = timezone.now() - timezone.timedelta(days=1)
    activities = get_specific_activities('connect', 0, user, 0)[:4]
    activities_pks = list(activities.values_list('pk', flat=True))
    increment_view_counts.delay(activities_pks)
    return activities

def static_proxy(request, filepath):
    # TODO: if this is ever extended with a dynamic filepath
    # make sure it is VERY VERY security conscious
    filepath = 'assets/landingpage/fusion/fusion-interface.svg'
    content_type = 'image/svg+xml'
    with open(filepath) as file:
        response = HttpResponse(file, content_type=content_type)
        return response

@staff_member_required
def new_bounty_daily_preview(request):
    profile = request.user.profile
    keywords = profile.keywords
    hours_back = 2000

    from marketing.mails import get_bounties_for_keywords
    new_bounties, all_bounties = get_bounties_for_keywords(keywords, hours_back)
    max_bounties = 5
    if len(new_bounties) > max_bounties:
        new_bounties = new_bounties[0:max_bounties]
    response_html, _ = render_new_bounty(settings.CONTACT_EMAIL, new_bounties, old_bounties='', offset=3, quest_of_the_day=quest_of_the_day(), upcoming_grant=upcoming_grant(), upcoming_hackathon=upcoming_hackathon(), latest_activities=latest_activities(request.user))
    return HttpResponse(response_html)
