from rest_framework import permissions, viewsets

from . import models, serializers


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for the Organization class"""

    queryset = models.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer
    permission_classes = [permissions.IsAuthenticated]
