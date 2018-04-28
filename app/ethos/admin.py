from django.contrib import admin

from ethos.models import Hop

# Register your models here.

class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']


admin.site.register(Hop, GeneralAdmin)
