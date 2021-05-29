from django.core.management.base import BaseCommand, CommandError

from grants.models import GrantCollection


class Command(BaseCommand):

    help = 'Generate thumbnails for collections'

    def handle(self, *args, **kwargs):
        for collection in GrantCollection.objects.filter(hidden=False):
            collection.generate_cache()
