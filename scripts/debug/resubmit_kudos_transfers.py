import time

from django.conf import settings

from dashboard.utils import get_web3
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from dashboard.utils import has_tx_mined
from kudos.utils import kudos_abi
from web3 import Web3
from kudos.models import KudosTransfer
from django.db.models import Q

#setup
network = 'mainnet'
w3 = get_web3(network)
kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_MAINNET)
kudos_owner_address = Web3.toChecksumAddress(settings.KUDOS_OWNER_ACCOUNT)
nonce = w3.eth.getTransactionCount(kudos_owner_address)

# pk range to re-send
min_pk = 1684
max_pk = 1740
TIME_SLEEP = 1
username = 'sgcrypto1983'
gas_clear_within_mins = 1
gas_multiplier = 1.9

kts = KudosTransfer.objects.filter(pk__gte=min_pk, pk__lte=max_pk)
kts = KudosTransfer.objects.filter(username=username).filter(Q(tx_status='dropped') | Q(txid='pending_celery'))
print(kts.count())

for kt in kts:

    token_id = kt.kudos_token_cloned_from.token_id
    address = kt.receive_address
    price_finney = kt.kudos_token_cloned_from.price_finney

    contract = w3.eth.contract(Web3.toChecksumAddress(kudos_contract_address), abi=kudos_abi())
    tx = contract.functions.clone(address, token_id, 1).buildTransaction({
        'nonce': nonce,
        'gas': 500000,
        'gasPrice': int(gas_multiplier * float(recommend_min_gas_price_to_confirm_in_time(gas_clear_within_mins)) * 10**9),
        'value': int(price_finney / 1000.0 * 10**18),
    })

    signed = w3.eth.account.signTransaction(tx, settings.KUDOS_PRIVATE_KEY)

    try:
        txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
        nonce += 1
        print(f'sent tx {nonce}')
        kt.txid = txid
        kt.tx_status = 'pending'
        kt.save()

        while not has_tx_mined(txid, network):
            time.sleep(TIME_SLEEP)


    except Exception as e:
        print(e)
        error = "Could not redeem your kudos.  Please try again soon."
