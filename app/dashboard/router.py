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
import time
from datetime import datetime

from django.db.models import Count, F, Q

import django_filters.rest_framework
from bounty_requests.models import BountyRequest
from kudos.models import KudosTransfer, Token
from rest_framework import routers, serializers, viewsets
from rest_framework.pagination import PageNumberPagination
from retail.helpers import get_ip

from .models import (
    Activity, Bounty, BountyFulfillment, BountyInvites, HackathonEvent, HackathonProject, Interest, Profile,
    ProfileSerializer, SearchHistory, TribeMember, UserDirectory,
)
from .tasks import increment_view_count

logger = logging.getLogger(__name__)


class BountyFulfillmentSerializer(serializers.ModelSerializer):
    """Handle serializing the BountyFulfillment object."""
    profile = ProfileSerializer()
    fulfiller_github_username = serializers.ReadOnlyField()

    class Meta:
        """Define the bounty fulfillment serializer metadata."""

        model = BountyFulfillment
        fields = ('pk', 'fulfiller_address',
                  'fulfiller_github_username', 'fulfiller_metadata',
                  'fulfillment_id', 'accepted', 'profile', 'created_on',
                  'accepted_on', 'fulfiller_github_url', 'payout_tx_id',
                  'payout_amount', 'token_name', 'payout_status', 'tenant',
                  'payout_type', 'fulfiller_identifier', 'funder_identifier')


class HackathonEventSerializer(serializers.ModelSerializer):
    """Handle serializing the hackathon object."""
    sponsor_profiles = ProfileSerializer(many=True)
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

# TODO : REMOVE KudosSerializer
class KudosSerializer(serializers.ModelSerializer):
    """Handle serializing the Kudos object."""

    class Meta:
        """Define the kudos serializer metadata."""

        model = KudosTransfer
        depth = 1
        fields = ('kudos_token_cloned_from', )


class KudosTokenSerializer(serializers.ModelSerializer):
    """Handle serializing the Kudos object."""

    class Meta:
        """Define the kudos serializer metadata."""

        model = Token
        depth = 1
        fields = ('price_finney', 'num_clones_allowed', 'num_clones_in_wild',
                  'num_clones_available_counting_indirect_send',
                  'cloned_from_id', 'popularity', 'popularity_week',
                  'popularity_month', 'popularity_quarter', 'name',
                  'override_display_name', 'description',
                  'image', 'rarity', 'tags', 'artist', 'platform',
                  'external_url',  'background_color', 'owner_address',
                  'txid', 'token_id', 'hidden',
                  'send_enabled_for_non_gitcoin_admins',
                  'preview_img_mode', 'suppress_sync', 'kudos_token_cloned_from')


class ActivitySerializer(serializers.ModelSerializer):
    """Handle serializing the Activity object."""

    profile = ProfileSerializer()
    kudos = KudosTokenSerializer()

    class Meta:
        """Define the activity serializer metadata."""

        model = Activity
        fields = ('activity_type', 'pk', 'created', 'profile', 'metadata', 'bounty', 'tip', 'kudos')


class InterestSerializer(serializers.ModelSerializer):
    """Handle serializing the Interest object."""

    profile = ProfileSerializer()

    class Meta:
        """Define the Interest serializer metadata."""
        model = Interest
        fields = ('pk', 'profile', 'created', 'pending', 'issue_message')


# Serializers define the API representation.
class BountySerializer(serializers.HyperlinkedModelSerializer):
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
            'url', 'created_on', 'modified_on', 'title', 'web3_created', 'value_in_token', 'token_name',
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


class HackathonProjectSerializer(serializers.ModelSerializer):
    bounty = BountySerializer()
    profiles = ProfileSerializer(many=True)
    hackathon = HackathonEventSerializer()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = HackathonProject
        fields = ('pk', 'chat_channel_id', 'status', 'badge', 'bounty', 'name', 'summary', 'work_url', 'profiles', 'hackathon', 'summary', 'logo', 'message', 'looking_members', 'winner', 'grant_obj', 'admin_url', 'comments', 'url_project_page')
        depth = 1

    def get_comments(self, obj):
        return Activity.objects.filter(activity_type='wall_post', project=obj).count()

class HackathonProjectsPagination(PageNumberPagination):
    page_size = 10


