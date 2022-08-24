from django.db import models
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel
from grants.utils import get_upload_filename


class GrantHallOfFame(SuperModel):
    """
    This contains the data relevant for the hall of fame page of the grants program.
    """
    total_donations = models.CharField(max_length=25, help_text=_("The total donations"), blank=False, null=False)

    top_matching_partners = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('The image with the top matching partners (recommended size 1114x390)'),
    )

    top_matching_partners_mobile = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('The image with the top matching partners for mobile (recommended size 290x437).'),
        null=True
    )

    top_individual_donors = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('The image with the top individual donors (recommended size 1114x346)'),
    )

    top_individual_donors_mobile = models.ImageField(
        upload_to=get_upload_filename,
        help_text=_('The image with the top individual donors for mobile (recommended size 290x480)'),
        null=True
    )

    graduated_grantees_description = models.TextField(
        help_text=_('Short description for graduated grantees'), blank=True,
    )

    share_your_story_email = models.CharField(
        max_length=100, help_text=_("The email where users can share their stories"), blank=False, null=False
    )

    is_published = models.BooleanField(
        help_text=_('True if this page is published. Only 1 object can be set to true at a given time.'),
        default=False,
    )

    def __str__(self):
        return f'#{self.pk} Hall of fame, total donation: {self.total_donations}'

    def get_grantees_data(self):
        for g in self.grantees.all().prefetch_related('grantee').order_by('pk'):
            yield {
                'name': g.name,
                'funded_by': g.funded_by,
                'amount': g.amount,
                'description': g.description,
                'accomplishment_1': g.accomplishment_1,
                'accomplishment_2': g.accomplishment_2,
                'grantee_handle': g.grantee.handle,
            }

    def publish(self):
        GrantHallOfFame.objects.filter(is_published=True).update(is_published=False)
        self.is_published = True
        self.save()


class GrantHallOfFameGrantee(SuperModel):
    """
    This contains information about one grantee listed in the hall of fame page
    """
    hall_of_fame = models.ForeignKey('GrantHallOfFame', on_delete=models.CASCADE, related_name='grantees')

    grantee = models.ForeignKey(
        'dashboard.Profile', null=True, blank=True, on_delete=models.SET_NULL, help_text=_('Sets the grantee profile')
    )

    name = models.CharField(max_length=100, help_text=_("Name"), blank=False, null=False)

    funded_by = models.CharField(max_length=100, help_text=_("Funded by ..."), blank=False, null=False)

    amount = models.CharField(max_length=20, help_text=_("The amount that has been rased"), blank=False, null=False)

    description = models.TextField(help_text=_("Project description"), blank=False, null=False)

    accomplishment_1 = models.TextField(help_text=_("Accomplishment 1"), blank=True, null=False)

    accomplishment_2 = models.TextField(help_text=_("Accomplishment 2"), blank=True, null=False)

    def __str__(self):
        return f'Grantee "{self.grantee}" ({self.name})'
