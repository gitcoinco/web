# Third-Party imports
from django.template.response import TemplateResponse

# gitcoin-web imports
# from .models import Job


def list_jobs(request):
    context = dict()
    return TemplateResponse(request, 'jobs/list.html', context=context)


def job_detail(request, pk):
    context = {
        'pk': pk
    }

    return TemplateResponse(request, 'jobs/detail.html', context=context)