class HackathonProjectsViewSet(viewsets.ModelViewSet):
    queryset = HackathonProject.objects.prefetch_related('bounty', 'profiles').all().order_by('id')
    serializer_class = HackathonProjectSerializer
    pagination_class = HackathonProjectsPagination

    def get_queryset(self):

        q = self.request.query_params.get('search', '')
        order_by = self.request.query_params.get('order_by', '-created_on')
        skills = self.request.query_params.get('skills', '')
        filters = self.request.query_params.get('filters', '')
        sponsor = self.request.query_params.get('sponsor', '')
        hackathon_id = self.request.query_params.get('hackathon', '')
        rating = self.request.query_params.get('rating', '')

        if hackathon_id:
            try:
                hackathon_event = HackathonEvent.objects.get(id=hackathon_id)
            except HackathonEvent.DoesNotExist:
                hackathon_event = HackathonEvent.objects.last()

            queryset = HackathonProject.objects.filter(hackathon=hackathon_event).exclude(
                status='invalid').prefetch_related('profiles', 'bounty').order_by('-winner', 'grant_obj', order_by, 'id')

            if sponsor:
                queryset = queryset.filter(
                    Q(bounty__github_url__icontains=sponsor) | Q(bounty__bounty_owner_github_username=sponsor)
                )
        elif sponsor:
            queryset = HackathonProject.objects.filter(Q(hackathon__sponsor_profiles__handle=sponsor.lower()) | Q(
                bounty__bounty_owner_github_username=sponsor)).exclude(
                status='invalid').prefetch_related('profiles', 'bounty').order_by('-winner', 'grant_obj', order_by, 'id')

            projects = []
            for project in queryset:
                bounty = project.bounty
                org_name = bounty.org_name
                if org_name != sponsor:
                    projects.append(project.pk)

            queryset = queryset.exclude(pk__in=projects)

        if q:
            queryset = queryset.filter(
                Q(name__icontains=q) |
                Q(summary__icontains=q) |
                Q(profiles__handle__icontains=q)
            )

        if skills:
            queryset = queryset.filter(
                Q(profiles__keywords__icontains=skills)
            )
        if rating:
            queryset = queryset.filter(
                Q(rating__gte=rating)
            )

        if 'winners' in filters:
            queryset = queryset.filter(
                Q(winner=True)
            )
        if 'grants' in filters:
            queryset = queryset.filter(
                Q(grant_obj__isnull=False)
            )
        if 'lfm' in filters:
            queryset = queryset.filter(
                Q(looking_members=True)
            )
        if 'submitted' in filters:
            queryset = queryset.filter(
                Q(bounty__bounty_state='work_submitted')
            )

        return queryset


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


