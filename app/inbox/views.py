from django.shortcuts import render
from django.core.paginator import Paginator
from inbox.models import Notification
from django.utils import timezone

from django.http import Http404, JsonResponse, HttpResponseForbidden

def inbox(request):
    """Handle grants explorer."""
    profile = request.user.profile if request.user.is_authenticated and request.user.profile else None
    limit = request.GET.get('limit', 25)
    page = request.GET.get('page', 1)
    sort = request.GET.get('sort_option', '-created_on')

    if profile == None:
        return HttpResponseForbidden('Not Allowed')

    '''_notifications = Notification.objects.filter(to_user_id=profile.id).order_by(sort)

    if request.method == 'POST':
        sort = request.POST.get('sort_option', '-created_on')
        _notifications = Notification.objects.order_by(sort)

    paginator = Paginator(_notifications, limit)
    notifications = paginator.get_page(page)
    '''
    all_notifs = Notification.objects.all()
    if len(all_notifs) == 0:
        a = Notification(created_on=timezone.now(), to_user_id=1, from_user_id=3, username="owocki",
            CTA_URL="http://localhost:8000",
            CTA_Text="You haven’t responded to #2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…",
            message_html="You haven’t responded to <b>#2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…</b>" )
        a.save()
        a = Notification(created_on=timezone.now(), to_user_id=1, from_user_id=3, username="octavioamu",
            CTA_URL="http://localhost:8000",
            CTA_Text="You haven’t responded to #2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…",
            message_html="You haven’t responded to <b>#2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…</b>" )
        a.save()
    params = []
    for i in all_notifs:
        params.append(i.to_standard_dict())


    '''params = [{'id': 1,
                'modified_on': '2018-12-04T20:32:48.524Z',
                'created_on': '2018-12-04T20:32:48.524Z',
                'to_user_id': 1,
                'from_user_id': 3,
                'username': 'octavioamu',
                'CTA_URL': 'http://localhost:8000',
                'CTA_Text': 'You haven’t responded to #2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…',
                'message_html': 'You haven’t responded to <b>#2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…</b>',
                'is_read': False
            },
            {'id': 2,
                'modified_on':'2018-12-04T04:39:36.662Z',
                'created_on': '2018-12-04T04:39:36.662Z',
                'to_user_id': 1,
                'from_user_id': 3,
                'username': 'owocki',
                'CTA_URL': 'http://localhost:8000',
                'CTA_Text': 'You haven’t responded to #2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…',
                'message_html': 'You haven’t responded to <b>#2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…</b>',
                'is_read': False
            },
            {'id': 3,
                'modified_on': '2018-12-04T11:39:36.662Z',
                'created_on': '2018-12-04T11:39:36.662Z',
                'to_user_id': 1,
                'from_user_id': 3,
                'username': 'octavioamu',
                'CTA_URL': 'http://localhost:8000',
                'CTA_Text': 'You haven’t responded to #2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…',
                'message_html': 'You haven’t responded to <b>#2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…</b>',
                'is_read': False
            },
            {'id': 4,
                'modified_on': '2018-12-04T11:39:36.662Z',
                'created_on': '2018-12-04T11:39:36.662Z',
                'to_user_id': 1,
                'from_user_id': 3,
                'username': 'octavioamu',
                'CTA_URL': 'http://localhost:8000',
                'CTA_Text': 'You haven’t responded to #2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…',
                'message_html': 'You haven’t responded to <b>#2186: [Design] Show Remarketed Issues… in 3 days. Please submit a WIP…</b>',
                'is_read': False
            },


    ]'''
    return JsonResponse(params, status=200, safe=False)
