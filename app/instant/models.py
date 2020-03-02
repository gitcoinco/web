from django.db import models
from economy.models import SuperModel
from django.contrib.auth.models import User

# Create your models here.


class Clients(SuperModel):
    """Records webchanenl clients."""

    channel_name = models.CharField(max_length=255, db_index=True)
    user = models.ForeignKey(User, related_name='clients', on_delete=models.SET_NULL, null=True, db_index=True)

    def __str__(self):
        return f"{self.user} {self.created_on}"