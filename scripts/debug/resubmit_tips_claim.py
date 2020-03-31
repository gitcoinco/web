from dashboard.models import Tip
from dashboard.utils import get_web3
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from web3 import Web3

ETH_ADDRESS="0x0000000000000000000000000000000000000000"
tip_id = options
tip = Tip.object.get(tip_id)
w3 = get_web3(tip.network)
tip_contract_address = tip.tokenAddress

nonce = w3.eth.getTransactionCount(tip.metadata['address'])
# TODO compute private key with shamir
shamir_computed_key = "0x0"
tx = False
if tip_contract_address is not ETH_ADDRESS :
    to_address = tip.receive_address
    price_finney = 1.00 #calculate best price given the data needs
    token_abi = [{'inputs': [], 'constant': True, 'name': 'mintingFinished', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [], 'constant': True, 'name': 'name', 'outputs': [{'type': 'string', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_spender'}, {'type': 'uint256', 'name': '_value'}], 'constant': False, 'name': 'approve', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [], 'constant': True, 'name': 'totalSupply', 'outputs': [{'type': 'uint256', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_from'}, {'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_value'}], 'constant': False, 'name': 'transferFrom', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [], 'constant': True, 'name': 'decimals', 'outputs': [{'type': 'uint8', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_amount'}], 'constant': False, 'name': 'mint', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [], 'constant': True, 'name': 'version', 'outputs': [{'type': 'string', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_owner'}], 'constant': True, 'name': 'balanceOf', 'outputs': [{'type': 'uint256', 'name': 'balance'}], 'payable': False, 'type': 'function'}, {'inputs': [], 'constant': False, 'name': 'finishMinting', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [], 'constant': True, 'name': 'owner', 'outputs': [{'type': 'address', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [], 'constant': True, 'name': 'symbol', 'outputs': [{'type': 'string', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_to'}, {'type': 'uint256', 'name': '_value'}], 'constant': False, 'name': 'transfer', 'outputs': [{'type': 'bool', 'name': ''}], 'payable': False, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': '_owner'}, {'type': 'address', 'name': '_spender'}], 'constant': True, 'name': 'allowance', 'outputs': [{'type': 'uint256', 'name': 'remaining'}], 'payable': False, 'type': 'function'}, {'inputs': [{'type': 'address', 'name': 'newOwner'}], 'constant': False, 'name': 'transferOwnership', 'outputs': [], 'payable': False, 'type': 'function'}, {'payable': False, 'type': 'fallback'}, {'inputs': [{'indexed': True, 'type': 'address', 'name': 'to'}, {'indexed': False, 'type': 'uint256', 'name': 'amount'}], 'type': 'event', 'name': 'Mint', 'anonymous': False}, {'inputs': [], 'type': 'event', 'name': 'MintFinished', 'anonymous': False}, {'inputs': [{'indexed': True, 'type': 'address', 'name': 'owner'}, {'indexed': True, 'type': 'address', 'name': 'spender'}, {'indexed': False, 'type': 'uint256', 'name': 'value'}], 'type': 'event', 'name': 'Approval', 'anonymous': False}, {'inputs': [{'indexed': True, 'type': 'address', 'name': 'from'}, {'indexed': True, 'type': 'address', 'name': 'to'}, {'indexed': False, 'type': 'uint256', 'name': 'value'}], 'type': 'event', 'name': 'Transfer', 'anonymous': False}]
    contract = w3.eth.contract(Web3.toChecksumAddress(tip_contract_address), abi=token_abi)
    tx = contract.functions.transfer(to_address, tip.amount_in_wei).buildTransaction({
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(2) * 10**9),
        'value': int(price_finney / 1000.0 * 10**18)
    })

else :
    price_finney = 1.00 #calculate best price given the data needs

    tx = w3.buildTransaction({
        'nonce': nonce,
        'gas': 22000,
        'gasPrice': int(recommend_min_gas_price_to_confirm_in_time(2) * 10 ** 9),
        'value': int(price_finney / 1000.0 * 10 ** 18)
    })

signed = w3.eth.account.signTransaction(tx, shamir_computed_key)

try:
    txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
    nonce += 1
    print(f'Re issued Tip {tip_id} tx {nonce}')
    tip.txid = txid
    tip.save()

except Exception as e:
    print(e)
    error = "Could not redeem your kudos.  Please try again soon."
