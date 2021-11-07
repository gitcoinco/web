import factory
from grants.models.grant import Grant


class GrantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Grant
