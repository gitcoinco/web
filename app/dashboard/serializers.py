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
import logging

from bounty_requests.models import BountyRequest
from kudos.models import KudosTransfer, Token
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from townsquare.models import Comment, PinnedPost

from .models import (
    Activity, Bounty, BountyFulfillment, BountyInvites, HackathonEvent, HackathonProject, Interest, Profile,
    TribeMember,
)

logger = logging.getLogger(__name__)


class ProfileSerializer(FlexFieldsModelSerializer):
    """Handle serializing the Profile object."""
    match_this_round = serializers.ReadOnlyField()
    url = serializers.ReadOnlyField()
    default_match_estimate = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField(source='data.name')
    type = serializers.ReadOnlyField(source='data.type')
    avatar_url = serializers.URLField()

    class Meta:
        """Define the profile serializer metadata."""

        model = Profile
        fields = '__all__'
        extra_kwargs = {'github_access_token': {'write_only': True}}

    def get_default_match_estimate(self, obj):
        return obj.matchranking_this_round.default_match_estimate if obj.matchranking_this_round else 0


class BountyFulfillmentSerializer(serializers.ModelSerializer):
    """Handle serializing the BountyFulfillment object."""
    profile = ProfileSerializer(fields=['handle'])
    fulfiller_email = serializers.ReadOnlyField()
    fulfiller_github_username = serializers.ReadOnlyField()
    class Meta:
        """Define the bounty fulfillment serializer metadata."""

        model = BountyFulfillment
        fields = ('pk', 'fulfiller_email', 'fulfiller_address',
                  'fulfiller_github_username', 'fulfiller_metadata',
                  'fulfillment_id', 'accepted', 'profile', 'created_on',
                  'accepted_on', 'fulfiller_github_url', 'payout_tx_id',
                  'payout_amount', 'token_name', 'payout_status', 'tenant',
                  'payout_type', 'fulfiller_identifier', 'funder_identifier')


class HackathonEventSerializer(FlexFieldsModelSerializer):
    """Handle serializing the hackathon object."""
    sponsor_profiles = ProfileSerializer(many=True, fields=['handle'])
    prizes = serializers.SerializerMethodField()
    winners = serializers.SerializerMethodField()

    def get_prizes(self, obj):
        return obj.get_total_prizes()

    def get_winners(self, obj):
        return obj.get_total_winners()

    class Meta:
        """Define the hackathon serializer metadata."""

        model = HackathonEvent
        fields = '__all__'


class KudosTransferSerializer(FlexFieldsModelSerializer):
    """Handle serializing the Kudos object."""

    class Meta:
        """Define the kudos serializer metadata."""

        model = KudosTransfer
        fields = ('id', 'kudos_token_cloned_from', 'username')


class KudosTokenSerializer(FlexFieldsModelSerializer):
    """Handle serializing the Kudos object."""

    class Meta:
        """Define the kudos serializer metadata."""

        model = Token
        fields = ('price_finney', 'id', 'num_clones_allowed', 'num_clones_in_wild',
                  'num_clones_available_counting_indirect_send',
                  'cloned_from_id', 'popularity', 'popularity_week',
                  'popularity_month', 'popularity_quarter', 'name',
                  'override_display_name', 'description', 'img_url',
                  'image', 'rarity', 'tags', 'artist', 'platform',
                  'external_url',  'background_color', 'owner_address',
                  'txid', 'token_id', 'hidden', 'ui_name', 'from_username',
                  'send_enabled_for_non_gitcoin_admins', 'preview_img_url',
                  'preview_img_mode', 'suppress_sync', 'kudos_token_cloned_from')


class PinnedPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = PinnedPost
        fields = '__all__'


class VoteSerializer(serializers.Serializer):
    choice = serializers.IntegerField(required=True)


class AwardCommentSerializer(serializers.Serializer):
    comment = serializers.IntegerField(required=True)


