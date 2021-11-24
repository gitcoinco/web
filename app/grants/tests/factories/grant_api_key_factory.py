import factory
from dashboard.tests.factories import ProfileFactory
from grants.models.grant_api_key import GrantAPIKey


class GrantAPIKeyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantAPIKey

    profile = factory.SubFactory(ProfileFactory)
