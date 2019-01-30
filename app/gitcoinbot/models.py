# -*- coding: utf-8 -*-
"""Define Gitcoin Bot specific models."""
from django.db import models

from economy.models import SuperModel


class GitcoinBotResponses(SuperModel):
    """Define the Gitcoin Bot response model for recording bot request data."""
    request = models.CharField(max_length=500, db_index=True, unique=True)
    response = models.CharField(max_length=500)
