from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel
from rest_framework import serializers


class Mentor(SuperModel):

    TIME_RANGE = [
        ('1_5', '1 - 5'),
        ('5_10', '5 - 10'),
        ('10_15', '10 - 15'),
        ('15_20', '15 - 20'),
        ('20_', '20+'),
    ]

    profile = models.ForeignKey('dashboard.Profile', related_name='mentor', on_delete=models.CASCADE)
    org = models.CharField(max_length=255)
    about = models.TextField(blank=True)
    experience = models.CharField(max_length=5, choices=TIME_RANGE, blank=True)
    skills_offered = ArrayField(models.CharField(max_length=255), blank=True, default=[],
                                help_text=_("comma delimited"))
    skills_needed = ArrayField(models.CharField(max_length=255), blank=True, default=[], help_text=_("comma delimited"))
    available = models.BooleanField(default=False)
    commitment_per_week = models.CharField(max_length=5, choices=TIME_RANGE, blank=True)


class MentorSerializer(serializers.BaseSerializer):
    """Handle serializing the Mentor object."""

    class Meta:
        """Define the mentor serializer metadata."""

        model = Mentor
        field = ('id', 'name', 'email', 'org', 'about', 'experience',
                 'skills_offered', 'skills_needed', 'available', 'commitment_per_week')

    def to_representation(self, instance):
        """Provide the serialized representation of Mentor"""

        return {
            'id': instance.id,
            'name': instance.profile.name,
            'email': instance.profile.email,
            'org': instance.org,
            'skills_offered': instance.skills_offered
        }
