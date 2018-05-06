from django.shortcuts import render

# Create your views here.
from django.template.response import TemplateResponse

from jobs.models import Jobs


def list_jobs(request):
    context = {'jobs': Jobs.objects.all()}

    return TemplateResponse(request, 'jobs/list.html', context=context)


def new_job(request):
    return TemplateResponse(request, 'jobs/submit_job.html', context={})
