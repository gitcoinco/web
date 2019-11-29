from django.conf import settings

from app.redis_service import RedisService
from celery import app, task
from celery.utils.log import get_task_logger

from mattermostdriver import Driver

mm_driver = Driver({
    'url': settings.CHAT_URL,
    'login_id': settings.CHAT_DRIVER_USER,
    'password': settings.CHAT_DRIVER_PASS,
    'token': settings.CHAT_DRIVER_TOKEN
})

mm_driver.login()

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2


@app.shared_task(bind=True, max_retries=3)
def create_channel(self, opts, retry: bool = True) -> None:
    """
    :param opts:
    :param retry:
    :return:
    """

    with redis.lock("tasks:create_channel:%s" % opts['channel_name'], timeout=LOCK_TIMEOUT):

        try:
            mm_driver.channels.create_channel(options={
                'team_id': opts['team_id'],
                'name': opts['channel_name'],
                'display_name': opts['channel_display_name'],
                'type': 'O'
            })
        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(30)
        except Exception as e:
            logger.error(str(e))
