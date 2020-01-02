from django.shortcuts import render
from django.template.response import TemplateResponse


# Create your views here.
def index(request):
    default_tab = 'my_tribes' if request.user.is_authenticated else 'everywhere'
    tab = request.GET.get('tab', default_tab)

    context = {
        'title': 'Town Square',
        'nav': 'home',
        'target': '/activity',
        'tab': tab,
    }
    return TemplateResponse(request, 'townsquare/index.html', context)
