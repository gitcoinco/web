from rest_framework import viewsets, mixins

from . import models, serializers, filters


class JobViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    queryset = models.Job.objects.filter(is_active=True)
    serializer_class = serializers.JobSerializer
    filter_backends = (filters.JobPostedFilter, filters.EmploymentTypeFilter,)
    ordering = ('-posted_at', )
