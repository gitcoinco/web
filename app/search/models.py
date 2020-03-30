from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from elasticsearch import Elasticsearch
from economy.models import SuperModel
from django.conf import settings
from django.utils import timezone


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


    def put_on_elasticserach(self):
        es = Elasticsearch([settings.ELASTIC_SEARCH_URL])
        doc = {
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'pk': self.pk,
            'img_url': self.img_url,
            'timestamp': timezone.now(),
        }
        res = es.index(index="search-index", id=self.pk, body=doc)


def search(query):
    es = Elasticsearch([settings.ELASTIC_SEARCH_URL])
    res = es.search(index="search-index", body={"query": {"match_all": {'title': query}}})
    return res


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
