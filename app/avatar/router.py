import logging

import django_filters.rest_framework
from rest_framework import routers, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import BaseAvatar, CustomAvatar
from .serializers import BaseAvatarSerializer, CustomAvatarSerializer

logger = logging.getLogger(__name__)


class UserAvatarsViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = BaseAvatarSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return BaseAvatar.objects.all().order_by('-id').filter(profile__pk=self.request.user.profile.pk)


class RecommendedByStaffAvatarsViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = CustomAvatarSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, )
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return CustomAvatar.objects.all().order_by('-id').filter(recommended_by_staff=True)


router = routers.DefaultRouter()
router.register(r'user-avatars', UserAvatarsViewSet, basename="user_avatars")
router.register(r'recommended-by-staff', RecommendedByStaffAvatarsViewSet, basename="recommended_by_staff_avatars")
