from inbox.models import Notification
from django.contrib.auth import get_user_model
import json
from django.http import JsonResponse, HttpResponseForbidden

def inbox(request):
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
            new_notif['username'] = get_user_model().objects.get(id=new_notif['from_user_id']).username

            params.append(new_notif)

        return JsonResponse(params, status=200, safe=False)

    else:
        return HttpResponseForbidden('Not Allowed')


def delete_notification(request):
    """For deleting a notification"""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    if request.method == 'DELETE' and profile is not None:
        params = dict()
        params['success'] = []
        for i in json.loads(request.body.decode('utf-8'))['delete']:
            entry = Notification.objects.filter(id=i)
            if entry.to_user_id == request.user.id and len(entry) != 0:
                entry.delete()
                params['success'].append(True)
            else:
                params['success'].append(False)
        return JsonResponse(params, status=200)

    else:
        return HttpResponseForbidden('Not Allowed')
