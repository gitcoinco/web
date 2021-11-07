import factory
from grants.models.grant_api_key import GrantAPIKey

from dashboard.tests.factories import ProfileFactory


class GrantAPIKeyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantAPIKey

    profile = factory.SubFactory(ProfileFactory)
