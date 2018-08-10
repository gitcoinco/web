from django import template

register = template.Library()


@register.filter
def lineup(ls):
    return ', '.join(ls[:-1]) + ' and ' + ls[-1] if len(ls) > 1 else ls[0]
