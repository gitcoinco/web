import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from dashboard.models import SearchHistory
from retail.helpers import get_ip

from .models import SearchResult


def search(request):
    keyword = request.GET.get('term', '')
    results = SearchResult.objects.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
    if request.user.is_authenticated:
        results = results.filter(Q(visible_to__isnull=True) | Q(visible_to=request.user.profile))
    else:
        results = results.filter(visible_to__isnull=True)
    results = [
        {
            'title': ele.title,
            'description': ele.description,
            'url': ele.url,
            'img_url': ele.img_url if ele.img_url else "/static/v2/images/helmet.svg",
            'source_type': str(ele.source_type)
        } for ele in results
    ]

    if request.user.is_authenticated:
        SearchHistory.objects.update_or_create(
            search_type='searchbar',
            user=request.user,
            data={'query': keyword},
            ip_address=get_ip(request)
        )

    mimetype = 'application/json'
    return HttpResponse(json.dumps(results), mimetype)
