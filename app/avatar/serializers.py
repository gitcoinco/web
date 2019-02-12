from rest_framework import serializers

from .models import BaseAvatar, CustomAvatar


class BaseAvatarSerializer(serializers.ModelSerializer):
    """Handle serializing the BaseAvatar object."""

    class Meta:
        """Define the milestone serializer metadata."""

        model = BaseAvatar
        fields = ('pk', 'avatar_url', 'active', 'hash')


class CustomAvatarSerializer(serializers.ModelSerializer):
    """Handle serializing the CustomAvatar object."""

    class Meta:
        """Define the milestone serializer metadata."""

        model = CustomAvatar
        fields = ('pk', 'avatar_url', 'active', 'hash')
