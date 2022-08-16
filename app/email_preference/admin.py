from django.contrib import admin

from .models import EmailPreferenceLog


class EmailPreferenceLogAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', 'event_data', 'response_data',
                    'processed_at']
    search_fields = ['created_on', 'event_data', 'response_data',
                     'processed_at']


admin.site.register(EmailPreferenceLog, EmailPreferenceLogAdmin)
