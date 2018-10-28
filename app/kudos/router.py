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

from .models import Token, Wallet


class TokenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Token
        fields = ('id', 'created_on', 'modified_on', 'name', 'description', 'image', 'rarity',
                  'price', 'num_clones_allowed', 'num_clones_in_wild', 'owner_address', 'tags')


class WalletSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Wallet
        fields = ('address', 'profile_id')


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all().order_by('-id')
    serializer_class = WalletSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        param_keys = self.request.query_params.keys()
        queryset = Wallet.objects.all().order_by('-id')

        # Filter by address
        if 'address' in param_keys:
            queryset = queryset.filter(address=self.request.query_params.get('address'))

        # Filter by profile_id
        if 'profile_id' in param_keys:
            queryset = queryset.filter(profile__id=self.request.query_params.get('profile_id'))

        # Filter by profile_id
        if 'profile_handle' in param_keys:
            queryset = queryset.filter(profile__handle=self.request.query_params.get('profile_handle'))

        return queryset


class TokenViewSet(viewsets.ModelViewSet):
    queryset = Token.objects.all().order_by('-id')
    serializer_class = TokenSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    # filter_fields = ('name', 'description', 'image', 'rarity', 'price', 'num_clones_allowed',
    #                  'num_clones_in_wild', 'owner_address', 'tags')

    def get_queryset(self):
        param_keys = self.request.query_params.keys()
        queryset = Token.objects.all().order_by('-id')

        # Filter by owner_address
        if 'owner_address' in param_keys:
            queryset = queryset.filter(owner_address__iexact=self.request.query_params.get('owner_address'))

        # Filter by name
        if 'name' in param_keys:
            queryset = queryset.filter(name__iexact=self.request.query_params.get('name'))

        # Filter by rarity
        if 'rarity' in param_keys:
            queryset = queryset.filter(rarity__iexact=self.request.query_params.get('rarity'))

        # Filter by price
        if 'price' in param_keys:
            queryset = queryset.filter(price__iexact=self.request.query_params.get('price'))

        # Filter by num_clones_allowed
        if 'num_clones_allowed' in param_keys:
            queryset = queryset.filter(num_clones_allowed__iexact=self.request.query_params.get('num_clones_allowed'))

        # Filter by num_clones_in_wild
        if 'num_clones_in_wild' in param_keys:
            queryset = queryset.filter(num_clones_in_wild__iexact=self.request.query_params.get('num_clones_in_wild'))

        # Filter by tags
        if 'tags' in param_keys:
            queryset = queryset.filter(tags__in=self.request.query_params.get('tags'))

        return queryset


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'kudos', TokenViewSet)
router.register(r'wallet', WalletViewSet)
