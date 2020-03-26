# -*- coding: utf-8 -*-
"""Define view for the inbox app.

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

import logging

from django.conf import settings
from django.http import Http404, JsonResponse
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from app.redis_service import RedisService
from chat.tasks import get_chat_url, get_driver
from marketing.models import Stat

logger = logging.getLogger(__name__)

def chat_presence(request):
    """Sets user presence on mattermost."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'OK'})

    profile = request.user.profile
    if not profile.chat_id:
        return JsonResponse({'status': 'OK'})

    # setup driver
    driver = get_driver()

    # determine current status/ should we set the user as online in mm?
    current_status = driver.client.post('/users/status/ids', [profile.chat_id])
    manual = current_status[0]['manual']
    current_status = current_status[0]['status']
    set_status = current_status == 'offline' or manual or settings.DEBUG

    # if so, make it so
    if set_status:
        new_status = 'online'
        if current_status in ['away', 'dnd']:
            new_status = current_status
        driver.client.put(f'/users/{profile.chat_id}/status', {'user_id': profile.chat_id, 'status': new_status})
        # set a marker of when this user was last seen..
        # so that get_user_prsence can clean it up later
        redis = RedisService().redis
        redis.set(profile.chat_id, timezone.now().timestamp())
        redis.set(f"chat:{profile.chat_id}", new_status)

    return JsonResponse({'status': 'OK'})


def chat(request):
    """Render chat landing page response."""

    try:
        users_online_count = Stat.objects.filter(key='chat_active_users').order_by('pk').first()
        users_total_count = Stat.objects.filter(key='chat_total_users').order_by('pk').first()

        users_online_count = users_online_count.val if users_online_count is not None else 'N/A'
        users_total_count = users_total_count.val if users_total_count is not None else 'N/A'

    except Exception as e:
        logger.error(str(e))
        users_online_count = 'N/A'
        users_total_count = 'N/A'
    context = {
        'users_online': users_online_count,
        'users_count': users_total_count,
        'title': "Chat",
        'cards_desc': f"Gitcoin chat has {users_online_count} users online now!"
    }

    return TemplateResponse(request, 'chat.html', context)


def embed(request):
    """Handle the chat embed view."""

    chat_url = get_chat_url(front_end=True)

    context = {
        'is_outside': True,
        'active': 'chat',
        'title': 'Chat',
        'card_title': _('Community Chat'),
        'card_desc': _('Come chat with the community'),
        'chat_url': chat_url
    }

    return TemplateResponse(request, 'embed.html', context)
