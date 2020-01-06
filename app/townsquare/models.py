from django.db import models
from django.utils import timezone
from economy.models import SuperModel
from django.utils.text import slugify


class Like(SuperModel):
    """A like is an indication of a favored activity feed item"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='likes', blank=True)
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.CASCADE, related_name='likes', blank=True, db_index=True)

    def __str__(self):
        return f"Like of {self.activity.pk} by {self.profile.handle}"

class Comment(SuperModel):
    """An comment on an activity feed item"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='comments', blank=True)
    activity = models.ForeignKey('dashboard.Activity',
        on_delete=models.CASCADE, related_name='comments', blank=True, db_index=True)
    comment = models.TextField(default='', blank=True)

    def __str__(self):
        return f"Comment of {self.activity.pk} by {self.profile.handle}: {self.comment}"

    @property
    def profile_handle(self):
        return self.profile.handle


class OfferQuerySet(models.QuerySet):
    """Handle the manager queryset for Offers."""

    def current(self):
        """Filter results down to current offers only."""
        return self.filter(valid_from__lte=timezone.now(), valid_to__gt=timezone.now())


class Offer(SuperModel):
    """An offer"""
    OFFER_TYPES = [
        ('daily', 'daily'),
        ('weekly', 'weekly'),
        ('monthly', 'monthly'),
        ('other', 'other'),
    ]

    offer_header = models.TextField(default='', blank=True)
    offer_text = models.TextField(default='', blank=True)
    url = models.URLField(db_index=True)
    valid_from = models.DateTimeField(db_index=True)
    valid_to = models.DateTimeField(db_index=True)
    key = models.CharField(max_length=50, db_index=True, choices=OFFER_TYPES)

    # Bounty QuerySet Manager
    objects = OfferQuerySet.as_manager()

    def __str__(self):
        return f"{self.offer_header}"

    @property
    def go_url(self):
        slug = slugify(self.offer_header)
        return f'/offer/{self.pk}/{slug}'


class OfferAction(SuperModel):
    """An offer action, where a click or a completion"""

    profile = models.ForeignKey('dashboard.Profile',
        on_delete=models.CASCADE, related_name='offeractions', blank=True)
    offer = models.ForeignKey('townsquare.Offer',
        on_delete=models.CASCADE, related_name='actions', blank=True)
    what = models.CharField(max_length=50, db_index=True) # click, completion, etc

    def __str__(self):
        return f"{self.profile.handle} => {self.offer.offer_header}"


