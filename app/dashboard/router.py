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

from django.db.models import Count, F, Prefetch, Q
from django.shortcuts import get_object_or_404

import django_filters.rest_framework
from marketing.mails import tip_comment_awarded_email
from rest_framework import mixins, routers, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from retail.helpers import get_ip
from townsquare.models import Comment, Favorite, Flag, Like, PinnedPost
from townsquare.tasks import increment_view_counts

from .models import Activity, Bounty, HackathonEvent, HackathonProject, Profile, SearchHistory
from .permissions import CanPinPost, IsOwner, ReadOnly
from .serializers import (
    ActivitySerializer, AwardCommentSerializer, BountySerializer, BountySerializerCheckIn, BountySerializerSlim,
    CommentSerializer, HackathonProjectSerializer, PinnedPostSerializer, VoteSerializer,
)
from .tasks import increment_view_count

logger = logging.getLogger(__name__)


class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('profile').order_by('-created_on')
    serializer_class = CommentSerializer
    pagination_class = CommentPagination
    filterset_fields = ['activity']
    permission_classes=[IsOwner|ReadOnly]

    def list(self, request, *args, **kwargs):
        activity = request.query_params.get('activity', False)

        if not activity:
            return Response(
                {'detail': 'You have not specified a resource type.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(profile=self.request.user.profile)

    def perform_update(self, serializer):
        serializer.save(
            profile=self.request.user.profile,
            is_edited=True
        )

    @action(detail=True, methods=['POST', 'DELETE'], name='Like Comment',
            permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        profile_pk = request.user.profile.pk

        if request.method == 'POST':
            already_likes = profile_pk in comment.likes
            if not already_likes:
                comment.likes.append(profile_pk)
            comment.save(update_fields=['likes'])
            return Response(status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            comment.likes = [ele for ele in comment.likes if ele != profile_pk]
            comment.save(update_fields=['likes'])
            return Response(status=status.HTTP_204_NO_CONTENT)


class ActivityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class ActivityViewSet(mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    queryset = (
        Activity.objects
        .select_related(
            'profile', 'bounty', 'grant', 'hackathonevent', 'kudos',
            'kudos_transfer', 'other_profile', 'project'
        ).prefetch_related(
            Prefetch(
                'comments',
                queryset=Comment.objects.select_related('profile')
            ),
            Prefetch(
                'likes',
                queryset=Like.objects.select_related('profile')
            )
        ).order_by('-id')
    )
    serializer_class = ActivitySerializer
    pagination_class = ActivityPagination
    filterset_fields = {
        'activity_type': ["in", "exact"],
        'bounty': ["exact"],
        'grant': ["exact"],
        'hackathonevent': ["exact"],
        'project': ["exact"],
        'profile': ["exact"],
        'kudos': ["exact"],
        'kudos_transfer': ["exact"],
        'subscription': ["exact"],
        'tip': ["exact"]
    }

    permission_classes = [IsOwner|ReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            # increment view counts
            activities_pks = [obj.pk for obj in page]
            increment_view_counts.delay(activities_pks)

            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], name='Award Comment',
            serializer_class=AwardCommentSerializer, permission_classes=[IsAuthenticated])
    def award(self, request, pk=None):
        comment_pk = request.data.get('comment')
        serializer = self.get_serializer(data={'comment': comment_pk})
        serializer.is_valid(raise_exception=True)
        comment = get_object_or_404(Comment, id=comment_pk)
        activity = self.get_object()

        if request.user.profile.pk == activity.profile.pk and comment.activity_id == activity.id:
            recipient_profile = comment.profile
            activity.tip.username = recipient_profile.username
            activity.tip.recipient_profile = comment.profile
            activity.tip.save(update_fields=['username', 'recipient_profile'])
            comment.tip = activity.tip
            comment.save(update_fields=['tip'])
            tip_comment_awarded_email(comment, [recipient_profile.email])
        else:
            return Response(
                {'detail': 'Only the post creator can award this comment.'},
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['POST', 'DELETE'], name='Favorite Activity',
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        activity = self.get_object()

        if request.method == 'POST':
            already_likes = Favorite.objects.filter(activity=activity, user=request.user).exists()
            if not already_likes:
                Favorite.objects.create(user=request.user, activity=activity)
            return Response(status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            Favorite.objects.filter(user=request.user, activity=activity).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'], name='Report Activity',
            permission_classes=[IsAuthenticated])
    def flag(self, request, pk=None):
        activity = self.get_object()

        if request.method == 'POST':
            Flag.objects.create(profile=request.user.profile, activity=activity)
            flag_threshold_to_hide = 3 # hides comment after 3 flags
            is_hidden_by_users = activity.flags.count() > flag_threshold_to_hide
            is_hidden_by_staff = activity.flags.filter(profile__user__is_staff=True).count() > 0
            is_hidden_by_moderators = activity.flags.filter(profile__user__groups__name='Moderators').count() > 0
            is_hidden = is_hidden_by_users or is_hidden_by_staff or is_hidden_by_moderators
            if is_hidden:
                activity.hidden = True
                activity.save(update_fields=['hidden'])
            return Response(status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            activity.flags.filter(profile=request.user.profile).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'], name='Like Activity',
            permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        activity = self.get_object()

        if request.method == 'POST':
            already_likes = request.user.profile.likes.filter(activity=activity).exists()
            if not already_likes:
                Like.objects.create(profile=request.user.profile, activity=activity)
            return Response(status=status.HTTP_200_OK)

        elif request.method == 'DELETE':
            activity.likes.filter(profile=request.user.profile).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST', 'DELETE'], serializer_class=PinnedPostSerializer,
            name='Pin Post', permission_classes=[CanPinPost])
    def pin(self, request, pk=None):
        what = request.data.get('what', False)

        if not what:
            return Response(
                {'what': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            pinned_post, _ = PinnedPost.objects.update_or_create(
                what=what,
                defaults={
                    'activity': self.get_object(),
                    'user': request.user.profile
                }
            )
            return Response(
                self.get_serializer(pinned_post).data,
                status=status.HTTP_200_OK
            )

        elif request.method == 'DELETE':
            PinnedPost.objects.filter(what=what).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'], serializer_class=VoteSerializer,
            name='Poll Vote', permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        index = request.data.get('choice')
        serializer = self.get_serializer(data={'choice': index})
        serializer.is_valid(raise_exception=True)
        activity = self.get_object()

        if not activity.has_voted(request.user):
            activity.metadata['poll_choices'][index]['answers'].append(request.user.profile.pk)
            activity.save(update_fields=['metadata'])

        return Response(status=status.HTTP_200_OK)


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

        return self.queryset


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


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'bounties/slim', BountiesViewSetSlim)
router.register(r'bounties', BountiesViewSet)
router.register(r'checkin', BountiesViewSetCheckIn)
router.register(r'activities', ActivityViewSet)
router.register(r'comments', CommentViewSet)

router.register(r'bounty', BountyViewSet)
router.register(r'projects_fetch', HackathonProjectsViewSet)
