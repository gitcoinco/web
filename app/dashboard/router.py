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

from rest_framework import routers, serializers, viewsets

from .filters import BountyFilter
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
        return obj.bounty_owner_email if can_make_visible_via_api else default

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
        .all()
    serializer_class = BountySerializer
    filter_class = BountyFilter
    ordering_fields = ('web3_created', '_val_usd_db',)
    ordering: '-web3_created'
    search_fields = ('title', 'issue_description')
    def get_queryset(self):
        queryset = Bounty.objects.prefetch_related(
            'fulfillments', 'interested', 'interested__profile') \
            .current()
        return queryset

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'bounties', BountyViewSet)
