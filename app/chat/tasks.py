from django.conf import settings

from app.redis_service import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from dashboard.models import Bounty, Profile
from mattermostdriver import Driver
from mattermostdriver.exceptions import ResourceNotFound

logger = get_task_logger(__name__)

redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2

driver_opts = {
    'scheme': 'https' if settings.CHAT_PORT == 443 else 'http',
    'url': settings.CHAT_URL,
    'port': settings.CHAT_PORT,
    'token': settings.CHAT_DRIVER_TOKEN
}

chat_driver = Driver(driver_opts)


def get_driver():
    chat_driver.login()
    return chat_driver


@app.shared_task(bind=True, max_retries=3)
def create_channel(self, options, bounty_id = None, retry: bool = True) -> None:
    """
    :param options:
    :param retry:
    :return:
    """
    with redis.lock("tasks:create_channel:%s" % options['channel_name'], timeout=LOCK_TIMEOUT):

        chat_driver.login()
        try:
            channel_lookup = chat_driver.channels.get_channel_by_name(
                options['team_id'],
                options['channel_name']
            )
            if bounty_id:
                active_bounty = Bounty.objects.get(id=bounty_id)
                active_bounty.chat_channel_id = channel_lookup['id']
                active_bounty.save()
            return channel_lookup
        except ResourceNotFound as RNF:
            new_channel = chat_driver.channels.create_channel(options={
                'team_id': options['team_id'],
                'name': options['channel_name'],
                'display_name': options['channel_display_name'],
                'type': 'O'
            })
            if bounty_id:
                active_bounty = Bounty.objects.get(id=bounty_id)
                active_bounty.chat_channel_id = new_channel['id']
                active_bounty.save()
            return new_channel
        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(30)
        except Exception as e:
            print("we got an exception when creating a channel")
            logger.error(str(e))


@app.shared_task(bind=True, max_retries=3)
def add_to_channel(self, channel_details, chat_user_ids, retry: bool = True) -> None:
    """
    :param channel_details:
    :param retry:
    :return:
    """
    chat_driver.login()
    try:
        for chat_id in chat_user_ids:
            if chat_id:
                response = chat_driver.channels.add_user(channel_details['id'], options={
                    'user_id': chat_id
                })
    except ConnectionError as exc:
        logger.info(str(exc))
        logger.info("Retrying connection")
        self.retry(30)
    except Exception as e:
        logger.error(str(e))


@app.shared_task(bind=True, max_retries=1)
def create_user(self, options, params, retry: bool = True):
    with redis.lock("tasks:create_user:%s" % options['username'], timeout=LOCK_TIMEOUT):
        try:
            chat_driver.login()
            create_user_response = chat_driver.users.create_user(
                options=options,
                params=params
            )
            return create_user_response
        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(30)
        except Exception as e:
            logger.error(str(e))
            return None


@app.shared_task(bind=True, max_retries=3)
def update_user(self, query_opts, update_opts, retry: bool = True) -> None:
    """
    :param self:
    :param query_opts:
    :param update_opts:
    :param retry:
    :return: None
    """

    if update_opts is None:
        return

    with redis.lock("tasks:update_user:%s" % query_opts['handle'], timeout=LOCK_TIMEOUT):

        try:

            if query_opts['chat_id'] is None:
                try:

                    chat_user = chat_driver.users.get_user_by_username(query_opts['handle'])
                    chat_id = chat_user['id']
                except Exception as e:
                    logger.info(f"Unable to find chat user for {query_opts['handle']}")
            else:
                chat_id = query_opts['chat_id']

            user_profile = Profile.objects.filter(handle=query_opts['handle'])
            user_profile.chat_id = chat_id
            user_profile.save()
            chat_driver.users.update_user(chat_id, options=update_opts)
        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(30)
        except Exception as e:
            logger.error(str(e))
