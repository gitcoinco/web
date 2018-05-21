from rest_framework import serializers

from . import models


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Organization
        fields = (
            'slug',
            'name',
            'created_on',
            'modified_on',
            'description',
        )
