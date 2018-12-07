from django.shortcuts import render
from django.core.paginator import Paginator
from inbox.models import Notification
from django.utils import timezone
from django.contrib.auth import get_user_model

from django.http import JsonResponse, HttpResponseForbidden

def inbox(request):
    """Handle grants explorer."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    if profile is None:
        return HttpResponseForbidden('Not Allowed')

    all_notifs = Notification.objects.filter(to_user_id=get_user_model().objects.get(username=profile).id)
    params = []
    for i in all_notifs:
        new_notif = i.to_standard_dict()
        new_notif['created_on'] = i.created_on
        new_notif['username'] = get_user_model().objects.get(id=new_notif['from_user_id']).username

        params.append(new_notif)

    return JsonResponse(params, status=200, safe=False)
