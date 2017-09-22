from django.template.response import TemplateResponse
# Create your views here.


def index(request):
    context = {'active': 'home'}
    return TemplateResponse(request, 'index.html', context)


def about(request):
    context = {
        'active': 'about',
        'title': 'About',
    }
    return TemplateResponse(request, 'about.html', context)


def get_gitcoin(request):
    context = {
        'active': 'get',
        'title': 'Get Gitcoin',
    }
    return TemplateResponse(request, 'getgitcoin.html', context)


def handler403(request):
    return error(request, 403)


def handler404(request):
    return error(request, 404)


def handler500(request):
    return error(request, 500)


def handler400(request):
    return error(request, 400)


def error(request, code):
    context = {
        'active': 'error', 
        'code': code
    }
    context['title'] = "Error {}".format(code)
    return TemplateResponse(request, 'error.html', context)
