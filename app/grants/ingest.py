import logging
import dateutil.parser

import pytz
import requests

from django.conf import settings

from datetime import datetime
from dashboard.models import Activity, Profile
from economy.models import Token
from economy.utils import convert_token_to_usdt
from grants.models import (
    Grant, Subscription,
)

from web3 import Web3

logger = logging.getLogger(__name__)

def get_token(w3, network, chain, address):
    """
        For a given token address, returns the token's details.
        For mainnet checkout in ETH, we change the token address to 0x0000000000000000000000000000000000000000
        For polygon checkout in MATIC, we change the token address to 0x0000000000000000000000000000000000001010
        since that's the address BulkCheckout uses 0xEeee as the zero address
    """

    if chain == 'std':
        # set network_id and override address for ETH on mainnet
        network_id = 1
        if (address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'):
            # 0xEeee... is used to represent ETH in the BulkCheckout contract
            address = '0x0000000000000000000000000000000000000000'

    elif chain == 'polygon':
        # set network_id and override address for ETH on mainnet
        network_id = 137 if network == 'mainnet' else 80001
        if (address == '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'):
            # 0xEeee... is used to represent MATIC in the BulkCheckout contract
            address = '0x0000000000000000000000000000000000001010'

    tokens = Token.objects.filter(
        network=network,
        network_id=network_id,
        approved=True
    )

    try:
        # First try checksum
        address_checksum = w3.toChecksumAddress(address)
        return tokens.filter(address=address_checksum).first().to_dict
    except AttributeError as e:
        # Retry with lowercase
        address_lowercase = address.lower()
        return tokens.filter(address=address_lowercase).first().to_dict

def save_data(profile, txid, network, created_on, symbol, value_adjusted, grant, checkout_type, from_address):
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
        transfer_tolerance = 0.05  # 1% tolerance to account for floating point
        amount_max = int(amount * (1 + transfer_tolerance))
        amount_min = int(amount * (1 - transfer_tolerance))

        amount_to_use = existing_subscription.amount_per_period

        if (
            amount_to_use >= amount_min and
            amount_to_use <= amount_max
        ):
            # Subscription exists
            logger.info("Subscription exists, exiting function\n")
            return

    # No subscription found, so create subscription and contribution
    try:
        # create objects
        validator_comment = f"created by ingest grant txn script"
        subscription = Subscription()
        subscription.is_postive_vote = True
        subscription.active = False
        subscription.error = True
        subscription.contributor_address = Web3.toChecksumAddress(from_address)
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
        subscription.last_contribution_date = created_on
        subscription.next_contribution_date = created_on
        subscription.split_tx_id = txid
        subscription.save()

        # Create contribution and set the contribution as successful
        contrib = subscription.successful_contribution(
            '0x0',  # subscription.new_approve_tx_id,
            True,  # include_for_clr
            checkout_type=checkout_type
        )
        contrib.success = True
        contrib.tx_cleared = True
        contrib.tx_override = True
        contrib.validator_comment = validator_comment
        contrib.created_on = created_on
        contrib.save()
        logger.info(f"ingested {subscription.pk} / {contrib.pk}")

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

        activity = Activity.objects.create(**kwargs)
        activity.populate_activity_index()
        logger.info("Saved!\n")

    except Exception as e:
        logger.exception(e)
        logger.info("\n")

def process_bulk_checkout_tx(w3, txid, profile, network, chain, do_write):
    # Make sure tx was successful
    receipt = w3.eth.getTransactionReceipt(txid)
    from_address = receipt[
        'from']  # this means wallets like Argent that use relayers will have the wrong from address
    if receipt.status == 0:
        raise Exception("Transaction was not successful")

    # Parse tx logs
    if network == 'mainnet' and chain == 'polygon':
        bulk_checkout_address = '0xb99080b9407436eBb2b8Fe56D45fFA47E9bb8877'
    elif network == 'testnet' and chain == 'polygon':
        bulk_checkout_address = '0x3E2849E2A489C8fE47F52847c42aF2E8A82B9973'
    else:
        bulk_checkout_address = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C'

    bulk_checkout_contract = w3.eth.contract(address=bulk_checkout_address, abi=settings.BULK_CHECKOUT_ABI)
    parsed_logs = bulk_checkout_contract.events.DonationSent().processReceipt(receipt)

    # Return if no donation logs were found
    if len(parsed_logs) == 0:
        raise Exception("No DonationSent events weren found in this transaction")

    # Get transaction timestamp
    block_info = w3.eth.getBlock(receipt['blockNumber'])

    created_on = pytz.UTC.localize(datetime.fromtimestamp(block_info['timestamp']))

    # For each event in the parsed logs, create the DB objects
    for (index, event) in enumerate(parsed_logs):
        logger.info(f'\nProcessing {index + 1} of {len(parsed_logs)}...')
        # Extract contribution parameters from events
        token_address = event["args"]["token"]
        value = event["args"]["amount"]
        to = event["args"]["dest"]

        value_adjusted = None
        symbol = None

        try:
            token = get_token(w3, network, chain, token_address)
            decimals = token["decimals"]
            symbol = token["name"]
            value_adjusted = int(value) / 10 ** int(decimals)
        except Exception as e:
            logger.exception(e)
            raise Exception(f"unknown token with address {token_address} on network {network}")

        try:
            # Find the grant
            grant = (
                Grant.objects.filter(admin_address__iexact=to)
                    .order_by("-positive_round_contributor_count")
                    .first()
            )
            logger.info(f"{value_adjusted}{symbol}  => {to}, {grant} ")

            if do_write:
                checkout_type = 'eth_std' if chain == 'std' else 'eth_polygon'
                save_data(profile, txid, network, created_on, symbol, value_adjusted, grant, checkout_type,
                            from_address)

        except Exception as e:
            logger.exception(e)
            logger.warning(f"{token_address} {value_adjusted} {symbol}  => {to}, Unknown Grant ")
            logger.warning("Skipping unknown grant\n")
            continue

    return

def handle_zksync_ingestion(profile, network, identifier, do_write):
    # Get history of transfers from this user's zkSync address using the zkSync API: https://zksync.io/api/v0.1.html#account-history
    user_address = identifier
    base_url = 'https://rinkeby-api.zksync.io/api/v0.1' if network == 'rinkeby' else 'https://api.zksync.io/api/v0.1'
    r = requests.get(
        f"{base_url}/account/{user_address}/history/older_than")  # gets last 100 zkSync transactions
    r.raise_for_status()
    transactions = r.json()  # array of zkSync transactions

    # Paginate if required. API returns last 100 transactions by default, so paginate if response length was 100
    if len(transactions) == 100:
        max_length = 500  # only paginate until a max of most recent 500 transactions or no transaction are left
        last_tx_id = transactions[-1]["tx_id"]
        while len(transactions) < max_length:
            r = requests.get(
                f"{base_url}/account/{user_address}/history/older_than?tx_id={last_tx_id}")  # gets next 100 zkSync transactions
            r.raise_for_status()
            new_transactions = r.json()
            if (len(new_transactions) == 0):
                break
            transactions.extend(new_transactions)  # append to array
            last_tx_id = transactions[-1]["tx_id"]

    for transaction in transactions:
        # Skip if this is not a transfer (can be Deposit, ChangePubKey, etc.)
        if transaction["tx"]["type"] != "Transfer":
            continue

        # Extract contribution parameters from the JSON
        symbol = transaction["tx"]["token"]
        value = transaction["tx"]["amount"]

        try:
            token = Token.objects.filter(
                network=network,
                symbol=transaction["tx"]["token"],
                approved=True
            ).first().to_dict
        except Exception as e:
            logger.exception(e)
            logger.warning(f"{value_adjusted}{symbol} => {to}, Unknown Token ")
            logger.warning("Skipping transaction with unknown token\n")
            continue

        decimals = token["decimals"]
        symbol = token["name"]
        value_adjusted = int(value) / 10 ** int(decimals)
        to = transaction["tx"]["to"]

        print(f"transfer from: {user_address} to: {to}")

        # Find the grant
        try:
            grant = Grant.objects.filter(admin_address__iexact=to).order_by(
                "-positive_round_contributor_count").first()
            if not grant:
                logger.warning(f"{value_adjusted}{symbol}  => {to}, Unknown Grant ")
                logger.warning("Skipping unknown grant\n")
                continue
            logger.info(f"{value_adjusted}{symbol}  => {to}, {grant} ")
        except Exception as e:
            logger.exception(e)
            logger.warning(f"{value_adjusted}{symbol}  => {to}, Unknown Grant ")
            logger.warning("Skipping unknown grant\n")
            continue

        if do_write:
            txid = transaction['hash']
            created_on = dateutil.parser.parse(transaction['created_at'])
            save_data(profile, txid, network, created_on, symbol, value_adjusted, grant, 'eth_zksync',
                        user_address)
