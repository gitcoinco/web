import pytest
from grants.models.grant_collection import GrantCollection

from .factories.grant_collection_factory import GrantCollectionFactory


@pytest.mark.django_db
class TestGrantCollection:
    """Test GrantCollection model."""

    def test_creation(self):
        """Test GrantCollection returned by factory is valid."""

        grant_collection = GrantCollectionFactory()

        assert isinstance(grant_collection, GrantCollection)
