from django.core.management.base import BaseCommand
from django.db.models import Q

from dashboard.models import Profile
from mentor.mails import mentors_match


class Command(BaseCommand):

    help = 'send mails about mentors match'

    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        for profile in profiles:
            matched_profiles = Profile.objects.filter(~Q(pk=profile.pk), skills_offered__id__in=profile.skills_needed.all())
            if matched_profiles:
                mentors_match(list(matched_profiles.all().distinct()), profile)
