from django.urls import path

from jobs.apps import JobsConfig
from jobs.views import list_jobs, new_job

app_name = JobsConfig.name

urlpatterns = [
    path('', list_jobs, name='jobs_list'),
    path('new', new_job, name='jobs_new')
]
