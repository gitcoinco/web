# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404, HttpResponse

from linkshortener.models import Link


# TODO: delete this view (and the app) after ETHDenver
def credits(request, shortcode):
    num_credits = 5

    try:
        link = Link.objects.get(shortcode=shortcode)
        num_remaining = num_credits - link.uses
        if num_remaining >= 0:
            return HttpResponse("<h1>Success</h1>")
        return HttpResponse("<h1>FAIL.  You're out of credits!</h1>")
    except Exception as e:
        print(e)
        raise Http404
