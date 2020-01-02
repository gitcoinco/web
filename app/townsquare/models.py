from django.db import models

from economy.models import SuperModel


class Like(SuperModel):
    """An A like is an indication of a favored activity feed"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.SET_NULL, related_name='likes', blank=True, null=True)
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.SET_NULL, related_name='likes', blank=True, null=True, db_index=True)

    def __str__(self):
        return f"Like of {self.activity.pk} by {self.profile.handle}"

class Comment(SuperModel):
    """An A like is an indication of a favored activity feed"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.SET_NULL, related_name='comments', blank=True, null=True)
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.SET_NULL, related_name='comments', blank=True, null=True, db_index=True)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        return f"Comment of {self.activity.pk} by {self.profile.handle}: {self.comment}"

    @property
    def profile_handle(self):
        return self.profile.handle
