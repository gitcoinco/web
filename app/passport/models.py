import uuid

from django.db import models

from economy.models import SuperModel


class PassportRequest(SuperModel):

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    nonce = models.IntegerField(default=0)
    address = models.CharField(max_length=255, default='', blank=True)
    network = models.CharField(max_length=255, default='', blank=True)
    uri = models.CharField(max_length=255, default='', blank=True)
    profile = models.ForeignKey(
        'dashboard.Profile', related_name='passport_requests', on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.profile.handle} => {self.created_on}"
