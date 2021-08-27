import factory
from grants.models.match_pledge import MatchPledge

from .profile_factory import ProfileFactory


class MatchPledgeFactory(factory.django.DjangoModelFactory):
    """Create mock MatchPledge for testing."""

    class Meta:
        model = MatchPledge

    profile = factory.SubFactory(ProfileFactory)
