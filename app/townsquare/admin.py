from django.contrib import admin

from .models import Comment, Like


# Register your models here.
class GenericAdmin(admin.ModelAdmin):
    list_display = ['created_on', '__str__']
    raw_id_fields = ['activity', 'profile']


admin.site.register(Comment, GenericAdmin)
admin.site.register(Like, GenericAdmin)
