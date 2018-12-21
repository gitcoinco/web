import json
from inbox.models import Notification
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
@require_GET
def notifications(request):
    """Handle all notifications."""
    limit = int(request.GET.get('limit', 10))
    page = int(request.GET.get('page', 1))
    all_notifs = Notification.objects.filter(to_user_id=request.user.id).order_by('-id')
    params = dict()
    all_pages = Paginator(all_notifs, limit)
    if page > 0 and page <= all_pages.num_pages:
        all_notifications = []
        for i in all_pages.page(page):
            new_notif = i.to_standard_dict()
            new_notif['username'] = i.from_user.username
            all_notifications.append(new_notif)
        params['data'] = all_notifications
        params['has_next'] = all_pages.page(page).has_next()
        params['num_notifications'] = all_pages.count
        params['num_pages'] = all_pages.num_pages
    else:
        params['total_pages'] = all_pages.num_pages
    return JsonResponse(params, status=200, safe=False)


@login_required
@require_http_methods(['DELETE'])
@csrf_exempt
def delete_notifications(request):
    """For deleting a notification."""
    params = {'success': []}
    try:
        req_body = json.loads(request.body.decode('utf-8'))
    except:
        pass
    if 'delete' in req_body:
        for i in req_body['delete']:
            try:
                obj = Notification.objects.get(id=i)
                if obj.to_user.id == request.user.id:
                    obj.delete()
                    params['success'].append(True)
                else:
                    params['success'].append(False)
            except Notification.DoesNotExist:
                params['success'].append(False)
    return JsonResponse(params, status=200)


@login_required
@require_http_methods(['PUT'])
@csrf_exempt
def unread_notifications(request):
    """Mark a notification as unread."""
    params = {'success': []}
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
                    params['success'].append(True)
                else:
                    params['success'].append(False)
            except Notification.DoesNotExist:
                params['success'].append(False)
    return JsonResponse(params, status=200)


@login_required
@require_http_methods(['PUT'])
@csrf_exempt
def read_notifications(request):
    """Mark a notification as read."""
    params = {'success': []}
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
                    params['success'].append(True)
                else:
                    params['success'].append(False)
            except Notification.DoesNotExist:
                params['success'].append(False)
    return JsonResponse(params, status=200)


def inbox(request):
    """Handles the inbox view."""
    context = {
        'is_outside': True,
        'active': 'inbox',
        'title': 'inbox',
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos/assets/kudos-image.png'),
    }
    return TemplateResponse(request, 'inbox.html', context)
