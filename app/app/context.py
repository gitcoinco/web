# -*- coding: utf-8 -*-
"""Define additional context data to be passed to any request.

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
import json

from django.conf import settings
from django.utils import timezone

from dashboard.models import Tip


def insert_settings(request):
    """Handle inserting pertinent data into the current context."""
    from marketing.utils import get_stat
    try:
        num_slack = int(get_stat('slack_users'))
    except Exception:
        num_slack = 0
    if num_slack > 1000:
        num_slack = f'{str(round((num_slack) / 1000, 1))}k'

    user_is_authenticated = request.user.is_authenticated
    profile = request.user.profile if user_is_authenticated and hasattr(request.user, 'profile') else None
    email_subs = profile.email_subscriptions if profile else None
    email_key = email_subs.first().priv if user_is_authenticated and email_subs and email_subs.exists() else ''

    context = {
        'mixpanel_token': settings.MIXPANEL_TOKEN,
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        'num_slack': num_slack,
        'github_handle': request.user.username if user_is_authenticated else False,
        'email': request.user.email if user_is_authenticated else False,
        'name': request.user.get_full_name() if user_is_authenticated else False,
        'sentry_address': settings.SENTRY_ADDRESS,
        'raven_js_version': settings.RAVEN_JS_VERSION,
        'raven_js_dsn': settings.SENTRY_JS_DSN,
        'release': settings.RELEASE,
        'env': settings.ENV,
        'email_key': email_key,
        'profile_id': profile.id if profile else '',
        'hotjar': settings.HOTJAR_CONFIG,
        'ipfs_config': {
            'host': settings.IPFS_HOST,
            'port': settings.IPFS_API_PORT,
            'protocol': settings.IPFS_API_SCHEME,
            'root': settings.IPFS_API_ROOT,
        },
        'access_token': profile.access_token if profile else '',
        'is_staff': request.user.is_staff if user_is_authenticated else False,
        'is_moderator': profile.is_moderator if profile else False,
    }
    context['json_context'] = json.dumps(context)

    if context['github_handle']:
        context['unclaimed_tips'] = Tip.objects.filter(
            expires_date__gte=timezone.now(),
            receive_txid='',
            username__iexact=context['github_handle'],
            web3_type='v3',
        ).exclude(txid='')
        if not settings.DEBUG:
            context['unclaimed_tips'] = context['unclaimed_tips'].filter(network='mainnet')

    return context
