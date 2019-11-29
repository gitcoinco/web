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
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _
from django.views.decorators.clickjacking import xframe_options_exempt

import requests


def embed(request):
    """Handle the chat embed view."""

    is_staff = request.user.is_staff if request.user.is_authenticated else False

    # if not is_staff:
    #     context = dict(active='error', code=404, title="Error {}".format(404))
    #     return TemplateResponse(request, 'error.html', context, status=404)

    context = {
        'is_outside': True,
        'active': 'chat',
        'title': 'Chat',
        'card_title': _('Community Chat'),
        'card_desc': _('Come chat with the community'),
        'chat_url': settings.CHAT_URL
    }

    return TemplateResponse(request, 'embed.html', context)
