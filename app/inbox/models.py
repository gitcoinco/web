from django.db import models
from economy.models import SuperModel
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


class Notification(SuperModel):
    """Model for each notification."""
    cta_url = models.URLField(max_length=255, blank=True)
    cta_text = models.CharField(max_length=255)
    message_html = models.CharField(max_length=255, blank=True, help_text=_("Html message"))
    is_read = models.BooleanField(default=False)
    to_user = models.ForeignKey(
            get_user_model(),
            on_delete=models.CASCADE,
            related_name='received_notifications'
        )
    from_user = models.ForeignKey(
            get_user_model(),
            on_delete=models.CASCADE,
            related_name='sent_notifications'
        )

    def __str__(self):
        return str(self.id)
