from datetime import datetime, timedelta

from rest_framework import filters


class JobPostedFilter(filters.BaseFilterBackend):
    """
    Filter on job_posted time of the Job.
    """
    def filter_queryset(self, request, queryset, view):
        job_posted = request.query_params.get('job_posted', None)
        if job_posted:
            job_posted_days_ago = int(job_posted)
            job_posted = datetime.now() - timedelta(days=job_posted_days_ago)
            return queryset.filter(posted_at__gte=job_posted)
        return queryset


class EmploymentTypeFilter(filters.BaseFilterBackend):
    """
    Filter on job_type for the Job.
    """
    def filter_queryset(self, request, queryset, view):
        job_type = request.query_params.get('employment_type', None)
        if job_type:
            return queryset.filter(job_type__iexact=job_type)
        return queryset
