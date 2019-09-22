from django.db import models

# Create your models here.
from economy.models import SuperModel
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.text import slugify


class Quest(SuperModel):
    title = models.CharField(max_length=1000)
    description = models.TextField(default='', blank=True)
    game_schema = JSONField(default=dict, blank=True)
    game_metadata = JSONField(default=dict, blank=True)

    def __str__(self):
        """Return the string representation of this obj."""
        return f'tile: {self.title}'


    @property
    def url(self):
        return f"/quests/{self.pk}/{slugify(self.title)}"

    @property
    def background(self):
        backgrounds = [
            'camping',
            'back_city',
            'city',
            'night',
        ]
        which_back = self.pk % len(backgrounds)
        return backgrounds[which_back]


class QuestAttempt(SuperModel):

    quest = models.ForeignKey('quests.Quest', blank=True, null=True, related_name='attempts', on_delete=models.SET_NULL)
    success = models.BooleanField(default=False)
    profile = models.ForeignKey(
        'dashboard.Profile',
        on_delete=models.CASCADE,
        related_name='quest_attempts',
    )

