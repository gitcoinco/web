from django.contrib import admin

# Register your models here.
from .models import Quest, QuestAttempt


class QuestAdmin(admin.ModelAdmin):
    raw_id_fields = ['kudos_reward', 'unlocked_by']
    ordering = ['-id']
    list_display = ['created_on', '__str__']

class QuestAttemptAdmin(admin.ModelAdmin):
    raw_id_fields = ['quest', 'profile']
    ordering = ['-id']
    list_display = ['created_on', '__str__']

admin.site.register(Quest, QuestAdmin)
admin.site.register(QuestAttempt, QuestAttemptAdmin)
