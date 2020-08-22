from django.shortcuts import render
from django.template.response import TemplateResponse

# Create your views here.
def index(request):
    params = {}
    response =  TemplateResponse(request, 'governance/games/diplomacy.html', params)
    return response
