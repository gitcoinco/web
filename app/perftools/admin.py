from django.contrib import admin

from .models import JSONStore


class GeneralAdmin(admin.ModelAdmin):

    ordering = ['-id']


admin.site.register(JSONStore, GeneralAdmin)
