from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
@stringfilter
def replace(value, arg=None):
    """String replacement eg `{{ "text"|replace:"x|s" }}`"""

    if len(arg.split('|')) != 2:
        return value

    _from, _to = arg.split('|')
    return value.replace(_from, _to)
