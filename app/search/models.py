from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from economy.models import SuperModel


class SearchResult(SuperModel):
    """Records SearchResult - the generic object for all search results on the platform ."""

    source_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    source_id = models.PositiveIntegerField()
    source = GenericForeignKey('source_type', 'source_id')
    title = models.CharField(max_length=1000, default='')
    description = models.TextField(default='', blank=True)
    url = models.CharField(max_length=500, default='')
    img_url = models.CharField(max_length=500, default='', null=True)
    visible_to = models.ForeignKey('dashboard.Profile', related_name='search_results_visible', on_delete=models.CASCADE, db_index=True, null=True)

    def __str__(self):
        return f"{self.source_type}; {self.url}"


class ProgrammingLanguage(SuperModel):
    """Records ProgrammingLanguage - the list for programming langauges"""
    val = models.CharField(max_length=255, default='')

    def __str__(self):
        return f"{self.val}"



class Page(SuperModel):
    """Records ProgrammingLanguage - the list for programming langauges"""
    title = models.CharField(max_length=255, default='')
    key = models.CharField(max_length=255, default='')
    description = models.TextField(default='', blank=True)

    def __str__(self):
        return f"{self.key} / {self.title}"
