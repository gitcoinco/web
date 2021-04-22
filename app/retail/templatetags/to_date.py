from django import template

import dateutil

register = template.Library()

@register.filter(name='to_date')
def to_date(value):
    return dateutil.parser.parse(value)
