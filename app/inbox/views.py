from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.paginator import Paginator
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from inbox.models import Notification

from django.http import JsonResponse, HttpResponseForbidden

def notifications(request):
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
