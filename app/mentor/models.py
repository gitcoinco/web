from django.utils.translation import gettext_lazy as _

from dashboard.models import Profile
from rest_framework import serializers
from rest_framework.fields import ListField


class TagSerializerField(ListField):

    child = serializers.CharField()

    def to_representation(self, data):
        return ", ".join(data.values_list('name', flat=True))


class MentorSerializer(serializers.ModelSerializer):
    """Handle serializing the Mentor object."""

    class Meta:
        """Define the mentor serializer metadata."""

        model = Profile
        fields = ('id', 'name', 'email', 'org', 'about', 'experience',
                  'skills_offered', 'skills_offered', 'skills_needed', 'commitment_per_week', 'available',
                  'skills_offered_list', 'skills_needed_list')

    email = serializers.CharField(
        style={'template': 'email-input.html'},
        label=_("Email")
    )

    org = serializers.CharField(
        style={'template': 'text-input.html'},
        label=_("Org"),
        max_length=255
    )

    about = serializers.CharField(
        style={'template': 'text-area-input.html'},
        label=_("About"),
        required=True
    )

    experience = serializers.ChoiceField(
        style={'template': 'select-input.html'},
        choices=Profile.TIME_RANGE,
        label=_("Experience")
    )

    commitment_per_week = serializers.ChoiceField(
        style={'template': 'select-input.html'},
        choices=Profile.TIME_RANGE,
        label=_("Commitment per week")
    )

    available = serializers.BooleanField(
        style={'template': 'checkbox-input.html'},
        label=_("Are you available to mentor now?")
    )

    skills_needed = TagSerializerField(
        style={'template': 'text-area-input.html'},
        label=_("Skills needed (comma separated list)"),
        required=True
    )

    skills_offered = TagSerializerField(
        style={'template': 'text-area-input.html'},
        label=_("Skills offered (comma separated list)"),
        required=True
    )

    skills_offered_list = serializers.SerializerMethodField()
    skills_needed_list = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        instance.email = validated_data.pop("email")
        instance.org = validated_data.pop("org")
        instance.about = validated_data.pop("about")
        instance.experience = validated_data.pop("experience")
        skills_needed = [x.strip() for x in validated_data.pop('skills_needed')[0].split(",")]
        instance.skills_needed.set(*skills_needed)
        skills_offered = [x.strip() for x in validated_data.pop('skills_offered')[0].split(",")]
        instance.skills_offered.set(*skills_offered)
        instance.commitment_per_week = validated_data.pop("commitment_per_week")
        instance.available = validated_data.pop("available")
        instance.save()
        return instance

    def get_skills_offered_list(self, obj):
        return obj.skills_offered.values_list('name', flat=True)

    def get_skills_needed_list(self, obj):
        return obj.skills_needed.values_list('name', flat=True)
