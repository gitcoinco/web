from django.contrib import admin

from search.models import Page, ProgrammingLanguage, SearchResult


class SearchResultAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['visible_to']

class GeneralAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']


admin.site.register(SearchResult, SearchResultAdmin)
admin.site.register(ProgrammingLanguage, GeneralAdmin)
admin.site.register(Page, GeneralAdmin)
