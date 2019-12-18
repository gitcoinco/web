from rest_framework import serializers

from dashboard.models import Bounty, Activity, Tip


def get_space_data(space, user, partial_schema):
    profile = user.profile
    if space == 'profile':
        return get_profile(profile)
    if space == 'activity':
        return ActivitySerializer(profile.activities, many=True).data
    if space == 'bounties':
        return BountySerializer(profile.bounties, many=True).data
    if space == 'preferences':
        return get_preference(profile)
    if space == 'tips':
        return TipSerializer(Tip.objects.all(), many=True).data

    return {}


class ActivitySerializer(serializers.ModelSerializer):
    type = serializers.CharField(source='activity_type')
    resource = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ('id', 'type', 'resource', 'url', 'created')

    def get_url(self, instance):
        resource = self.get_resource(instance)
        if resource in ('bounty', ):
            return instance.bounty.get_absolute_url()

        if resource in ('kudos', ):
            return instance.kudos.kudos_token.get_absolute_url()

        if resource in ('profile', ):
            return instance.profile.absolute_url

        return ''

    def get_resource(self, instance):
        resource = ''
        if instance.activity_type in ('new_bounty', 'start_work', 'stop_work', 'work_submitted',
                                      'work_done', 'worker_approved', 'worker_rejected',
                                      'worker_applied', 'increased_bounty', 'killed_bounty'
                                      'bounty_abandonment_escalation_to_mods',
                                      'new_crowdfund'
                                      'bounty_abandonment_warning', 'bounty_removed_by_funder',
                                      'bounty_removed_slashed_by_staff',
                                      'bounty_removed_by_staff'):
            resource = 'bounty'

        elif instance.activity_type in ('new_tip', 'receive_tip'):
            resource = 'tip'

        elif instance.activity_type in ('new_kudos',):
            resource = 'kudos'

        elif instance.activity_type in ('joined', 'updated_avatar'):
            resource = 'profile'
        return resource

    def get_created(self, instance):
        return instance.created.isoformat()


class BountySerializer(serializers.ModelSerializer):
    """Handle serializing the Bounty object."""
    state = serializers.CharField(source='idx_status')
    provider = serializers.CharField(default='gitcoin')
    issue_provider = serializers.CharField(default='github')
    reserved_for_user = serializers.CharField(source='bounty_reserved_for_user')
    issue_url = serializers.CharField(source='github_url')
    url = serializers.CharField(source='get_absolute_url')
    created = serializers.SerializerMethodField()
    expires_date = serializers.SerializerMethodField()


    class Meta:
        """Define the bounty serializer metadata."""
        model = Bounty
        fields = ('id', 'title', 'token_name', 'token_address', 'bounty_type',
                  'project_length', 'estimated_hours', 'experience_level', 'canceled_on',
                  'value_in_token', 'value_in_usdt', 'reserved_for_user', 'is_open',
                  'standard_bounties_id', 'accepted', 'fulfillment_accepted_on',
                  'fulfillment_submitted_on', 'fulfillment_started_on', 'funding_organisation',
                  'canceled_bounty_reason', 'project_type', 'bounty_categories', 'submissions_comment',
                  # Custom fields
                  'created', 'state', 'provider', 'issue_provider', 'expires_date', 'issue_url', 'url'
                  )

    def get_created(self, instance):
        return instance.created_on.isoformat()

    def get_expires_date(self, instance):
        return instance.expires_date.isoformat()


def get_profile(profile):
    avatar = profile.avatar_url if profile.has_custom_avatar() else ''

    return {
        'name': profile.user.get_full_name(),
        'handle': profile.handle,
        'tagline': profile.custom_tagline,
        'keywords': profile.keywords,
        'avatar': avatar,
        'wallpaper': profile.profile_wallpaper,
        'funder': profile.persona_is_funder,
        'hunter': profile.persona_is_hunter,
        'gitcoin.last_login': profile.user.last_login.isoformat(),
        'gitcoin.date_joined': profile.user.date_joined.isoformat(),
    }


def get_preference(profile):
    return {
        'hide_profile': profile.hide_profile,
        'preferred_payout_address': profile.preferred_payout_address,
        'preferred_acknowledgment_wallet': profile.preferred_kudos_wallet,
        'preferred_lang': profile.pref_lang_code
    }


class TipSerializer(serializers.ModelSerializer):
    expires = serializers.SerializerMethodField()
    created = serializers.SerializerMethodField()
    status = serializers.CharField(source='tx_status')
    token = serializers.CharField(source='tokenName')
    token_address = serializers.CharField(source='tokenAddress')
    rewarded_for = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    comments_private = serializers.CharField(source='comments_priv')

    class Meta:
        model = Tip
        fields = ('id', 'expires', 'created', 'comments_private', 'status', 'comments_public',
                  'recipient', 'sender', 'amount', 'token', 'token_address', 'rewarded_for',
                  'value_in_usdt')

    def get_expires(self, instance):
        return instance.expires_date.isoformat()

    def get_created(self, instance):
        return instance.created_on.isoformat()

    def get_recipient(self, instance):
        return instance.recipient_profile.handle

    def get_sender(self, instance):
        return instance.sender_profile.handle

    def get_rewarded_for(self, instance):
        bounty = instance.bounty
        if bounty:
            return bounty.get_absolute_url()

        return ''
