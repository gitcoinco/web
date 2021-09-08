import pytest
from dashboard.models import Profile
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

    def test_grant_collection_has_associated_profile(self):
        """Test profile attribute is present."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'profile')
        assert isinstance(grant_collection.profile, Profile)

    def test_grant_collection_has_a_title(self):
        """Test title attribute is present."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'title')
        assert grant_collection.title == ''

    def test_grant_collection_has_a_description(self):
        """Test description attribute is present and defaults to empty string."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'description')
        assert grant_collection.description == ''

    def test_grant_collection_has_a_cover(self):
        """Test cover attribute is present."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'cover')
        assert grant_collection.cover == None

    def test_grant_collection_has_hidden_attribute(self):
        """Test hidden attribute is present and defaults to False."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'hidden')
        assert grant_collection.hidden == False

    def test_grant_collection_has_cache(self):
        """Test cache attibute is present and defaults to empty dictionary."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'cache')
        assert grant_collection.cache == {}

    

    
