import django_filters.rest_framework
from rest_framework import routers, viewsets

from .models import Grant, Subscription
from .serializers import GrantSerializer, SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """Handle the Subscription API view behavior."""

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )

    def get_queryset(self):
        """Get the queryset for Subscription.

        TODO:
            * Add filter functionality.

        Returns:
            QuerySet: The Subscription queryset.

        """
        queryset = Subscription.objects.all()
        return queryset


class GrantViewSet(viewsets.ModelViewSet):
    """Handle the Grant API view behavior."""

    queryset = Grant.objects.active()
    serializer_class = GrantSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )

    def get_queryset(self):
        """Get the queryset for Grant.

        TODO:
            * Add additional filters.

        Returns:
            QuerySet: The Grant queryset.

        """
        param_keys = self.request.query_params.keys()
        queryset = Grant.objects.active()

        # Filter by title.
        if 'title' in param_keys:
            queryset = queryset.filter(title_iexact=self.request.query_params.get('title'))

        # Filter by description.
        if 'description' in param_keys:
            queryset = queryset.filter(description_iexact=self.request.query_params.get('description'))

        # Filter by description.
        if 'keyword' in param_keys:
            queryset = queryset.keyword(self.request.query_params.get('keyword'))

        return queryset


router = routers.DefaultRouter()
router.register(r'grants', GrantViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
