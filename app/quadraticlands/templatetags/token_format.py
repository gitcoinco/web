from django import template

register = template.Library()

@register.filter
def token_format(value):
    return "%.2f" % float(value) if float(value) > 1 else str('{:.18f}'.format(value)).rstrip('0')
