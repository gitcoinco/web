import pytest
from grants.models.grant import Grant

from .factories.grant_factory import GrantFactory


@pytest.mark.django_db
class TestGrant:
    """Test Grant model."""

    def test_creation(self):
        """Test instance of Grant returned by factory is valid."""

        grant = GrantFactory()

        assert isinstance(grant, Grant)

    def test_grant_has_vector_column(self):
        """Test vector_column attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'vector_column')
        assert grant.vector_column == None

    def test_grant_has_active_attribute(self):
        """Test active attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'active')
        assert grant.active == True