class BountiesViewSet(viewsets.ModelViewSet):
    """Handle Bounties view behavior."""
    queryset = Bounty.objects.prefetch_related('fulfillments', 'interested', 'interested__profile', 'activities', 'event') \
        .all().order_by('-web3_created')
    serializer_class = BountySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        """Get the queryset for Bounty.

        Returns:
            QuerySet: The Bounty queryset.

        """
        param_keys = self.request.query_params.keys()
        queryset = Bounty.objects.prefetch_related(
            'fulfillments', 'interested', 'interested__profile', 'activities', 'event')
        if 'not_current' not in param_keys:
            queryset = queryset.current()

        queryset = queryset.order_by('-web3_created')

        # filtering
        event_tag = self.request.query_params.get('event_tag', '')
        if event_tag:
            if event_tag == 'all':
                pass
            else:
                try:
                    evt = HackathonEvent.objects.filter(slug__iexact=event_tag).latest('id')
                    queryset = queryset.filter(event__pk=evt.pk)
                except HackathonEvent.DoesNotExist:
                    return Bounty.objects.none()
        # else:
        #     queryset = queryset.filter(event=None)

        for key in ['raw_data', 'experience_level', 'project_length', 'bounty_type', 'bounty_categories',
                    'bounty_owner_address', 'idx_status', 'network', 'bounty_owner_github_username',
                    'standard_bounties_id', 'permission_type', 'project_type', 'pk']:
            if key in param_keys:
                # special hack just for looking up bounties posted by a certain person
                request_key = key if key != 'bounty_owner_address' else 'coinbase'
                val = self.request.query_params.get(request_key, '')

                values = val.strip().split(',')
                values = [value for value in values if value and val.strip()]
                if values:
                    _queryset = queryset.none()
                    for value in values:
                        args = {}
                        args[f'{key}__icontains'] = value.strip()
                        _queryset = _queryset | queryset.filter(**args)
                    queryset = _queryset

        if 'reserved_for_user_handle' in param_keys:
            handle = self.request.query_params.get('reserved_for_user_handle', '')
            if handle:
                try:
                    profile = Profile.objects.filter(handle=handle.lower()).first()
                    queryset = queryset.filter(bounty_reserved_for_user=profile)
                except:
                    logger.warning(f'reserved_for_user_handle: Unknown handle: ${handle}')

        # filter by PK
        if 'pk__gt' in param_keys:
            queryset = queryset.filter(pk__gt=self.request.query_params.get('pk__gt'))

        # Filter by a list of PKs
        if 'pk__in' in param_keys:
            try:
                list_of_pks = self.request.query_params.get('pk__in').split(',')
                queryset = queryset.filter(pk__in=list_of_pks)
            except Exception:
                pass

        # filter by standard_bounties_id
        if 'standard_bounties_id__in' in param_keys:
            statuses = self.request.query_params.get('standard_bounties_id__in').split(',')
            queryset = queryset.filter(standard_bounties_id__in=statuses)

        # filter by statuses
        if 'status__in' in param_keys:
            statuses = self.request.query_params.get('status__in').split(',')
            queryset = queryset.filter(idx_status__in=statuses)

        applicants = self.request.query_params.get('applicants')
        if applicants == '0':
            queryset = queryset.annotate(
                interested_count=Count("interested")
            ).filter(interested_count=0)
        elif applicants == '1-5':
            queryset = queryset.annotate(
                interested_count=Count("interested")
            ).filter(interested_count__gte=1).filter(interested_count__lte=5)

        # filter by who is interested
        if 'started' in param_keys:
            queryset = queryset.filter(interested__profile__handle__in=[self.request.query_params.get('started')])

        # filter by is open or not
        if 'is_open' in param_keys:
            queryset = queryset.filter(is_open=self.request.query_params.get('is_open', '').lower() == 'true')
            queryset = queryset.filter(expires_date__gt=datetime.now())

        # filter by urls
        if 'github_url' in param_keys:
            urls = self.request.query_params.get('github_url').split(',')
            queryset = queryset.filter(github_url__in=urls)

        # filter by orgs
        if 'org' in param_keys:
            val = self.request.query_params.get('org', '')
            values = val.strip().split(',')
            values = [value for value in values if value and val.strip()]
            if values:
                _queryset = queryset.none()
                for value in values:
                    org = value.strip()
                    _queryset = _queryset | queryset.filter(github_url__icontains=f'https://github.com/{org}')
                queryset = _queryset

        # Retrieve all fullfilled bounties by fulfiller_username
        if 'fulfiller_github_username' in param_keys:
            queryset = queryset.filter(
                fulfillments__profile__handle__iexact=self.request.query_params.get('fulfiller_github_username')
            )

        # Retrieve all DONE fullfilled bounties by fulfiller_username
        if 'fulfiller_github_username_done' in param_keys:
            queryset = queryset.filter(
                fulfillments__profile__handle__iexact=self.request.query_params.get('fulfiller_github_username'),
                fulfillments__accepted=True,
            )

        # Retrieve all interested bounties by profile handle
        if 'interested_github_username' in param_keys:
            queryset = queryset.filter(
                interested__profile__handle=self.request.query_params.get('interested_github_username').lower()
            )

        # Retrieve all mod bounties.
        # TODO: Should we restrict this to staff only..? Technically I don't think we're worried about that atm?
        if 'moderation_filter' in param_keys:
            mod_filter = self.request.query_params.get('moderation_filter')
            if mod_filter == 'needs_review':
                queryset = queryset.needs_review()
            elif mod_filter == 'warned':
                queryset = queryset.warned()
            elif mod_filter == 'escalated':
                queryset = queryset.escalated()
            elif mod_filter == 'closed_on_github':
                queryset = queryset.closed()
            elif mod_filter == 'hidden':
                queryset = queryset.hidden()
            elif mod_filter == 'not_started':
                queryset = queryset.not_started()

        # All Misc Api things
        if 'misc' in param_keys:
            if self.request.query_params.get('misc') == 'hiring':
                queryset = queryset.exclude(attached_job_description__isnull=True).exclude(attached_job_description='')

        if 'event' in param_keys:
            queryset = queryset.filter(
                repo_type=self.request.query_params.get('event'),
            )

        # Keyword search to search all comma separated keywords
        queryset_original = queryset
        if 'keywords' in param_keys:
            for index, keyword in enumerate(self.request.query_params.get('keywords').split(',')):
                if index == 0:
                    queryset = queryset_original.keyword(keyword)
                else:
                    queryset |= queryset_original.keyword(keyword)

        if 'is_featured' in param_keys:
            queryset = queryset.filter(
                is_featured=bool(self.request.query_params.get('is_featured')),
                is_open=True,
            )

        if 'repo_type' in param_keys:
            queryset = queryset.filter(
                repo_type=self.request.query_params.get('repo_type'),
            )
        # order
        order_by = self.request.query_params.get('order_by')
        if order_by and order_by != 'null':
            if order_by == 'recently_marketed':
                queryset = queryset.order_by(F('last_remarketed').desc(nulls_last = True), '-web3_created')
            else:
                order_by_options = ['-web3_created', 'web3_created', '-_val_usd_db', '_val_usd_db']
                if order_by not in order_by_options:
                    order_by = '-web3_created'
                queryset = queryset.order_by(order_by)

        queryset = queryset.distinct()

        # offset / limit
        if 'is_featured' not in param_keys:
            limit = self.request.query_params.get('limit', '5')
            limit = 5 if not limit.isdigit() else int(limit)
            max_bounties = 100
            if limit > max_bounties:
                limit = max_bounties
            offset = self.request.query_params.get('offset', '0')
            if limit:
                start = int(offset) if offset.isdigit() else 0
                end = start + int(limit)
                queryset = queryset[start:end]

        data = dict(self.request.query_params)
        data.pop('is_featured', None)

        # save search history, but only not is_featured
        if 'is_featured' not in param_keys:
            if self.request.user and self.request.user.is_authenticated:
                data['nonce'] = int(time.time()  * 1000000)
                try:
                    SearchHistory.objects.update_or_create(
                        search_type='bounty',
                        user=self.request.user,
                        data=data,
                        ip_address=get_ip(self.request)
                    )
                except Exception as e:
                    logger.debug(e)
                    pass

        # increment view counts
        pks = [ele.pk for ele in queryset]
        if len(pks):
            view_type = 'individual' if len(pks) == 1 else 'list'
            increment_view_count.delay(pks, queryset[0].content_type, self.request.user.id, view_type)

        return queryset


