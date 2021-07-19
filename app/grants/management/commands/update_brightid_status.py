from django.core.management.base import BaseCommand

from dashboard.brightid_utils import get_verified_uuids
from dashboard.models import Profile


class Command(BaseCommand):

    help = 'Checks for verified BrightID users and updates them in the database'

    def handle(self, *args, **options):
        verified_uuids = get_verified_uuids()

        for uuid in verified_uuids:
            results = Profile.objects.filter(brightid_uuid=uuid).filter(is_brightid_verified=False)
            if len(results) > 0:
                user = results[0]
                user.is_brightid_verified = True
                user.save(update_fields=['is_brightid_verified'])
