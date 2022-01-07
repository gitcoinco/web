import factory
from grants.models.hall_of_fame import GrantHallOfFame, GrantHallOfFameGrantee


class GrantHallOfFameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantHallOfFame

class GrantHallOfFameGranteeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GrantHallOfFameGrantee

    hall_of_fame = factory.SubFactory(GrantHallOfFameFactory)