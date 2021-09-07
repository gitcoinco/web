import factory
from grants.models.grant import Grant

from .grant_type_factory import GrantTypeFactory


class GrantFactory(factory.django.DjangoModelFactory):
    """Create mock Grant for testing."""

    class Meta:
        model = Grant

    grant_type = factory.SubFactory(GrantTypeFactory)

    @factory.post_generation
    def team_members(self, create, team_members, **kwargs):
        if not create:
            return

        if team_members:
            for team_member in team_members:
                self.team_members.add(team_member)

    @factory.post_generation
    def categories(self, create, grant_categories, **kwargs):
        if not create:
            return

        if grant_categories:
            for grant_category in grant_categories:
                self.categories.add(grant_category)
