# -*- coding: utf-8 -*-
"""Define the Grant tx ingestion command.

Copyright (C) 2020 Gitcoin Core

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

import datetime
import os

from django.conf import settings
from django.core.management.base import BaseCommand

import pytz
import requests
from dashboard.models import Activity, Profile
from economy.models import Token
from economy.tx import headers
from economy.utils import convert_token_to_usdt
from grants.models import Contribution, Grant, Subscription
from web3 import Web3

"""
NOTE: This script only supports (1) regular L1 BulkCheckout, and (2) zkSync with L1 deposit. The
third case, pure zkSync donations, is not yet supported because none of the missing contributions
(at the time of this writing) are from this case.
"""

# ============================== Set the variables for this run here ===============================
network = "rinkeby" # "mainnet" or "rinkeby"
handle = "mds1" # Gitcoin username of user who made the contributions
txid = "0xdc85d562b0c0caf25e03e692d0ccc696ebcf5046cb36d12d4fdf88ceb7cac0e1" # L1 transaction hash
token = "USDT" # token contributions were made in
to_address = "0xaBEA9132b05A70803a4E85094fD0e1800777fBEF" # recipient of the L1 transaction
from_address = "0x60A5dcB2fC804874883b797f37CbF1b0582ac2dD" # from address for hash given by txid 
do_write = True # Use True to save contributions to Database
created_on = datetime.datetime(2020, 10, 5, 17, 22, tzinfo=pytz.UTC) # UTC timestamp oftxid 
gitcoin_zksync_addr = "0x5b4e39e6649a9c0afd39f068f7076f0ea3125e8a" # user's Gitcoin zkSync address, only used for zkSync cases


class Command(BaseCommand):

    help = "Inserts missing subscriptions and contributions into the database"

    def get_token(self, w3, network, address):
        if (address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'):
            address = '0x0000000000000000000000000000000000000000'
        try:
            # First try checksum
            address_checksum = w3.toChecksumAddress(address)
            return Token.objects.filter(network=network, address=address_checksum, approved=True).first().to_dict
        except AttributeError as e:
            address_lowercase = address.lower()
            return Token.objects.filter(network=network, address=address_lowercase, approved=True).first().to_dict

    def save_data(self, profile, txid, network, created_on, symbol, value_adjusted, grant):
        """
        Creates contribution and subscription and saves it to database if no matching one exists
        """
        currency = symbol
        amount = value_adjusted
        usd_val = amount * convert_token_to_usdt(symbol)

        # Check that subscription with these parameters does not exist
        existing_subscriptions = Subscription.objects.filter(
            grant__pk=grant.pk, contributor_profile=profile, split_tx_id=txid, token_symbol=currency
        )
        for existing_subscription in existing_subscriptions:
            tolerance = 0.01  # 1% tolerance to account for floating point
            amount_max = amount * (1 + tolerance)
            amount_min = amount * (1 - tolerance)

            if (
                existing_subscription.amount_per_period_minus_gas_price > amount_min
                and existing_subscription.amount_per_period_minus_gas_price < amount_max
            ):
                # Subscription exists
                print("Subscription exists, exiting function\n")
                return

        # No subscription found, so create subscription and contribution
        try:
            # create objects
            validator_comment = f"created by ingest grant txn script"
            subscription = Subscription()
            subscription.is_postive_vote = True
            subscription.active = False
            subscription.error = True
            subscription.contributor_address = "N/A"
            subscription.amount_per_period = amount
            subscription.real_period_seconds = 2592000
            subscription.frequency = 30
            subscription.frequency_unit = "N/A"
            subscription.token_address = "0x0"
            subscription.token_symbol = currency
            subscription.gas_price = 0
            subscription.new_approve_tx_id = "0x0"
            subscription.num_tx_approved = 1
            subscription.network = network
            subscription.contributor_profile = profile
            subscription.grant = grant
            subscription.comments = validator_comment
            subscription.amount_per_period_usdt = usd_val
            subscription.created_on = created_on
            subscription.split_tx_id = txid
            subscription.save()

            contrib = Contribution.objects.create(
                success=True,
                tx_cleared=True,
                tx_override=True,
                split_tx_id=txid,
                subscription=subscription,
                validator_passed=True,
                validator_comment=validator_comment,
                created_on=created_on,
            )
            print(f"ingested {subscription.pk} / {contrib.pk}")

            metadata = {
                "id": subscription.id,
                "value_in_token": str(subscription.amount_per_period),
                "value_in_usdt_now": str(round(subscription.amount_per_period_usdt, 2)),
                "token_name": subscription.token_symbol,
                "title": subscription.grant.title,
                "grant_url": subscription.grant.url,
                "num_tx_approved": subscription.num_tx_approved,
                "category": "grant",
            }
            kwargs = {
                "profile": profile,
                "subscription": subscription,
                "grant": subscription.grant,
                "activity_type": "new_grant_contribution",
                "metadata": metadata,
            }

            Activity.objects.create(**kwargs)
            print("Saved!\n")

        except Exception as e:
            print(e)
            print("\n")

    def handle(self, *args, **options):
        # Setup ============================================================================================
        # Setup web3 provider
        PROVIDER = f"wss://{network}.infura.io/ws/v3/{settings.INFURA_V3_PROJECT_ID}"
        w3 = Web3(Web3.WebsocketProvider(PROVIDER))

        # Get users profile
        profile = Profile.objects.get(handle=handle)

        # BulkCheckout contract info
        bulk_checkout_address = "0x7d655c57f71464B6f83811C55D84009Cd9f5221C"  # same address on mainnet and rinkeby
        bulk_checkout_abi = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"address","name":"dest","type":"address"},{"indexed":true,"internalType":"address","name":"donor","type":"address"}],"name":"DonationSent","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"address","name":"dest","type":"address"}],"name":"TokenWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address payable","name":"dest","type":"address"}],"internalType":"struct BulkCheckout.Donation[]","name":"_donations","type":"tuple[]"}],"name":"donate","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"_dest","type":"address"}],"name":"withdrawEther","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_tokenAddress","type":"address"},{"internalType":"address","name":"_dest","type":"address"}],"name":"withdrawToken","outputs":[],"stateMutability":"nonpayable","type":"function"}]'
        bulk_checkout_contract = w3.eth.contract(address=bulk_checkout_address, abi=bulk_checkout_abi)

        # zkSync contract info
        zksync_address = "0xaBEA9132b05A70803a4E85094fD0e1800777fBEF"
        zksync_abi = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"blockNumber","type":"uint32"}],"name":"BlockVerification","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"totalBlocksVerified","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"totalBlocksCommitted","type":"uint32"}],"name":"BlocksRevert","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"DepositCommit","type":"event"},{"anonymous":false,"inputs":[],"name":"ExodusMode","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint32","name":"nonce","type":"uint32"},{"indexed":false,"internalType":"bytes","name":"fact","type":"bytes"}],"name":"FactAuth","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"uint32","name":"zkSyncBlockId","type":"uint32"},{"indexed":true,"internalType":"uint32","name":"accountId","type":"uint32"},{"indexed":false,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"FullExitCommit","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"sender","type":"address"},{"indexed":false,"internalType":"uint64","name":"serialId","type":"uint64"},{"indexed":false,"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"indexed":false,"internalType":"bytes","name":"pubData","type":"bytes"},{"indexed":false,"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"name":"NewPriorityRequest","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"sender","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"},{"indexed":true,"internalType":"address","name":"owner","type":"address"}],"name":"OnchainDeposit","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"uint16","name":"tokenId","type":"uint16"},{"indexed":false,"internalType":"uint128","name":"amount","type":"uint128"}],"name":"OnchainWithdrawal","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsAdd","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"uint32","name":"queueStartIndex","type":"uint32"},{"indexed":false,"internalType":"uint32","name":"queueEndIndex","type":"uint32"}],"name":"PendingWithdrawalsComplete","type":"event"},{"constant":true,"inputs":[],"name":"EMPTY_STRING_KECCAK","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint32","name":"","type":"uint32"}],"name":"authFacts","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"bytes22","name":"","type":"bytes22"}],"name":"balancesToWithdraw","outputs":[{"internalType":"uint128","name":"balanceToWithdraw","type":"uint128"},{"internalType":"uint8","name":"gasReserveValue","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"blocks","outputs":[{"internalType":"uint32","name":"committedAtBlock","type":"uint32"},{"internalType":"uint64","name":"priorityOperations","type":"uint64"},{"internalType":"uint32","name":"chunks","type":"uint32"},{"internalType":"bytes32","name":"withdrawalsDataHash","type":"bytes32"},{"internalType":"bytes32","name":"commitment","type":"bytes32"},{"internalType":"bytes32","name":"stateRoot","type":"bytes32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint64","name":"_n","type":"uint64"}],"name":"cancelOutstandingDepositsForExodusMode","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint32","name":"_feeAccount","type":"uint32"},{"internalType":"bytes32[]","name":"_newBlockInfo","type":"bytes32[]"},{"internalType":"bytes","name":"_publicData","type":"bytes"},{"internalType":"bytes","name":"_ethWitness","type":"bytes"},{"internalType":"uint32[]","name":"_ethWitnessSizes","type":"uint32[]"}],"name":"commitBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_n","type":"uint32"}],"name":"completeWithdrawals","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint104","name":"_amount","type":"uint104"},{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"address","name":"_franklinAddr","type":"address"}],"name":"depositETH","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"uint16","name":"_tokenId","type":"uint16"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"}],"name":"exit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"},{"internalType":"uint16","name":"","type":"uint16"}],"name":"exited","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"exodusMode","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPendingWithdrawalIndex","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"firstPriorityRequestId","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_accountId","type":"uint32"},{"internalType":"address","name":"_token","type":"address"}],"name":"fullExit","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"internalType":"address","name":"_address","type":"address"},{"internalType":"uint16","name":"_tokenId","type":"uint16"}],"name":"getBalanceToWithdraw","outputs":[{"internalType":"uint128","name":"","type":"uint128"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"getNoticePeriod","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"initializationParameters","type":"bytes"}],"name":"initialize","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"isReadyForUpgrade","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"numberOfPendingWithdrawals","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint32","name":"","type":"uint32"}],"name":"pendingWithdrawals","outputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint16","name":"tokenId","type":"uint16"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"internalType":"uint64","name":"","type":"uint64"}],"name":"priorityRequests","outputs":[{"internalType":"enum Operations.OpType","name":"opType","type":"uint8"},{"internalType":"bytes","name":"pubData","type":"bytes"},{"internalType":"uint256","name":"expirationBlock","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_maxBlocksToRevert","type":"uint32"}],"name":"revertBlocks","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"_pubkey_hash","type":"bytes"},{"internalType":"uint32","name":"_nonce","type":"uint32"}],"name":"setAuthPubkeyHash","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksCommitted","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalBlocksVerified","outputs":[{"internalType":"uint32","name":"","type":"uint32"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalCommittedPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"totalOpenPriorityRequests","outputs":[{"internalType":"uint64","name":"","type":"uint64"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"triggerExodusIfNeeded","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"bytes","name":"upgradeParameters","type":"bytes"}],"name":"upgrade","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeCanceled","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeFinishes","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[],"name":"upgradeNoticePeriodStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActivationTime","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"upgradePreparationActive","outputs":[{"internalType":"bool","name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[],"name":"upgradePreparationStarted","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint32","name":"_blockNumber","type":"uint32"},{"internalType":"uint256[]","name":"_proof","type":"uint256[]"},{"internalType":"bytes","name":"_withdrawalsData","type":"bytes"}],"name":"verifyBlock","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawERC20","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"contract IERC20","name":"_token","type":"address"},{"internalType":"address","name":"_to","type":"address"},{"internalType":"uint128","name":"_amount","type":"uint128"},{"internalType":"uint128","name":"_maxAmount","type":"uint128"}],"name":"withdrawERC20Guarded","outputs":[{"internalType":"uint128","name":"withdrawnAmount","type":"uint128"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"internalType":"uint128","name":"_amount","type":"uint128"}],"name":"withdrawETH","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"}]'
        zksync_contract = w3.eth.contract(address=zksync_address, abi=zksync_abi)

        # Main Execution ===================================================================================
        if w3.toChecksumAddress(to_address) == w3.toChecksumAddress(bulk_checkout_address):
            # BulkCheckout
            # Make sure tx was successful
            receipt = w3.eth.getTransactionReceipt(txid)
            if receipt.status == 0:
                raise Exception("Transaction was not successful")

            # Parse tx logs
            parsed_logs = bulk_checkout_contract.events.DonationSent().processReceipt(receipt)

            # Return if no donation logs were found
            if len(parsed_logs) == 0:
                raise Exception("No DonationSent events found")

            # For each event in the parsed logs, create the DB objects
            for event in parsed_logs:
                # Extract contribution parameters from events
                token_address = event["args"]["token"]
                value = event["args"]["amount"]
                token = self.get_token(w3, network, token_address)
                decimals = token["decimals"]
                symbol = token["name"]
                value_adjusted = int(value) / 10 ** int(decimals)
                to = event["args"]["dest"]

                # Find the grant
                try:
                    print(to)
                    grant = (
                        Grant.objects.filter(admin_address__iexact=to)
                        .order_by("-positive_round_contributor_count")
                        .first()
                    )
                    print(f"{value_adjusted}{symbol}  => {to}, {grant.url} ")
                except Exception as e:
                    print(e)
                    print(f"{value_adjusted}{symbol}  => {to}, Unknown Grant ")
                    print("Skipping unknown grant\n")
                    continue

                if do_write:
                    self.save_data(profile, txid, network, created_on, symbol, value_adjusted, grant)
            return

        else:
            # zkSync
            # Get history of transfers from this user's Gitcoin zkSync address
            if network == "mainnet":
                r = requests.get(f"https://api.zksync.io/api/v0.1/account/{gitcoin_zksync_addr}/history/older_than")
            else:
                r = requests.get(f"https://rinkeby-api.zksync.io/api/v0.1/account/{gitcoin_zksync_addr}/history/older_than")
            r.raise_for_status()
            transactions = r.json()  # array of zkSync transactions

            for transaction in transactions:
                # Skip if this is not a transfer (can be Deposit, ChangePubKey, etc.)
                if transaction["tx"]["type"] != "Transfer":
                    continue

                # Skip if we are sending back to the user
                to = w3.toChecksumAddress(transaction["tx"]["to"])
                if to == w3.toChecksumAddress(gitcoin_zksync_addr) or to == w3.toChecksumAddress(from_address):
                    continue

                # Extract contribution parameters from the JSON
                symbol = transaction["tx"]["token"]
                value = transaction["tx"]["amount"]
                token = Token.objects.filter(network=network, symbol=transaction["tx"]["token"], approved=True).first().to_dict
                decimals = token["decimals"]
                symbol = token["name"]
                value_adjusted = int(value) / 10 ** int(decimals)
                to = transaction["tx"]["to"]

                # Find the grant
                try:
                    grant = Grant.objects.filter(admin_address__iexact=to).order_by("-positive_round_contributor_count").first()
                    print(f"{value_adjusted}{symbol}  => {to}, {grant.url} ")
                except Exception as e:
                    print(e)
                    print(f"{value_adjusted}{symbol}  => {to}, Unknown Grant ")
                    print("Skipping unknown grant\n")
                    continue

                if do_write:
                    self.save_data(profile, txid, network, created_on, symbol, value_adjusted, grant)
