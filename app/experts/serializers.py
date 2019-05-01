from dashboard.router import ProfileSerializer
from rest_framework import serializers

from .models import ExpertSession, ExpertSessionInterest


class ExpertSessionInterestSerializer(serializers.ModelSerializer):
    """Handle serializing the ExpertSession object."""

    profile = ProfileSerializer()
    # session_id =

    class Meta:
        """Define the SessionInterest serializer metadata."""

        model = ExpertSessionInterest
        fields = (
            'id', 'created_on', 'signature', 'profile', 'session_id',
            'main_address', 'delegate_address'
        )


class ExpertSessionSerializer(serializers.ModelSerializer):
    """Handle serializing the ExpertSession object."""

    requested_by = ProfileSerializer()
    interests = ExpertSessionInterestSerializer(many=True)
    accepted_interest = ExpertSessionInterestSerializer()

    class Meta:
        """Define the Session serializer metadata."""

        model = ExpertSession
        fields = (
            'id', 'status', 'requested_by', 'title', 'description', 'created_on', 'modified_on',
            'interests', 'accepted_interest', 'value', 'claim_tx_hash', 'signature',
            'channel_id'
        )
