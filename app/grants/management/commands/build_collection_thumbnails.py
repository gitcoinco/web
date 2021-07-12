from django.core.management.base import BaseCommand

from grants.models import GrantCollection
from grants.tasks import generate_collection_cache


class Command(BaseCommand):

    help = 'Generate thumbnails for collections'

    def handle(self, *args, **kwargs):
        for collection in GrantCollection.objects.filter(hidden=False):
            generate_collection_cache.delay(collection.pk)
