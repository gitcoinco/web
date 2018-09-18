import json

from django.template.response import TemplateResponse

from marketing.models import Keyword

from .models import Grant

# Create your views here.


def grant_show(request, grant_id):
    grant = Grant.objects.get(pk=grant_id)

    params = {
        'active': 'dashboard',
        'title': 'Grant Show',
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'grants/show.html', params)

def new_grant(request):
    """Handle new grant."""
    profile_id = request.session.get('profile_id')
    profile = request.user.profile if request.user.is_authenticated else None

    if request.method == "POST":
        grant = Grant()

        grant.title = request.POST.get('input-name')
        grant.description = request.POST.get('description')
        grant.reference_url = request.POST.get('reference_url')
        grant.image_url = request.POST.get('input-image')
        # grant.adminAddress = request.POST.get('admin_address')
        # grant.freguency = request.POST.get('frequency')
        grant.amountGoal = request.POST.get('amount_goal')
        grant.adminProfile = profile
        # grant.teamMemberProfiles = Need to do a profile search based on enetered emails

        grant.save()
    else:
        grant = {}

    params = {
        'active': 'dashboard',
        'title': 'New Grant',
        'grant': grant,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }

    return TemplateResponse(request, 'grants/new.html', params)

def grants(request):
    """Handle grants explorer."""
    grants = Grant.objects.all()

    params = {
        'active': 'dashboard',
        'title': 'Grants Explorer',
        'grants': grants,
        'keywords': json.dumps([str(key) for key in Keyword.objects.all().values_list('keyword', flat=True)]),
    }
    return TemplateResponse(request, 'grants/index.html', params)

def fund_grant(request):
    params = {
        'title': 'Fund Grant'
    }

    return TemplateResponse(request, 'grants/fund.html', params)

def cancel_grant(request):
    params = {
        'title': 'Fund Grant'
    }

    return TemplateResponse(request, 'grants/cancel.html', params)
