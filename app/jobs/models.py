from datetime import timedelta

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

# Create your models here.

JOB_TYPE_CHOICES = (
    ('Full Time', 'Full-Time'),
    ('Part Time', 'Part-Time'),
    ('Contract', 'Contract'),
)


def get_expiry_time():
    return timezone.now() + timedelta(days=30)


class Job(models.Model):
    title = models.CharField(
        verbose_name=_('Title'), max_length=200, null=False, blank=False
    )
    description = models.TextField(verbose_name=_('Description'))
    github_profile_link = models.URLField(
        verbose_name=_('Github Profile Link'), null=False, blank=True
    )
    location = models.CharField(
        _('Location'), max_length=50, null=False, blank=True
    )
    job_type = models.CharField(
        _('Job Type'), max_length=50, choices=JOB_TYPE_CHOICES, null=False,
        blank=False
    )
    apply_url = models.URLField(null=False, blank=True)
    is_active = models.BooleanField(
        verbose_name=_('Is this job active?'), default=False,
        null=False, blank=True
    )
    skills = models.CharField(
        verbose_name=_('skill'), max_length=60, null=False, blank=True
    )
    expiry_date = models.DateTimeField(
        _('Expiry Date'), null=False, blank=False, default=get_expiry_time
    )
    company = models.CharField(_('Company'), max_length=50, null=True, blank=True)
    apply_email = models.EmailField(_('Contact Email for Job'), null=True, blank=True)
    posted_by_gitcoin_username = models.CharField(
        _('Username of person who posted Job'), max_length=50, null=True, blank=True
    )

    @property
    def posted_by_user_profile_url(self):
        if self.posted_by_gitcoin_username:
            return reverse('profile', args=[self.posted_by_gitcoin_username])
        return None

    def get_absolute_url(self):
        """Get the absolute URL for the Job.

        Returns:
            str: The absolute URL for the Job.

        """
        return settings.BASE_URL + self.get_relative_url(preceding_slash=False)

    def get_relative_url(self, preceding_slash=True):
        """Get the relative URL for the Job.

        Attributes:
            preceding_slash (bool): Whether or not to include a preceding slash.

        Returns:
            str: The relative URL for the Job.

        """
        job_id = self.id
        return f"{'/' if preceding_slash else ''}jobs/{job_id}/"

    @property
    def url(self):
        return self.get_absolute_url()

    class Meta:
        db_table = 'job'
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
