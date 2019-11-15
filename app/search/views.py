from django.shortcuts import render
from django.http import HttpResponse
import json
from .models import SearchResult
from django.db.models import Q

# Create your views here.
def search(request):
    keyword = request.GET.get('term', '')
    results = SearchResult.objects.filter(Q(title__icontains=keyword) | Q(description__icontains=keyword))
    if request.user.is_authenticated:
        results = results.filter(Q(visible_to__isnull=True) | Q(visible_to=request.user.profile))
    else:
        results = results.filter(visible_to__isnull=True)
    results = [
        {'title': ele.title, 'description': ele.description, 'url': ele.url} for ele in results
    ]

    mimetype = 'application/json'
    return HttpResponse(json.dumps(results), mimetype)
