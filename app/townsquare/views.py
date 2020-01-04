from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Activity
from ratelimit.decorators import ratelimit
from django.shortcuts import redirect

from .models import Comment, Like, Offer, OfferAction


def index(request):

    # TODO: temporary until town square is approved for non-staff use
    if not request.user.is_authenticated or not request.user.is_staff:
        from retail.views import index as regular_homepage
        return regular_homepage(request)

    tabs = [{
        'title': "My Tribes",
        'slug': 'my_tribes',
    }, {
        'title': "Everywhere",
        'slug': 'everywhere',
    }]

    for keyword in request.user.profile.keywords:
        tabs.append({
            'title': keyword.title(),
            'slug': f'keyword-{keyword}',
        })

    default_tab = 'my_tribes' if request.user.is_authenticated else 'everywhere'
    tab = request.GET.get('tab', default_tab)
    offers = Offer.objects.current()
    target = f'/activity?what={tab}'
    context = {
        'title': 'Home',
        'nav': 'home',
        'target': target,
        'tab': tab,
        'tabs': tabs,
        'offers': offers,
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


def offer(request, offer_id, offer_slug):

    try:
        offer = Offer.objects.current().get(pk=offer_id)
        if not request.user.is_authenticated:
            return redirect('/login/github?next=' + request.get_full_path())
        OfferAction.objects.create(profile=request.user.profile, offer=offer, what='click')
        return redirect(offer.url)
    except:
        raise Http404
