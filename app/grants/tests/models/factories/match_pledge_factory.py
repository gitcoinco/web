import factory
from grants.models.match_pledge import MatchPledge


class MatchPledgeFactory(factory.django.DjangoModelFactory):
    """Create mock MatchPledge for testing."""

    class Meta:
        model = MatchPledge