import pytest
from dashboard.models import Profile
from grants.models.grant_api_key import GrantAPIKey

from .factories.grant_api_key_factory import GrantAPIKeyFactory


@pytest.mark.django_db
class TestGrantAPIKey:
    """Test GrantAPIKey attributes."""

    def test_creation(self):
        grant_api_key = GrantAPIKeyFactory()

        assert isinstance(grant_api_key, GrantAPIKey)

    def test_grant_api_key_has_a_key_attribute(self):
       grant_api_key = GrantAPIKeyFactory()

       assert hasattr(grant_api_key, "key")
       assert grant_api_key.key == ''

    def test_grant_api_key_has_a_secret_attribute(this):
       grant_api_key = GrantAPIKeyFactory()

       assert hasattr(grant_api_key, "secret")
       assert grant_api_key.secret == ''