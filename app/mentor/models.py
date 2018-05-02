from django.utils.translation import gettext_lazy as _

from dashboard.models import Profile
from rest_framework import serializers
from rest_framework.fields import CharField


class StringArrayField(CharField):
    """
    String representation of an array field.
    """
    def to_representation(self, obj):
        return ", ".join(obj)

    def to_internal_value(self, data):
        return [x.strip() for x in data.split(',')]


class MentorSerializer(serializers.ModelSerializer):
    """Handle serializing the Mentor object."""

    class Meta:
        """Define the mentor serializer metadata."""

        model = Profile
        fields = ('id', 'name', 'email', 'org', 'about', 'experience',
                  'skills_offered', 'skills_needed', 'commitment_per_week', 'available')
    # TODO: take directly from model
    TIME_RANGE = [
        ('1_5', '1 - 5'),
        ('5_10', '5 - 10'),
        ('10_15', '10 - 15'),
        ('15_20', '15 - 20'),
        ('20_', '20+'),
    ]

    email = serializers.CharField(
        style={'template': 'email-input.html'},
        label=_("Email")
    )

    org = serializers.CharField(
        style={'template': 'text-input.html'},
        label=_("Org")
    )

    about = serializers.CharField(
        style={'template': 'text-area-input.html'},
        label=_("About")
    )

    experience = serializers.ChoiceField(
        style={'template': 'select-input.html'},
        choices=TIME_RANGE,
        label=_("Experience")
    )

    skills_offered = StringArrayField(
        style={'template': 'text-area-input.html'},
        label=_("Skills offered")
    )

    skills_needed = StringArrayField(
        style={'template': 'text-area-input.html'},
        label=_("Skills needed")
    )

    commitment_per_week = serializers.ChoiceField(
        style={'template': 'select-input.html'},
        choices=TIME_RANGE,
        label=_("Commitment per week")
    )

    available = serializers.BooleanField(
        style={'template': 'checkbox-input.html'},
        label=_("Are you available to mentor now?")
    )
