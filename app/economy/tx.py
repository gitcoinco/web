from decimal import Decimal

from django.conf import settings
from django.utils import timezone

from dashboard.abi import erc20_abi
from economy.models import Token
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput


def maybeprint(_str, _str2=None, _str3=None):
    pass
    #print(_str)

## web3 Exceptions
class TransactionNotFound(Exception):
    """
    Raised when a tx hash used to lookup a tx in a jsonrpc call cannot be found.
    """
    pass

# scrapper settings
ethurl = "https://etherscan.io/tx/"
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
headers = {'User-Agent': user_agent}


# ERC20 / ERC721 tokens
# Transfer(address,address,uint256)
# Deposit(address, uint256)
# Approval(address,address, uint256)
SEARCH_METHOD_TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
SEARCH_METHOD_DEPOSIT = '0xaef05ca429cf234724843763035496132d10808feeac94ee79441c83b6dd519a'
SEARCH_METHOD_APPROVAL = '0x7c3bc83eb61feb549a19180bb8de62c55c110922b2a80e511547cf8deda5b25a'

PROVIDER = "wss://mainnet.infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
w3 = Web3(Web3.WebsocketProvider(PROVIDER))
check_transaction = lambda txid: w3.eth.getTransaction(txid)
check_amount = lambda amount: int(amount[75:], 16) if len(amount) == 138 else print (f"{bcolors.FAIL}{bcolors.UNDERLINE} {index_transaction} txid: {transaction_tax[:10]} -> status: 0 False - amount was off by 0.001 {bcolors.ENDC}")
check_token = lambda token_address: len(token_address) == 42
check_contract = lambda token_address, abi : w3.eth.contract(token_address, abi=abi)
check_event_transfer =  lambda contract_address, search, txid : w3.eth.filter({ "address": contract_address, "topics": [search, txid]})
get_decimals = lambda contract : int(contract.functions.decimals().call())

bulk_checkout_abi = '[{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":false,"internalType":"address","name":"dest","type":"address"},{"indexed":true,"internalType":"address","name":"donor","type":"address"}],"name":"DonationSent","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Paused","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"token","type":"address"},{"indexed":true,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":true,"internalType":"address","name":"dest","type":"address"}],"name":"TokenWithdrawn","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"account","type":"address"}],"name":"Unpaused","type":"event"},{"inputs":[{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address payable","name":"dest","type":"address"}],"internalType":"struct BulkCheckout.Donation[]","name":"_donations","type":"tuple[]"}],"name":"donate","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"pause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"paused","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"unpause","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"_dest","type":"address"}],"name":"withdrawEther","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_tokenAddress","type":"address"},{"internalType":"address","name":"_dest","type":"address"}],"name":"withdrawToken","outputs":[],"stateMutability":"nonpayable","type":"function"}]'

def getReplacedTX(tx):
    from economy.models import TXUpdate
    txus = TXUpdate.objects.filter(body__hash__iexact=tx)
    for txu in txus:
        replace_hash = txu.body.get('replaceHash')
        if replace_hash:
            return replace_hash
    return None


def transaction_status(transaction, txid):
    """This function is core for check grants transaction list"""
    try:
        contract_address = transaction.to
        contract = check_contract(contract_address, erc20_abi)
        approve_event = check_event_transfer(contract.address, SEARCH_METHOD_APPROVAL, txid)
        transfer_event = check_event_transfer(contract.address, SEARCH_METHOD_TRANSFER, txid)
        deposit_event = check_event_transfer(contract.address, SEARCH_METHOD_DEPOSIT, txid)
        get_symbol = lambda contract: str(contract.functions.symbol().call())
        decimals = get_decimals(contract)
        contract_value = contract.decode_function_input(transaction.input)[1]['_value']
        contract_symbol = get_symbol(contract)
        human_readable_value = Decimal(int(contract_value)) / Decimal(10 ** decimals) if decimals else None
        transfers_web3py = get_token_recipient_senders(recipient_address, dai_address)

        if (transfer_event or deposit_event):
            return {
                'token_amount': human_readable_value,
                'to': '',
                'token_name': contract_symbol,
            }
    except BadFunctionCallOutput as e:
        pass
    except Exception as e:
        maybeprint(89, e)


