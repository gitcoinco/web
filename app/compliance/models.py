from django.db import models

from economy.models import SuperModel


class Entity(SuperModel):
    firstName = models.CharField(max_length=500)
    lastName = models.CharField(max_length=500)
    fullName = models.CharField(max_length=500)
    sdnType = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    country = models.CharField(max_length=500)
    program = models.CharField(max_length=500)
    stateOrProvince = models.CharField(max_length=500)
    uid = models.CharField(max_length=25)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.fullName}'


class Country(SuperModel):
    name = models.CharField(max_length=500)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'{self.name}'
