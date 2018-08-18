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

import django_filters.rest_framework
from rest_framework import routers, serializers, viewsets

from .models import ExternalBounty


# Serializers define the API representation.
class ExternalBountySerializer(serializers.HyperlinkedModelSerializer):
    """Handle serializing the ExternalBounty object."""

    class Meta:
        """Define the external bounty serializer metadata."""

        model = ExternalBounty
        fields = (
            'title', 'description', 'created_on', 'action_url', 'source_project', 'amount', 'amount_denomination',
            'tags',
        )


class ExternalBountyViewSet(viewsets.ModelViewSet):
    """Handle the Bounty view behavior."""

    queryset = ExternalBounty.objects.filter(active=True).order_by('-pk')
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    serializer_class = ExternalBountySerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'universe', ExternalBountyViewSet)
