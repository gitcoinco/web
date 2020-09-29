from django.core.management.base import BaseCommand

from grants.models import Grant, GrantStat, CartActivity
from django.utils import timezone


class Command(BaseCommand):

    help = 'creates a grants snapshot'

    def handle(self, *args, **kwargs):
        for grant in Grant.objects.all():
            # setup
            last_snapshot = grant.stats.filter(snapshot_type='total').order_by('-created_on').first()

            # snapshot
            data = {
                'impressions': grant.get_view_count,
                'in_cart': CartActivity.objects.filter(metad
   ...: ata__icontains=f'/grants/{grant.pk}/').filter(latest=True, created_on__gt=(timezone.now() - timezone.timedelta(days=14))).count(),
                'contributions': grant.contribution_count
            }
            snapshot_type = 'total'
            GrantStat.objects.create(
                snapshot_type=snapshot_type,
                data=data,
                grant=grant,
                )

            # increment
            if last_snapshot:
                snapshot_type = "increment"
                increment_data = {
                }
                for key in data.keys():
                    increment_data[key] = data[key] - last_snapshot.data[key]
                GrantStat.objects.create(
                    snapshot_type=snapshot_type,
                    data=increment_data,
                    grant=grant,
                    )

            print(grant.pk)
