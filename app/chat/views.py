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

from chat.tasks import get_driver


def chat(request):
    """Render chat landing page response."""

    try:
        chat_driver = get_driver()

        chat_stats = chat_driver.teams.get_team_stats(settings.GITCOIN_CHAT_TEAM_ID)
        if 'message' not in chat_stats:
            users_online = chat_stats['active_member_count']
        else:
            users_online = 'N/A'
    except Exception as e:
        print(str(e))
        users_online = 'N/A'
    context = {
        'users_online': users_online,
        'title': "Chat",
        'cards_desc': f"Gitcoin chat has {users_online} users online now!"
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
