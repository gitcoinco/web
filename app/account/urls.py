from django.urls import include, path

from rest_framework import routers

from . import api, views

app_name = "account"

router = routers.DefaultRouter()
router.register(r'organization', api.OrganizationViewSet)


urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)

urlpatterns += (
    # urls for Organization
    path('organization/', views.OrganizationListView.as_view(), name='account_organization_list'),
    path('organization/create/', views.OrganizationCreateView.as_view(), name='account_organization_create'),
    path('organization/detail/<slug:slug>/', views.OrganizationDetailView.as_view(), name='account_organization_detail'),
    path('organization/update/<slug:slug>/', views.OrganizationUpdateView.as_view(), name='account_organization_update'),
)
