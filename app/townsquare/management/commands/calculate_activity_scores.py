from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Activity
from townsquare.views import activity_score

class Command(BaseCommand):

        def handle(self, *args, **options):
            recent_activities = Activity.objects.filter(created__gt=timezone.now() - timezone.timedelta(hours=72))
            for a in recent_activities:
                try:
                    a.activity_score = activity_score(a)
                    a.save()
                except Exception as e:
                    continue
