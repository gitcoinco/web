from django import template
from django.utils.timesince import timesince

import dateutil.parser

register = template.Library()


@register.filter(is_safe=False)
def timesince_fromisoformat(value, arg=None):
    """Convert value to datetime.datetime object then format as timesince."""
    
    if not value:
        return ''
    try:
        if arg:
            return timesince(dateutil.parser.parse(value), arg)
        return timesince(dateutil.parser.parse(value))
    except (ValueError, TypeError):
        return ''