class CommentSerializer(FlexFieldsModelSerializer):
    profile = ProfileSerializer(fields=[
        'id', 'handle', 'name', 'type', 'github_url', 'avatar_url', 'keywords', 'organizations'
    ], read_only=True)
    likes_count = serializers.SerializerMethodField()
    viewer_reactions = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            'id', 'created_on', 'profile', 'activity', 'comment', 'tip', 'likes',
            'likes_handles', 'likes_count', 'tip_count_eth', 'is_edited', 'is_owner', 'viewer_reactions'
        )

    def get_viewer_reactions(self, obj):
        user = self.context['request'].user
        viewer_reactions = None

        if user.is_authenticated:
            viewer_reactions = {
                'like': user.profile.pk in obj.likes
            }

        return viewer_reactions

    def get_is_owner(self, obj):
        user = self.context['request'].user
        return user.profile.pk == obj.profile.id if hasattr(user, 'profile') else None

    def get_likes_count(self, obj):
        return len(obj.likes)


class ActivitySerializer(FlexFieldsModelSerializer):
    """Handle serializing the Activity object."""
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    profile = ProfileSerializer(fields=[
        'id', 'handle', 'avatar_url', 'github_url', 'organizations', 'keywords',
        'name', 'type', 'match_this_round', 'default_match_estimate'
    ])
    viewer_reactions = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        """Define the activity serializer metadata."""

        model = Activity
        fields = (
            'pk', 'activity_type', 'humanized_activity_type', 'profile', 'comments', 'likes',
            'metadata', 'bounty', 'tip_count_eth', 'tip_count_usd', 'kudos', 'kudos_transfer',
            'grant', 'subscription', 'hackathonevent', 'other_profile', 'action_url', 'hidden',
            'view_count', 'comments_count', 'likes_count', 'show_token_info', 'token_name',
            'secondary_avatar_url', 'created', 'created_on', 'created_human_time', 'is_owner',
            'viewer_reactions'
        )
        expandable_fields = {
            'grant': (
                'grants.serializers.GrantSerializer',
                {'fields': ['id', 'title', 'logo', 'description']}
            ),
            'bounty': (
                'dashboard.serializers.BountySerializer',
                {
                    'fields': [
                        'id', 'title', 'value_true', 'value_in_usdt_now', 'token_name', 'network',
                        'funding_organisation', 'bounty_owner_github_username'
                    ]
                }
            ),
            'hackathonevent': (
                'dashboard.serializers.HackathonEventSerializer',
                {'fields': ['id', 'slug', 'name', 'relative_url']}
            ),
            'kudos': (
                'dashboard.serializers.KudosTokenSerializer',
                {
                    'fields': [
                        'id', 'artist', 'url', 'ui_name', 'from_username', 'preview_img_url',
                        'description', 'img_url'
                    ]
                }
            ),
            'kudos_transfer': (
                'dashboard.serializers.KudosTransferSerializer', {'fields': ['id','username']}
            ),
            'other_profile': (
                'dashboard.serializers.ProfileSerializer', {'fields': ['url', 'handle']}
            ),
            'project': (
                'dashboard.serializers.HackathonProjectSerializer',
                {'fields': ['id', 'name', 'logo', 'bounty', 'hackathon']}
            )
        }

    def get_comments(self, obj):
        comments = CommentSerializer(
            obj.comments.order_by('-created_on')[:2],
            many=True,
            context=self.context
        ).data
        comments.reverse()
        return comments

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_likes(self, obj):
        likes = list(
            obj.likes.order_by('-created_on')\
                .values_list('profile__handle', flat=True).distinct()[:5]
        )
        return likes

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_owner(self, obj):
        user = self.context['request'].user
        return user.profile.pk == obj.profile.id if hasattr(user, 'profile') else None

    def get_viewer_reactions(self, obj):
        user = self.context['request'].user
        viewer_reactions = None

        if user.is_authenticated:
            viewer_reactions = {
                'like': obj.likes.filter(profile=user.profile).exists(),
                'favorite': user.favorites.filter(activity=obj).exists(),
                'flag': user.profile.flags.filter(activity=obj).exists()
            }

        return viewer_reactions


