from dashboard.models import ProfileSerializer
from rest_flex_fields import FlexFieldsModelSerializer

from .models import GTCSteward


class GTCStewardSerializer(FlexFieldsModelSerializer):
    """Handle serializing of GTCSteward"""
    class Meta:
        """Define the GrantCLR serializer metadata."""
        model = GTCSteward
        fields = ('profile', 'real_name', 'bio', 'gtc_address', 'profile_link', 'custom_steward_img', 'steward_since', 'forum_posts_count', 'delegators_count', 'voting_power', 'voting_participation', 'score')
        expandable_fields = {
          'profile': ProfileSerializer
        }
