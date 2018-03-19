# -*- coding: utf-8 -*-
"""Define Gitcoin Bot specific models."""
from django.contrib import admin

from gitcoinbot.models import GitcoinBotResponses


class GitcoinBotResponsesAdmin(admin.ModelAdmin):
    """Define the Gitcoin Bot response admin model for displaying bot request data."""
    fields = ('request', 'response', )
    list_display = ('request', 'response', )


admin.site.register(GitcoinBotResponses, GitcoinBotResponsesAdmin)
