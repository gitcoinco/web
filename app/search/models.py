from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from economy.models import SuperModel
from elasticsearch import Elasticsearch


class SearchResult(SuperModel):
    """Records SearchResult - the generic object for all search results on the platform ."""

    source_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    source_id = models.PositiveIntegerField(db_index=True)
    source = GenericForeignKey('source_type', 'source_id')
    title = models.CharField(max_length=1000, default='')
    description = models.TextField(default='', blank=True)
    url = models.CharField(max_length=500, default='')
    img_url = models.CharField(max_length=600, default='', null=True)
    visible_to = models.ForeignKey('dashboard.Profile', related_name='search_results_visible', on_delete=models.CASCADE, db_index=True, null=True)

    def __str__(self):
        return f"{self.source_type}; {self.url}"


    def put_on_elasticsearch(self):
        if self.visible_to:
            return None

        es = Elasticsearch([settings.ELASTIC_SEARCH_URL])
        source_type  = str(str(self.source_type).replace('token', 'kudos')).title()
        full_search = f"{self.title}{self.description}{source_type}"
        doc = {
            'title': self.title,
            'description': self.description,
            'full_search': full_search,
            'url': self.url,
            'pk': self.pk,
            'img_url': self.img_url,
            'timestamp': timezone.now(),
            'source_type': source_type,
        }
        res = es.index(index="search-index", id=self.pk, body=doc)


def search(query, num_results=500):
    if not settings.ELASTIC_SEARCH_URL:
        return {}
    es = Elasticsearch([settings.ELASTIC_SEARCH_URL])
    res = es.search(index="search-index", body={
      "from" : 0, "size" : num_results,
      "query": {
        "match": {
          "full_search": query,
        }
      }
    })
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
