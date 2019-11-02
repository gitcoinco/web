# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_GET


@login_required
@require_GET
def embed(request):
    """Handle the embed view."""

    context = {
        'is_outside': True,
        'title': 'GitCoin Chat',
        'card_title': _('GitCoin Chat'),
        'card_desc': _('Communicate with the community'),
    }
    return TemplateResponse(request, 'embed.html', context)
