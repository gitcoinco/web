import json
from inbox.models import Notification
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt


def notifications(request):
    """Handle all notifications."""
    if request.method == 'GET':
        profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
        if profile is None:
            return HttpResponseForbidden('Not Allowed')
        limit = 10
        page = 1
        if 'limit' in request.GET:
            limit = int(request.GET['limit'])
        if 'page' in request.GET:
            page = int(request.GET['page'])
        print(limit, page)
        all_notifs = Notification.objects.filter(to_user_id=request.user.id).order_by('id')[::-1]
        params = dict()
        all_pages = Paginator(all_notifs, limit)
        if page > 0 and page <= all_pages.num_pages:
            all_notifications = []
            for i in all_pages.page(page):
                new_notif = i.to_standard_dict()
                new_notif['created_on'] = i.created_on
                new_notif['modified_on'] = i.modified_on
                new_notif['username'] = get_user_model().objects.get(id=new_notif['from_user_id']).username

                all_notifications.append(new_notif)
            params['data'] = all_notifications
            params['has_next'] = all_pages.page(page).has_next()
            params['num_notifications'] = all_pages.count
            params['num_pages'] = all_pages.num_pages
        else:
            params['total_pages'] = all_pages.num_pages
        return JsonResponse(params, status=200, safe=False)

    else:
        return HttpResponseForbidden('Not Allowed')


@csrf_exempt
def delete_notifications(request):
    """For deleting a notification."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    if request.method == 'DELETE' and profile is not None:
        params = {'success': []}
        try:
            req_body = json.loads(request.body.decode('utf-8'))
        except:
            pass
        if 'delete' in req_body:
            for i in req_body['delete']:
                entry = Notification.objects.filter(id=i)
                if len(entry) != 0:
                    obj = entry[0]
                    if obj.to_user_id.id == request.user.id:
                        obj.delete()
                        params['success'].append(True)
                    else:
                        params['success'].append(False)
                else:
                    params['success'].append(False)
        return JsonResponse(params, status=200)

    else:
        return HttpResponseForbidden('Not Allowed')


@csrf_exempt
def unread_notifications(request):
    """Mark a notification as unread."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    if request.method == 'PUT' and profile is not None:
        params = dict()
        params['success'] = []
        try:
            req_body = json.loads(request.body.decode('utf-8'))
        except:
            pass
        if 'unread' in req_body:
            for i in req_body['unread']:
                entry = Notification.objects.filter(id=i)
                if len(entry) != 0:
                    obj = entry[0]
                    if obj.to_user_id.id == request.user.id:
                        obj.is_read = False
                        obj.save()
                        params['success'].append(True)
                    else:
                        params['success'].append(False)
                else:
                    params['success'].append(False)
        return JsonResponse(params, status=200)

    else:
        return HttpResponseForbidden('Not Allowed')


@csrf_exempt
def read_notifications(request):
    """Mark a notification as read."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    if request.method == 'PUT' and profile is not None:
        params = dict()
        params['success'] = []
        try:
            req_body = json.loads(request.body.decode('utf-8'))
        except:
            pass
        if 'read' in req_body:
            for i in req_body['read']:
                entry = Notification.objects.filter(id=i)
                if len(entry) != 0:
                    obj = entry[0]
                    if obj.to_user_id.id == request.user.id:
                        obj.is_read = True
                        obj.save()
                        params['success'].append(True)
                    else:
                        params['success'].append(False)
                else:
                    params['success'].append(False)
        return JsonResponse(params, status=200)

    else:
        return HttpResponseForbidden('Not Allowed')


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
