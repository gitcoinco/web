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

from django.conf import settings
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from marketing.models import Stat


def chat(request):
    """Render chat landing page response."""

    try:
        users_online_count = Stat.objects.get(key='chat_active_users')
        users_total_count = Stat.objects.get(key='chat_total_users')

    except Exception as e:
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

    chat_url = settings.CHAT_URL
    if settings.CHAT_PORT not in [80, 443]:
        chat_url = f'http://{settings.CHAT_URL}:{settings.CHAT_PORT}'
    else:
        chat_url = f'https://{chat_url}'
    context = {
        'is_outside': True,
        'active': 'chat',
        'title': 'Chat',
        'card_title': _('Community Chat'),
        'card_desc': _('Come chat with the community'),
        'chat_url': chat_url
    }

    return TemplateResponse(request, 'embed.html', context)
