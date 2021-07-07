from dashboard.router import ProfileSerializer
from rest_framework import serializers

from .models import Contribution, Grant, Subscription
from .utils import amount_in_wei, get_converted_amount, which_clr_round


class GrantSerializer(serializers.ModelSerializer):
    """Handle serializing the Grant object."""

    admin_profile = ProfileSerializer()
    team_members = ProfileSerializer(many=True)

    class Meta:
        """Define the grant serializer metadata."""

        model = Grant
        fields = (
            'active', 'title', 'slug', 'description', 'reference_url', 'logo', 'admin_address',
            'amount_received', 'token_address', 'token_symbol', 'contract_address', 'metadata',
            'network', 'required_gas_price', 'admin_profile', 'team_members', 'clr_prediction_curve',
            'clr_round_num', 'is_clr_active', 'amount_received_in_round', 'positive_round_contributor_count',
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

class TransactionsSerializer(serializers.Serializer):
    """Handle serializing Transactions information."""

    asset = serializers.CharField(source='subscription.token_symbol')
    timestamp = serializers.DateTimeField(source='created_on')
    amount = serializers.SerializerMethodField()
    clr_round = serializers.SerializerMethodField()
    usd_value = serializers.SerializerMethodField()
    tx_hash = serializers.SerializerMethodField()

    def get_amount(self, obj):
        subscription = obj.subscription
        return format(amount_in_wei(subscription.token_address, subscription.amount_per_period_minus_gas_price), '.0f')

    def get_clr_round(self, obj):
        return which_clr_round(obj.created_on)

    def get_usd_value(self, obj):
        subscription = obj.subscription
        return subscription.get_converted_amount(ignore_gitcoin_fee=False)

    def get_tx_hash(self, obj):
        return obj.tx_id if obj.tx_id else obj.split_tx_id

    class Meta:
        """Define the Transactions serializer metadata."""

        fields = ('asset', 'timestamp', 'amount', 'clr_round', 'usd_value', 'tx_hash')

class CLRPayoutsSerializer(serializers.Serializer):
    """Handle serializing CLR Payout information."""

    amount = serializers.FloatField()
    asset = serializers.CharField(default='DAI')
    usd_value = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(source='created_on')
    round = serializers.IntegerField(source='round_number')
    tx_hash = serializers.CharField(source='payout_tx')

    def get_usd_value(self, obj):
        return get_converted_amount(obj.amount, 'DAI')

    class Meta:
        """Define the CLRPayout serializer metadata."""

        fields = ('amount', 'asset', 'usd_value', 'timestamp', 'round', 'tx_hash')

class DonorSerializer(serializers.Serializer):
    """Handle serializing Donor information."""

    grant_name = serializers.CharField(source='subscription.grant.title')
    asset = serializers.CharField(source='subscription.token_symbol')
    timestamp = serializers.DateTimeField(source='created_on')
    grant_amount = serializers.SerializerMethodField()
    gitcoin_maintenance_amount = serializers.SerializerMethodField()
    grant_usd_value = serializers.SerializerMethodField()
    gitcoin_usd_value = serializers.SerializerMethodField()
    
    def get_grant_amount(self, obj):
        subscription = obj.subscription
        grant_amount = format(amount_in_wei(subscription.token_address, subscription.amount_per_period_minus_gas_price), '.0f')
        return grant_amount

    def get_gitcoin_maintenance_amount(self, obj):
        subscription = obj.subscription
        gitcoin_maintenance_amount = format(amount_in_wei(subscription.token_address, subscription.amount_per_period_to_gitcoin), '.0f')
        return gitcoin_maintenance_amount

    def get_grant_usd_value(self, obj):
        subscription = obj.subscription
        grant_usd_value = subscription.get_converted_amount(ignore_gitcoin_fee=False)
        return grant_usd_value

    def get_gitcoin_usd_value(self, obj):
        subscription = obj.subscription
        gitcoin_usd_value = subscription.get_converted_amount(only_gitcoin_fee=True)
        return gitcoin_usd_value

    class Meta:
        """Define the Donor serializer metadata."""

        fields = ('grant_name', 'asset', 'timestamp', 'grant_amount', 'gitcoin_maintenance_amount', 'grant_usd_value', 'gitcoin_usd_value')
