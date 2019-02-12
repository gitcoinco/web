from django.contrib import admin

from .models import JSONStore


class GeneralAdmin(admin.ModelAdmin):

    ordering = ['-id']
    search_fields = ['key']


admin.site.register(JSONStore, GeneralAdmin)
