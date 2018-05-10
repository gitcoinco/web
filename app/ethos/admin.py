from django.contrib import admin

from ethos.models import Hop


class HopAdmin(admin.ModelAdmin):
    """Define the Hop administration layout."""

    ordering = ['-id']


admin.site.register(Hop, HopAdmin)
