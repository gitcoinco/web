from django.contrib import admin

from .models import Event_ETHDenver2019_Customizing_Kudos


class ETHDenver2019_CustomizingAdmin(admin.ModelAdmin):
    ordering = ['-id']
    raw_id_fields = ['kudos_required']


admin.site.register(Event_ETHDenver2019_Customizing_Kudos, ETHDenver2019_CustomizingAdmin)
