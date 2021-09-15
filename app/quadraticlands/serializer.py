from dashboard.serializers import ProfileSerializer
from rest_flex_fields import FlexFieldsModelSerializer

from .models import GTCSteward


class GTCStewardSerializer(FlexFieldsModelSerializer):
    """Handle serializing of GTCSteward"""
    class Meta:
        """Define the GrantCLR serializer metadata."""
        model = GTCSteward
        fields = ('profile', 'real_name', 'bio', 'gtc_address', 'profile_link', 'custom_steward_img')
        expandable_fields = {
          'profile': ProfileSerializer
        }
