# Third-Party imports
from django.contrib import messages
from django.shortcuts import render
from django.template.response import TemplateResponse

# gitcoin-web imports
from .forms import JobForm


def list_jobs(request):
    context = {}
    return TemplateResponse(request, 'jobs/list.html', context=context)


def job_detail(request, pk):
    context = {
        'pk': pk
    }

    return TemplateResponse(request, 'jobs/detail.html', context=context)


def create_job(request):
    context = {}
    if request.method == 'POST':
        form = JobForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job has been submitted!')
    else:
        form = JobForm(user=request.user)
    context['form'] = form
    return render(request, 'jobs/create_job.html', context)
