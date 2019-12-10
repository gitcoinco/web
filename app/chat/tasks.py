from django.conf import settings

from app.redis_service import RedisService
from celery import app, group
from dashboard.models import Profile
from celery.utils.log import get_task_logger
from mattermostdriver import Driver

mm_driver = Driver({
    'url': settings.CHAT_URL,
    'port': 443,
    'token': settings.CHAT_DRIVER_TOKEN
})

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
        mm_driver.login()

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


@app.shared_task(bind=True, max_retries=0)
def sync_gitcoin_users_to_chat(self, invite_token=None, retry: bool = False) -> None:
    """
    :param opts:
    :param retry:
    :return:
    """

    with redis.lock("tasks:sync_gitcoin_users_to_chat", timeout=60 * 10):

        try:
            mm_driver.login()

            users = Profile.objects.filter(user__is_active=True).prefetch_related('user')

            tasks = []

            for profile in users:
                # if profile.chat_id is None:
                print(profile)
                tasks.append(create_user.si(options={
                    "email": profile.user.email,
                    "username": profile.handle,
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "nickname": "string",
                    "auth_data": profile.user.id,
                    "auth_service": "gitcoin",
                    "locale": "en",
                    "props": {},
                    "notify_props": {
                        "email": False if should_suppress_notification_email(profile.user.email, 'chat') else True
                    }
                }, params={
                    "iid": invite_token if invite_token else ""
                }))
            print(tasks)
            job = group(tasks)

            result = job.apply_async()

            print(result.ready())

            print(result.successful())

            print(result.get())

        except ConnectionError as exec:
            print(str(exec))
            self.retry(30)
        except Exception as e:
            logger.error(str(e))


@app.shared_task(bind=True, max_retries=1)
def create_user(self, options, params, retry: bool = True):
    with redis.lock("tasks:create_user:%s" % options['username'], timeout=LOCK_TIMEOUT):
        mm_driver.login()

        try:
            create_user_response = mm_driver.users.create_user(options=options, params=params)

            return create_user_response
        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(30)
        except Exception as e:
            logger.error(str(e))
            return None


@app.shared_task(bind=True, max_retries=3)
def update_user(self, user, update_opts, retry: bool = True) -> None:
    """
    :param self:
    :param user:
    :param update_opts:
    :param retry:
    :return: None
    """

    if update_opts is None:
        return

    with redis.lock("tasks:update_user:%s" % user.profile.handle, timeout=LOCK_TIMEOUT):
        mm_driver.login()

        try:
            if user.profile.chat_id is None:
                chat_user = mm_driver.users.get_user_by_username(user.profile.handle)
                if chat_user is None:
                    raise ValueError(f'chat_user id is None for {user.profile.handle}')
                user.profile.chat_id = chat_user.id
                user.profile.save()

            mm_driver.users.update_user(user.chat_id, options=update_opts)
        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(30)
        except Exception as e:
            logger.error(str(e))
