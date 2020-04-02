from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand
from grants.models import Contribution
from grants.views import next_round_start, round_end
from grants.clr import grants_transaction_validator

class Command(BaseCommand):

    help = 'inputs the information '

    def handle(self, *args, **kwargs):
        start = next_round_start
        end = round_end

        contributions = Contribution.objects.filter(created_on__gt=start, created_on__lt=end, success=True, subscription__network='mainnet')
        print("tx_id1, tx_id2, from address, amount, amount_minus_gitcoin, token_address")
        inputs = []
        for contribution in contributions:
            _input = [contribution.tx_id, 
                contribution.split_tx_id,
                contribution.subscription.contributor_address,
                contribution.subscription.amount_per_period, 
                contribution.subscription.amount_per_period_minus_gas_price,
                contribution.subscription.token_address]
            inputs.append(_input)
        grants_transaction_validator(inputs)
