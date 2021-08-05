from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel
from grants.utils import get_upload_filename



class GrantBrandingRoutingPolicy(SuperModel):
    """
    This manages the background that would be put on a grant page (or grant CLR based on a regex matching in the URL)

    For a grant, there are several models and views that handle different kinds of grants, CLRs  and categories.
    This routing policy model sits in the middle and handles the banner and background image of specific sub-url group
    """
    policy_name = models.CharField(
        max_length=25,
        help_text=_("name to make it easier to identify"),
        blank=True,
        null=True
    )
    url_pattern = models.CharField(max_length=255, help_text=_("A regex url pattern"))
    banner_image = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('The banner image for a grant page'),
    )
    priority = models.PositiveSmallIntegerField(
        help_text=_("The priority ranking of this image 1-255. Higher priorities would be loaded first")
    )
    background_image = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('Background image'),
        blank=True,
        null=True
    )
    inline_css = models.TextField(default='', blank=True, help_text=_('Inline css to customize the banner fit'))

    def __str__(self):
        return f'{self.url_pattern} >> {self.priority}'