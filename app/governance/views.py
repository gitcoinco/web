from django.shortcuts import render
from django.template.response import TemplateResponse
from django.shortcuts import redirect

# Create your views here.
def index(request):

    return redirect('/quadraticlands/mission')
