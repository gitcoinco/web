'''
    Copyright (C) 2021 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

'''
    Used to verify the match payouts that are set in the Grants Round 8 Payout contract. This
    contract is deployed on both mainnet and Rinkeby at 0xAf32BDf2e2720f6C6a2Fce8B50Ed66fd2b46d478
'''

# run me like this
# deploy contract
# ./manage.py payout_round set_payouts 131,121,120,119,118 9
# ./manage.py payout_round_noncustodial set_payouts mainnet --clr_pks=131,121,120,119,118 --clr_round=9 --process_all

import json
import math
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.abi import erc20_abi
from dashboard.models import Activity, Profile
from grants.models import CLRMatch, Contribution, Grant, GrantCLR, GrantPayout, Subscription
from marketing.mails import grant_match_distribution_final_txn, grant_match_distribution_kyc
from townsquare.models import Comment
from web3 import Web3

match_payouts_abi = settings.MATCH_PAYOUTS_ABI
SCALE = Decimal(1e18) # scale factor for converting Dai units
WAIT_TIME_BETWEEN_TXS = 15 # seconds

class Command(BaseCommand):

    help = 'Sets or verifies the match payouts in the Grants Round 8 Payout contract.'

    def add_arguments(self, parser):
        # Required arguments
        parser.add_argument('what',
            default='verify',
            type=str,
            help="what do we do? (finalize, payout_test, prepare_final_payout, verify, set_payouts, notify_users)"
        )

        # Required if what != verify
        parser.add_argument('--clr_pks',
            default=None,
            type=str,
            help="what CLR PKs should we payout? (eg 1,2,3,4)"
        )
        parser.add_argument('--clr_round',
            default=None,
            type=int,
            help="what CLR round number is this? eg 7"
        )

        parser.add_argument('--grant_payout_pk',
            default=None,
            type=int,
            help="Payout Contract Record"
        )

        parser.add_argument('--process_all', help='process_all, not just is_ready', action='store_true')


    def handle(self, *args, **options):

        # Parse inputs
        what = options['what']
        process_all = options['process_all']
        grant_payout_pk = options['grant_payout_pk']

        valid_whats = ['finalize', 'payout_test', 'prepare_final_payout', 'verify', 'set_payouts', 'notify_users']
        if what not in valid_whats:
            raise Exception(f"Invalid value {what} for 'what' arg")
        if not options['clr_round'] or not options['clr_pks']:
            raise Exception('Must provide clr_round and clr_pks')
        if not grant_payout_pk:
            raise Exception('Must provide grant_payout_pk containing payout contract info')

        # fetch GrantPayout contract
        grant_payout = GrantPayout.objects.get(pk=grant_payout_pk)

        # get deployed contract address
        match_payouts_address = Web3.toChecksumAddress(grant_payout.contract_address)

        # get network on which the contract is deployed
        network = grant_payout.network

        token_name = grant_payout.payout_token

        # Define parameters that vary by network. The expected total DAI amount uses the value here
        from_block = 11466409 if network == 'mainnet' else 7731622 # block contract was deployed at

        # TODO: fetch token_address from grant_payout
        dai_address = '0x6B175474E89094C44Da98b954EedeAC495271d0F' if network == 'mainnet' else '0x2e055eEe18284513B993dB7568A592679aB13188'

        expected_total_dai_amount = 100_000 if network == 'mainnet' else 5000 # in dollars, not wei, e.g. 500 = 500e18

        # Get contract instances
        PROVIDER = "wss://" + network + ".infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
        w3 = Web3(Web3.WebsocketProvider(PROVIDER))

        match_payouts = w3.eth.contract(address=match_payouts_address, abi=match_payouts_abi)
        dai = w3.eth.contract(address=dai_address, abi=erc20_abi)

        # Setup
        clr_round = options['clr_round']
        clr_pks = options['clr_pks'].split(',')
        KYC_THRESHOLD = settings.GRANTS_PAYOUT_CLR_KYC_THRESHOLD

        # Get data
        gclrs = GrantCLR.objects.filter(pk__in=clr_pks)
        pks = []
        for gclr in gclrs:
            pks += gclr.grants.values_list('pk', flat=True)
        scheduled_matches = CLRMatch.objects.filter(round_number=clr_round)
        grants = Grant.objects.filter(active=True, network='mainnet', is_clr_eligible=True, link_to_new_grant__isnull=True, pk__in=pks)
        self.stdout.write(f"got {grants.count()} grants")

        # Finalize rankings ------------------------------------------------------------------------
        if what == 'finalize':
            total_owed_grants = 0
            for grant in grants:
                try:
                    for gclr in grant.clr_calculations.filter(grantclr__in=gclrs, latest=True):
                        total_owed_grants += gclr.clr_prediction_curve[0][1]
                except:
                    pass
            total_owed_matches = sum(sm.amount for sm in scheduled_matches)
            self.stdout.write(f"there are {grants.count()} grants to finalize worth ${round(total_owed_grants,2)}")
            self.stdout.write(f"there are {scheduled_matches.count()} Match Payments already created worth ${round(total_owed_matches,2)}")
            print('------------------------------')
            
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return

            clr_matches_created = 0
            for grant in grants:
                amount = sum(ele.clr_prediction_curve[0][1] for ele in grant.clr_calculations.filter(grantclr__in=gclrs, latest=True))
                has_already_kyc = grant.clr_matches.filter(has_passed_kyc=True).exists()
                
                if not amount:
                    continue
                already_exists = scheduled_matches.filter(grant=grant).exists()
                if already_exists:
                    continue
                needs_kyc = amount > KYC_THRESHOLD and not has_already_kyc
                comments = "" if not needs_kyc else "Needs KYC"
                ready_for_test_payout = not needs_kyc
                match = CLRMatch.objects.create(
                    round_number=clr_round,
                    amount=amount,
                    grant=grant,
                    comments=comments,
                    ready_for_test_payout=ready_for_test_payout,
                    grant_payout=grant_payout
                )
                clr_matches_created += 1
                if needs_kyc:
                    grant_match_distribution_kyc(match)
            self.stdout.write(f"{clr_matches_created} matches were created")

        # Payout rankings (round must be finalized first) ------------------------------------------
        if what in ['prepare_final_payout']:
            payout_matches = scheduled_matches.filter(ready_for_payout=False)
            payout_matches_amount = sum(sm.amount for sm in payout_matches)
            self.stdout.write(f"there are {payout_matches.count()} UNPAID Match Payments already created worth ${round(payout_matches_amount,2)} {network} DAI")
            print(f"All these are users would need KYC. Do not do this for mainnet")
            print('------------------------------')
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return
            for match in payout_matches:
                match.ready_for_payout=True
                match.save()
            self.stdout.write('promoted')

        # Set payouts (round must be finalized first) ----------------------------------------------
        if what in ['set_payouts']:
            is_real_payout = what == 'set_payouts'

            # matches which have already been paid manually
            paid_scheduled_matches = scheduled_matches.filter(ready_for_payout=True).exclude(payout_tx='')

            unpaid_scheduled_matches = scheduled_matches.filter(payout_tx='')

            # matches which need KYC but still should be uploaded to contract
            pending_kyc_unpaid_matches = unpaid_scheduled_matches.filter(ready_for_payout=False)

            # matches which don't need KYC but need to be uploaded to contract
            no_kyc_unpaid_matches = unpaid_scheduled_matches.filter(ready_for_payout=True)

            total_paid_matches = sum(sm.amount for sm in paid_scheduled_matches)
            total_owed_matches = sum(sm.amount for sm in unpaid_scheduled_matches)
            total_pending_kyc_matches = sum(sm.amount for sm in pending_kyc_unpaid_matches)
            total_no_kyc_matches = sum(sm.amount for sm in no_kyc_unpaid_matches)


            print('=============================')
            print(f"there are {paid_scheduled_matches.count()} PAID Match (MADE MANUALLY/ALREADY UPLOADED) ${round(total_paid_matches,2)} {network} {token_name}")

            print(f"there are {unpaid_scheduled_matches.count()} UNPAID Match Payments worth ${round(total_owed_matches,2)} {network} {token_name} of which: ")
            print(f"------> {pending_kyc_unpaid_matches.count()} UNPAID Matches PENDING KYC ${round(total_pending_kyc_matches,2)}")
            print(f"------> {no_kyc_unpaid_matches.count()} UNPAID Matches SKIPPING KYC ${round(total_no_kyc_matches,2)}")

            print('=============================')

            target_matches = unpaid_scheduled_matches
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return

            print(f"continuing with {target_matches.count()} unpaid scheduled payouts (pending KYC + skipped KYC)")

            if is_real_payout:
                user_input = input(f"THIS IS A REAL PAYOUT FOR {network} {token_name}. ARE YOU DOUBLE SECRET SUPER SURE? (y/n) ")
                if user_input != 'y':
                    return

            # Generate dict of payout mapping that we'll use to set the contract's payout mapping
            full_payouts_mapping_dict = {}
            for match in target_matches.order_by('amount'):

                try:
                    # Amounts to set
                    recipient = w3.toChecksumAddress(match.grant.admin_address)
                    amount = Decimal(match.amount) * SCALE # convert to wei

                    # This ensures that even when multiple grants have the same receiving address,
                    # all match funds are accounted for
                    if recipient in full_payouts_mapping_dict.keys():
                        full_payouts_mapping_dict[recipient] += amount
                    else:
                        full_payouts_mapping_dict[recipient] = amount
                except Exception as e:
                    print(f"could not payout grant:{match.grant.pk} bc exception{e}")

            # Convert dict to array to use it as inputs to the contract
            full_payouts_mapping = []
            for key, value in full_payouts_mapping_dict.items():
                full_payouts_mapping.append([key, str(int(value))])

            # In tests, it took 68,080 gas to set 2 payout values. Let's be super conservative
            # and say it's 50k gas per payout mapping. If we are ok using 6M gas per transaction,
            # that means we can set 6M / 50k = 120 payouts per transaction. So we chunk the
            # payout mapping into sub-arrays with max length of 120 each
            # KO 12/21 - edited with Matt to make 2.1x that
            def chunks(lst, n):
                """Yield successive n-sized chunks from lst. https://stackoverflow.com/a/312464"""
                for i in range(0, len(lst), n):
                    yield lst[i:i + n]
            chunk_size = 250 if not settings.DEBUG else 120
            chunked_payouts_mapping = chunks(full_payouts_mapping, chunk_size)
            # Set payouts
            for payout_mapping in chunked_payouts_mapping:

                #tx = match_payouts.functions.setPayouts(payout_mapping).buildTransaction(tx_args)

                print(f"#TODO: Send this txn view etherscan {match_payouts_address}")
                print(json.dumps(payout_mapping))
                print("UPLOAD THE ABOVE CHUNK TO ETHERSCAN")

        # Verify contract is set properly ----------------------------------------------------------
        if what == 'verify':
            from web3.middleware import geth_poa_middleware
            w3.middleware_stack.inject(geth_poa_middleware, layer=0)


            # Get expected total match amount
            total_owed_grants = 0
            for grant in grants:
                try:
                    for gclr in grant.clr_calculations.filter(grantclr__in=gclrs, latest=True):
                        total_owed_grants += gclr.clr_prediction_curve[0][1]
                except:
                    pass
            expected_total_dai_amount = sum(sm.amount for sm in scheduled_matches)

            # Get PayoutAdded events
            payout_added_filter = match_payouts.events.PayoutAdded.createFilter(fromBlock=from_block)
            payout_added_logs = payout_added_filter.get_all_entries() # print these if you need to inspect them

            # Sort payout logs by ascending block number, this way if a recipient appears in multiple blocks
            # we use the value from the latest block
            sorted_payout_added_logs = sorted(payout_added_logs, key=lambda log:log['blockNumber'], reverse=False)

            # Get total required DAI balance based on PayoutAdded events. Events will be sorted chronologically,
            # so if a recipient is duplicated we only keep the latest entry. We do this by storing our own
            # mapping from recipients to match amount and overwriting it as needed just like the contract would.
            # We keep another dict that maps the recipient's addresses to the block it was found in. If we find
            # two entries for the same user in the same block, we throw, since we don't know which is the
            # correct one
            payment_dict = {}
            user_block_dict = {}

            for log in sorted_payout_added_logs:
                # Parse parameters from logs
                recipient = log['args']['recipient']
                amount = Decimal(log['args']['amount'])
                block = log['blockNumber']

                # Check if recipient's payout has already been set in this block
                if recipient in user_block_dict and user_block_dict[recipient] == block:
                    raise Exception(f'Recipient {recipient} payout was set twice in block {block}, so unclear which to use')

                # Recipient not seen in this block, so save data
                payment_dict[recipient] = amount
                user_block_dict[recipient] = block

            # Sum up each entry to get the total required amount
            total_dai_required_wei = sum(payment_dict[recipient] for recipient in payment_dict.keys())

            # Convert to human units
            total_dai_required = total_dai_required_wei / SCALE

            # TODO: REMOVE THIS AFTER ROUND 11 PAYOUT
            # THIS IS DUE TO SECOND CONTRACT DEPLOY FOR PAYOUT
            # expected_total_dai_amount = total_dai_required

            # Verify that total DAI required (from event logs) equals the expected amount
            if math.floor(expected_total_dai_amount) != math.floor(total_dai_required):
                print('\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
                print('Total DAI payout amount in the contract does not equal the expected value!')
                print('  Total expected amount:  ', expected_total_dai_amount)
                print('  Total amount from logs: ', total_dai_required)
                print('* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n')
                raise Exception('Total payout amount in the contract does not equal the expected value!')
            print('Total payout amount in the contracts is the expected value')

            # Get contract DAI balance
            dai_balance = Decimal(dai.functions.balanceOf(match_payouts_address).call()) / SCALE

            # Verify that contract has sufficient DAI balance to cover all payouts
            print('\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
            if dai_balance == total_dai_required:
                print(f'Contract balance of {dai_balance} DAI is exactly equal to the required amount')

            elif dai_balance < total_dai_required:
                shortage = total_dai_required - dai_balance
                print('Contract DAI balance is insufficient')
                print('  Required balance: ', total_dai_required)
                print('  Current balance:  ', dai_balance)
                print('  Extra DAI needed: ', shortage)
                print(f'\n Contract needs another {shortage} DAI')

            elif dai_balance > total_dai_required:
                excess = dai_balance - total_dai_required
                print('Contract has excess DAI balance')
                print('  Required balance:  ', total_dai_required)
                print('  Current balance:   ', dai_balance)
                print('  Excess DAI amount: ', excess)
                print(f'\n Contract has an excess of {excess} DAI')
            print('* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n')


        # Create Contributions and send emails ----------------------------------------------------------
        if what == 'notify_users':

            unpaid_scheduled_matches = scheduled_matches.filter(
                ready_for_payout=True,
                payout_tx=''
            )
            target_matches = unpaid_scheduled_matches if not process_all else scheduled_matches

            tx_id = input("enter the last chunk txid:  ")

            # All payouts have been successfully set, so now we update the database
            for match in target_matches.order_by('amount'):
                # make save state to DB
                match.payout_tx = tx_id
                match.payout_tx_date = timezone.now()
                grant_match_distribution_final_txn(match, True)
                match.save()

                # create payout obj artifacts
                profile = Profile.objects.get(handle__iexact='gitcoinbot')
                validator_comment = f"created by ingest payout_round_script"
                subscription = Subscription()
                subscription.is_postive_vote = True
                subscription.active = False
                subscription.error = True
                subscription.contributor_address = 'N/A'
                subscription.amount_per_period = match.amount
                subscription.real_period_seconds = 2592000
                subscription.frequency = 30
                subscription.frequency_unit = 'N/A'
                subscription.token_address = dai_address
                subscription.token_symbol = token_name
                subscription.gas_price = 0
                subscription.new_approve_tx_id = '0x0'
                subscription.num_tx_approved = 1
                subscription.network = network
                subscription.contributor_profile = profile
                subscription.grant = match.grant
                subscription.comments = validator_comment
                subscription.amount_per_period_usdt = match.amount
                subscription.save()

                contrib = Contribution.objects.create(
                    success=True,
                    tx_cleared=True,
                    tx_override=True,
                    tx_id=tx_id,
                    subscription=subscription,
                    validator_passed=True,
                    validator_comment=validator_comment,
                )
                print(f"ingested {subscription.pk} / {contrib.pk}")

                match.payout_contribution = contrib
                match.save()

                metadata = {
                    'id': subscription.id,
                    'value_in_token': str(subscription.amount_per_period),
                    'value_in_usdt_now': str(round(subscription.amount_per_period_usdt,2)),
                    'token_name': subscription.token_symbol,
                    'title': subscription.grant.title,
                    'grant_url': subscription.grant.url,
                    'num_tx_approved': subscription.num_tx_approved,
                    'category': 'grant',
                }
                kwargs = {
                    'profile': profile,
                    'subscription': subscription,
                    'grant': subscription.grant,
                    'activity_type': 'new_grant_contribution',
                    'metadata': metadata,
                }

                activity = Activity.objects.create(**kwargs)
                activity.populate_activity_index()

                comment = f"CLR Round {clr_round} Payout"
                comment = Comment.objects.create(profile=profile, activity=activity, comment=comment)
