from django import template
from django.utils.text import slugify

from unidecode import unidecode

register = template.Library()

@register.filter
def slug(value):
    return slugify(unidecode(value))
