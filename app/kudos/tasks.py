# -*- coding: utf-8 -*-

import time

from django.conf import settings

from app.services import RedisService
from celery import app
from celery.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded
from celery.utils.log import get_task_logger
from dashboard.utils import get_web3, has_tx_mined
from gas.utils import recommend_min_gas_price_to_confirm_in_time
from hexbytes import HexBytes
from kudos.models import KudosTransfer, TokenRequest
from kudos.utils import kudos_abi
from marketing.mails import notify_kudos_minted, send_mail
from web3 import Web3

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2
delay_if_gas_prices_gt_mint = 150

@app.shared_task(bind=True, max_retries=10)
def mint_token_request(self, token_req_id, send_notif_email=True, retry=False):
    """
    :param self:
    :param token_req_id:
    :return:
    """
    #with redis.lock("tasks:all_kudos_requests", timeout=LOCK_TIMEOUT):
    if True:
        with redis.lock("tasks:token_req_id:%s" % token_req_id, timeout=LOCK_TIMEOUT):
            from kudos.management.commands.mint_all_kudos import sync_latest
            from gas.utils import recommend_min_gas_price_to_confirm_in_time
            from dashboard.utils import has_tx_mined
            obj = TokenRequest.objects.get(pk=token_req_id)
            multiplier = 1
            gas_price = int(float(recommend_min_gas_price_to_confirm_in_time(1)) * multiplier)
            if gas_price > delay_if_gas_prices_gt_mint and self.request.retries < self.max_retries:
                self.retry(countdown=120)
                return
            if obj.gas_price_overide:
                gas_price = obj.gas_price_overide
            tx_id = obj.mint(gas_price)
            if tx_id:
                while not has_tx_mined(tx_id, obj.network):
                    time.sleep(1)
                for i in range(0, 5):
                    sync_latest(i, network=obj.network)
                if send_notif_email:
                    notify_kudos_minted(obj)
            else:
                self.retry(countdown=(30 * (self.request.retries + 1)))


@app.shared_task(bind=True, max_retries=10, rate_limit="60/h")
def redeem_bulk_kudos(self, kt_id, delay_if_gas_prices_gt_redeem= 50, override_gas_price=None, send_notif_email=False, override_lock_timeout=LOCK_TIMEOUT, retry=False):
    """
    :param self:
    :param kt_id:
    :return:
    """
    try:
        with redis.lock("tasks:all_kudos_requests", timeout=LOCK_TIMEOUT):
            with redis.lock("tasks:redeem_bulk_kudos:%s" % kt_id, timeout=override_lock_timeout):
                multiplier = 1
                gas_price = int(float(recommend_min_gas_price_to_confirm_in_time(1)) * multiplier * 10**9)
                if network == 'xdai':
                    gas_price = 1 * 10**9

                if override_gas_price:
                    gas_price = override_gas_price
                if gas_price > delay_if_gas_prices_gt_redeem:
                    # do not retry is gas prices are too high
                    # TODO: revisit this when gas prices go down
                    # self.retry(countdown=60*10)
                    return

                if override_gas_price:
                    gas_price = override_gas_price * 10 ** 9
                obj = KudosTransfer.objects.get(pk=kt_id)
                w3 = get_web3(obj.network)
                token = obj.kudos_token_cloned_from
                if token.owner_address.lower() != '0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F'.lower():
                    raise Exception("kudos isnt owned by Gitcoin; cowardly refusing to spend Gitcoin's ETH minting it")
                kudos_owner_address = settings.KUDOS_OWNER_ACCOUNT
                kudos_owner_address = Web3.toChecksumAddress(kudos_owner_address)
                contract_addr = settings.KUDOS_CONTRACT_MAINNET
                if obj.network == 'xdai':
                    contract_addr = settings.KUDOS_CONTRACT_XDAI
                if obj.network == 'rinkeby':
                    contract_addr = settings.KUDOS_CONTRACT_RINKEBY
                kudos_contract_address = Web3.toChecksumAddress(contract_addr)
                contract = w3.eth.contract(Web3.toChecksumAddress(kudos_contract_address), abi=kudos_abi())
                nonce = w3.eth.getTransactionCount(kudos_owner_address)
                tx = contract.functions.clone(Web3.toChecksumAddress(obj.receive_address), token.token_id, 1).buildTransaction({
                    'nonce': nonce,
                    'gas': 500000,
                    'gasPrice': gas_price,
                    'value': int(token.price_finney / 1000.0 * 10**18),
                })
                private_key = settings.KUDOS_PRIVATE_KEY
                signed = w3.eth.account.signTransaction(tx, private_key)
                obj.txid = w3.eth.sendRawTransaction(signed.rawTransaction).hex()
                obj.receive_txid = obj.txid
                obj.save()
                while not has_tx_mined(obj.txid, obj.network):
                    time.sleep(1)
                pass
                if send_notif_email:
                    from_email = 'kevin@gitcoin.co'
                    from_name = 'Kevin @ Gitcoin'
                    _to_email = obj.recipient_profile.email
                    subject = f"Your '{obj.kudos_token_cloned_from.name}' Kudos has been minted 🌈"
                    block_url = f'https://etherscan.io/tx/{obj.txid}'
                    if obj.network == 'xdai':
                        block_url = f'https://blockscout.com/poa/xdai/tx/{obj.txid}/internal-transactions'
                    body = f'''
    Hello @{obj.recipient_profile.handle},

    Back on {obj.created_on} you minted a '{obj.kudos_token_cloned_from.name}' Kudos, but the Ethereum network's gas fees were too high for us to mint it on-chain.

    We're writing with good news.  The gas prices on Ethereum have come down, and we are have now minted your token.  You can now see the Kudos in your gitcoin profile ( https://gitcoin.co/{obj.recipient_profile.handle} ) or any blockchain wallet that connects to the {obj.network} network ( {block_url} ).  HOORAY!

    Party on,
    Kevin + the Gitcoin team
                    '''
                    send_mail(from_email, _to_email, subject, body, from_name=from_name)
    except (SoftTimeLimitExceeded, TimeLimitExceeded):
        print('max timeout for bulk kudos redeem exceeded ... giving up!')
    except Exception as e:
        print(e)
        if self.request.retries < self.max_retries:
            self.retry(countdown=(30 * (self.request.retries + 1)))
        else:
            print("max retries for bulk kudos redeem exceeded ... giving up!")
