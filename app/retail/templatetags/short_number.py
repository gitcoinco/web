from django import template

register = template.Library()


@register.filter(name='short_number')
def short_number(num):
    """
        Returns the num in shorhand conotation ex 1000 = "1k".
    """
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
