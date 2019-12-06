from app.redis_service import RedisService
from celery import app
from celery.utils.log import get_task_logger
from kudos.models import TokenRequest

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2


@app.shared_task(bind=True, max_retries=3)
def mint_token_request(self, token_req_id, retry=False):
    """
    :param self:
    :param token_req_id:
    :return:
    """
    with redis.lock("tasks:token_req_id:%s" % token_req_id, timeout=LOCK_TIMEOUT):
        from kudos.management.commands.mint_all_kudos import sync_latest
        obj = TokenRequest.objects.get(pk=token_req_id)
        tx_id = obj.mint()
        if tx_id:
            sync_latest(0)
            sync_latest(1)
            sync_latest(2)
            sync_latest(3)
        else:
            self.retry(30)
