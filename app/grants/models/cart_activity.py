from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import gettext_lazy as _

from economy.models import SuperModel

from .grant import Grant


class CartActivity(SuperModel):
    ACTIONS = (
        ('ADD_ITEM', 'Add item to cart'),
        ('REMOVE_ITEM', 'Remove item to cart'),
        ('CLEAR_CART', 'Clear cart')
    )
    grant = models.ForeignKey(Grant, null=True, on_delete=models.CASCADE, related_name='cart_actions',
                              help_text=_('Related Grant Activity '))
    profile = models.ForeignKey('dashboard.Profile', on_delete=models.CASCADE, related_name='cart_activity',
                                help_text=_('User Cart Activity'))
    action = models.CharField(max_length=20, choices=ACTIONS, help_text=_('Type of activity'))
    metadata = JSONField(default=dict, blank=True, help_text=_('Related data to the action'))
    bulk = models.BooleanField(default=False)
    latest = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.action} {self.grant.id if self.grant else "bulk"} from the cart {self.profile.handle}'