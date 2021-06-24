import json

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from app.sitemaps import sitemaps


@cache_page(60 * 60 * 24)
def sitemap(request, section=None, template_name='sitemap.xml', mimetype='application/xml'): 
    from django.contrib.sitemaps.views import sitemap
    return sitemap(request, sitemaps, section, template_name, mimetype)


@csrf_exempt
def blocknative(request):
    from economy.models import TXUpdate
    if not request.body:
        from dashboard.views import profile
        return profile(request, 'blocknative')
    body = json.loads(request.body)
    if body['apiKey'] == settings.BLOCKNATIVE_API:
        txu = TXUpdate.objects.create(body=body)
        txu.process_callbacks()
        txu.save()
    return HttpResponse(status=200)
