from django.contrib import admin

from ethos.models import Hop, ShortCode


class GeneralAdmin(admin.ModelAdmin):
    """Define the GeneralAdmin administration layout."""

    ordering = ['-id']


admin.site.register(Hop, GeneralAdmin)
admin.site.register(ShortCode, GeneralAdmin)
