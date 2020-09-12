import json

from django.conf import settings

from avatar.models import CustomAvatar
from grants.models import Grant
from rest_framework import serializers

from .models import Activity, Bounty, FeedbackEntry, Tip


class ProfileExportSerializer(serializers.BaseSerializer):
    """Handle serializing the exported Profile object."""

    def to_representation(self, instance):
        """Provide the serialized representation of the Profile.

           Notice: Add understore (_) before a key to indicate it's a private key/value pair, otherwise the key/value pair will be saved publicly after exported.

        Args:
            instance (Profile): The Profile object to be serialized.

        Returns:
            dict: The serialized Profile.

        """

        d = instance.as_dict

        return {
            # basic info
            'id': instance.id,
            'username': instance.handle,
            'full_name': instance.user.get_full_name(),
            'gitcoin_url': instance.absolute_url,
            'github_url': instance.github_url,
            'avatar_url': instance.avatar_url,
            'wallpaper': instance.profile_wallpaper,
            'keywords': instance.keywords,
            'portfolio_keywords': d['portfolio_keywords'],
            'position': instance.get_contributor_leaderboard_index(),
            '_locations': instance.locations,
            'organizations': instance.get_who_works_with(network=None),
            '_email': instance.email,
            '_pref_lang_code': instance.pref_lang_code,
            '_preferred_payout_address': instance.preferred_payout_address,
            'persona': instance.selected_persona or instance.dominant_persona,
            'persona_is_funder': instance.persona_is_funder,
            'persona_is_hunter': instance.persona_is_hunter,

            # job info
            # 'linkedin_url': instance.linkedin_url,
            # '_job_search_status': instance.job_search_status,
            # '_job_type': instance.job_type,
            # '_job_salary': instance.job_salary,
            # '_job_location': instance.job_location,
            # '_resume': instance.resume,

            # stats
            'last_visit': instance.last_visit,
            'longest_streak': instance.longest_streak,
            'activity_level': instance.activity_level,
            'avg_hourly_rate': instance.avg_hourly_rate,
            'success_rate': instance.success_rate,
            'reliability': instance.reliability,
            'rank_funder': instance.rank_funder,
            'rank_org': instance.rank_org,
            'rank_coder': instance.rank_coder,
            # contribution v.s. funding
            'completed_bounties_count': d['count_bounties_completed'],
            'funded_bounties_count': d['funded_bounties_count'],
            'earnings_total': d['earnings_total'],
            'earnings_count': d['earnings_count'],
            'spent_total': d['spent_total'],
            'spent_count': d['spent_count'],
            'sum_eth_collected': d['sum_eth_collected'],
            'sum_eth_funded': d['sum_eth_funded'],
            'hackathons_participated_in': d['hackathons_participated_in'],
            'hackathons_funded': d['hackathons_funded'],
            'total_tips_sent': d['total_tips_sent'],
            'total_tips_received': d['total_tips_received'],
            # rating
            'overall_average_rating': d['avg_rating']['overall'],
            'code_quality_average_rating': d['avg_rating']['code_quality_rating'],
            'communication_rating': d['avg_rating']['communication_rating'],
            'recommendation_rating': d['avg_rating']['recommendation_rating'],
            'satisfaction_rating': d['avg_rating']['satisfaction_rating'],
            'speed_rating': d['avg_rating']['speed_rating'],
            'total_rating_count': d['avg_rating']['total_rating'],
        }


class GrantExportSerializer(serializers.ModelSerializer):
    """Handle serializing the exported Grant object."""
    org = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    contribution_count = serializers.SerializerMethodField()
    contributor_count = serializers.SerializerMethodField()

    class Meta:

        model = Grant
        fields = ('id', 'active', 'grant_type', 'title', 'slug',
                  'description', 'description_rich', 'reference_url', 'logo',
                  'admin_address', 'contract_owner_address',
                  'monthly_amount_subscribed', 'amount_received', 'token_address',
                  'token_symbol', 'contract_address', 'network',
                  'org', 'created_at', 'url', 'contribution_count', 'contributor_count', 'project_link'
                  )

    def get_created_at(self, instance):
        return instance.created_on.isoformat()

    def get_org(self, instance):
        return instance.org_name

    def get_url(self, instance):
        return instance.get_absolute_url()

    def get_contributor_count(self, instance):
        return instance.get_contributor_count()

    def get_contribution_count(self, instance):
        return instance.get_contribution_count


class BountyExportSerializer(serializers.ModelSerializer):
    """Handle serializing the exported Bounty object."""
    gitcoin_link = serializers.CharField(source='get_absolute_url')
    status = serializers.CharField(source='idx_status')
    gitcoin_provider = serializers.CharField(default='gitcoin')
    github_provider = serializers.CharField(default='github')
    created_at = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()

    class Meta:

        model = Bounty
        fields = ('id', 'title', 'gitcoin_link', 'github_url', 'token_name', 'token_address',
                  'bounty_type', 'project_type', 'bounty_categories', 'project_length',
                  'estimated_hours', 'experience_level', 'value_in_token', 'value_in_usdt',
                  'bounty_reserved_for_user', 'is_open', 'standard_bounties_id', 'accepted',
                  'funding_organisation', 'gitcoin_provider', 'github_provider',
                  'canceled_bounty_reason', 'submissions_comment', 'fulfillment_accepted_on',
                  'fulfillment_submitted_on', 'fulfillment_started_on', 'canceled_on',
                  'created_at', 'expires_at', 'status'
                )

    def get_created_at(self, instance):
        return instance.created_on.isoformat()

    def get_expires_at(self, instance):
        return instance.expires_date.isoformat()


