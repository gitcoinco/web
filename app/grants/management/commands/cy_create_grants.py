import json

from django.core.management.base import BaseCommand

from grants.tests.factories import GrantFactory


class Command(BaseCommand):
    help = 'Create grants for use in cypress testing'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        grant = GrantFactory()
        self.stdout.write(json.dumps([dict(id=grant.id, title=grant.title)]))
