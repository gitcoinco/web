from datetime import datetime, timedelta

from django.core.paginator import EmptyPage, Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_control
import django_filters.rest_framework
from ratelimit.decorators import ratelimit
from rest_framework import generics, mixins, routers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import CLRMatch, Contribution, Grant, GrantCLR, GrantCollection, GrantTag, GrantType, Subscription
from .serializers import (
    CLRPayoutsSerializer, DonorSerializer, GrantCLRSerializer, GrantCollectionSerializer, GrantSerializer,
    GrantTagSerializer, GrantTypeSerializer, SubscriptionSerializer, TransactionsSerializer,
)


class GrantCLRPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class GrantsClrViewSet(viewsets.ModelViewSet):
    queryset = GrantCLR.objects.select_related('owner').order_by('-created_on')
    serializer_class = GrantCLRSerializer
    pagination_class = GrantCLRPagination
    filterset_fields = ['customer_name']


class GrantCollectionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class GrantCollectionViewSet(viewsets.ModelViewSet):
    queryset = GrantCollection.objects.order_by('id')
    serializer_class = GrantCollectionSerializer
    pagination_class = GrantCollectionPagination
    filterset_fields = ['featured', 'profile']


class GrantTypeViewSet(viewsets.ModelViewSet):
    queryset = GrantType.objects.order_by('id')
    serializer_class = GrantTypeSerializer
    # pagination_class = GrantTypePagination
    # filterset_fields = ['customer_name']


class GranTagFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = GrantTag
        fields = ['name']


