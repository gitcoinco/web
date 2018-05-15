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

from .models import Bounty, BountyFulfillment, Interest, ProfileSerializer


class BountyFulfillmentSerializer(serializers.ModelSerializer):
    """Handle serializing the BountyFulfillment object."""

    class Meta:
        """Define the bounty fulfillment serializer metadata."""

        model = BountyFulfillment
        fields = ('fulfiller_address', 'fulfiller_email',
                  'fulfiller_github_username', 'fulfiller_name',
                  'fulfillment_id', 'accepted', 'profile', 'created_on', 'accepted_on', 'fulfiller_github_url')


class InterestSerializer(serializers.ModelSerializer):
    """Handle serializing the Interest object."""

    profile = ProfileSerializer()

    class Meta:
        """Define the Interest serializer metadata."""

        model = Interest
        fields = ('profile', 'created')


# Serializers define the API representation.
class BountySerializer(serializers.HyperlinkedModelSerializer):
    """Handle serializing the Bounty object."""

    fulfillments = BountyFulfillmentSerializer(many=True)
    interested = InterestSerializer(many=True)
    bounty_owner_email = serializers.SerializerMethodField('override_bounty_owner_email')
    bounty_owner_name = serializers.SerializerMethodField('override_bounty_owner_name')

    def override_bounty_owner_email(self, obj):
        can_make_visible_via_api = bool(int(obj.privacy_preferences.get('show_email_publicly', 1)))
        default = "(hidden email)"
        return obj.bounty_owner_email if can_make_visible_via_api else default

    def override_bounty_owner_name(self, obj):
        can_make_visible_via_api = bool(int(obj.privacy_preferences.get('show_name_publicly', 1)))
        default = "(hidden name)"
        return obj.bounty_owner_name if can_make_visible_via_api else default

    class Meta:
        """Define the bounty serializer metadata."""

        model = Bounty
        fields = (
            'url', 'created_on', 'modified_on', 'title', 'web3_created',
            'value_in_token', 'token_name', 'token_address',
            'bounty_type', 'project_length', 'experience_level',
            'github_url', 'github_comments', 'bounty_owner_address',
            'bounty_owner_email', 'bounty_owner_github_username', 'bounty_owner_name',
            'fulfillments', 'interested', 'is_open', 'expires_date',
            'keywords', 'current_bounty', 'value_in_eth',
            'token_value_in_usdt', 'value_in_usdt_now', 'value_in_usdt', 'status', 'now',
            'avatar_url', 'value_true', 'issue_description', 'network',
            'org_name', 'pk', 'issue_description_text',
            'standard_bounties_id', 'web3_type', 'can_submit_after_expiration_date',
            'github_issue_number', 'github_org_name', 'github_repo_name',
            'idx_status', 'token_value_time_peg', 'fulfillment_accepted_on', 'fulfillment_submitted_on',
            'fulfillment_started_on', 'canceled_on', 'action_urls',
        )

    def create(self, validated_data):
        """Handle creation of m2m relationships and other custom operations."""
        fulfillments_data = validated_data.pop('fulfillments')
        bounty = Bounty.objects.create(**validated_data)
        for fulfillment_data in fulfillments_data:
            BountyFulfillment.objects.create(bounty=bounty, **fulfillment_data)
        return bounty

    def update(self, validated_data):
        """Handle updating of m2m relationships and other custom operations."""
        fulfillments_data = validated_data.pop('fulfillments')
        bounty = Bounty.objects.update(**validated_data)
        for fulfillment_data in fulfillments_data:
            BountyFulfillment.objects.update(bounty=bounty, **fulfillment_data)
        return bounty


class BountyViewSet(viewsets.ModelViewSet):
    """Handle the Bounty view behavior."""

    queryset = Bounty.objects.prefetch_related(
        'fulfillments', 'interested', 'interested__profile') \
        .all().order_by('-web3_created')
    serializer_class = BountySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        """Get the queryset for Bounty.

        Returns:
            QuerySet: The Bounty queryset.

        """
        queryset = Bounty.objects.prefetch_related(
            'fulfillments', 'interested', 'interested__profile') \
            .current().order_by('-web3_created')
        param_keys = self.request.query_params.keys()

        # filtering
        for key in ['raw_data', 'experience_level', 'project_length', 'bounty_type', 'bounty_owner_address',
                    'idx_status', 'network', 'bounty_owner_github_username', 'standard_bounties_id']:
            if key in param_keys:
                # special hack just for looking up bounties posted by a certain person
                request_key = key if key != 'bounty_owner_address' else 'coinbase'
                val = self.request.query_params.get(request_key, '')

                vals = val.strip().split(',')
                _queryset = queryset.none()
                for val in vals:
                    if val.strip():
                        args = {}
                        args['{}__icontains'.format(key)] = val.strip()
                        _queryset = _queryset | queryset.filter(**args)
                queryset = _queryset

        # filter by PK
        if 'pk__gt' in param_keys:
            queryset = queryset.filter(pk__gt=self.request.query_params.get('pk__gt'))

        # filter by who is interested
        if 'started' in param_keys:
            queryset = queryset.filter(interested__profile__handle__in=[self.request.query_params.get('started')])

        # filter by is open or not
        if 'is_open' in param_keys:
            queryset = queryset.filter(is_open=self.request.query_params.get('is_open') == 'True')
            queryset = queryset.filter(expires_date__gt=datetime.now())

        # filter by urls
        if 'github_url' in param_keys:
            urls = self.request.query_params.get('github_url').split(',')
            queryset = queryset.filter(github_url__in=urls)

        # Retrieve all fullfilled bounties by fulfiller_username
        if 'fulfiller_github_username' in param_keys:
            queryset = queryset.filter(
                fulfillments__fulfiller_github_username__iexact=self.request.query_params.get('fulfiller_github_username')
            )

        # Retrieve all interested bounties by profile handle
        if 'interested_github_username' in param_keys:
            queryset = queryset.filter(
                interested__profile__handle__iexact=self.request.query_params.get('interested_github_username')
            )

        # order
        order_by = self.request.query_params.get('order_by')
        if order_by:
            queryset = queryset.order_by(order_by)

        queryset = queryset.distinct()

        # offset / limit
        limit = self.request.query_params.get('limit', None)
        offset = self.request.query_params.get('offset', 0)
        if limit:
            queryset = queryset[int(offset):int(limit)]

        return queryset


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'bounties', BountyViewSet)
