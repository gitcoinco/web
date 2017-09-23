from django.core.management.base import BaseCommand
from marketing.mail import *
from django.conf import settings
from dashboard.models import Bounty


class Command(BaseCommand):

    help = 'sends a test email'

    def handle(self, *args, **options):

        b = Bounty.objects.all().last()
        #new_bounty(b, [settings.CONTACT_EMAIL])
        #weekly_roundup([settings.CONTACT_EMAIL])
        #new_bounty(b, [settings.CONTACT_EMAIL])
        #new_bounty_claim(b, [settings.CONTACT_EMAIL])
        #new_bounty_rejection(b, [settings.CONTACT_EMAIL])
        #new_bounty_acceptance(b, [settings.CONTACT_EMAIL])
        #bounty_expire_warning(b, [settings.CONTACT_EMAIL])