class BountiesViewSetSlim(BountiesViewSet):
    queryset = Bounty.objects.all().order_by('-web3_created')
    serializer_class = BountySerializerSlim

class BountiesViewSetCheckIn(BountiesViewSet):
    queryset = Bounty.objects.all().order_by('standard_bounties_id')
    serializer_class = BountySerializerCheckIn


class BountyViewSet(viewsets.ModelViewSet):
    """API response for an individual bounty by url"""

    queryset = Bounty.objects.prefetch_related(
        'fulfillments', 'fulfillments__profile', 'interested', 'interested__profile', 'activities',
        'event'
    )
    serializer_class = BountySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get_queryset(self):
        """Constructs queryset for an individual bounty

        Returns:
            QuerySet: The Bounty queryset.

        """

        param_keys = self.request.query_params.keys()

        queryset = Bounty.objects.prefetch_related(
            'fulfillments', 'interested', 'interested__profile', 'activities',
            'event'
        )

        queryset = queryset.current()

        if 'github_url' in param_keys:
            url = self.request.query_params.get('github_url')
            queryset = queryset.filter(github_url=url)

        queryset = queryset.order_by('-web3_created')
        queryset = queryset.distinct()

        return queryset


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


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'bounties/slim', BountiesViewSetSlim)
router.register(r'bounties', BountiesViewSet)
router.register(r'checkin', BountiesViewSetCheckIn)

router.register(r'bounty', BountyViewSet)
router.register(r'projects_fetch', HackathonProjectsViewSet)
