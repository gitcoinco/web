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

from app.utils import get_location_from_ip
from dashboard.models import Activity, Tip, UserAction
from dashboard.utils import _get_utm_from_cookie
from kudos.models import KudosTransfer
from retail.helpers import get_ip

RECORD_VISIT_EVERY_N_SECONDS = 60 * 60


def preprocess(request):
    """Handle inserting pertinent data into the current context."""

    # make lbcheck super lightweight
    if request.path == '/lbcheck':
        return {}

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
    if user_is_authenticated and profile and profile.pk:
        # what actions to take?
        record_join = not profile.last_visit
        record_visit = not profile.last_visit or profile.last_visit < (
            timezone.now() - timezone.timedelta(seconds=RECORD_VISIT_EVERY_N_SECONDS)
        )

        if record_visit:
            ip_address = get_ip(request)
            profile.last_visit = timezone.now()
            profile.save()
            metadata = {'useragent': request.META['HTTP_USER_AGENT'], }
            UserAction.objects.create(
                user=request.user,
                profile=profile,
                action='Visit',
                location_data=get_location_from_ip(ip_address),
                ip_address=ip_address,
                utm=_get_utm_from_cookie(request),
                metadata=metadata,
            )

        if record_join:
            Activity.objects.create(profile=profile, activity_type='joined')

    context = {
        'STATIC_URL': settings.STATIC_URL,
        'MEDIA_URL': settings.MEDIA_URL,
        'num_slack': num_slack,
        'github_handle': request.user.username if user_is_authenticated else False,
        'email': request.user.email if user_is_authenticated else False,
        'name': request.user.get_full_name() if user_is_authenticated else False,
        'raven_js_version': settings.RAVEN_JS_VERSION,
        'raven_js_dsn': settings.SENTRY_JS_DSN,
        'release': settings.RELEASE,
        'env': settings.ENV,
        'email_key': email_key,
        'profile_id': profile.id if profile else '',
        'hotjar': settings.HOTJAR_CONFIG,
        'ipfs_config': {
            'host': settings.JS_IPFS_HOST,
            'port': settings.IPFS_API_PORT,
            'protocol': settings.IPFS_API_SCHEME,
            'root': settings.IPFS_API_ROOT,
        },
        'access_token': profile.access_token if profile else '',
        'is_staff': request.user.is_staff if user_is_authenticated else False,
        'is_moderator': profile.is_moderator if profile else False,
        'persona_is_funder': profile.persona_is_funder if profile else False,
        'persona_is_hunter': profile.persona_is_hunter if profile else False,
    }
    context['json_context'] = json.dumps(context)

    if context['github_handle']:
        context['unclaimed_tips'] = Tip.objects.filter(
            expires_date__gte=timezone.now(),
            receive_txid='',
            username__iexact=context['github_handle'],
            web3_type='v3',
        ).send_happy_path()
        context['unclaimed_kudos'] = KudosTransfer.objects.filter(
            receive_txid='', username__iexact="@" + context['github_handle'], web3_type='v3',
        ).send_happy_path()

        if not settings.DEBUG:
            context['unclaimed_tips'] = context['unclaimed_tips'].filter(network='mainnet')
            context['unclaimed_kudos'] = context['unclaimed_kudos'].filter(network='mainnet')

    return context
