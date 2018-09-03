import json

from django.shortcuts import render
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

        grant.title = request.POST.get('title')
        grant.pitch = request.POST.get('pitch')
        grant.description = request.POST.get('description')
        grant.reference_url = request.POST.get('reference_url')
        grant.goal_funding = request.POST.get('goal_funding')
        grant.profile = profile

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
