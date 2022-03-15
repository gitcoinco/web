import json
import logging

from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render

from dashboard.models import SearchHistory
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from search.models import SearchResult, search

logger = logging.getLogger(__name__)


@ratelimit(key='ip', rate='30/m', method=ratelimit.UNSAFE, block=True)
def get_search(request):
    mimetype = 'application/json'
    keyword = request.GET.get('term', '')
    page = request.GET.get('page', 0)
    # set the number of items to display per page
    per_page = 100
    # fetch the results for the keyword on the given page
    return_results, results_total, next_page = search_helper(request, keyword, page, per_page)
    # return a JSON obj of the results + meta
    return HttpResponse(json.dumps({
        'results': return_results,
        'total': results_total,
        'page': next_page,
        'perPage': per_page
    }), mimetype)

def search_helper(request, keyword='', page=0, per_page=100):
    # attempt elasticsearch first
    return_results = []
    results_total = 0
    next_page = 0
    try:
        # collect the results from elasticsearch instance
        all_result_sets = search(keyword, page, per_page)
        # get the total number of available records
        results_total = all_result_sets.get('hits', {}).get('total', {}).get('value', 0)
        # check if there is a next page
        next_page = int(page) + 1 if results_total > (int(page) + 1) * per_page else False
        # pull the results from the es response
        return_results = [ele['_source'] for ele in all_result_sets['hits']['hits']]
        # record that a search was made for this keyword
        if request and request.user.is_authenticated:
            data = {'keyword': keyword}
            SearchHistory.objects.update_or_create(
                search_type='sitesearch',
                user=request.user,
                data=data,
                ip_address=get_ip(request)
            )
    # return results + meta
    except Exception as e:
        logger.exception(e)
    finally:
        if not settings.DEBUG or results_total:
            return return_results, results_total, next_page

    # fetch the results for the given keyword
    raw_results = SearchResult.objects.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
    if request.user.is_authenticated:
        raw_results = raw_results.filter(Q(visible_to__isnull=True) | Q(visible_to=request.user.profile))
    else:
        raw_results = raw_results.filter(visible_to__isnull=True)
    # get the total number of available records
    results_total = raw_results.count()
    # check if there is a next page
    next_page = int(page) + 1 if results_total > (int(page) + 1) * per_page else False
    # slice the current page from the results
    all_result_sets = [raw_results[int(page) * per_page:(int(page) + 1) * per_page]]
    # transform result into expected format
    return_results = []
    exclude_pks = []
    for results in all_result_sets:
        inner_results = [
            {
                'title': ele.title,
                'description': ele.description,
                'url': ele.url,
                'img_url': ele.img_url if ele.img_url else "/static/v2/images/helmet.svg",
                'source_type': str(str(ele.source_type).replace('token', 'kudos')).title()
            } for ele in results
        ]
        return_results = return_results + inner_results
    # record that a search was made for this keyword
    if request.user.is_authenticated:
        SearchHistory.objects.update_or_create(
            search_type='searchbar',
            user=request.user,
            data={'query': keyword},
            ip_address=get_ip(request)
        )

    # return results + meta
    return return_results, results_total, next_page
