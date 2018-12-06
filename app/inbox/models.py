from django.db import models
from django.utils.translation import gettext_lazy as _
from economy.models import SuperModel

# Create your models here.

class Notification(SuperModel):
    created_on = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    to_user_id = models.IntegerField()
    from_user_id = models.IntegerField()
    username = models.CharField(max_length=255)
    CTA_URL = models.URLField(max_length=255, null=True)
    CTA_Text = models.CharField(max_length=255)
    message_html = models.CharField(max_length=255, null=True, help_text=_("Html message"))
    is_read = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=255)

    def __str__(self):
        return self.notification_type
