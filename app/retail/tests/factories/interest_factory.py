import factory
import pytest
from dashboard.models import Interest

from .profile_factory import ProfileFactory


@pytest.mark.django_db
class InterestFactory(factory.django.DjangoModelFactory):
    """Create instance of Interest for testing."""

    class Meta:
        model = Interest

    profile = factory.SubFactory(ProfileFactory)
