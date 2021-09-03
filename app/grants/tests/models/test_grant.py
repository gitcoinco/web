import pytest
from grants.models.grant import Grant
from grants.models.grant_type import GrantType

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

    def test_grant_has_associated_grant_type(self):
        """Test association with GrantType."""

        grant = GrantFactory()

        assert hasattr(grant, 'grant_type')
        assert isinstance(grant.grant_type, GrantType)

    def test_grant_has_a_title(self):
        """Test title attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'title')
        assert grant.title == ''

    def test_grant_has_a_slug(self):
        """Test slug attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'slug')
    
    def test_grant_has_a_description(self):
        """Test description attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'description')
        assert grant.description == ''

    def test_grant_has_description_rich_attribute(self):
        """Test description_rich attribute and default."""

        grant = GrantFactory()

        assert hasattr(grant, 'description_rich')
        assert grant.description_rich == ''

    def test_grant_has_reference_url(self):
        """Test reference_url attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'reference_url')
        assert grant.reference_url == ''

    def test_grant_has_github_project_url(self):
        """Test github_project_url attribute."""

        grant = GrantFactory()

        assert hasattr(grant, 'github_project_url')
        assert grant.github_project_url == None

    def test_grant_has_is_clr_eligible_attribute(self):
        """Test is_clr_eligible attribute and default value."""

        grant = GrantFactory()

        assert hasattr(grant, 'is_clr_eligible')
        assert grant.is_clr_eligible == True

    

    