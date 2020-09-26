from django.contrib import admin

from .models import GameFeed, Game

class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']

class GameAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['creator']

class GameFeedAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['game', 'sender']


admin.site.register(Game, GameAdmin)
admin.site.register(GameFeed, GameFeedAdmin)
