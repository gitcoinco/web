from django.contrib import admin

from .models import JSONStore, StaticJsonEnv


class JSONStoreAdmin(admin.ModelAdmin):

    ordering = ['-id']
    search_fields = ['key', 'view']


class StaticJsonEnvAdmin(admin.ModelAdmin):

    ordering = ['-id']
    search_fields = ['key']


admin.site.register(JSONStore, JSONStoreAdmin)
admin.site.register(StaticJsonEnv, StaticJsonEnvAdmin)
