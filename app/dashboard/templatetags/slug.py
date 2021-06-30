from django import template
from unidecode import unidecode
from django.utils.text import slugify

register = template.Library()

@register.filter
def slug(value):
    return slugify(unidecode(value))
