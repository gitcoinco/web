from django.shortcuts import render
from django.views.decorators.cache import cache_page

from app.sitemaps import sitemaps


@cache_page(60 * 60 * 24)
def sitemap(request, section=None, template_name='sitemap.xml', mimetype='application/xml'): 
    from django.contrib.sitemaps.views import sitemap
    return sitemap(request, sitemaps, section, template_name, mimetype)
