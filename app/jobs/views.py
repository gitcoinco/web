# Third-Party imports
from django.template.response import TemplateResponse

# gitcoin-web imports
from .models import Job


def list_jobs(request):
    context = {
        'jobs': Job.objects.all()
    }

    return TemplateResponse(request, 'jobs/list.html', context=context)


def job_detail(request, pk):
    job = Job.objects.filter(pk=pk)
    context = {
        'job': job
    }

    return TemplateResponse(request, 'jobs/detail.html', context=context)
