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


MAINNET_DAI_ADDRESS = '0x6B175474E89094C44Da98b954EedeAC495271d0F'
RINKEBY_DAI_ADDRESS = '0x2e055eEe18284513B993dB7568A592679aB13188'


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

        # get token information in which the payout will be done
        token_info = grant_payout.token

        if not token_info:
            raise Exception(f"Token is not set for GrantPayout Entry")

        token_symbol = token_info.symbol
        token_address = token_info.address
        token_decimal = token_info.decimals

        if not token_address:
            # Default to network DAI address
            self.stdout.write('Token address. Are you sure you want to proceed with default DAI address ?')
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return

            token_address = MAINNET_DAI_ADDRESS if network == 'mainnet' else RINKEBY_DAI_ADDRESS

        # Get contract instances
        PROVIDER = "wss://" + network + ".infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
        w3 = Web3(Web3.WebsocketProvider(PROVIDER))

        token_contract = w3.eth.contract(address=token_address, abi=erc20_abi)

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
            total_owed_matches_in_usd = sum(sm.amount for sm in scheduled_matches)
            self.stdout.write(f"there are {grants.count()} grants to finalize worth ${round(total_owed_grants, 2)}")
            self.stdout.write(f"there are {scheduled_matches.count()} Match Payments already created worth ${round(total_owed_matches_in_usd, 2)}")
            self.stdout.write('------------------------------')

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

                # get token amount
                token_amount = amount * grant_payout.conversion_rate

                match = CLRMatch.objects.create(
                    round_number=clr_round,
                    amount=amount,
                    token_amount=token_amount,
                    grant=grant,
                    comments=comments,
                    grant_payout=grant_payout
                )
                clr_matches_created += 1
                if needs_kyc:
                    grant_match_distribution_kyc(match)
            self.stdout.write(f"{clr_matches_created} matches were created")

        # Payout rankings (round must be finalized first) ------------------------------------------
        if what in ['prepare_final_payout']:
            payout_matches = scheduled_matches.filter(ready_for_payout=False)
            payout_matches_amount_in_usd = sum(sm.amount for sm in payout_matches)
            payout_matches_amount_in_token = sum(sm.token_amount for sm in payout_matches)
            self.stdout.write(f"There are {payout_matches.count()} UNPAID Match Payments already created worth {round(payout_matches_amount_in_token,2)} {token_symbol} ( AKA ${round(payout_matches_amount_in_usd, 2)} ) on {network}")
            self.stdout.write(f"All these are users would need KYC. Do not do this for mainnet")
            self.stdout.write('------------------------------')
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return
            for match in payout_matches:
                match.ready_for_payout=True
                match.save()
            self.stdout.write('promoted')

        # Set payouts (round must be finalized first) ----------------------------------------------
        if what in ['set_payouts']:

            # matches which have already been paid manually
            paid_scheduled_matches = scheduled_matches.filter(ready_for_payout=True).exclude(payout_tx='')

            unpaid_scheduled_matches = scheduled_matches.filter(payout_tx='')

            # matches which need KYC but still should be uploaded to contract
            pending_kyc_unpaid_matches = unpaid_scheduled_matches.filter(ready_for_payout=False)

            # matches which don't need KYC but need to be uploaded to contract
            no_kyc_unpaid_matches = unpaid_scheduled_matches.filter(ready_for_payout=True)

            # total payout breakdown in USD
            total_paid_matches_in_usd = sum(sm.amount for sm in paid_scheduled_matches)
            total_owed_matches_in_usd = sum(sm.amount for sm in unpaid_scheduled_matches)
            total_pending_kyc_matches_in_usd = sum(sm.amount for sm in pending_kyc_unpaid_matches)
            total_no_kyc_matches_in_usd = sum(sm.amount for sm in no_kyc_unpaid_matches)


            # total payout breakdown in token_amount
            total_paid_matches_in_token = sum(sm.token_amount for sm in paid_scheduled_matches)
            total_owed_matches_in_token = sum(sm.token_amount for sm in unpaid_scheduled_matches)
            total_pending_kyc_matches_in_token = sum(sm.token_amount for sm in pending_kyc_unpaid_matches)
            total_no_kyc_matches_in_token = sum(sm.token_amount for sm in no_kyc_unpaid_matches)

            self.stdout.write('=============================')

            self.stdout.write(f"there are {paid_scheduled_matches.count()} PAID Match (MADE MANUALLY/ALREADY UPLOADED) {round(total_paid_matches_in_token, 2)} {token_symbol} ( AKA ${round(total_paid_matches_in_usd, 2)} ) on {network}")
            self.stdout.write(f"there are {unpaid_scheduled_matches.count()} UNPAID Match Payments worth {round(total_owed_matches_in_token, 2)} ( AKA ${round(total_owed_matches_in_usd, 2)} ) on {network} of which: ")
            self.stdout.write(f"------> {pending_kyc_unpaid_matches.count()} UNPAID Matches PENDING KYC {round(total_pending_kyc_matches_in_token, 2)} ( AKA ${round(total_pending_kyc_matches_in_usd, 2)} )")
            self.stdout.write(f"------> {no_kyc_unpaid_matches.count()} UNPAID Matches SKIPPING KYC {round(total_no_kyc_matches_in_token, 2)} ( AKA ${round(total_no_kyc_matches_in_usd, 2)} )")

            self.stdout.write('=============================')

            target_matches = unpaid_scheduled_matches
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return

            self.stdout.write('=============================')
            self.stdout.write(f"Generating input for merkle contract for {target_matches.count()} grants for payout (pending KYC + skipped KYC)")
            self.stdout.write('=============================')

            # Generate dict of payout mapping that we'll use to set the contract's payout mapping
            full_payouts_mapping_dict = {}
            for match in target_matches.order_by('token_amount'):

                try:
                    address = w3.toChecksumAddress(match.grant.admin_address)

                    # This ensures that even when multiple grants have the same receiving address,
                    # all match funds are accounted for
                    if address in full_payouts_mapping_dict.keys():
                        full_payouts_mapping_dict[address] += match.token_amount
                    else:
                        full_payouts_mapping_dict[address] = match.token_amount
                except Exception as e:
                    self.stdout.write(f"could not payout grant:{match.grant.pk} bc exception{e}")


            merkle_input = []
            for address, token_amount in full_payouts_mapping_dict.items():
                payout = {
                    'address': address,
                    'amount': token_amount
                }
                merkle_input.append(payout)

            self.stdout.write('=============================')
            self.stdout.write(f'{merkle_input}')
            self.stdout.write('=============================')
            self.stdout.write("UPLOAD THE ABOVE OUTPUT TO https://github.com/thelostone-mc/merkle_payouts/blob/main/scripts/input.ts")
            self.stdout.write('=============================')


        # Verify contract is set properly ----------------------------------------------------------
        if what == 'verify':
            from web3.middleware import geth_poa_middleware
            w3.middleware_stack.inject(geth_poa_middleware, layer=0)


            # Get total token amount
            total_token_amount = Decimal(0)
            clr_matches = CLRMatch.objects.filter(round_number=clr_round)
            for clr_match in clr_matches:
                total_token_amount += Decimal(clr_match.amount)

            TOKEN_DECIMALS =  Decimal(10 ** token_decimal)
            # Get contract token balance
            token_balance = Decimal(
                token_contract.functions.balanceOf(match_payouts_address).call()
            ) / TOKEN_DECIMALS

            # Verify that contract has sufficient token balance to cover all payouts
            self.stdout.write('\n* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *')
            if token_balance == total_token_amount:
                self.stdout.write(f'Contract balance of {token_balance} ${token_symbol} is exactly equal to the required amount')

            elif token_balance < total_token_amount:
                shortage = total_token_amount - token_balance
                self.stdout.write(f'Contract {token_symbol} balance is insufficient')
                self.stdout.write(f'Required balance: {total_token_amount}')
                self.stdout.write(f'Current balance:  {token_balance}')
                self.stdout.write(f'Extra {token_symbol} needed: {shortage}')
                self.stdout.write(f'\n Contract needs another {shortage} {token_symbol}')

            elif token_balance > total_token_amount:
                excess = token_balance - total_token_amount
                self.stdout.write('Contract has excess {token_symbol} balance')
                self.stdout.write('Required balance:  {total_token_amount}')
                self.stdout.write('Current balance:   {token_balance}')
                self.stdout.write('Excess {token_symbol} amount: {excess}')
                self.stdout.write(f'\n Contract has an excess of {excess} {token_symbol}')
            self.stdout.write('* * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *\n')


        # Create Contributions and send emails ----------------------------------------------------------
        if what == 'notify_users':

            unpaid_scheduled_matches = scheduled_matches.filter(
                ready_for_payout=True,
                payout_tx=''
            )
            target_matches = unpaid_scheduled_matches if not process_all else scheduled_matches

            tx_id = input("enter the merkle contract deploy txn:  ")

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
                subscription.amount_per_period = match.token_amount
                subscription.real_period_seconds = 2592000
                subscription.frequency = 30
                subscription.frequency_unit = 'N/A'
                subscription.token_address = token_address
                subscription.token_symbol = token_symbol
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
                self.stdout.write(f"ingested {subscription.pk} / {contrib.pk}")

                match.payout_contribution = contrib
                match.save()

                metadata = {
                    'id': subscription.id,
                    'value_in_token': str(subscription.amount_per_period),
                    'value_in_usdt_now': str(round(subscription.amount_per_period_usdt, 2)),
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
