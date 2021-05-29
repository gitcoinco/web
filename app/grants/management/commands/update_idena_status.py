from django.conf import settings
from django.core.management.base import BaseCommand

from dashboard.models import Profile
from requests.exceptions import RequestException


class Command(BaseCommand):

    help = 'Checks for connected Idena users and updates them in the database'

    def handle(self, *args, **options):
        connected_profiles = Profile.objects.filter(is_idena_connected=True)
        total_count = Profile.objects.filter(is_idena_connected=True).count()

        for index, profile in enumerate(connected_profiles):
            prev = profile.idena_status
            try:
                profile.update_idena_status()
                profile.save()
                print(f'{index + 1}/{total_count} -> Updating {profile.handle}: {prev} -> {profile.idena_status}')
            except RequestException as ex:
                print(f'{index + 1}/{total_count} -> Error getting {profile.handle}: {ex}')
