from django import template
from django.utils.formats import date_format

import dateutil.parser

register = template.Library()


@register.filter(expects_localtime=True, is_safe=False)
def date_fromisoformat(value, arg=None):
    """Get datetime.datetime from isofromat string then use given format."""

    if value in (None, ''):
        return ''
    try:
        return date_format(dateutil.parser.parse(value), arg)
    except AttributeError:
        try:
            return format(dateutil.parser.parse(value), arg)
        except AttributeError:
            return ''
