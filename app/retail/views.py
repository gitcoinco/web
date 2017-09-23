'''
    Copyright (C) 2017 Gitcoin Core 

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''
from django.template.response import TemplateResponse
# Create your views here.


def index(request):
    context = {
        'active': 'home',
    }
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
