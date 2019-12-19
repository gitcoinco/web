from rest_framework import serializers
from .models import (Activity, Bounty)
from grants.models import (Grant)

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
            'github_url': instance.github_url,
            'avatar_url': instance.avatar_url,
            'profile_wallpaper': instance.profile_wallpaper,
            'keywords': instance.keywords,
            'portfolio_keywords': d['portfolio_keywords'],
            'url': instance.get_relative_url(),
            'position': instance.get_contributor_leaderboard_index(),
            'organizations': instance.get_who_works_with(network=None),
            '_email': instance.email,
            '_gitcoin_discord_username': instance.gitcoin_discord_username,
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
            'total_earned': instance.get_eth_sum(network=None),
            'earnings_count': d['earnings_count'],
            'avg_rating': d['avg_rating']['overall'],
            'longest_streak': instance.longest_streak,
            'activity_level': instance.activity_level,
            'avg_hourly_rate': instance.avg_hourly_rate,
            'success_rate': instance.success_rate,
            'reliability': instance.reliability,
            'rank_funder': instance.rank_funder,
            'rank_org': instance.rank_org,
            'rank_coder': instance.rank_coder
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
                  'admin_address', 'contract_owner_address', 'amount_goal',
                  'monthly_amount_subscribed', 'amount_received', 'token_address',
                  'token_symbol', 'contract_address', 'network',
                  'org', 'created_at', 'url', ''
                  )

    def get_created_at(self, instance):
        return instance.created_on.isoformat()

    def get_org(self, instance):
        return instance.org_name()

    def get_url(self, instance):
        return instance.get_absolute_url()

    def get_contributor_count(self, instance):
        return instance.get_contributor_count()

    def get_contribution_count(self, instance):
        return instance.get_contribution_count()


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
        action = self.get_action(instance)
        if action in ('bounty', ):
            return instance.bounty.get_absolute_url()

        if action in ('kudos', ):
            return instance.kudos.kudos_token.get_absolute_url()

        if action in ('profile', ):
            return instance.profile.absolute_url

        return ''

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
