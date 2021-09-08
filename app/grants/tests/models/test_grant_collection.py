import pytest
from grants.models.grant import Grant
from grants.models.grant_collection import GrantCollection

from .factories.grant_collection_factory import GrantCollectionFactory
from .factories.grant_factory import GrantFactory


@pytest.mark.django_db
class TestGrantCollection:
    """Test GrantCollection model."""

    def test_creation(self):
        """Test GrantCollection returned by factory is valid."""

        grant_collection = GrantCollectionFactory()

        assert isinstance(grant_collection, GrantCollection)

    def test_grant_collection_has_related_grants(self):
        """Test grants attribute is present and blank by default."""

        grants = (GrantFactory(), GrantFactory())
        grant_collection = GrantCollectionFactory(grants=(grants))

        assert hasattr(grant_collection, 'grants')
        assert isinstance(grant_collection.grants.first(), Grant)
        assert len(grant_collection.grants.all()) == len(grants)

    
