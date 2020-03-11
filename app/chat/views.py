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

from chat.tasks import get_chat_url
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

import logging
from marketing.models import Stat

logger = logging.getLogger(__name__)


def chat(request):
    """Render chat landing page response."""

    try:
        users_online_count = Stat.objects.filter(key='chat_active_users').order_by('pk').first()
        users_total_count = Stat.objects.filter(key='chat_total_users').order_by('pk').first()

        users_online_count = users_online_count if users_online_count is not None else 'N/A'
        users_total_count = users_total_count if users_total_count is not None else 'N/A'

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
