from django.contrib import admin
from search.models import SearchResult



class SearchResultAdmin(admin.ModelAdmin):
    ordering = ['-id']
    list_display = ['created_on', '__str__']
    raw_id_fields = ['visible_to']


admin.site.register(SearchResult, SearchResultAdmin)
