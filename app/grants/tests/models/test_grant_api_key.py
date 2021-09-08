import pytest
from dashboard.models import Profile
from grants.models.grant_api_key import GrantAPIKey

from .factories.grant_api_key_factory import GrantAPIKeyFactory


@pytest.mark.django_db
class TestGrantAPIKey:
    """Test GrantAPIKey model."""

    def test_creation(self):
        """Test GrantAPIKey returned by factory is valid."""

        grant_api_key = GrantAPIKeyFactory()

        assert isinstance(grant_api_key, GrantAPIKey)

    def test_grant_api_key_has_a_key(self):
        """Test key attribute is present and is blank."""

        grant_api_key = GrantAPIKeyFactory()

        assert hasattr(grant_api_key, 'key')
        assert grant_api_key.key == ''

    def test_grant_api_key_has_a_secret(self):
        """Test secret attribute is present and is blank."""

        grant_api_key = GrantAPIKeyFactory()

        assert hasattr(grant_api_key, 'secret')
        assert grant_api_key.secret == ''

    def test_grant_api_key_belongs_to_a_profile(self):
        """Test profile attribute is present."""

        grant_api_key = GrantAPIKeyFactory()

        assert hasattr(grant_api_key, 'profile')
        assert isinstance(grant_api_key.profile, Profile)
