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

import time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.abi import erc20_abi as abi
from dashboard.models import Activity, Profile
from dashboard.utils import get_web3, has_tx_mined
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from grants.models import CLRMatch, Contribution, Grant, GrantCLR, Subscription
from marketing.mails import (
    grant_match_distribution_final_txn, grant_match_distribution_kyc, grant_match_distribution_test_txn,
)
from townsquare.models import Comment
from web3 import Web3

WAIT_TIME_BETWEEN_PAYOUTS = 15

class Command(BaseCommand):

    help = 'finalizes + sends grants round payouts'

    def add_arguments(self, parser):
        parser.add_argument('what',
            default='finalize',
            type=str,
            help="what do we do? (finalize, payout_test, prepare_final_payout, payout_dai)"
            )

        parser.add_argument('clr_pks',
            default='',
            type=str,
            help="what CLR PKs should we payout? (eg 1,2,3,4)"
            )

        parser.add_argument('clr_round',
            default='',
            type=int,
            help="what CLR round number is this? eg 7"
            )


    def handle(self, *args, **options):

        # setup
        payment_threshold_usd = 0
        KYC_THRESHOLD = settings.GRANTS_PAYOUT_CLR_KYC_THRESHOLD
        network = 'mainnet' if not settings.DEBUG else 'rinkeby'
        from_address = settings.GRANTS_PAYOUT_ADDRESS
        from_pk = settings.GRANTS_PAYOUT_PRIVATE_KEY
        DECIMALS = 18
        what = options['what']
        clr_round = options['clr_round']
        DAI_ADDRESS = '0x6b175474e89094c44da98b954eedeac495271d0f' if network=='mainnet' else '0x6a6e8b58dee0ca4b4ee147ad72d3ddd2ef1bf6f7'
        CLR_TOKEN_ADDRESS = '0xe4101d014443af2b7f6f9f603e904adc9faf0de5' if network=='mainnet' else '0xc19b694ebd4309d7a2adcd9970f8d7f424a1528b'

        # get data
        clr_pks = options['clr_pks'].split(',')
        gclrs = GrantCLR.objects.filter(pk__in=clr_pks)
        pks = []
        for gclr in gclrs:
            pks += gclr.grants.values_list('pk', flat=True)
        scheduled_matches = CLRMatch.objects.filter(round_number=clr_round)
        grants = Grant.objects.filter(active=True, network='mainnet', link_to_new_grant__isnull=True, pk__in=pks)
        print(f"got {grants.count()} grants")

        # finalize rankings
        if what == 'finalize':
            total_owed_grants = 0
            for grant in grants:
                try:
                    for gclr in grant.clr_calculations.filter(grantclr__in=gclrs, latest=True):
                        total_owed_grants += gclr.clr_prediction_curve[0][1]
                except:
                    pass
            total_owed_matches = sum(sm.amount for sm in scheduled_matches)
            print(f"there are {grants.count()} grants to finalize worth ${round(total_owed_grants,2)}")
            print(f"there are {scheduled_matches.count()} Match Payments already created worth ${round(total_owed_matches,2)}")
            print('------------------------------')
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return
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
                    )
                if needs_kyc:
                    grant_match_distribution_kyc(match)


        # payout rankings (round must be finalized first)
        if what in ['prepare_final_payout']:
            payout_matches = scheduled_matches.exclude(test_payout_tx='').filter(ready_for_payout=False)
            payout_matches_amount = sum(sm.amount for sm in payout_matches)
            print(f"there are {payout_matches.count()} UNPAID Match Payments already created worth ${round(payout_matches_amount,2)} {network} DAI")
            print('------------------------------')
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return
            for match in payout_matches:
                match.ready_for_payout=True
                match.save()
            print('promoted')


        # payout rankings (round must be finalized first)
        if what in ['payout_test', 'payout_dai']:
            is_real_payout = what == 'payout_dai'
            TOKEN_ADDRESS = DAI_ADDRESS if is_real_payout else CLR_TOKEN_ADDRESS
            kwargs = {}
            token_name = f'CLR{clr_round}' if not is_real_payout else 'DAI'
            key = 'ready_for_test_payout' if not is_real_payout else 'ready_for_payout'
            kwargs[key] = False
            not_ready_scheduled_matches = scheduled_matches.filter(**kwargs)
            kwargs[key] = True
            kwargs2 = {}
            key2 = 'test_payout_tx' if not is_real_payout else 'payout_tx'
            kwargs2[key2] = ''
            unpaid_scheduled_matches = scheduled_matches.filter(**kwargs).filter(**kwargs2)
            paid_scheduled_matches = scheduled_matches.filter(**kwargs).exclude(**kwargs2)
            total_not_ready_matches = sum(sm.amount for sm in not_ready_scheduled_matches)
            total_owed_matches = sum(sm.amount for sm in unpaid_scheduled_matches)
            total_paid_matches = sum(sm.amount for sm in paid_scheduled_matches)
            print(f"there are {not_ready_scheduled_matches.count()} NOT READY Match Payments already created worth ${round(total_not_ready_matches,2)} {network} {token_name}")
            print(f"there are {unpaid_scheduled_matches.count()} UNPAID Match Payments already created worth ${round(total_owed_matches,2)} {network} {token_name}")
            print(f"there are {paid_scheduled_matches.count()} PAID Match Payments already created worth ${round(total_paid_matches,2)} {network} {token_name}")
            print('------------------------------')
            user_input = input("continue? (y/n) ")
            if user_input != 'y':
                return

            print(f"continuing with {unpaid_scheduled_matches.count()} unpaid scheduled payouts")

            if is_real_payout:
                user_input = input(F"THIS IS A REAL PAYOUT FOR {network} {token_name}.  ARE YOU DOUBLE SECRET SUPER SURE? (y/n) ")
                if user_input != 'y':
                    return

            for match in unpaid_scheduled_matches.order_by('amount'):

                # issue payment
                print(f"- issuing payout {match.pk} worth {match.amount} {token_name}")
                address = match.grant.admin_address
                amount_owed = match.amount

                w3 = get_web3(network)
                contract = w3.eth.contract(Web3.toChecksumAddress(TOKEN_ADDRESS), abi=abi)
                address = Web3.toChecksumAddress(address)

                amount = int(amount_owed * 10**DECIMALS)
                tx_args = {
                    'nonce': w3.eth.getTransactionCount(from_address),
                    'gas': 100000,
                    'gasPrice': int(float(recommend_min_gas_price_to_confirm_in_time(1)) * 10**9 * 1.4)
                }
                tx = contract.functions.transfer(address, amount).buildTransaction(tx_args)

                signed = w3.eth.account.signTransaction(tx, from_pk)
                tx_id = None
                success = False
                counter = 0
                while not success:
                    try:
                        tx_id = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
                        success = True
                    except Exception as e:
                        counter +=1
                        if 'replacement transaction underpriced' in str(e):
                            print(f'replacement transaction underpriced. retrying {counter}')
                            time.sleep(WAIT_TIME_BETWEEN_PAYOUTS)
                        elif 'nonce too low' in str(e):
                            print(f'nonce too low. retrying {counter}')
                            time.sleep(WAIT_TIME_BETWEEN_PAYOUTS)

                            # rebuild txn
                            tx_args['nonce'] = w3.eth.getTransactionCount(from_address)
                            tx = contract.functions.transfer(address, amount).buildTransaction(tx_args)
                            signed = w3.eth.account.signTransaction(tx, from_pk)
                        else:
                            raise e

                if not tx_id:
                    print("cannot pay advance, did not get a txid")
                    continue

                print("paid via", tx_id)

                # make save state to DB
                if is_real_payout:
                    match.payout_tx = tx_id
                else:
                    match.test_payout_tx = tx_id
                match.save()

                # wait for tx to clear
                while not has_tx_mined(tx_id, network):
                    time.sleep(1)

                # make save state to DB
                if is_real_payout:
                    match.payout_tx_date = timezone.now()
                    grant_match_distribution_final_txn(match)
                else:
                    match.test_payout_tx_date = timezone.now()
                    grant_match_distribution_test_txn(match)
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
                subscription.token_address = TOKEN_ADDRESS
                subscription.token_symbol = token_name
                subscription.gas_price = 0
                subscription.new_approve_tx_id = '0x0'
                subscription.num_tx_approved = 1
                subscription.network = network
                subscription.contributor_profile = profile
                subscription.grant = match.grant
                subscription.comments = validator_comment
                subscription.amount_per_period_usdt = match.amount if is_real_payout else 0
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

                if is_real_payout:
                    match.payout_contribution = contrib
                else:
                    match.test_payout_contribution = contrib
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

                if is_real_payout:
                    comment = f"CLR Round {clr_round} Payout"
                    comment = Comment.objects.create(profile=profile, activity=activity, comment=comment)

                print("SLEEPING")
                time.sleep(WAIT_TIME_BETWEEN_PAYOUTS)
                print("DONE SLEEPING")
