import factory
from grants.models.grant import Grant

from .grant_type_factory import GrantTypeFactory


class GrantFactory(factory.django.DjangoModelFactory):
    """Create mock Grant for testing."""

    class Meta:
        model = Grant

    grant_type = factory.SubFactory(GrantTypeFactory)

    @factory.post_generation
    def team_members(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for team_member in extracted:
                self.team_members.add(team_member)