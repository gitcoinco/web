import pprint
import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from economy.tx import grants_transaction_validator
from grants.models import Contribution
from grants.views import next_round_start, round_end


class Command(BaseCommand):

    help = 'validate grants transactions for this recent round'

    def add_arguments(self, parser):
        parser.add_argument('type', default='round', type=str, help="the type of sync (all, round, or last_hour)")

    def handle(self, *args, **kwargs):
        start = next_round_start
        end = round_end
        network = 'mainnet'
        if kwargs['type'] == 'all':
            start = timezone.datetime(1990, 1, 1)
            end = timezone.now()
        if kwargs['type'] == 'last_hour':
            start = timezone.now() - timezone.timedelta(hours=1)
            end = timezone.now()


        contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True, subscription__network=network)
        #contributions = contributions.filter(subscription__grant__grant_type='health')
        contributions = contributions.filter(originated_address='0x0')
        #contributions = contributions.filter(pk=14487)
        inputs = []
        start_time = time.time()
        counter = 0
        pp = pprint.PrettyPrinter(indent=4)
        total = contributions.count()
        for contribution in contributions:
            try:
                # get data from API
                response = grants_transaction_validator(contribution)
                #print('---------------------------------')
                #pp.pprint(response)

                if len(response['originator']):
                    contribution.originated_address = response['originator'][0]
                contribution.validator_passed = response['validation']['passed']
                contribution.validator_comment = response['validation']['comment']
                contribution.save()

                #housekeeping
                counter += 1
                time_per_row = round((time.time() - start_time) / counter, 2)
                left = total - counter
                est_time_left = round(time_per_row * left / 60 / 60, 2)
                print(f"debug {counter}/{total}: this is taking {time_per_row}s/row. estimated time left: {est_time_left}h")
            except Exception as e:
                print(e)
