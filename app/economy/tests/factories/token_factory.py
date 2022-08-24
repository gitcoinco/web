import factory
import pytest
from economy.models import Token


@pytest.mark.django_db
class TokenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Token
