# -*- coding: utf-8 -*-
"""Define the management command to pull new price data for tokens.

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

"""
from django.core.management.base import BaseCommand

from dashboard.models import BountyFulfillment, Earning, Tip
from economy.models import Token
from grants.models import Contribution
from kudos.models import KudosTransfer


def updateContributionEarnings (earnings):
    ''' This should ensure gitcoin contributions aren't counted'''
    print("===========================================")
    print(f"Total Earning Contributions Count: {earnings.count()}")

    contributions = Contribution.objects.all()
    for earning in earnings:
        try:
            print(f'#{earning.pk}')
            contribution = contributions.get(pk=earning.source_id)
            if contribution.subscription.amount_per_period_minus_gas_price:
                earning.token_value = contribution.subscription.amount_per_period_minus_gas_price

                if contribution.success == False:
                    earning.success = False
                earning.save()
        except:
            print(f'unable to find contribution {earning.source_id}')


def updateKudosEarnings (earnings):
    print("===========================================")
    print(f"Total Earning Kudos Count: {earnings.count()}")
    kudos_transfers = KudosTransfer.objects.all()
    for earning in earnings:
        try:
            kudo = kudos_transfers.get(pk=earning.source_id)
            if kudo.amount:
                earning.token_value = kudo.amount
                earning.save()
        except:
            print(f'unable to find kudos {earning.source_id}')



def updateBountyEarnings (earnings):
    print("===========================================")
    print(f"Total Earning Bounties Fulfillment Count: {earnings.count()}")
    bounty_fulfillments = BountyFulfillment.objects.all()
    for earning in earnings:
        try:
            bounty_fulfillment = bounty_fulfillments.get(pk=earning.source_id)
            if bounty_fulfillment.payout_amount:
                earning.token_value = bounty_fulfillment.payout_amount
                earning.save()
        except:
            print(f'unable to find Bounty {earning.source_id}')


def updateTipEarnings (earnings):
    print("===========================================")
    print(f"Total Earning Tips Count: {earnings.count()}")
    tips = Tip.objects.all()
    for earning in earnings:
        try:
            tip = tips.get(pk=earning.source_id)
            if tip.amount:
                earning.token_value = tip.amount
                earning.save()
        except:
            print(f'unable to find Tip {earning.source_id}')


def fixBountyFulfillmentAmount ():
    print("===========================================")
    bounty_fulfillments = BountyFulfillment.objects.filter(payout_amount__gt=1000000)

    print(f"Fixing Amount for {bounty_fulfillments.count()}")

    tokens = Token.objects.filter(approved=True)

    for bounty_fulfillment in bounty_fulfillments:
        token_name = bounty_fulfillment.token_name
        token = tokens.filter(symbol=token_name).first()
        if token:       
            bounty_fulfillment.payout_amount = bounty_fulfillment.payout_amount / (10**token.decimals)
            bounty_fulfillment.save()
        else:
            print(f'error: unable to find {token_name}')


class Command(BaseCommand):
    """Define the management command to fix up earnings."""

    def handle(self, *args, **options):
        """Fix earnings."""

        print("Pulling in every Earning")
        # e = Earning.objects.all()
        # print(f"Total Count: {e.count()}")

        # fetch successful earnings
        earnings = Earning.objects.all()
        print(f"Total Count: {earnings.count()}")

        # filter mainnet 
        earnings_mainnet = earnings.filter(network='mainnet')
        print(f"Total Mainnet Earnings: {earnings_mainnet.count()}")


        # filter earning which have txid
        earnings_with_txid = earnings_mainnet.filter(txid__isnull=False).exclude(txid__exact='').exclude(txid__exact='0x0')
        print(f"Total Mainnet Earnings with txnid: {earnings_with_txid.count()}")
        
        #  ============================= STEP 1 =======================
        # fetch only grant contributions
        earning_contributions = earnings_with_txid.filter(source_type='81')
        # Ensure Gitcoin contributions are ignored and fixes decimal issue
        updateContributionEarnings(earning_contributions)


        #  ============================= STEP 2 =======================
        # fetch only kudos and fixes decimal issue
        earning_kudos = earnings_with_txid.filter(source_type='72')
        updateKudosEarnings(earning_kudos)

        # Refer below metabse query on why this function needs to be run
        # https://metabase.gitcoin.co/question/1054
        fixBountyFulfillmentAmount()

        #  ============================= STEP 3 =======================
        # fetch only bounty fulfillments and fixes decimal issue
        earning_bounty_fulfillments = earnings_with_txid.filter(source_type='35')
        updateBountyEarnings(earning_bounty_fulfillments)


        #  ============================= STEP 4 =======================
        # fetch only bounty fulfillments and fixes decimal issue
        earning_tips = earnings_with_txid.filter(source_type='21')
        updateTipEarnings(earning_tips)
