# -*- coding: utf-8 -*-
"""Define dashboard specific DRF API routes.

Copyright (C) 2018 Gitcoin Core

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
from datetime import datetime

import django_filters.rest_framework
from rest_framework import routers, serializers, viewsets

from .models import Job


# Serializers define the API representation.
class JobSerializer(serializers.HyperlinkedModelSerializer):
    """Handle serializing the Job object."""

    class Meta:
        """Define the serializer metadata."""

        model = Job
        fields = (
            'id', 'url', 'created_on', 'modified_on', 'title', 'skills', 'description', 'active',
            'apply_location', 'company', 'job_type', 'github_profile', 'job_location',
        )

    def create(self, validated_data):
        job = Job.objects.create(**validated_data)
        return job

    def update(self, validated_data):
        job = Job.objects.update(**validated_data)
        return job


class JobViewSet(viewsets.ModelViewSet):
    """Handle the Job view behavior."""
    queryset = Job.objects.all().order_by('-created_on')
    serializer_class = JobSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        """Get the queryset for Job.

        Returns:
            QuerySet: The Job queryset.

        """
        param_keys = self.request.query_params.keys()
        queryset = Job.objects.filter(active=True)
        queryset = queryset.order_by('-created_on')

        # filtering
        for key in ('job_type', ):
            if key in param_keys:
                request_key = key
                val = self.request.query_params.get(request_key, '')

                values = [v.strip() for v in val.split(',') if v and v.strip()]
                _queryset = queryset.none()
                for value in values:
                    _queryset = _queryset | queryset.filter(**{f'{key}__icontains': value.strip()})
                queryset = _queryset

        # order
        order_by = self.request.query_params.get('order_by')
        if order_by and order_by != 'null':
            queryset = queryset.order_by(order_by)

        queryset = queryset.distinct()

        # offset / limit
        limit = int(self.request.query_params.get('limit', 25))
        max_count = 25
        if limit > max_count:
            limit = max_count
        offset = self.request.query_params.get('offset', 0)
        if limit:
            start = int(offset)
            end = start + int(limit)
            queryset = queryset[start:end]

        return queryset


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'jobs', JobViewSet)
