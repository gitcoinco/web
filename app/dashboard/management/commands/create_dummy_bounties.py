from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from dashboard.models import Bounty

class Command(BaseCommand):

    help = 'creates sample bounties for testing / debug purposes'

    def add_arguments(self, parser):
        parser.add_argument('--num', default=10)

    def handle(self, *args, **options):
        if not settings.DEBUG:
            print("Not debug");
            exit()

        for i in range(0, options['num']):
            Bounty.objects.create(
                title="Sample Title {}".format(i),
                web3_created=timezone.now() - timezone.timedelta(hours=i),
                value_in_token=i+1,
                token_name='REP',
                token_address='0x0',
                bounty_type='bug',
                project_length='days',
                experience_level='advanced',
                github_url="https://github.com/owocki",
                bounty_owner_address="0x00000",
                claimeee_address="0x00000000",
                is_open=True,
                expires_date=timezone.now(),
                raw_data=(),
                )
            print(i)
