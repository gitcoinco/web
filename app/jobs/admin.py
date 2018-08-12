from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    """Define the Jobs administration layout."""
    list_display = ['id', 'title', 'skills', 'is_active']
