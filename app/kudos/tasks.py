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
from marketing.mails import notify_kudos_minted
from web3 import Web3

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2
delay_if_gas_prices_gt_redeem = 50
delay_if_gas_prices_gt_mint = 150

@app.shared_task(bind=True, max_retries=10)
def mint_token_request(self, token_req_id, retry=False):
    """
    :param self:
    :param token_req_id:
    :return:
    """
    with redis.lock("tasks:all_kudos_requests", timeout=LOCK_TIMEOUT):
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
                sync_latest(0)
                sync_latest(1)
                sync_latest(2)
                sync_latest(3)
                notify_kudos_minted(obj)
            else:
                self.retry(countdown=(30 * (self.request.retries + 1)))


@app.shared_task(bind=True, max_retries=10, rate_limit="60/h")
def redeem_bulk_kudos(self, kt_id, retry=False):
    """
    :param self:
    :param kt_id:
    :return:
    """
    try:
        with redis.lock("tasks:redeem_bulk_kudos:%s" % kt_id, timeout=LOCK_TIMEOUT):
            multiplier = 1
            # high gas prices, 5 hour gas limit - DL
            gas_price = int(float(recommend_min_gas_price_to_confirm_in_time(300)) * multiplier)
            if gas_price > delay_if_gas_prices_gt_redeem:
                # do not retry is gas prices are too high
                # TODO: revisit this when gas prices go down
                # self.retry(countdown=60*10)
                return

            obj = KudosTransfer.objects.get(pk=kt_id)
            w3 = get_web3(obj.network)
            token = obj.kudos_token_cloned_from
            if token.owner_address.lower() != '0x6239FF1040E412491557a7a02b2CBcC5aE85dc8F'.lower():
                raise Exception("kudos isnt owned by Gitcoin; cowardly refusing to spend Gitcoin's ETH minting it")
            kudos_owner_address = settings.KUDOS_OWNER_ACCOUNT
            kudos_owner_address = Web3.toChecksumAddress(kudos_owner_address)
            kudos_contract_address = Web3.toChecksumAddress(settings.KUDOS_CONTRACT_MAINNET)
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
    except (SoftTimeLimitExceeded, TimeLimitExceeded):
        print('max timeout for bulk kudos redeem exceeded ... giving up!')
    except Exception as e:
        print(e)
        if self.request.retries < self.max_retries:
            self.retry(countdown=(30 * (self.request.retries + 1)))
        else:
            print("max retries for bulk kudos redeem exceeded ... giving up!")