@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class GrantTagViewSet(viewsets.ModelViewSet):
    queryset = GrantTag.objects.order_by('id')
    serializer_class = GrantTagSerializer
    filterset_class = GranTagFilter



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
        queryset = queryset[offset:(offset+limit)]

        return queryset


    @action(detail=False)
    @ratelimit(key='ip', rate='2/s')
    def clr_round_metadata(self, request):
        """
            Generate CLR Round metadata for Grants
            URL: api/v0.1/grants/get_clr_round_metadata/
        """

        clr_rounds = GrantCLR.objects.all()

        pk = self.request.query_params.get('id')
        active = self.request.query_params.get('active', False)
        to_timestamp = self.request.query_params.get('to_timestamp')
        from_timestamp = self.request.query_params.get('from_timestamp')
        format = '%Y-%m-%d'

        if pk:
            clr_rounds = clr_rounds.filter(pk=pk)

        if active:
            clr_rounds = clr_rounds.filter(is_active=True)

        if from_timestamp:
            try:
                from_timestamp = datetime.strptime(from_timestamp, format)
            except ValueError:
                return Response({
                    'error': 'from_timestamp is is not in the format YYYY-MM-DD'
                })
            clr_rounds = clr_rounds.filter(start_date__gte=from_timestamp)

        if to_timestamp:
            try:
                to_timestamp = datetime.strptime(to_timestamp, format)
            except ValueError:
                return Response({
                    'error': 'to_timestamp is is not in the format YYYY-MM-DD'
                })
            clr_rounds = clr_rounds.filter(start_date__lte=to_timestamp)

        clr_serializer = GrantCLRSerializer
        data = clr_serializer(clr_rounds,  many=True).data

        return Response({
            'rounds': data
        })


    @action(detail=False)
    @ratelimit(key='ip', rate='5/s')
    def contributions_rec_report(self, request):
        """
            Generate Grantee Report for an Grant
            URL: api/v0.1/grants/contributions_rec_report/?id=<grant-id>&format=json
        """

        results_limit = 30

        page = self.request.query_params.get('page', '1')
        if not page or not page.isdigit():
            page = 1

        grant_pk = self.request.query_params.get('id')
        if not grant_pk or not grant_pk.isdigit():
            return Response({
                'error': 'missing manadatory parameter id'
            })

        now = datetime.now()
        to_timestamp = self.request.query_params.get('to_timestamp')
        from_timestamp = self.request.query_params.get('from_timestamp')
        format = '%Y-%m-%d'

        # Check timestamp
        if not from_timestamp:
            from_timestamp = now - timedelta(days=30)
        else:
            try:
                from_timestamp = datetime.strptime(from_timestamp, format)
            except ValueError:
                return Response({
                    'error': 'from_timestamp is not in format YYYY-MM-DD'
                })

        if not to_timestamp:
            to_timestamp = now
        else:
            try:
                to_timestamp = datetime.strptime(to_timestamp, format)
            except ValueError:
                return Response({
                    'error': 'to_timestamp is is not in the format YYYY-MM-DD'
                })

        if (to_timestamp - from_timestamp).days > 31:
            return Response({
                'error': 'timeperiod should be less than 31 days'
            })

        try:
            grant = Grant.objects.get(pk=grant_pk)
        except Exception:
            return Response({
                'error': 'unable to find grant id'
            })

        txn_serializer = TransactionsSerializer

        contributions_queryset = Contribution.objects.prefetch_related(
            'subscription__grant'
        ).filter(
            subscription__grant=grant,
            created_on__lte=to_timestamp,
            created_on__gt=from_timestamp,
            subscription__network='mainnet',
            tx_cleared=True,
            success=True
        )
        all_contributions = Paginator(contributions_queryset, results_limit)

        try:
            contributions_queryset = all_contributions.page(page)
        except EmptyPage:
            return Response({
                'error': 'no results for this page'
            })
        transactions = txn_serializer(contributions_queryset, many=True).data

        clr_serializer = CLRPayoutsSerializer
        clr_payouts = clr_serializer(CLRMatch.objects.filter(grant=grant), many=True).data

        return Response({
            'transactions': transactions,
            'clr_payouts': clr_payouts,
            'metadata' : {
                'grant_name': grant.title,
                'created_on': grant.created_on,
                'from_timestamp': from_timestamp,
                'to_timestamp': to_timestamp,
                'count': all_contributions.count,
                'current_page': page,
                'num_pages': all_contributions.num_pages,
                'has_next': all_contributions.page(page).has_next()
            }

        })


    @action(detail=False)
    @ratelimit(key='ip', rate='5/s')
    def contributions_sent_report(self, request):
        """
            Generate report for grant contributions made by an address
            URL: api/v0.1/grants/contributions_sent_report/?address=<address>&format=json
        """

        donor_serializer = DonorSerializer
        results_limit = 30

        # Validate input pararms
        page = self.request.query_params.get('page', '1')
        if not page or not page.isdigit():
            page = 1

        address = self.request.query_params.get('address', None)
        if not address:
            return Response({
                'error': 'address is a mandatory parameter'
            })

        now = datetime.now()
        to_timestamp = self.request.query_params.get('to_timestamp')
        from_timestamp = self.request.query_params.get('from_timestamp')
        format = '%Y-%m-%d'

        # Check timestamp
        if not from_timestamp:
            from_timestamp = now - timedelta(days=30)
        else:
            try:
                from_timestamp = datetime.strptime(from_timestamp, format)
            except ValueError:
                return Response({
                    'error': 'from_timestamp is not in format YYYY-MM-DD'
                })

        if not to_timestamp:
            to_timestamp = now
        else:
            try:
                to_timestamp = datetime.strptime(to_timestamp, format)
            except ValueError:
                return Response({
                    'error': 'to_timestamp is is not in the format YYYY-MM-DD'
                })

        if (to_timestamp - from_timestamp).days > 31:
            return Response({
                'error': 'timeperiod should be less than 31 days'
            })

        # Filter Contributions made by given address

        contributions_queryset = Contribution.objects.prefetch_related('subscription').filter(
            subscription__contributor_address=address,
            created_on__lte=to_timestamp,
            created_on__gt=from_timestamp,
            subscription__network='mainnet',
            tx_cleared=True,
            success=True
        )

        all_contributions = Paginator(contributions_queryset, results_limit)
        try:
            contributions_queryset = all_contributions.page(page)
        except EmptyPage:
            return Response({
                'error': 'no results for this page'
            })
        data = donor_serializer(contributions_queryset, many=True).data

        response = Response({
            'metadata' : {
                'from': from_timestamp,
                'to': to_timestamp,
                'count': all_contributions.count,
                'current_page': page,
                'num_pages': all_contributions.num_pages,
                'has_next': all_contributions.page(page).has_next()
            },
            'data': data,
        })

        return response

router = routers.DefaultRouter()
router.register(r'grants', GrantViewSet)
router.register(r'subscriptions', SubscriptionViewSet)
router.register(r'grants_clr', GrantsClrViewSet)
router.register(r'grants_type', GrantTypeViewSet)
router.register(r'grants_tag', GrantTagViewSet)
router.register(r'grants_collections', GrantCollectionViewSet)
