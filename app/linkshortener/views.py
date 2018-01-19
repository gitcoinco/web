# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import Http404
from django.shortcuts import redirect

from linkshortener.models import Link


def linkredirect(request, shortcode):
    try:
        link = Link.objects.get(shortcode=shortcode)
        link.uses += 1
        link.save()
        return redirect(link.url)
    except Exception as e:
        print(e)
        raise Http404
