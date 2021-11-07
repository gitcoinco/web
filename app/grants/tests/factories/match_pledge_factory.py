import json

import factory
from grants.models.match_pledge import MatchPledge

from .grant_clr_factory import GrantCLRFactory
from dashboard.tests.factories import ProfileFactory


class MatchPledgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MatchPledge

    profile = factory.SubFactory(ProfileFactory)
    data = factory.LazyFunction(lambda: json.dumps(dict()))
    clr_round_num = factory.SubFactory(GrantCLRFactory)
