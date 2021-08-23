import pytest
from grants.models.grant_type import GrantType

from .factories.grant_type_factory import GrantTypeFactory


@pytest.mark.django_db
class TestGrantType:
    """Test GrantType model."""

    def test_creation(self):
        """Test instance of GrantType returned by factory is valid."""

        grant_type = GrantTypeFactory()

        assert isinstance(grant_type, GrantType)

    def test_grant_type_has_a_name(self):
        """Test 'name' attribute."""

        grant_type = GrantTypeFactory()

        assert hasattr(grant_type, 'name')
        assert grant_type.name == ''


