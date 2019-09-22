from django.contrib import admin

# Register your models here.
from .models import Quest, QuestAttempt

class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']

class QuestAttemptAdmin(admin.ModelAdmin):
    raw_id_fields = ['quest', 'profile']
    ordering = ['-id']
    list_display = ['created_on', '__str__']

admin.site.register(Quest, GeneralAdmin)
admin.site.register(QuestAttempt, QuestAttemptAdmin)