def get_token(token_symbol, network, chain='std'):
    """
    For a given token symbol and amount, returns the token's details.
    For mainnet checkout in ETH, we change the token address to 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE
    For polygon checkout in MATIC, we change the token address to 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE
    since that's the address BulkCheckout uses to represent ETH (default here is the zero address)
    """

    network_id = 1

    if chain == 'polygon':
        if network == 'mainnet':
            network_id = 137
        else:
            network_id = 80001

    token = Token.objects.filter(
        network=network, network_id=network_id, symbol=token_symbol, approved=True).first().to_dict

    if (
        (token_symbol == 'ETH' and chain == 'std') or
        (token_symbol == 'MATIC' and chain == 'polygon')
    ):
        token['addr'] = '0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE'

    return token


def parse_token_amount(token_symbol, amount, network, chain='std'):
    """
    For a given token symbol and amount, returns the integer version in "wei", i.e. the integer
    form based on the token's number of decimals
    """
    token = get_token(token_symbol, network, chain)
    decimals = token['decimals']
    parsed_amount = int(amount * 10 ** decimals)
    return parsed_amount


def check_for_replaced_tx(tx_hash, network, datetime=None, chain='std'):
    """
    Get status of the provided transaction hash, and look for a replacement transaction hash. If a
    replacement exists, return the status and hash of the new transaction
    """
    from dashboard.utils import get_tx_status

    if not datetime:
        datetime = timezone.now()

    status, timestamp = get_tx_status(tx_hash, network, datetime, chain=chain)
    if status in ['pending', 'dropped', 'unknown', '']:
        new_tx = getReplacedTX(tx_hash)
        if new_tx:
            tx_hash = new_tx
            status, timestamp = get_tx_status(tx_hash, network, datetime)

    return tx_hash, status, timestamp


