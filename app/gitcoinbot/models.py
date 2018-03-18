from django.db import models


class GitcoinBotResponses(models.Model):
    request = models.CharField(max_length=500, db_index=True, unique=True)
    response = models.CharField(max_length=500)
