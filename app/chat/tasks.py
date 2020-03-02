from app.redis_service import RedisService
from celery import app, group
from celery.utils.log import get_task_logger
from dashboard.models import HackathonEvent, HackathonRegistration, Bounty, Profile
import datetime
import logging

logger = logging.getLogger(__name__)
from django.conf import settings
from django.utils.text import slugify

from marketing.utils import should_suppress_notification_email
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


def create_channel_if_not_exists(channel_opts):
    try:
        chat_driver = get_driver()

        channel_lookup_response = chat_driver.channels.get_channel_by_name(
            channel_opts['team_id'], channel_opts['channel_name']
        )
        return False, channel_lookup_response

    except ResourceNotFound as RNF:
        try:
            result = create_channel.apply_async(args=[channel_opts])
            channel_id_response = result.get()

            if 'message' in channel_id_response:
                raise ValueError(channel_id_response['message'])

            return True, channel_id_response
        except Exception as e:
            logger.error(str(e))


def update_chat_notifications(profile, notification_key, status):
    query_opts = {}
    if profile.chat_id is not '' or profile.chat_id is not None:
        query_opts['chat_id'] = profile.chat_id
    else:
        query_opts['handle'] = profile.handle

    update_user.delay(query_opts=query_opts, update_opts={'notify_props': {notification_key: status}})


def associate_chat_to_profile(profile):
    if profile.chat_id is not '':
        return False, profile

    chat_driver = get_driver()
    try:

        current_chat_user = chat_driver.users.get_user_by_username(profile.handle)
        profile.chat_id = current_chat_user['id']
        profile.save()

        if profile.gitcoin_chat_access_token is not '':
            profile_access_token = chat_driver.users.get_user_access_token(profile.gitcoin_chat_access_token)
            profile.gitcoin_chat_access_token = profile_access_token['id']
        return False, current_chat_user
    except ResourceNotFound as RNF:
        if profile.chat_id is '':
            new_user_request = create_user.apply_async(args=[{
                "email": profile.user.email,
                "username": profile.handle,
                "first_name": profile.user.first_name,
                "last_name": profile.user.last_name,
                "nickname": profile.handle,
                "auth_data": f'{profile.user.id}',
                "auth_service": "gitcoin",
                "locale": "en",
                "props": {},
                "notify_props": {
                    "email": "false" if should_suppress_notification_email(profile.user.email, 'chat') else "true",
                    "push": "mention",
                    "desktop": "all",
                    "desktop_sound": "true",
                    "mention_keys": f'{profile.handle}, @{profile.handle}',
                    "channel": "true",
                    "first_name": "false"
                },
            }, {
                "tid": settings.GITCOIN_HACK_CHAT_TEAM_ID
            }])
            response = new_user_request.get()
            profile.chat_id = response['id']
            profile.save()
        else:
            try:
                profile_access_token = chat_driver.users.create_user_access_token(user_id=profile.chat_id, options={
                    'description': "Grants Gitcoin access to modify your account"})
                profile.gitcoin_chat_access_token = profile_access_token['id']
            except Exception as e:
                logger.error(str(e))

        return True, profile


def get_chat_url():
    chat_url = settings.CHAT_URL
    if settings.CHAT_PORT not in [80, 443]:
        chat_url = f'http://{settings.CHAT_URL}:{settings.CHAT_PORT}'
    else:
        chat_url = f'https://{chat_url}'
    return chat_url


def get_driver():
    chat_driver.login()
    return chat_driver


@app.shared_task(bind=True, max_retries=3)
def create_channel(self, options, bounty_id=None, retry: bool = True) -> None:
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
                'purpose': options['channel_purpose'] if options['channel_purpose'] else '',
                'header': options['channel_header'] if options['channel_header'] else '',
                'display_name': options['channel_display_name'],
                'type': options['channel_type'] or 'O'
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
def hackathon_chat_sync(self, hackathon_id: str, profile_handle: str = None, retry: bool = True) -> None:
    try:
        hackathon = HackathonEvent.objects.get(id=hackathon_id)
        channels_to_connect = []
        if not hackathon.chat_channel_id:
            created, channel_details = create_channel_if_not_exists({
                'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                'channel_display_name': f'general-{hackathon.slug}'[:60],
                'channel_name': f'general-{hackathon.name}'[:60]
            })
            hackathon.chat_channel_id = channel_details['id']
            hackathon.save()
        channels_to_connect.append(hackathon.chat_channel_id)
        regs_to_sync = HackathonRegistration.objects.filter(hackathon=hackathon)
        profiles_to_connect = []
        if profile_handle is None:
            for reg in regs_to_sync:
                if reg.registrant and not reg.registrant.chat_id:
                    created, reg.registrant = associate_chat_to_profile(reg.registrant)
                profiles_to_connect.append(reg.registrant.chat_id)
        else:
            profiles_to_connect = [profile_handle]

        for hack_sponsor in hackathon.sponsors.all():
            if not hack_sponsor.chat_channel_id:
                created, channel_details = create_channel_if_not_exists({
                    'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                    'channel_display_name': f'company-{slugify(hack_sponsor.sponsor.name)}'[:60],
                    'channel_name': f'company-{hack_sponsor.sponsor.name}'[:60]
                })
                hack_sponsor.chat_channel_id = channel_details['id']
                hack_sponsor.save()
            channels_to_connect.append(hack_sponsor.chat_channel_id)

        for channel_id in channels_to_connect:
            # how can we better store this
            current_channel_users = [member['id'] for member in
                                     chat_driver.channels.get_channel_members(channel_id)]
            profiles_to_connect = list(set(current_channel_users) | set(profiles_to_connect))
            if len(profiles_to_connect) > 0:
                add_to_channel.delay({'id': channel_id}, profiles_to_connect)

    except Exception as e:
        logger.info(f'No hackathon found for id: {hackathon_id}')
        logger.error(str(e))


@app.shared_task(bind=True, max_retries=3)
def add_to_channel(self, channel_details, chat_user_ids: list, retry: bool = True) -> None:
    """
    :param channel_details:
    :param chat_user_ids:
    :param retry:
    :return:
    """
    chat_driver.login()
    try:
        current_channel_users = [member['id'] for member in
                                 chat_driver.channels.get_channel_members(channel_details['id'])]
        for chat_user_id in chat_user_ids:
            if chat_user_id not in current_channel_users:
                response = chat_driver.channels.add_user(channel_details['id'], options={
                    'user_id': chat_user_id
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
            chat_id = None
            if query_opts['chat_id'] is None and query_opts['handle']:
                try:

                    chat_user = chat_driver.users.get_user_by_username(query_opts['handle'])
                    chat_id = chat_user['id']
                    user_profile = Profile.objects.filter(handle=query_opts['handle'])
                    user_profile.chat_id = chat_id
                    user_profile.save()
                except Exception as e:
                    logger.info(f"Unable to find chat user for {query_opts['handle']}")
            else:
                chat_id = query_opts['chat_id']

            chat_driver.users.update_user(chat_id, options=update_opts)
        except ConnectionError as exc:
            logger.info(str(exc))
            logger.info("Retrying connection")
            self.retry(30)
        except Exception as e:
            logger.error(str(e))
