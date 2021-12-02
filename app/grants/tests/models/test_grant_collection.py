import pytest
from dashboard.models import Profile
from dashboard.tests.factories import ProfileFactory
from grants.models.grant import Grant
from grants.models.grant_collection import GrantCollection
from grants.tests.factories import GrantCollectionFactory, GrantFactory


@pytest.mark.django_db
class TestGrantCollection:
    """Test GrantCollection model."""

    def test_creation(self):
        """Test GrantCollection returned by factory is valid."""

        grant_collection = GrantCollectionFactory()

        assert isinstance(grant_collection, GrantCollection)

    def test_grant_collection_has_related_grants(self):
        """Test 'grants' attribute is present and can have many Grants."""

        grants = (GrantFactory(), GrantFactory())
        grant_collection = GrantCollectionFactory(grants=(grants))

        assert hasattr(grant_collection, 'grants')
        assert isinstance(grant_collection.grants.first(), Grant)
        assert len(grant_collection.grants.all()) == len(grants)

    def test_grant_collection_has_associated_profile(self):
        """Test profile attribute is present and is an instance of Profile."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'profile')
        assert isinstance(grant_collection.profile, Profile)

    def test_grant_collection_has_a_title(self):
        """Test title attribute is present."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'title')

    def test_grant_collection_has_a_description(self):
        """Test description attribute is present and defaults to empty string."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'description')
        assert grant_collection.description == ''

    def test_grant_collection_has_a_cover(self):
        """Test cover attribute is present."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'cover')

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
        assert len(grant_collection.cache) == 0

    def test_grant_collection_has_featured_attribute(self):
        """Test featured attribute is present and defaults to False."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'featured')
        assert grant_collection.featured == False

    def test_grant_collection_has_shuffle_rank(self):
        """Test shuffle_rank attribute is present and defaults to 1."""

        grant_collection = GrantCollectionFactory()

        assert hasattr(grant_collection, 'shuffle_rank')
        assert grant_collection.shuffle_rank == 1

    def test_grant_collection_has_associated_curators(self):
        """Test curators are present and GrantCollection can have many."""

        curators = (ProfileFactory(), ProfileFactory())
        grant_collection = GrantCollectionFactory(curators=(curators))

        assert hasattr(grant_collection, 'curators')
        assert isinstance(grant_collection.curators.first(), Profile)
        assert len(grant_collection.curators.all()) == len(curators)
