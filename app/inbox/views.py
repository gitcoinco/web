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

import json

from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from inbox.models import Notification


@login_required
@require_GET
def notifications(request):
    """Handle all notifications."""

    limit = int(request.GET.get('limit', 10))
    page = int(request.GET.get('page', 1))
    all_notifs = Notification.objects.filter(to_user_id=request.user.id).order_by('-id')
    params = dict()
    all_pages = Paginator(all_notifs, limit)
    if page <= 0 or page > all_pages.num_pages:
        page = 1
    all_notifications = []
    for i in all_pages.page(page):
        new_notif = i.to_standard_dict()
        new_notif['username'] = i.from_user.username
        all_notifications.append(new_notif)
    params['data'] = all_notifications
    params['has_next'] = all_pages.page(page).has_next()
    params['count'] = all_pages.count
    params['num_pages'] = all_pages.num_pages
    return JsonResponse(params, status=200, safe=False)


@login_required
@require_http_methods(['DELETE'])
@csrf_exempt
def delete_notifications(request):
    """For deleting a notification."""

    try:
        req_body = json.loads(request.body.decode('utf-8'))
    except:
        pass
    if 'delete' in req_body:
        Notification.objects.filter(
            id__in=req_body['delete'],
            to_user=request.user
        ).delete()
    return HttpResponse(status=204)


@login_required
@require_http_methods(['PUT'])
@csrf_exempt
def unread_notifications(request):
    """Mark a notification as unread."""

    try:
        req_body = json.loads(request.body.decode('utf-8'))
    except:
        pass
    if 'unread' in req_body:
        for i in req_body['unread']:
            try:
                obj = Notification.objects.get(id=i)
                if obj.to_user.id == request.user.id:
                    obj.is_read = False
                    obj.save()
            except Notification.DoesNotExist:
                pass
    return HttpResponse(status=204)


@login_required
@require_http_methods(['PUT'])
@csrf_exempt
def read_notifications(request):
    """Mark a notification as read."""

    try:
        req_body = json.loads(request.body.decode('utf-8'))
    except:
        pass
    if 'read' in req_body:
        for i in req_body['read']:
            try:
                obj = Notification.objects.get(id=i)
                if obj.to_user.id == request.user.id:
                    obj.is_read = True
                    obj.save()
            except Notification.DoesNotExist:
                pass
    return HttpResponse(status=204)


def inbox(request):
    """Handle the inbox view."""

    context = {
        'is_outside': True,
        'active': 'inbox',
        'title': 'Inbox',
        'card_title': _('Inbox notifications'),
        'card_desc': _('Manage all your notifications.'),
        'avatar_url': static('v2/images/helmet.png'),
    }
    return TemplateResponse(request, 'inbox.html', context)
