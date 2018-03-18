from django.contrib import admin

from gitcoinbot.models import GitcoinBotResponses


class GitcoinBotResponsesAdmin(admin.ModelAdmin):
    fields = ('_request', 'response',)
    list_display =  ('_request', 'response',)


admin.site.register(GitcoinBotResponses, GitcoinBotResponsesAdmin)
