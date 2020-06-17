# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import PersonalToken, RedemptionToken, PurchasePToken


class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['id', 'created_on', '__str__']


admin.site.register(PersonalToken, GeneralAdmin)
admin.site.register(RedemptionToken, GeneralAdmin)
admin.site.register(PurchasePToken, GeneralAdmin)
