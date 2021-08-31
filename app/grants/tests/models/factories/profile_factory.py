import factory
from dashboard.models import Profile


class ProfileFactory(factory.django.DjangoModelFactory):
    """Create mock Profile for testing."""

    class Meta:
        model = Profile

    handle = factory.Sequence(lambda n: "Contributor_%03d" % n)
    data = {} 