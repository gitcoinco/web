from itertools import groupby

import web3
from django.core.management.base import BaseCommand
from django.db.models import Q

from grants.models import GrantPayout
from web3 import Web3

from app import settings

class MatchesContract:
    def __init__(self, address, network):
        provider = f"wss://{network}.infura.io/ws/v3/{settings.INFURA_V3_PROJECT_ID}"
        w3 = Web3(web3.WebsocketProvider(provider))

        self.contract = w3.eth.contract(address=address, abi=settings.MATCH_PAYOUTS_ABI)

    def get_payout_claimed_entries(self):
        payout_claim_filter = self.contract.events.PayoutClaimed.createFilter(fromBlock='0x0')
        entries = payout_claim_filter.get_all_entries()
        return [{'recipient': log['args']['recipient'], 'tx_hash': log['transactionHash'].hex() } for log in entries]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--network',
            '-n',
            dest='network',
            help='The network the match contract has been deployed (eg. mainnet, rinkeby)',
            required=True,
        )
        parser.add_argument(
            '--contract-address',
            '-c',
            dest='contract_address',
            help='The contract address for the matches contract',
            required=True,
        )

    def handle(self, *args, **kwargs):
        network = kwargs.get('network').strip()
        contract_address = kwargs.get('contract_address').strip()

        payout = GrantPayout.objects.get(contract_address=contract_address, network=network)
        clr_matches = payout.clr_matches.filter(Q(claim_tx='0x0') | Q(claim_tx=None)).select_related('grant')
        grouped_matches = groupby(clr_matches, lambda m: m.grant.admin_address)

        self.stdout.write(f'Number of unclaimed CLR Matches: {len(clr_matches)}')

        event_logs = MatchesContract(address=contract_address, network=network).get_payout_claimed_entries()

        for event in event_logs:
           matches = grouped_matches.get(event['recipient'], [])
           for match in matches:
               match.claim_tx = event['tx_hash']
               match.save()



