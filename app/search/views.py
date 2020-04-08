import json
import logging

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from dashboard.models import SearchHistory
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip

from .models import SearchResult, search

logger = logging.getLogger(__name__)


@ratelimit(key='ip', rate='30/m', method=ratelimit.UNSAFE, block=True)
def search(request):
    keyword = request.GET.get('term', '')

    # attempt elasticsearch first
    mimetype = 'application/json'
    return_results = []
    try:
        all_result_sets = search(keyword)
        return_results = [ele['_source'] for ele in all_result_sets['hits']['hits']]
    except Exception as e:
        print(e)
    finally:
        if not settings.DEBUG or len(return_results):
            return HttpResponse(json.dumps(return_results), mimetype)

    all_result_sets = [SearchResult.objects.filter(title__icontains=keyword), SearchResult.objects.filter(description__icontains=keyword)]
    return_results = []
    exclude_pks = []
    for results in all_result_sets:
        if request.user.is_authenticated:
            results = results.filter(Q(visible_to__isnull=True) | Q(visible_to=request.user.profile))
        else:
            results = results.filter(visible_to__isnull=True)
        results = results.exclude(pk__in=exclude_pks)
        inner_results = [
            {
                'title': ele.title,
                'description': ele.description,
                'url': ele.url,
                'img_url': ele.img_url if ele.img_url else "/static/v2/images/helmet.svg",
                'source_type': str(str(ele.source_type).replace('token', 'kudos')).title()
            } for ele in results
        ]
        exclude_pks = exclude_pks + list(results.values_list('pk', flat=True))
        return_results = return_results + inner_results

    if request.user.is_authenticated:
        SearchHistory.objects.update_or_create(
            search_type='searchbar',
            user=request.user,
            data={'query': keyword},
            ip_address=get_ip(request)
        )

    mimetype = 'application/json'
    return HttpResponse(json.dumps(return_results), mimetype)
