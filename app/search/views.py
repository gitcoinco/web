import json
import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType

from dashboard.models import SearchHistory
from ratelimit.decorators import ratelimit
from retail.helpers import get_ip
from search.models import SearchResult, search, search_by_type

logger = logging.getLogger(__name__)


@ratelimit(key='ip', rate='30/m', method=ratelimit.UNSAFE, block=True)
def get_search(request):
    mimetype = 'application/json'
    keyword = request.GET.get('term', '')
    page = request.GET.get('page', 0)
    search_type = request.GET.get('type')
    # set the number of items to display per page
    per_page = 100
    # fetch the results for the keyword on the given page
    return_results, results_totals, next_page = search_helper(request, keyword, search_type, page, per_page)
    # return a JSON obj of the results + meta
    return HttpResponse(json.dumps({
        'results': return_results,
        'totals': results_totals,
        'page': next_page,
        'perPage': per_page
    }), mimetype)

mapped_labels = {
        82: 'Grant',
        16: 'Bounty',
        25: 'Profile',
        73: 'Kudos',
        133: 'Quest',
        120: 'Page'
    }

def format_totals(aggregations):
    buckets = aggregations['search-totals']['buckets']
    # get content type keys from search results
    type_keys = map(lambda d: d['key'], buckets)
    # Get content types for search results that were returned
    content_types = ContentType.objects.filter(pk__in=type_keys).values('id', 'app_label', 'model')

    
    totals = {}
    total_all = 0
    for content_type in content_types:
        # find total based on content type
        bucket_index = buckets.index(next(filter(lambda n: n.get('key') == content_type['id'], buckets)))
        bucket = buckets[bucket_index]
        if bucket['key']:
            bucket['label'] = mapped_labels[bucket['key']]
            # link mapped_labels to search total
            totals[mapped_labels[bucket['key']]] = bucket['doc_count']
            total_all += bucket['doc_count']
    totals['All'] = total_all

    return totals

def get_type_id(val):
    for key, value in mapped_labels.items():
         if val == value:
             return key
 
    return "key doesn't exist"

def search_helper(request, keyword='', search_type=None, page=0, per_page=100):
    # attempt elasticsearch first
    return_results = []
    results_total = 0
    next_page = 0
    results_totals = None
    try:
        all_result_sets = None
        if search_type:
            # collect the results from elasticsearch instance based on content type
            all_result_sets = search_by_type(keyword, get_type_id(search_type), page, per_page)    
        else:
            # collect the results from elasticsearch instance
            all_result_sets = search(keyword, page, per_page)
        
        # get the totals for each category
        results_totals = format_totals(all_result_sets['aggregations'])

        # check if there is a next page
        next_page = int(page) + 1 if int(results_totals[search_type if search_type else 'All']) > (int(page) + 1) * per_page else False
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
        print(e, 'eeeeeee')
        logger.exception(e)
    finally:
        print(settings.DEBUG, results_totals, 'settings.DEBUG, results_totalssettings.DEBUG, results_totals')
        if not settings.DEBUG or results_totals:
            return return_results, results_totals, next_page

    print('fetch not elasticccc')
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
