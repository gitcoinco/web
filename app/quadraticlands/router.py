# -*- coding: utf-8 -*-
"""Define dashboard specific DRF API routes.

Copyright (C) 2021 Gitcoin Core

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

"""
from quadraticlands.serializer import GTCStewardSerializer
from rest_framework import routers, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import GTCSteward


class GTCStewardPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'


class GTCStewardViewSet(viewsets.ModelViewSet):
    queryset = GTCSteward.objects.all()
    serializer_class = GTCStewardSerializer
    pagination_class = GTCStewardPagination


router = routers.DefaultRouter()
router.register(r'stewards', GTCStewardViewSet)
