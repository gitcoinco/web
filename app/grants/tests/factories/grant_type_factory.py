import factory
from grants.models.grant_type import GrantType


class GrantTypeFactory(factory.django.DjangoModelFactory):
    """Create mock GrantType for testing."""

    class Meta:
        model = GrantType

    @factory.post_generation
    def categories(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for category in extracted:
                self.categories.add(category)

