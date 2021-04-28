from datetime import datetime

import django_filters.rest_framework
from rest_framework import routers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import Contribution, Grant, Subscription
from .serializers import DonorSerializer, GranteeSerializer, GrantSerializer, SubscriptionSerializer


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
            queryset = queryset.filter(title__iexact=self.request.query_params.get('title'))

        # Filter by pk.
        if 'pk' in param_keys:
            queryset = queryset.filter(pk=self.request.query_params.get('pk'))

        # Filter by admin_address.
        if 'admin_address' in param_keys:
            queryset = queryset.filter(admin_address__iexact=self.request.query_params.get('admin_address'))

        # Filter by description.
        if 'description' in param_keys:
            queryset = queryset.filter(description__iexact=self.request.query_params.get('description'))

        # Filter by keyword.
        if 'keyword' in param_keys:
            queryset = queryset.keyword(self.request.query_params.get('keyword'))

        # Filter by grant_type.
        if 'grant_type' in param_keys:
            queryset = queryset.filter(grant_type__name=self.request.query_params.get('grant_type'))

        max_limit = 100
        limit = str(self.request.GET.get('limit', max_limit))
        offset = str(self.request.GET.get('offset', '0'))
        if not limit.isnumeric() or int(limit) > max_limit:
            limit = max_limit
        if not offset.isnumeric() or int(offset) < 0:
            offset = 0
        offset = int(offset)
        limit = int(limit)
        queryset = queryset[offset:limit]

        return queryset

    @action(detail=False)
    def report(self, request):
        return Response({'error': 'reports temporarily offline'})

    @action(detail=False)
    def report_real(self, request):
        """Generate Grants report for an ethereum address"""

        grants_queryset = Grant.objects.all()
        contributions_queryset = Contribution.objects.all()

        grantee_serializer = GranteeSerializer
        donor_serializer = DonorSerializer

        param_keys = self.request.query_params.keys()
        if 'eth_address' not in param_keys:
            raise NotFound(detail='Missing required parameter: eth_address')
        eth_address = self.request.query_params.get('eth_address')

        # Filter Grants and Contributions by the given eth_address
        grants_queryset = grants_queryset.filter(admin_address=eth_address)
        contributions_queryset = contributions_queryset.filter(subscription__contributor_address=eth_address)

        # Filter Grantee info by from_timestamp
        format = '%Y-%m-%dT%H:%M:%SZ'
        if 'from_timestamp' in param_keys:
            from_timestamp = self.request.query_params.get('from_timestamp')
            try:
                from_timestamp = datetime.strptime(from_timestamp, format)
            except ValueError:
                raise NotFound(detail="Please provide from_timestamp in the format: "+format)
        else:
            from_timestamp = datetime(1, 1, 1, 0, 0)
        grants_queryset = grants_queryset.filter(subscriptions__subscription_contribution__created_on__gte=from_timestamp)

        # Filter Grantee info by to_timestamp
        if 'to_timestamp' in param_keys:
            to_timestamp = self.request.query_params.get('to_timestamp')
            try:
                to_timestamp = datetime.strptime(to_timestamp, format)
            except ValueError:
                raise NotFound(detail="Please provide to_timestamp in the format: "+format)
        else:
            to_timestamp = datetime.now()
        grants_queryset = grants_queryset.filter(subscriptions__subscription_contribution__created_on__lte=to_timestamp)
        grants_queryset = grants_queryset.distinct()

        grantee_data = grantee_serializer(grants_queryset, many=True).data
        donor_data = donor_serializer(contributions_queryset, many=True).data

        response = Response({
            'grantee': grantee_data,
            'donor': donor_data
        })

        return response

router = routers.DefaultRouter()
router.register(r'grants', GrantViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
