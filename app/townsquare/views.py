from django.shortcuts import render
from django.template.response import TemplateResponse


# Create your views here.
def index(request):
    context = {
        'title': 'Town Square',
        'nav': 'home',
    }
    return TemplateResponse(request, 'townsquare/index.html', context)

