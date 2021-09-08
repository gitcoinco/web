import factory
from grants.models.grant_collection import GrantCollection

from .profile_factory import ProfileFactory


class GrantCollectionFactory(factory.django.DjangoModelFactory):
    """Create mock GrantCollection for testing."""

    class Meta:
        model = GrantCollection

    profile = factory.SubFactory(ProfileFactory)

    @factory.post_generation
    def grants(self, create, grants, **kwargs):
        if not create:
            return

        if grants:
            for grant in grants:
                self.grants.add(grant)
