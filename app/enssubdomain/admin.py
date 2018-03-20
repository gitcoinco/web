# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from enssubdomain.models import ENSSubdomainRegistration


class ENSSubdomainAdmin(admin.ModelAdmin):

    ordering = ['-id']


admin.site.register(ENSSubdomainRegistration, ENSSubdomainAdmin)
