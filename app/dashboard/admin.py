# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Bounty, Subscription, BountySyncRequest

# Register your models here.
class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']

admin.site.register(Subscription, GeneralAdmin)
admin.site.register(Bounty, GeneralAdmin)
admin.site.register(BountySyncRequest, GeneralAdmin)
