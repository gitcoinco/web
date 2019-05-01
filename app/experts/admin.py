from django.contrib import admin

from .models import ExpertSession, ExpertSessionInterest

admin.site.register([
    ExpertSession,
    ExpertSessionInterest
], admin.ModelAdmin)
