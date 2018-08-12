from rest_framework import mixins, viewsets

from . import filters, models, serializers


class JobViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.CreateModelMixin,
                 viewsets.GenericViewSet):
    queryset = models.Job.objects.filter(is_active=True)
    serializer_class = serializers.JobSerializer
    filter_backends = (filters.JobPostedFilter, filters.EmploymentTypeFilter,)
    ordering = ('-created_at', )