def grants_transaction_validator(contribution, w3, chain='std'):
    """
    This function is used to validate contributions sent on L1 & Polygon L2 through the BulkCheckout contract.
    This contract can be found here:
      - On GitHub: https://github.com/gitcoinco/BulkTransactions/blob/master/contracts/BulkCheckout.sol
      - On mainnet: https://etherscan.io/address/0x7d655c57f71464b6f83811c55d84009cd9f5221c
      - On Polygon mainnet: https://polygonscan.com/address/0xb99080b9407436eBb2b8Fe56D45fFA47E9bb8877
      - On Polygon testnet: https://mumbai.polygonscan.com/address/0x3E2849E2A489C8fE47F52847c42aF2E8A82B9973

    To facilitate testing on Rinkeby and Mumbai, we pass in a web3 instance instead of using the mainnet
    instance defined at the top of this file
    """

    # Get specific info about this contribution that we use later
    tx_hash = contribution.split_tx_id
    network = contribution.subscription.network

    if network == 'mainnet' and chain == 'polygon':
        bulk_checkout_address = '0xb99080b9407436eBb2b8Fe56D45fFA47E9bb8877'
    elif network == 'testnet' and chain == 'polygon':
        bulk_checkout_address = '0x3E2849E2A489C8fE47F52847c42aF2E8A82B9973'
    else:
        bulk_checkout_address = '0x7d655c57f71464B6f83811C55D84009Cd9f5221C'

    # Get bulk checkout contract instance
    bulk_checkout_contract = w3.eth.contract(address=bulk_checkout_address, abi=bulk_checkout_abi)

    # Response that calling function uses to set fields on Contribution. Set the defaults here
    response = {
        # We set `passed` to `True` if matching transfer is found for this contribution. The
        # `comment` field is used to provide details when false
        'validation': {
            'passed': False,
            'comment': 'Default'
        },
        # Array of addresses where funds were intially sourced from. This is used to detect someone
        # funding many addresses from a single address. This functionality is currently not
        # implemented in `grants_transaction_validator()` so for now we assume the originator is
        # msg.sender. If this needs to be implemented, take a look at this function in older
        # commits to find the logic used
        'originator': [ '' ],
        # Once `tx_cleared` is true, the validator is not run again for this contribution
        'tx_cleared': False,
        # True if the checkout transaction was mined
        'split_tx_confirmed': False
    }

    # Return if tx_hash is not valid
    if not tx_hash or len(tx_hash) != 66:
        # Set to True so this doesn't run again, since there's no transaction hash to check
        response['tx_cleared'] = True
        response['validation']['comment'] = 'Invalid transaction hash in split_tx_id'
        return response

    # Check for dropped and replaced txn
    tx_hash, status, _ = check_for_replaced_tx(tx_hash, network, chain=chain)

    # If transaction was successful, continue to validate it
    if status == 'success':
        # Transaction was successful so we know it cleared
        response['tx_cleared'] = True
        response['split_tx_confirmed'] = True

        # Get the receipt to parse parameters
        receipt = w3.eth.getTransactionReceipt(tx_hash)

        # Validator currently assumes msg.sender == originator as described above
        response['originator'] = [ receipt['from'] ]

        # Parse receipt logs to look for expected transfer info. We don't need to distinguish
        # between ETH and token transfers, and don't need to look at any other receipt parameters,
        # because all contributions are emitted as an event
        receipt = w3.eth.getTransactionReceipt(tx_hash)
        parsed_logs = bulk_checkout_contract.events.DonationSent().processReceipt(receipt)

        # Return if no donation logs were found
        if (len(parsed_logs) == 0):
            response['validation']['comment'] = 'No DonationSent events found in this BulkCheckout transaction'
            return response

        # Parse out the transfer details we are looking to find in the event logs
        token_symbol = contribution.normalized_data['token_symbol']
        expected_recipient = contribution.normalized_data['admin_address'].lower()
        expected_token = get_token(token_symbol, network, chain)['addr'].lower() # we compare by token address
        amount_to_use = contribution.subscription.amount_per_period

        expected_amount = parse_token_amount(
            token_symbol=token_symbol,
            amount=amount_to_use,
            network=network,
            chain=chain
        )
        transfer_tolerance = 0.05 # use a 5% tolerance when checking amounts to account for floating point error
        expected_amount_min = int(expected_amount * (1 - transfer_tolerance))
        expected_amount_max = int(expected_amount * (1 + transfer_tolerance))

        # Loop through each event to find one that matches
        for event in parsed_logs:
            is_correct_recipient = event['args']['dest'].lower() == expected_recipient
            is_correct_token = event['args']['token'].lower() == expected_token

            transfer_amount = event['args']['amount']
            is_correct_amount = transfer_amount >= expected_amount_min and transfer_amount <= expected_amount_max

            # if is_correct_recipient:
            #     print('==========================')
            #     print(f"subscription {contribution.subscription.amount_per_period_minus_gas_price}")
            #     print(f"contribution.subscription.amount_per_period  {contribution.subscription.amount_per_period }")
            #     print(f"contribution.subscription.amount_per_period_minus_gas_price { contribution.subscription.amount_per_period_minus_gas_price}")
            #     print(f"paid to gitcoin  {float(contribution.subscription.amount_per_period) - float(contribution.subscription.amount_per_period_minus_gas_price) } ")

            #     print(f"tx_hash: {tx_hash}")
            #     print(f"amount_to_use: {amount_to_use}")
            #     print(f"expected_amount: {expected_amount}")
            #     print(f"Expected amount range: {expected_amount_min} - {expected_amount_max}")
            #     print(f"transfer_amount : {transfer_amount}")
            #     print(f"is_correct_amount: {is_correct_amount}")

            #     print(f"expected_token: {expected_token}")
            #     print(f"token from event: {event['args']['token'].lower()}")
            #     print(f"is_correct_token: {is_correct_token}")

            #     print(f"expected_recipient: {expected_recipient}")
            #     print(f"recipient from event: {event['args']['dest'].lower()}")
            #     print(f"is_correct_recipient: {is_correct_recipient}")
            #     print('==========================')

            if is_correct_recipient and is_correct_token and is_correct_amount:
                # We found the event log corresponding to the contribution parameters
                response['validation']['passed'] = True
                response['validation']['comment'] = 'BulkCheckout. Success'
                return response

        # Transaction was successful, but the expected contribution was not included in the transaction
        response['validation']['comment'] = 'DonationSent event with expected recipient, amount, and token was not found in transaction logs'
        return response

    # If we get here, none of the above failure conditions have been met, so we try to find
    # more information about why it failed
    if status == 'pending':
        response['validation']['comment'] = 'Transaction is still pending'
        return response

    try:
        # Get receipt and set originator to msg.sender for reasons described above
        receipt = w3.eth.getTransactionReceipt(tx_hash) # equivalent to eth_getTransactionReceipt
        tx_info = w3.eth.getTransaction(tx_hash) # equivalent to eth_getTransactionByHash
        response['originator'] = [ receipt['from'] ]

        if receipt.status == 0:
            # Transaction was mined but it failed, try to find out why
            gas_limit = tx_info['gas']
            gas_used = receipt['gasUsed']
            if gas_limit == gas_used:
                response['tx_cleared'] = True
                response['split_tx_confirmed'] = True
                response['validation']['comment'] = 'Transaction failed. Out of gas'
                return response

            if gas_used > 0.99 * gas_limit:
                # Some out of gas failures don't use all gas, e.g. https://etherscan.io/tx/0xac37f5bc0e9b75dd0f296b8569f72181a066458b9bee1bbed088ec2298fb4344
                response['tx_cleared'] = True
                response['split_tx_confirmed'] = True
                response['validation']['comment'] = 'Transaction failed. Likely out of gas. Check Etherscan or Tenderly for more details'
                return response

            response['tx_cleared'] = True
            response['split_tx_confirmed'] = True
            response['validation']['comment'] = 'Transaction failed. Unknown reason. See Etherscan or Tenderly for more details'
            return response

        # If here, transaction was successful. This code block should never execute because it means
        # the transaction was successful but for some unknown reason it was not parsed above
        raise Exception('Unknown transaction validation flow 1')

    except w3.exceptions.TransactionNotFound:
        response['validation']['comment'] = 'Transaction receipt not found. Transaction may still be pending or was dropped'
        return response

    # We should always return before getting here. If we don't, above parsing logic should be fixed
    raise Exception('Unknown transaction validation flow 2')


def trim_null_address(address):
    if address == '0x0000000000000000000000000000000000000000':
        return '0x0'
    else:
        return address


def get_token_recipient_senders(recipient_address, token_address):
    PROVIDER = "wss://mainnet.infura.io/ws/v3/" + settings.INFURA_V3_PROJECT_ID
    w3 = Web3(Web3.WebsocketProvider(PROVIDER))
    contract = w3.eth.contract(
        address=token_address,
        abi=erc20_abi,
    )

    balance = contract.functions.balanceOf(recipient_address).call()

    transfers = contract.events.Transfer.getLogs(
        fromBlock=0,
        toBlock="latest",
        argument_filters={"to": recipient_address})

    return [
        trim_null_address(transfer.args['from'])
        for transfer in transfers
    ]


auth = settings.ALETHIO_KEY
headers = {'Authorization': f'Bearer {auth}'}
validation_threshold_pct = 0.05
validation_threshold_total = 0.05
