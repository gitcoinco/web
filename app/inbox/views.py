from django.shortcuts import render
from django.core.paginator import Paginator
from inbox.models import Notification
from django.utils import timezone

from django.http import JsonResponse, HttpResponseForbidden

def inbox(request):
    """Handle grants explorer."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    limit = request.GET.get('limit', 25)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', '-created_on')

    if profile is None:
        return HttpResponseForbidden('Not Allowed')

    '''_notifications = Notification.objects.filter(to_user_id=profile.id).order_by(sort)

    if request.method == 'POST':
        sort = request.POST.get('sort_option', '-created_on')
        _notifications = Notification.objects.order_by(sort)

    paginator = Paginator(_notifications, limit)
    notifications = paginator.get_page(page)
    '''
    all_notifs = Notification.objects.all()
    params = []
    for i in all_notifs:
        new_notif = i.to_standard_dict()
        new_notif['created_on'] = i.created_on
        params.append(new_notif)

    return JsonResponse(params, status=200, safe=False)
