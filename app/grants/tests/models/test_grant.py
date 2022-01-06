import pytest
from grants.models.grant import Grant
from grants.models.grant_type import GrantType
from grants.tests.factories import GrantFactory


@pytest.mark.django_db
class TestGrant:
    """Test Grant model."""

    def test_creation(self):
        """Test instance of Grant returned by factory is valid."""

        grant = GrantFactory()

        assert isinstance(grant, Grant)

    def test_grant_has_vector_column(self):
        grant = GrantFactory()

        assert hasattr(grant, 'vector_column')

    def test_grant_has_active_attribute(self):
        grant = GrantFactory()

        assert hasattr(grant, 'active')
        assert grant.active == True

    def test_grant_has_associated_grant_type(self):
        grant = GrantFactory()

        assert hasattr(grant, 'grant_type')
        assert isinstance(grant.grant_type, GrantType)

    def test_grant_has_a_title(self):
        grant = GrantFactory()

        assert hasattr(grant, 'title')