class InterestSerializer(serializers.ModelSerializer):
    """Handle serializing the Interest object."""

    profile = ProfileSerializer(fields=['handle'])

    class Meta:
        """Define the Interest serializer metadata."""
        model = Interest
        fields = ('pk', 'profile', 'created', 'pending', 'issue_message')


class BountySerializer(FlexFieldsModelSerializer):
    """Handle serializing the Bounty object."""

    fulfillments = BountyFulfillmentSerializer(many=True)
    interested = InterestSerializer(many=True)
    activities = ActivitySerializer(many=True)
    event = HackathonEventSerializer(many=False)
    bounty_owner_email = serializers.SerializerMethodField('override_bounty_owner_email')
    bounty_owner_name = serializers.SerializerMethodField('override_bounty_owner_name')

    def override_bounty_owner_email(self, obj):
        can_make_visible_via_api = bool(int(obj.privacy_preferences.get('show_email_publicly', 0)))
        default = "Anonymous"
        return obj.bounty_owner_email if can_make_visible_via_api else default

    def override_bounty_owner_name(self, obj):
        can_make_visible_via_api = bool(int(obj.privacy_preferences.get('show_name_publicly', 0)))
        default = "Anonymous"
        return obj.bounty_owner_name if can_make_visible_via_api else default

    class Meta:
        """Define the bounty serializer metadata."""

        model = Bounty
        fields = (
            'url', 'pk', 'created_on', 'modified_on', 'title', 'web3_created', 'value_in_token', 'token_name',
            'token_address', 'bounty_type', 'bounty_categories', 'project_length', 'experience_level',
            'github_url', 'github_comments', 'bounty_owner_address', 'bounty_owner_email',
            'bounty_owner_github_username', 'bounty_owner_name', 'fulfillments', 'interested', 'is_open',
            'expires_date', 'activities', 'keywords', 'current_bounty', 'value_in_eth',
            'token_value_in_usdt', 'value_in_usdt_now', 'value_in_usdt', 'status', 'now', 'avatar_url',
            'value_true', 'issue_description', 'network', 'org_name', 'pk', 'issue_description_text',
            'standard_bounties_id', 'web3_type', 'can_submit_after_expiration_date', 'github_issue_number',
            'github_org_name', 'github_repo_name', 'idx_status', 'token_value_time_peg',
            'fulfillment_accepted_on', 'fulfillment_submitted_on', 'fulfillment_started_on', 'canceled_on',
            'canceled_bounty_reason', 'action_urls', 'project_type', 'permission_type',
            'attached_job_description', 'needs_review', 'github_issue_state', 'is_issue_closed',
            'additional_funding_summary', 'funding_organisation', 'paid', 'event',
            'admin_override_suspend_auto_approval', 'reserved_for_user_handle', 'is_featured',
            'featuring_date', 'repo_type', 'funder_last_messaged_on', 'can_remarket', 'is_reserved'
        )

    def create(self, validated_data):
        """Handle creation of m2m relationships and other custom operations."""
        fulfillments_data = validated_data.pop('fulfillments')
        bounty = Bounty.objects.create(**validated_data)
        for fulfillment_data in fulfillments_data:
            bounty_fulfillment = BountyFulfillment.objects.create(bounty=bounty, **fulfillment_data)
            bounty_invite = BountyInvites.objects.filter(
                bounty=bounty,
                invitee=bounty_fulfillment.profile.user
            ).first()
            if bounty_invite:
                bounty_invite.status = 'completed'
                bounty_invite.save()
        return bounty

    def update(self, validated_data):
        """Handle updating of m2m relationships and other custom operations."""
        fulfillments_data = validated_data.pop('fulfillments')
        bounty = Bounty.objects.update(**validated_data)
        for fulfillment_data in fulfillments_data:
            bounty_fulfillment = BountyFulfillment.objects.create(bounty=bounty, **fulfillment_data)
            bounty_invite = BountyInvites.objects.filter(
                bounty=bounty,
                invitee=bounty_fulfillment.profile.user
            ).first()
            if bounty_invite:
                bounty_invite.status = 'completed'
                bounty_invite.save()
        return bounty


