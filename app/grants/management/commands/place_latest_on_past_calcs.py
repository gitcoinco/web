from django.core.management.base import BaseCommand
from django.db import connection

from grants.models import GrantCLR
from grants.models.grant_clr_calculation import GrantCLRCalculation


class Command(BaseCommand):
    help = 'Restore the latest entry on past clr calculations'

    def handle(self, *args, **options):

        clrs = GrantCLR.objects.all()

        for clr in clrs:

            print(f'- setting latest=True for {clr.id}')

            # get the latest calculations for the grantclr_id
            getLatest = f'''
                WITH roundsCLR AS (
                    SELECT
                        a.id,
                        ROW_NUMBER() OVER(PARTITION BY a.grant_id ORDER BY a.id DESC) AS rank
                    FROM grants_grantclrcalculation a WHERE a.grantclr_id = {clr.id}
                )
                SELECT roundsCLR.id FROM roundsCLR WHERE rank = 1
            '''

            with connection.cursor() as cursor:
                cursor.execute(getLatest)
                for _row in cursor.fetchall():
                    calc = GrantCLRCalculation.objects.filter(pk=_row[0]).first()
                    calc.latest = True
                    calc.save()
