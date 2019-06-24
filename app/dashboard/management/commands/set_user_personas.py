from django.core.management.base import BaseCommand

from dashboard.models import Profile


class Command(BaseCommand):

    help = 'sets the profile persona flags for each profile based on their historical activity'

    def handle(self, *args, **options):
        for profile in Profile.objects.all():
            profile.calculate_and_save_persona()
