from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Activity
from ratelimit.decorators import ratelimit

from .models import Comment, Like


def index(request):

    # TODO: temporary until town square is approved for non-staff use
    if not request.user.is_authenticated or not request.user.is_staff:
        from retail.views import index as regular_homepage
        return regular_homepage(request)

    default_tab = 'my_tribes' if request.user.is_authenticated else 'everywhere'
    tab = request.GET.get('tab', default_tab)

    context = {
        'title': 'Town Square',
        'nav': 'home',
        'target': '/activity',
        'tab': tab,
    }
    return TemplateResponse(request, 'townsquare/index.html', context)

@ratelimit(key='ip', rate='10/m', method=ratelimit.UNSAFE, block=True)
@csrf_exempt
def api(request, activity_id):

    # pull back the obj
    try:
        activity = Activity.objects.get(pk=activity_id)
    except:
        raise Http404

    # setup response
    response = {}

    # check for permissions
    has_perms = request.user.is_authenticated
    if request.POST.get('method') == 'delete':
        has_perms = activity.profile == request.user.profile
    if not has_perms:
        raise Http404

    # deletion request
    if request.POST.get('method') == 'delete':
        activity.delete()
    # like request
    elif request.POST.get('method') == 'like':
        if request.POST['direction'] == 'liked':
            Like.objects.create(profile=request.user.profile, activity=activity)
        if request.POST['direction'] == 'unliked':
            activity.likes.filter(profile=request.user.profile).delete()
    # comment request
    elif request.POST.get('method') == 'comment':
        comment = request.POST.get('comment')
        Comment.objects.create(profile=request.user.profile, activity=activity, comment=comment)
    elif request.GET.get('method') == 'comment':
        comments = activity.comments.order_by('-created_on')
        comments = [comment.to_standard_dict(properties=['profile_handle']) for comment in comments]
        response['comments'] = comments
    return JsonResponse(response)
