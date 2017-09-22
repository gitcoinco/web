# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import ConversionRate

# Register your models here.
class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']


admin.site.register(ConversionRate, GeneralAdmin)
