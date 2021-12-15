import factory
import pytest
from grants.models.grant_type import GrantType


@pytest.mark.django_db
class GrantTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantType

    name = factory.Sequence(lambda n: f"gr{n}")
    label = "gr12"
