from django.contrib import admin

from .models import Clients

class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['user']


# Register your models here.
admin.site.register(Clients, GeneralAdmin)
