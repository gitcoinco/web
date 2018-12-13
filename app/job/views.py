# -*- coding: utf-8 -*-
"""Define external job related views.

Copyright (C) 2018 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from django.core.paginator import Paginator
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from app.utils import ellipses
from job.forms import JobForm
from job.models import Job
from marketing.mails import new_job_notification


def sort_index(request, jobs):
    direction = "" if request.GET.get('direction') == 'asc' else '-'
    column = 'created_on'
    sort = request.GET.get('sort')
    if sort == _('Created'):
        column = 'created_on'

    jobs = jobs.order_by(f"{direction}{column}")

    return jobs, sort, direction


def job_index(request):
    """Handle Job Board index page.

    Returns:
        django.TemplateResponse: The external job index view.

    """
    skills = []
    jobs_results = []
    jobs = Job.objects.filter(active=True).order_by('-created_on')
    search_query = request.GET.get('q', False)
    if search_query == 'False':
        search_query = None
    if search_query:
        master_jobs = jobs
        jobs = master_jobs.filter(title__contains=search_query)
        jobs = jobs | master_jobs.filter(description__contains=search_query)
        jobs = jobs | master_jobs.filter(company__contains=search_query)
        jobs = jobs | master_jobs.filter(skills__overlap=[search_query])
        jobs = jobs.distinct()
    jobs, sorted_by, sort_direction = sort_index(request, jobs)
    num_jobs = jobs.count()
    page = request.GET.get('page', 1)
    for job in jobs:
        skills = skills + job.skills
    jobs = Paginator(jobs, 25)
    jobs_paginator = jobs.get_page(page)
    for job_request in jobs_paginator:
        job = {
            "created_on": job_request.created_on,
            "title": job_request.title,
            "crypto_price": round(job_request.amount, 2) if job_request.amount else None,
            "skills": job_request.skills,
            "url": job_request.url,
        }
        jobs_results.append(job)
    categories = list(set(skills))
    categories = [ele.lower() for ele in categories if ele]
    categories.sort()
    params = {
        'active': 'job',
        'title': _('Job Board'),
        'card_desc': _('Find your next job.'),
        'jobs': jobs_results,
        'categories': categories,
        'sort_direction': sort_direction,
        'sorted_by': sorted_by,
        'q': search_query,
        'page': page,
        'num_jobs': num_jobs,
        'jobs_paginator': jobs_paginator,
    }
    return TemplateResponse(request, 'job_index.html', params)


def job_new(request):
    """Create a new external job.

    Returns:
        django.TemplateResponse: The new external job form or submission status.

    """
    params = {
        'active': 'job',
        'title': _('New Job Posting'),
        'card_desc': _('Create a new Job Posting for your company on GitCoin.'),
        'formset': JobForm,
    }

    if request.POST:
        new_job = JobForm(request.POST)

        if request.user and request.user.is_authenticated and hasattr(request.user, 'profile'):
            new_job.posted_by = request.user.profile

        new_job.save()
        new_job_notification()
        params['msg'] = _("An email has been sent to an administrator to approve your submission")

    return TemplateResponse(request, 'job_new.html', params)


def job_show(request, pk):
    """Handle Job show page.

    Args:
        pk (int): db primary key.

    Returns:
        django.TemplateResponse: The external job details view.

    """

    try:
        job = Job.objects.get(pk=pk, active=True)
    except Exception:
        raise Http404

    params = {
        'active': 'job',
        'title': _('Job Board'),
        'card_desc': ellipses(job.description, 300),
        "job": job,
    }

    return TemplateResponse(request, 'job/show.html', params)