class HackathonProjectSerializer(FlexFieldsModelSerializer):
    bounty = BountySerializer(fields=[
        'pk', 'url', 'avatar_url', 'org_name', 'funding_organisation', 'bounty_owner_github_username'
    ])
    profiles = ProfileSerializer(many=True, fields=['handle'])
    hackathon = HackathonEventSerializer(fields=['id', 'name', 'slug'])
    comments = serializers.SerializerMethodField()

    class Meta:
        model = HackathonProject
        fields = (
            'pk', 'id', 'chat_channel_id', 'status', 'badge', 'bounty', 'name', 'summary',
            'work_url', 'profiles', 'hackathon', 'summary', 'logo', 'message',
            'looking_members', 'winner', 'grant_obj', 'admin_url', 'comments', 'url_project_page'
        )
        depth = 1

    def get_comments(self, obj):
        return Activity.objects.filter(activity_type='wall_post', project=obj).count()


class BountySerializerSlim(BountySerializer):

    class Meta:
        """Define the bounty serializer metadata."""
        model = Bounty
        fields = (
            'pk', 'url', 'title', 'experience_level', 'status', 'fulfillment_accepted_on', 'event',
            'fulfillment_started_on', 'fulfillment_submitted_on', 'canceled_on', 'web3_created', 'bounty_owner_address',
            'avatar_url', 'network', 'standard_bounties_id', 'github_org_name', 'interested', 'token_name', 'value_in_usdt',
            'keywords', 'value_in_token', 'project_type', 'is_open', 'expires_date', 'latest_activity', 'token_address',
            'bounty_categories'
        )


class BountySerializerCheckIn(BountySerializer):
    class Meta:
        model = Bounty
        fields = (
            'url', 'title', 'bounty_owner_name', 'status', 'github_url',
            'created_on', 'standard_bounties_id', 'bounty_owner_github_username',
            'no_of_applicants', 'num_fulfillments', 'has_applicant', 'warned', 'escalated', 'event'
        )


class TribesTeamSerializer(serializers.ModelSerializer):

    user_is_following = serializers.SerializerMethodField(method_name='user_following')
    followers_count = serializers.SerializerMethodField(method_name='follow_count')

    def follow_count(self, instance):
        return TribeMember.objects.filter(org=instance).exclude(status='rejected').exclude(profile__user=None).count()

    def user_following(self, instance):
        request = self.context.get('request')
        user_profile = request.user.profile if request and request.user and hasattr(request.user, 'profile') else None
        if user_profile:
            return len(user_profile.tribe_members.filter(org__handle=instance.handle.lower())) > 0

    class Meta:
        model = Profile
        fields = ('id', 'name', 'handle', 'avatar_url', 'followers_count', 'user_is_following')
        depth = 1


class BountyRequestSerializer(serializers.ModelSerializer):

    requested_by = TribesTeamSerializer()

    class Meta:
        model = BountyRequest
        fields = ('id', 'created_on', 'token_name', 'amount', 'comment', 'github_url', 'title', 'requested_by', 'status')
        depth = 1


class TribesSerializer(serializers.ModelSerializer):
    """Handle serializing the Profile object."""
    team_or_none_if_timeout = TribesTeamSerializer(many=True, read_only=True)
    suggested_bounties = BountyRequestSerializer(many=True)
    tribes_cover_image = serializers.ImageField(allow_empty_file=True)

    def __init__(self, *args, **kwargs):
        super(TribesSerializer, self).__init__(*args, **kwargs)
        # We pass the "upper serializer" context to the "nested one"
        self.fields['team_or_none_if_timeout'].context.update(self.context)

    class Meta:
        model = Profile
        """Define the profile serializer metadata."""
        fields = ('profile_wallpaper', 'tribes_cover_image', 'rank_org','name', 'linkedin_url', 'team_or_none_if_timeout', 'suggested_bounties', 'handle', 'tribe_description', 'avatar_url', 'follower_count', 'following_count', 'data', 'tribe_priority')
        depth = 1
