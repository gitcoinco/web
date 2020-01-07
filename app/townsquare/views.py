from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Activity
from ratelimit.decorators import ratelimit

from .models import Comment, Flag, Like, Offer, OfferAction


def get_next_time_available(key):
    d = timezone.now()
    if key == 'daily':
        hours = int(d.strftime('%H'))
        minutes = int(d.strftime('%M'))
        d = d + timezone.timedelta(hours=hours) + timezone.timedelta(minutes=minutes)
    if key == 'weekly':
        d = d + timezone.timedelta(days=5 - d.weekday())
    if key == 'monthly':
        month = int(d.strftime('%m'))
        year = int(d.strftime('%Y'))
        year += 1 if month > 11 else 0
        month += 1
        d = timezone.datetime(year=year, month=month, day=1)
    return d

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
    offers_by_category = {}
    for key in ['daily', 'weekly', 'monthly']:
        next_time_available = get_next_time_available(key)
        offer = Offer.objects.current().filter(key=key).first()
        if request.user.is_authenticated:
            if request.user.profile.offeractions.filter(what='click', offer=offer):
                offer = None
        offers_by_category[key] = {
            'offer': offer,
            'time': next_time_available.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }
    context = {
        'title': 'Home',
        'nav': 'home',
        'target': f'/activity?what={tab}',
        'tab': tab,
        'tabs': tabs,
        'offers_by_category': offers_by_category,
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

    # flag request
    elif request.POST.get('method') == 'flag':
        if request.POST['direction'] == 'flagged':
            Flag.objects.create(profile=request.user.profile, activity=activity)
        if request.POST['direction'] == 'unflagged':
            activity.flags.filter(profile=request.user.profile).delete()

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
        if request.user.profile.offeractions.filter(what='click', offer=offer):
            raise Exception('already visited this offer')
        OfferAction.objects.create(profile=request.user.profile, offer=offer, what='click')
        return redirect(offer.url)
    except:
        raise Http404
