# -*- coding: utf-8 -*-
"""Define bounty request views.

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

from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt

from linkshortener.models import Link
from marketing.mails import new_bounty_request
from ratelimit.decorators import ratelimit

from .forms import BountyRequestForm
from .models import BountyRequest


@ratelimit(key='ip', rate='5/m', method=ratelimit.UNSAFE, block=True)
@csrf_exempt
def bounty_request(request):
    user = request.user if request.user.is_authenticated else None
    profile = request.user.profile if user and hasattr(request.user, 'profile') else None

    comments_prefill = None
    if request.GET.get('code', False):
        code = request.GET.get('code')
        ls = Link.objects.filter(shortcode=code, comments__icontains='Gitcoin Request Coin', uses__lt=5)
        if ls.exists():
            ls = ls.first()
            comments_prefill = f"{ls.comments} : {ls.shortcode}"

    if request.body:
        if not user or not profile or not profile.handle:
            return JsonResponse(
                {'error': _('You must be Authenticated via Github to use this feature!')},
                status=401)

        try:
            result = BountyRequestForm(json.loads(request.body))
            if not result.is_valid():
                raise
        except:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        model = result.save(commit=False)
        model.requested_by = profile
        model.save()
        new_bounty_request(model)
        return JsonResponse({'msg': _('Bounty Request received.')}, status=200)

    form = BountyRequestForm()
    params = {
        'form': form,
        'title': _('Request a Bounty'),
        'comments_prefill': comments_prefill,
        'card_title': _('Gitcoin Requests'),
        'card_desc': _('Have an open-source issue that you think would benefit the community? '
                       'Suggest it be given a bounty!')
    }

    return TemplateResponse(request, 'bounty_request_form.html', params)
