from django.contrib import admin
from django.utils.safestring import mark_safe

# Register your models here.
from .models import Quest, QuestAttempt, QuestFeedback, QuestPointAward


class QuestAdmin(admin.ModelAdmin):
    raw_id_fields = ['kudos_reward', 'unlocked_by_quest', 'unlocked_by_hackathon', 'creator', 'reward_tip']
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    readonly_fields = ['feedback', 'background_preview']

    def response_change(self, request, obj):
        from django.shortcuts import redirect
        if "_approve_quest" in request.POST:
            if obj.visible:
                self.message_user(request, f"Quest was already approved.")
            else:
                from quests.helpers import record_quest_activity, record_award_helper
                from quests.models import QuestAttempt
                from marketing.mails import new_quest_approved
                from django.conf import settings

                if obj.kudos_reward.owner_address.lower() != settings.KUDOS_OWNER_ACCOUNT.lower():
                    self.message_user(request, f"Cannot approve quest. The owner address is not the Gitcoin Airdropper")
                    return super().response_change(request, obj)
                if obj.is_dead_end:
                    self.message_user(request, f"Cannot approve quest. The quest has a dead end question in it!")
                    return super().response_change(request, obj)
                quest = obj
                obj.value = 1
                qa = QuestAttempt.objects.create(
                    quest=obj,
                    success=True,
                    profile=quest.creator,
                    )
                record_award_helper(qa, quest.creator, 1, 'Created', 3)
                record_quest_activity(quest, quest.creator, "created_quest")
                obj.visible = True
                obj.save()
                new_quest_approved(obj)
                self.message_user(request, f"Quest Approved + Points awarded + Made Live.")
        return redirect(obj.admin_url)

    def feedback(self, instance):
        fb = instance.feedbacks
        html = f"""
<pre>
ratio: {fb['ratio']}

stats: {fb['stats']}

feedback: {fb['feedback']}

</pre>
        """
        return mark_safe(html)

    def background_preview(self, instance):
        html = ''
        for ext in ['jpeg']:
            url = f'/static/v2/images/quests/backs/{instance.background}.{ext}'
            html += f"<img style='max-width: 400px;' src='{url}'>"
        return mark_safe(html)


class QuestAttemptAdmin(admin.ModelAdmin):
    raw_id_fields = ['quest', 'profile']
    ordering = ['-id']
    list_display = ['created_on', '__str__']


class QuestFeedbackAdmin(admin.ModelAdmin):
    raw_id_fields = ['quest', 'profile']
    ordering = ['-id']
    list_display = ['created_on', '__str__']


class QuestPointAwardAdmin(admin.ModelAdmin):
    raw_id_fields = ['questattempt', 'profile']
    ordering = ['-id']
    list_display = ['created_on', '__str__']

admin.site.register(QuestFeedback, QuestFeedbackAdmin)
admin.site.register(QuestPointAward, QuestPointAwardAdmin)
admin.site.register(Quest, QuestAdmin)
admin.site.register(QuestAttempt, QuestAttemptAdmin)
