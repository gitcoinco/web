from django import template

import numpy as np

register = template.Library()

@register.filter
def token_format(value):
    return "%.2f" % value if value >= 1 else np.format_float_positional(value)
