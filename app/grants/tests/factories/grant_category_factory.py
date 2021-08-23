import factory
from grants.models.grant_category import GrantCategory


class GrantCategoryFactory(factory.django.DjangoModelFactory):
    """Create mock GrantCategory for testing."""

    class Meta:
        model = GrantCategory

    category = factory.Sequence(lambda n: "Category #%s" % n)
