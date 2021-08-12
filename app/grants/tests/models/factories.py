import factory
from grants.models import *


class GrantTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantType

    name = "TestGrantType"
    label = "TestLabel"
    is_active = True
    is_visible = True
