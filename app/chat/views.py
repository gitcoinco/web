# -*- coding: utf-8 -*-
"""Define view for the inbox app.

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


from django.conf import settings
from django.templatetags.static import static
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
import requests
from django.views.decorators.clickjacking import xframe_options_exempt


def embed(request):
    """Handle the inbox view."""

    # check to see if currently a user in the chat app,
    # if so don't include their invite url just send them to the app login


    context = {
        'is_outside': True,
        'active': 'chat',
        'title': 'Chat',
        'card_title': _('Community Chat'),
        'card_desc': _('Come chat with the community'),
        'avatar_url': static('v2/images/helmet.png'),
        'is_chat_user': False,
        'chat_url': settings.CHAT_URL
    }

    return TemplateResponse(request, 'embed.html', context)
