from dashboard.router import ProfileSerializer
from rest_framework import serializers

from .models import Contribution, Grant, Milestone, Subscription


class MilestoneSerializer(serializers.ModelSerializer):
    """Handle serializing the Milestone object."""

    class Meta:
        """Define the milestone serializer metadata."""

        model = Milestone
        fields = ('title', 'description', 'due_date', 'completion_date')


class GrantSerializer(serializers.ModelSerializer):
    """Handle serializing the Grant object."""

    admin_profile = ProfileSerializer()
    team_members = ProfileSerializer(many=True)
    milestones = MilestoneSerializer(many=True)

    class Meta:
        """Define the grant serializer metadata."""

        model = Grant
        fields = (
            'active', 'title', 'slug', 'description', 'reference_url', 'logo', 'admin_address', 'amount_goal',
            'amount_received', 'token_address', 'token_symbol', 'contract_address', 'transaction_hash', 'metadata',
            'network', 'required_gas_price', 'admin_profile', 'team_members', 'percentage_done', 'milestones',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Handle serializing the Subscription object."""

    contributor_profile = ProfileSerializer()
    grant = GrantSerializer()

    class Meta:
        """Define the subscription serializer metadata."""

        model = Subscription
        fields = (
            'active', 'subscription_hash', 'contributor_signature', 'contributor_address', 'amount_per_period',
            'real_period_seconds', 'frequency_unit', 'frequency', 'token_address', 'token_symbol', 'gas_price',
            'network', 'grant', 'contributor_profile',
        )


class ContributionSerializer(serializers.ModelSerializer):
    """Handle serializing the Contribution object."""

    subscription = SubscriptionSerializer()

    class Meta:
        """Define the contribution serializer metadata."""

        model = Contribution
        fields = (
            'tx_id', 'from_address', 'to_address', 'token_address', 'token_amount', 'period_seconds', 'gas_price',
            'nonce', 'subscription',
        )
