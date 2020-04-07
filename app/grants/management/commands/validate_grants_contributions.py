from django.core.management.base import BaseCommand
from grants.models import Contribution
from grants.views import next_round_start, round_end
from economy.tx import grants_transaction_validator
import pprint

class Command(BaseCommand):

    help = 'validate grants transactions for this recent round'

    def handle(self, *args, **kwargs):
        start = next_round_start
        end = round_end
        network = 'mainnet'

        contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True, subscription__network=network)
        inputs = []
        pp = pprint.PrettyPrinter(indent=4)
        for contribution in contributions:
            tx_list = [contribution.tx_id, contribution.split_tx_id]
            token_address = contribution.subscription.token_address
            response = grants_transaction_validator(tx_list, token_address, network)
            print('---------------------------------')
            pp.pprint(response)
