from django.core.management.base import BaseCommand

from dashboard.models import Profile
from mentor.mails import mentors_match
from django.db.models import Q


class Command(BaseCommand):

    help = 'send mails about mentors match'

    def handle(self, *args, **options):
        profiles = Profile.objects.filter(skills_needed__isnull=False)
        for profile in profiles:
            matched_profiles = Profile.objects.filter(~Q(pk=profile.pk), skills_offered__overlap=profile.skills_needed)
            if matched_profiles:
                mentors_match(list(matched_profiles.all()), profile.email)
