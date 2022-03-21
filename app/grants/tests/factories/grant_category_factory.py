import factory
from grants.models.grant_category import GrantCategory


class GrantCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantCategory
