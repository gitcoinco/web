from django.db import models

# Create your models here.
from economy.models import SuperModel
from django.contrib.postgres.fields import ArrayField, JSONField
from django_extensions.db.fields import AutoSlugField

class Game(SuperModel):

    invite_codes = JSONField(default=dict)
    gameboard = JSONField(default=dict)
    title = models.TextField(max_length=500, blank=True)
    slug = AutoSlugField(populate_from='title')
    admin_profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grant_admin',
        on_delete=models.CASCADE,
        help_text=_('The game administrator\'s profile.'),
        null=True,
    )


class GameFeed(SuperModel):

    game = models.ForeignKey(
        'diplomacy.Game',
        related_name='feed',
        null=True,
        on_delete=models.CASCADE,
        help_text=_('Link to Game')
    )
    sender = models.ForeignKey(
        'dashboard.Profile',
        related_name='game_feed',
        on_delete=models.CASCADE,
        help_text=_('The game feed update creators\'s profile.'),
        null=True,
    )
    data = JSONField(default=dict)
    message = models.TextField(max_length=5000, blank=True)
