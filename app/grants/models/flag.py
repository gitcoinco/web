from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel


class Flag(SuperModel):

    grant = models.ForeignKey(
        'grants.Grant',
        related_name='flags',
        on_delete=models.CASCADE,
        null=False,
        help_text=_('The associated Grant.'),
    )
    profile = models.ForeignKey(
        'dashboard.Profile',
        related_name='grantflags',
        on_delete=models.SET_NULL,
        help_text=_("The flagger's profile."),
        null=True,
    )
    comments = models.TextField(default='', blank=True, help_text=_('The comments.'))
    processed = models.BooleanField(default=False, help_text=_('Was it processed?'))
    comments_admin = models.TextField(default='', blank=True, help_text=_('The comments of an admin.'))
    tweet = models.URLField(blank=True, help_text=_('The associated reference URL of the Grant.'))

    def post_flag(self):
        from dashboard.models import Activity, Profile
        from townsquare.models import Comment

        profile = Profile.objects.filter(handle='gitcoinbot').first()
        activity = Activity.objects.create(profile=profile, activity_type='flagged_grant', grant=self.grant)
        activity.populate_grant_activity_index()
        
        Comment.objects.create(
            profile=profile,
            activity=activity,
            comment=f"Comment from anonymous user: {self.comments}"
        )



    def __str__(self):
        """Return the string representation of a Grant."""
        return f"id: {self.pk}, processed: {self.processed}, comments: {self.comments} "
