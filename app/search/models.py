from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from economy.models import SuperModel
from elasticsearch import Elasticsearch
from grants.models import Grant


class SearchResult(SuperModel):
    """Records SearchResult - the generic object for all search results on the platform ."""

    source_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    source_id = models.PositiveIntegerField(db_index=True)
    source = GenericForeignKey('source_type', 'source_id')
    title = models.CharField(max_length=1000, default='')
    description = models.TextField(default='', blank=True)
    url = models.CharField(max_length=500, default='')
    img_url = models.CharField(max_length=600, default='', null=True)
    visible_to = models.ForeignKey('dashboard.Profile', related_name='search_results_visible',
                                   on_delete=models.CASCADE, db_index=True, null=True)

    def __str__(self):
        return f"{self.source_type}; {self.url}"

    def check_for_active_grant(self):
        grant = Grant.objects.get(pk=self.source_id)
        return grant.active and not grant.hidden

    def put_on_elasticsearch(self, index='search-index'):
        if self.visible_to:
            return None

        if self.source_type_id == 82:
            active_grant = self.check_for_active_grant()
            if not active_grant:
                return None

        es = Elasticsearch(settings.ELASTIC_SEARCH_URL)
        source_type = str(str(self.source_type).replace('token', 'kudos')).title()
        full_search = f"{self.title} {self.description} {source_type}"
        doc = {
            'title': self.title,
            'description': self.description,
            'full_search': full_search,
            'url': self.url,
            'pk': self.pk,
            'img_url': self.img_url,
            'timestamp': timezone.now(),
            'source_type': source_type,
            # in order to aggregate totals by type an int needs to be indexed as opposed to a string
            'source_type_id': self.source_type_id
        }
        res = es.index(index=index, id=self.pk, body=doc)

def search_by_type(query, content_type, page=0, num_results=500):
    if not settings.ELASTIC_SEARCH_URL and not settings.ACTIVE_ELASTIC_INDEX:
        return {}

    es = Elasticsearch(settings.ELASTIC_SEARCH_URL)
    res = es.search(index=settings.ACTIVE_ELASTIC_INDEX, body={
        "from": page, "size": num_results,
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "source_type_id": {
                            "query": content_type
                        }
                    }
                },
                "should": [
                    {
                        "query_string": {
                            "query": f"*{query}*",
                            "fields": ["title^10", "description", "source_type"],
                        }
                    }
                ],
                "minimum_should_match": "1"
            }
        },
        "aggs": {
            "search-totals": {
                "terms": {
                    "field": "source_type_id"
                }
            }
        }
    })
    return res


def search(query, page=0, num_results=500):
    if not settings.ELASTIC_SEARCH_URL and not settings.ELASTIC_SEARCH_URL:
        return {}
    es = Elasticsearch(settings.ELASTIC_SEARCH_URL)
    # queries for wildcarded paginated results using boosts to lift by title and source_type=grant
    # index name will need updated once index is ready to be searched
    res = es.search(index=settings.ACTIVE_ELASTIC_INDEX, body={
        "from": page, "size": num_results,
        "query": {
            "bool": {
                "should": [
                    {
                        "query_string": {
                            "query": f"*{query}*",
                            "fields": ["title^10", "description", "source_type"],
                        }
                    }
                ],
                "minimum_should_match": "1"
            }
        },
        "aggs": {
            "search-totals": {
                "terms": {
                    "field": "source_type_id"
                }
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
