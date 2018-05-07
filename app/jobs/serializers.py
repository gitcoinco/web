
# Third Party Stuff
from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = (
            'title', 'description', 'github_profile_link', 'apply_url',
            'is_active', 'skills', 'expiry_date', 'location',
            'job_type'
        )
