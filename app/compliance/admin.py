from django.contrib import admin

from .models import Country, Entity


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']

admin.site.register(Country, GeneralAdmin)
admin.site.register(Entity, GeneralAdmin)
