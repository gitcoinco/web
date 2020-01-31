from django.contrib import admin

from questions.models import Question, Answer

class QuestionAdmin(admin.ModelAdmin):

        ordering = ['-id']
        list_display = ['id', 'text']
        raw_id_fields = ['owner']

class AnswerAdmin(admin.ModelAdmin):

        ordering = ['-id']
        list_display = ['id', 'text', 'is_accepted']
        raw_id_fields = ['owner']

admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
