from django import template
#TODO: CHANGE to:
#from django.contrib.sites.models import Site
from django.conf import settings

register = template.Library()


@register.simple_tag
def current_domain():
    #TODO: CHANGE to:
    #return 'http://%s' % Site.objects.get_current().domain
    return settings.BASE_URL
