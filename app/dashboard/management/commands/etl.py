import logging

from django.core.management.base import BaseCommand
from django.db import connection

from haystack.management.commands.update_index import Command as UpdateIndex

logger = logging.getLogger(__name__)

def etl():
    refresh_view_sql = 'REFRESH MATERIALIZED VIEW dashboard_userdirectory'

    try:
        with connection.cursor() as cursor:
            cursor.execute(refresh_view_sql)
    except Exception as e:
        logger.info("Unable to refresh user_directory view")
        logger.debug(str(e))

    UpdateIndex().handle()


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write('Running ETL...')
        etl()
        self.stdout.write('ETL finished!')
