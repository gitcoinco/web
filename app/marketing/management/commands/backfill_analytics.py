from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty
from marketing.models import Stat


class Command(BaseCommand):

    help = 'backfills analytics that havent been pull by pull stats'

    def handle(self, *args, **options):

        that_time = timezone.now()
        while True:
            that_time = that_time - timezone.timedelta(hours=1)
            bounties = Bounty.objects.filter(
                fulfillment_accepted_on__gt=(that_time - timezone.timedelta(hours=24)),
                fulfillment_accepted_on__lt=that_time)
            hours = 0
            value = 0
            for bounty in bounties:
                try:
                    hours += bounty.fulfillments.filter(accepted=True).first().fulfiller_hours_worked
                    value += bounty.value_in_usdt
                except Exception:
                    pass
            print(that_time, bounties.count(), value, hours)
            if value and hours:
                val = round(float(value)/float(hours), 2)
                try:
                    key = 'bounties_hourly_rate_inusd_last_24_hours'
                    Stat.objects.create(
                        created_on=that_time,
                        key=key,
                        val=(val),
                        )
                except Exception:
                    pass
