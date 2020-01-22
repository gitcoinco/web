from datetime import datetime

import pytz
from rest_framework import serializers

from mentor.models import MentoringAvailable


class AvailabilitySerializer(serializers.ModelSerializer):
    available = serializers.SerializerMethodField()
    joined = serializers.DateTimeField(source='created_on')
    profile = serializers.SerializerMethodField()

    class Meta:
        model = MentoringAvailable
        fields = ('available', 'active_until', 'period_time', 'joined', 'profile')

    def get_profile(self, instance):
        mentor = instance.mentor
        return {
            'name': mentor.name,
            'id': mentor.id,
            'handle': mentor.handle,
            'avatar': mentor.avatar_url
        }

    def get_available(self, instance):
        return instance.is_active()