class ActivityExportSerializer(serializers.ModelSerializer):
    """Handle serializing the exported Activity object."""

    created_at = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    category = serializers.CharField(source='activity_type')
    action = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ('id', 'created_at', 'category', 'action', 'url', )

    def get_created_at(self, instance):
        return instance.created.isoformat()

    def get_url(self, instance):
        return instance.action_url

    def get_action(self, instance):
        action = ''
        t = instance.activity_type
        if t in ('joined', 'updated_avatar'):
            action = 'profile'
        elif t in ('bounty_abandonment_warning', 'bounty_removed_by_funder',
                  'bounty_removed_slashed_by_staff', 'bounty_removed_by_staff','new_bounty',
                  'start_work', 'stop_work', 'work_done', 'worker_approved', 'worker_rejected',
                  'worker_applied', 'increased_bounty', 'killed_bounty',
                  'bounty_abandonment_escalation_to_mods', 'new_crowdfund', 'work_submitted'
                  ):
            action = 'bounty'
        elif t in ('new_kudos',):
            action = 'kudos'
        elif t in ('new_tip', 'receive_tip'):
            action = 'tip'

        return action

class TipExportSerializer(serializers.ModelSerializer):
    bounty_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    expires_at = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    recipient = serializers.SerializerMethodField()
    status = serializers.CharField(source='tx_status')
    token = serializers.CharField(source='tokenName')
    token_address = serializers.CharField(source='tokenAddress')
    transaction_address = serializers.CharField(source='receive_address')
    public_comments = serializers.CharField(source='comments_public')
    private_comments = serializers.CharField(source='comments_priv')

    class Meta:
        model = Tip
        fields = ('id', 'status', 'sender', 'recipient',  'amount', 'token', 'token_address',
                  'transaction_address', 'bounty_url', 'value_in_usdt', 'public_comments',
                  'private_comments', 'created_at', 'expires_at')

    def get_bounty_url(self, instance):
        bounty = instance.bounty
        if bounty:
            return bounty.get_absolute_url()

        return ''

    def get_created_at(self, instance):
        return instance.created_on.isoformat()

    def get_expires_at(self, instance):
        return instance.expires_date.isoformat()

    def get_sender(self, instance):
        return instance.sender_profile.handle if instance.sender_profile else ''

    def get_recipient(self, instance):
        return instance.recipient_profile.handle if instance.recipient_profile else ''

class FeedbackExportSerializer(serializers.ModelSerializer):
    bounty_url = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()
    feedback_type = serializers.CharField(source='feedbackType')
    comment = serializers.SerializerMethodField()

    class Meta:
        model = FeedbackEntry
        fields = ('id', 'sender', 'receiver', 'bounty_url', 'rating',
                  'satisfaction_rating', 'created_at',
                  'communication_rating', 'speed_rating', 'code_quality_rating',
                  'recommendation_rating', 'feedback_type', 'comment')

    def get_bounty_url(self, instance):
        bounty = instance.bounty
        if bounty:
            return bounty.get_absolute_url()

        return ''

    def get_created_at(self, instance):
        return instance.created_on.isoformat()

    def get_sender(self, instance):
        return instance.sender_profile.handle if instance.sender_profile else ''

    def get_receiver(self, instance):
        return instance.receiver_profile.handle if instance.receiver_profile else ''

    def get_comment(self, instance):
        return instance.anonymized_comment

class CustomAvatarExportSerializer(serializers.ModelSerializer):
    """Handle serializing the exported CustomAvatar object."""

    url = serializers.SerializerMethodField()
    png = serializers.SerializerMethodField()
    svg = serializers.SerializerMethodField()
    config = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = CustomAvatar
        fields = ('id', 'url', 'active', 'svg', 'png', 'hash', 'autogenerated',
                  'created_at', 'recommended_by_staff', 'style', 'config')

    def get_url(self, instance):
        return get_absolute_url(instance.avatar_url)

    def get_png(self, instance):
        return get_absolute_url(instance.png.url) if instance.png else ''

    def get_svg(self, instance):
        return get_absolute_url(instance.svg.url) if instance.svg else ''

    def get_created_at(self, instance):
        return instance.created_on.isoformat()

    def get_config(self, instance):
        return json.dumps(instance.config)


privacy_fields = {
  "tip": ["private_comments"],
  "feedback": []
}

exporters = {
  "tip": TipExportSerializer,
  "feedback": FeedbackExportSerializer
}

def get_absolute_url(url):
    if url and url[0] == '/':
        return settings.BASE_URL + url[1:]
    else:
        return url

def filter_items(model, data, private):
  if not (data and len(data) > 0):
      return []
  private_keys = privacy_fields[model]
  if private:
    private_keys.append("id")
    return [{k:item[k] for k in private_keys} for item in data]
  else:
    public_keys = list(set(data[0].keys()) - set(private_keys))
    return [{k:item[k] for k in public_keys} for item in data]

def filtered_list_data(model, items, private_items, private_fields):
  if private_items is not None:
    items = items.filter(private=private_items)
  exporter = exporters[model]
  data = exporter(items, many=True).data

  if private_items:
    return data
  else:
    if private_fields is None:
      return data
    elif private_fields:
      return filter_items(model, data, private=True)
    else:
      return filter_items(model, data, private=False)
