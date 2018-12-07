from django.db import models
from django.utils.translation import gettext_lazy as _
from economy.models import SuperModel
from django.contrib.auth import get_user_model

class Notification(SuperModel):
    created_on = models.DateTimeField(auto_now_add=True, editable=False)
    CTA_URL = models.URLField(max_length=255, null=True)
    CTA_Text = models.CharField(max_length=255)
    message_html = models.CharField(max_length=255, null=True, help_text=_("Html message"))
    is_read = models.BooleanField(default=False)
    to_user_id = models.ForeignKey(
            get_user_model(),
            on_delete=models.CASCADE,
            related_name='to_user'
        )
    from_user_id = models.ForeignKey(
            get_user_model(),
            on_delete=models.CASCADE,
            related_name='from_user'
        )

    def __str__(self):
        return str(self.id)
