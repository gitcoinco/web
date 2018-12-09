from django.contrib.staticfiles.templatetags.staticfiles import static
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from inbox.models import Notification
from django.contrib.auth import get_user_model
import json
from django.http import JsonResponse, HttpResponseForbidden


def notifications(request):
    """Handle all notifications."""
    if request.method == 'GET':
        profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
        if profile is None:
            return HttpResponseForbidden('Not Allowed')

        all_notifs = Notification.objects.filter(to_user_id=request.user.id).order_by('id')[::-1]
        params = []
        for i in all_notifs:
            new_notif = i.to_standard_dict()
            new_notif['created_on'] = i.created_on
            new_notif['modified_on'] = i.modified_on
            new_notif['username'] = get_user_model().objects.get(id=new_notif['from_user_id']).username

            params.append(new_notif)

        return JsonResponse(params, status=200, safe=False)

    else:
        return HttpResponseForbidden('Not Allowed')


def delete_notifications(request):
    """For deleting a notification"""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    if request.method == 'DELETE' and profile is not None:
        params = dict()
        params['success'] = []
        try:
            req_body = json.loads(request.body.decode('utf-8'))
        except:
            pass
        if 'delete' in req_body:
            for i in req_body['delete']:
                entry = Notification.objects.filter(id=i)
                if entry.to_user_id == request.user.id and len(entry) != 0:
                    entry.delete()
                    params['success'].append(True)
                else:
                    params['success'].append(False)
        return JsonResponse(params, status=200)

    else:
        return HttpResponseForbidden('Not Allowed')


def unread_notifications(request):
    """Mark a notification as unread"""
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
                if entry.to_user_id == request.user.id and len(entry) != 0:
                    obj = entry[0]
                    obj.is_read = False
                    obj.save()
                    params['success'].append(True)
                else:
                    params['success'].append(False)
        return JsonResponse(params, status=200)

    else:
        return HttpResponseForbidden('Not Allowed')


def read_notifications(request):
    """Mark a notification as read"""
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
                if entry.to_user_id == request.user.id and len(entry) != 0:
                    obj = entry[0]
                    obj.is_read = True
                    obj.save()
                    params['success'].append(True)
                else:
                    params['success'].append(False)
        return JsonResponse(params, status=200)

    else:
        return HttpResponseForbidden('Not Allowed')


def inbox(request):

    context = {
        'is_outside': True,
        'active': 'inbox',
        'title': 'inbox',
        'card_title': _('Each Kudos is a unique work of art.'),
        'card_desc': _('It can be sent to highlight, recognize, and show appreciation.'),
        'avatar_url': static('v2/images/kudos/assets/kudos-image.png'),
    }
    return TemplateResponse(request, 'inbox.html', context)
