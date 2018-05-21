from django.urls import include, path

from rest_framework import routers

from . import api

app_name = "account"

router = routers.DefaultRouter()
router.register(r'organization', api.OrganizationViewSet)


urlpatterns = (
    # urls for Django Rest Framework API
    path('api/v1/', include(router.urls)),
)
