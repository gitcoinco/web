import factory
from grants.models.grant_collection import GrantCollection

from dashboard.tests.factories import ProfileFactory


class GrantCollectionFactory(factory.django.DjangoModelFactory):
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

    @factory.post_generation
    def curators(self, create, curators, **kwargs):
        if not create:
            return

        if curators:
            for curator in curators:
                self.curators.add(curator)
