import django_filters.rest_framework
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import IntegrityError
from django.http import JsonResponse
from rest_framework import routers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from dashboard.models import Profile, ProfileSerializer
from experts.consumers import USER_CHANNEL_NAME
from .models import ExpertSession, ExpertSessionInterest
from .serializers import ExpertSessionSerializer


class ExpertSessionViewSet(viewsets.ModelViewSet):
    """Handle the ExpertSession API view behavior."""

    queryset = ExpertSession.objects.all()  # TODO filter
    serializer_class = ExpertSessionSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Get the queryset for ExpertSession
        """
        return ExpertSession.objects.all()  # TODO filter

    @action(detail=False, methods=['post'])
    def new(self, request, pk=None):
        """ Create a new session requesting help. """
        # TODO validation
        session = ExpertSession.objects.create(
            requested_by=Profile.objects.get(user=request.user),
            title=request.data['title'],
            description=request.data['description'],
        )
        return JsonResponse(ExpertSessionSerializer(session).data)

    @action(detail=True, methods=['get'])
    def app_init(self, request, pk=None):
        # Return data required to initialise Experts app
        # session, user profile
        session = ExpertSession.objects.get(pk=pk)
        return JsonResponse({
            'session': ExpertSessionSerializer(session).data,
            'profile': ProfileSerializer(Profile.objects.get(user=request.user)).data
        })

    @action(detail=True, methods=['post'])
    def send_join_request(self, request, pk=None):
        session = ExpertSession.objects.get(pk=pk)
        try:
            ExpertSessionInterest.objects.create(
                session=session,
                profile=Profile.objects.get(user=request.user),
                signature=request.data['signature'],
                main_address=request.data['main_address'],
                delegate_address=request.data['delegate_address'],
            )
        except IntegrityError as e:
            return JsonResponse({'error': 'TODO'}, status=400)

        session = ExpertSession.objects.get(pk=pk)
        session.send_group_message(
            'session_update',
            ExpertSessionSerializer(session).data)

        return JsonResponse({'message': 'ok'})

    @action(detail=True, methods=['post'])
    def accept_join_request(self, request, pk=None):
        session = ExpertSession.objects.get(
            pk=pk,
            requested_by=Profile.objects.get(user=request.user))
        session_interest = ExpertSessionInterest.objects.get(
            pk=request.data['interest_id'],
            session=session,
        )
        session.status = ExpertSession.STATUS_READY
        session.accepted_interest = session_interest
        session.save()
        session.send_group_message(
            'session_update', ExpertSessionSerializer(session).data
        )
        return JsonResponse({'message': 'ok'})

    @action(detail=True, methods=['post'])
    def request_ticket(self, request, pk=None):
        session = ExpertSession.objects.get(
            pk=pk,
            accepted_interest__profile__user=request.user,
            status=ExpertSession.STATUS_ACTIVE
        )
        channel_layer = get_channel_layer()
        channel_data = {
            "type": "send_group_action",
            "action_type": 'ticket_request',
            "data": request.data
        }
        user_channel = USER_CHANNEL_NAME.format(session.requested_by.handle)
        async_to_sync(channel_layer.group_send)(user_channel, channel_data)

        return JsonResponse({'message': 'ok'})

    @action(detail=True, methods=['post'])
    def send_ticket(self, request, pk=None):
        # TODO verify signature
        session = ExpertSession.objects.get(
            pk=pk,
            requested_by__user=request.user,
            status=ExpertSession.STATUS_ACTIVE
        )
        session.value = request.data['value']
        session.signature = request.data['signature']
        session.save()

        channel_layer = get_channel_layer()
        channel_data = {
            "type": "send_group_action",
            "action_type": 'send_ticket',
            "data": request.data
        }
        user_channel = USER_CHANNEL_NAME.format(session.accepted_interest.profile.handle)
        async_to_sync(channel_layer.group_send)(user_channel, channel_data)

        session.send_group_message(
            'session_update', ExpertSessionSerializer(session).data)

        return JsonResponse({'message': 'ok'})

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        # one of the users has closed the session
        # TODO filter for users
        session = ExpertSession.objects.get(
            pk=pk,
            status=ExpertSession.STATUS_ACTIVE
        )
        session.status = ExpertSession.STATUS_CLOSED
        session.save()
        session.send_group_message(
            'session_ended', {
                'session': ExpertSessionSerializer(session).data
            }
        )
        return JsonResponse({'message': 'ok'})

    @action(detail=True, methods=['post'])
    def start_confirmed(self, request, pk=None):
        # host has started the session (has tx been confirmed yet?)
        session = ExpertSession.objects.get(
            pk=pk,
            requested_by__user=request.user
        )
        session.status = ExpertSession.STATUS_ACTIVE
        session.start_tx_hash = request.data['tx_hash']
        session.channel_id = request.data['channel_id']
        session.save()
        session.send_group_message(
            'session_started', {
                'session': ExpertSessionSerializer(session).data
            })
        return JsonResponse({'message': 'ok'})

    @action(detail=True, methods=['post'])
    def funds_claimed(self, request, pk=None):
        # payee has claimed the funds
        session = ExpertSession.objects.get(
            pk=pk,
            accepted_interest__profile__user=request.user
        )
        session.claim_tx_hash = request.data['tx_hash']
        session.status = ExpertSession.STATUS_CLOSED
        session.save()
        session.send_group_message(
            'session_update', ExpertSessionSerializer(session).data
        )
        return JsonResponse({'message': 'ok'})

    @action(detail=True, methods=['post'])
    def cancel_join_request(self, request, pk=None):
        # someone no longer wants to join the session
        ExpertSessionInterest.objects.get(
            profile__user=request.user,
            pk=request.data['interest_id'],
            session_id=pk,
        ).delete()

        session = ExpertSession.objects.get(
            pk=pk
        )
        session.send_group_message(
            'session_update', ExpertSessionSerializer(session).data
        )
        return JsonResponse({'message': 'ok'})


router = routers.DefaultRouter()
router.register(r'sessions', ExpertSessionViewSet)
