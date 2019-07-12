from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Profile, UserAction


class Command(BaseCommand):

    help = 'sets the profile persona flags for each profile based on their historical activity'

    def handle(self, *args, **options):
        last_24hr = timezone.now() - timezone.timedelta(hours=24)
        actions = UserAction.objects.filter(created_on__gt=last_24hr).distinct('profile')
        profiles = Profile.objects.filter(pk__in=actions.values_list('profile', flat=True))
        for profile in profiles:
            profile.calculate_and_save_persona()
