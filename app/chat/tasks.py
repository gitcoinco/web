import logging

from django.conf import settings
from django.utils.text import slugify

from app.services import RedisService
from celery import app, group
from dashboard.models import Bounty, HackathonEvent, HackathonRegistration, HackathonSponsor, HackathonProject, Profile
from marketing.utils import should_suppress_notification_email
from mattermostdriver import Driver
from mattermostdriver.exceptions import ResourceNotFound

logger = logging.getLogger(__name__)
redis = RedisService().redis

# Lock timeout of 2 minutes (just in the case that the application hangs to avoid a redis deadlock)
LOCK_TIMEOUT = 60 * 2

driver_opts = {
    'scheme': 'https' if settings.CHAT_PORT == 443 else 'http',
    'url': settings.CHAT_SERVER_URL,
    'port': settings.CHAT_PORT,
    'token': settings.CHAT_DRIVER_TOKEN,
    'verify': False
}


def create_channel_if_not_exists(options):
    try:
        chat_driver.login()
        channel_lookup_response = chat_driver.channels.get_channel_by_name(
            options['team_id'], options['channel_name']
        )
        return False, channel_lookup_response

    except ResourceNotFound as RNF:
        try:
            chat_driver.login()
            new_channel = chat_driver.channels.create_channel(options={
                'team_id': options['team_id'],
                'name': options['channel_name'],
                'purpose': options['channel_purpose'] if 'channel_purpose' in options else '',
                'header': options['channel_header'] if 'channel_header' in options else '',
                'display_name': options['channel_display_name'],
                'type': options['channel_type'] if 'channel_type' in options else 'O'
            })
            if 'message' in new_channel:
                raise ValueError(new_channel['message'])

            return True, new_channel
        except Exception as e:
            logger.info(str(e))


def update_chat_notifications(profile, notification_key, status):
    query_opts = {}
    if profile.chat_id is not '' or profile.chat_id is not None:
        query_opts['chat_id'] = profile.chat_id

    query_opts['handle'] = profile.handle
    # TODO: set this to retreive current chat notification propers and then just patch whats diff
    notify_props = chat_notify_default_props(profile)

    notify_props[notification_key] = "true" if status else "false"

    patch_chat_user.delay(query_opts=query_opts, update_opts={'notify_props': notify_props})


def chat_notify_default_props(profile):
    return {
        "email": "false" if should_suppress_notification_email(profile.user.email, 'chat') else "true",
        "push": "mention",
        "comments": "never",
        "desktop": "all",
        "desktop_sound": "true",
        "mention_keys": f'{profile.handle}, @{profile.handle}',
        "channel": "true",
        "first_name": "false",
        "push_status": "away"
    }


def associate_chat_to_profile(profile):
    chat_driver.login()
    try:

        current_chat_user = chat_driver.users.get_user_by_username(profile.handle)
        profile.chat_id = current_chat_user['id']
        profile_access_token = {'token': ''}
        if profile.gitcoin_chat_access_token is '' or profile.gitcoin_chat_access_token is None:
            try:
                profile_access_tokens = chat_driver.users.get_user_access_token(profile.chat_id)
                for pat in profile_access_tokens:
                    if pat.is_active:
                        profile_access_token = pat
                        break
            except Exception as e:
                logger.info(str(e))
                try:
                    profile_access_token = chat_driver.users.create_user_access_token(user_id=profile.chat_id, options={
                        'description': "Grants Gitcoin access to modify your account"})
                except Exception as e:
                    logger.info(str(e))

            profile.gitcoin_chat_access_token = profile_access_token['token']

        profile.save()

        return False, profile
    except ResourceNotFound as RNF:
        if not profile.chat_id:
            create_user_response = chat_driver.users.create_user(
                options={
                    "email": profile.user.email,
                    "username": profile.handle,
                    "first_name": profile.user.first_name,
                    "last_name": profile.user.last_name,
                    "nickname": profile.handle,
                    "auth_data": f'{profile.user.id}',
                    "auth_service": "gitcoin",
                    "locale": "en",
                    "props": {},
                    "notify_props": chat_notify_default_props(profile),
                },
                params={
                    "tid": settings.GITCOIN_CHAT_TEAM_ID
                })
            profile.chat_id = create_user_response['id']
            chat_driver.teams.add_user_to_team(
                settings.GITCOIN_HACK_CHAT_TEAM_ID,
                options={'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                         'user_id': create_user_response['id']}
            )
            try:
                profile_access_tokens = chat_driver.users.get_user_access_token(profile.chat_id)
                for pat in profile_access_tokens:
                    if pat.is_active:
                        profile_access_token = pat
                        break

            except Exception as e:
                logger.info(str(e))
                profile_access_token = chat_driver.users.create_user_access_token(user_id=profile.chat_id, options={
                    'description': "Grants Gitcoin access to modify your account"})

            profile.gitcoin_chat_access_token = profile_access_token['token']

            profile.save()

        return True, profile


def get_chat_url(front_end=False):
    chat_url = settings.CHAT_URL
    if not front_end:
        chat_url = settings.CHAT_SERVER_URL
    if settings.CHAT_PORT not in [80, 443]:
        chat_url = f'http://{chat_url}:{settings.CHAT_PORT}'
    else:
        chat_url = f'https://{chat_url}'
    return chat_url


chat_driver = Driver(driver_opts)


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
                'purpose': options['channel_purpose'] if 'channel_purpose' in options else '',
                'header': options['channel_header'] if 'channel_header' in options else '',
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
            self.retry(30)
        except Exception as e:
            print("we got an exception when creating a channel")
            logger.info(str(e))


@app.shared_task(bind=True, max_retries=3)
def hackathon_chat_sync(self, hackathon_id: str, profile_handle: str = None, retry: bool = True) -> None:
    try:
        chat_driver.login()
        hackathon = HackathonEvent.objects.get(id=hackathon_id)
        channels_to_connect = []

        for channel_name in hackathon.default_channels:
            created, new_channel_details = create_channel_if_not_exists({
                'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                'channel_display_name': channel_name[:60],
                'channel_name': channel_name[:60]
            })
            channels_to_connect.append(new_channel_details['id'])

        if hackathon.chat_channel_id is '' or hackathon.chat_channel_id is None:
            created, new_channel_details = create_channel_if_not_exists({
                'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                'channel_display_name': f'general-{hackathon.slug}'[:60],
                'channel_name': f'general-{slugify(hackathon.name)}'[:60]
            })
            hackathon.chat_channel_id = new_channel_details['id']
            hackathon.save()
        channels_to_connect.append(hackathon.chat_channel_id)

        profiles_to_connect = []
        if profile_handle is None:
            regs_to_sync = HackathonRegistration.objects.filter(hackathon__id=hackathon_id).select_related('registrant')
            for reg in regs_to_sync:
                if reg.registrant is None:
                    continue

                if reg.registrant.chat_id is '' or reg.registrant.chat_id is None:
                    created, updated_profile = associate_chat_to_profile(reg.registrant)
                    profiles_to_connect.append(updated_profile.chat_id)
                else:
                    profiles_to_connect.append(reg.registrant.chat_id)
        else:
            profile = Profile.objects.get(handle__iexact=profile_handle)
            if profile.chat_id is '' or profile.chat_id is None:
                created, updated_profile = associate_chat_to_profile(profile)
                profiles_to_connect.append(updated_profile.chat_id)
            else:
                profiles_to_connect = [profile.chat_id]
        for hack_sponsor in hackathon.sponsor_profiles.all():
            created, new_channel_details = create_channel_if_not_exists({
                'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                'channel_display_name': f'company-{slugify(hack_sponsor.name)}'[:60],
                'channel_name': f'company-{hack_sponsor.handle}'[:60]
            })
            channels_to_connect.append(new_channel_details['id'])

        for channel_id in channels_to_connect:
            try:
                current_channel_members = chat_driver.channels.get_channel_members(channel_id)
            except Exception as e:
                continue
            current_channel_users = [member['user_id'] for member in current_channel_members]
            connect = list(set(profiles_to_connect) - set(current_channel_users))
            if len(connect) > 0:
                add_to_channel.delay({'id': channel_id}, connect)

    except Exception as e:
        logger.info(str(e))


@app.shared_task(bind=True, max_retries=3)
def hackathon_project_chat_sync(self, hackathon_id: str = None, bounty_owner_handle: str = None, project_id: str = None,
                                retry: bool = True) -> None:
    try:
        if not hackathon_id:
            return

        if project_id is not None:
            projects = HackathonProject.objects.filter(id=project_id)
            bounty_owner_handle = projects.first().bounty.bounty_owner_github_username
        else:
            projects = HackathonProject.objects.get(bounty__event__id=hackathon_id)

        chat_driver.login()
        admins = []
        mentors = []

        try:
            bounty_profile = Profile.objects.get(handle__iexact=bounty_owner_handle)
            if bounty_profile.chat_id is '' or bounty_profile.chat_id is None:
                created, bounty_profile = associate_chat_to_profile(bounty_profile)

            mentors.append(bounty_profile.chat_id)
        except Exception as e:
            logger.info("Bounty Profile owner not apart of gitcoin")

        bounty_mentors = Profile.objects.filter(
            user__groups__name=f'sponsor-org-{bounty_owner_handle}-mentors')

        for mentor in bounty_mentors:
            if mentor.chat_id is '' or mentor.chat_id is None:
                created, mentor = associate_chat_to_profile(mentor)
            mentors.append(mentor.chat_id)

        hackathon_admins = Profile.objects.filter(user__groups__name='hackathon-admin')

        for hack_admin in hackathon_admins:
            if hack_admin.chat_id is '' or hack_admin.chat_id is None:
                created, hack_admin = associate_chat_to_profile(hack_admin)
            admins.append(hack_admin.chat_id)



        for project in projects:

            bounty_obj = project.bounty
            profiles_to_connect = admins + mentors

            project_channel_name = slugify(
                f'{"-" + bounty_obj.event.short_code if bounty_obj.event and project.bounty_obj.short_code else ""}{project.name}')
            project_display_name = f'PRJ-{project_channel_name}'

            created, channel_details = create_channel_if_not_exists({
                'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                'channel_purpose': project.summary[:200],
                'channel_display_name': project_display_name[:60],
                'channel_name': project_channel_name[:60]
            })

            for profile_id in project.profiles:
                curr_profile = Profile.objects.get(id=profile_id)
                if not curr_profile.chat_id:
                    created, curr_profile = associate_chat_to_profile(curr_profile)
                profiles_to_connect.append(curr_profile.chat_id)

            try:
                current_channel_members = chat_driver.channels.get_channel_members(channel_details['id'])

                current_channel_users = [member['user_id'] for member in current_channel_members]
                connect = list(set(profiles_to_connect) - set(current_channel_users))
                if len(connect) > 0:
                    add_to_channel.delay(channel_details, connect)

            except Exception as e:
                logger.info(str(e))
    except Exception as e:
        logger.info(str(e))


@app.shared_task(bind=True, max_retries=3)
def add_to_channel(self, channel_details, chat_user_ids: list, retry: bool = True) -> None:
    """
    :param channel_details:
    :param chat_user_ids:
    :param retry:
    :return:
    """
    try:
        chat_driver.login()
        for chat_user_id in chat_user_ids:
            try:
                if chat_user_id is '' or chat_user_id is None:
                    continue
                chat_driver.channels.add_user(channel_details['id'], options={
                    'user_id': chat_user_id
                })
            except Exception as e:
                logger.info(str(e))
                continue
    except ConnectionError as exc:
        logger.info(str(exc))
        self.retry(countdown=30)


@app.shared_task(bind=True, max_retries=1)
def create_user(self, options, params, profile_handle='', retry: bool = True):
    with redis.lock("tasks:create_user:%s" % options['username'], timeout=LOCK_TIMEOUT):
        try:
            chat_driver.login()
            create_user_response = chat_driver.users.create_user(
                options=options,
                params=params
            )
            if profile_handle:
                profile = Profile.objects.get(handle=profile_handle.lower())
                profile.chat_id = create_user_response['id']

                profile_access_token = chat_driver.users.create_user_access_token(user_id=create_user_response['id'],
                                                                                  options={
                                                                                      'description': "Grants Gitcoin access to modify your account"})
                profile.gitcoin_chat_access_token = profile_access_token['id']
                profile.save()

                chat_driver.teams.add_user_to_team(
                    settings.GITCOIN_HACK_CHAT_TEAM_ID,
                    options={'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                             'user_id': create_user_response['id']}
                )

            return create_user_response
        except ConnectionError as exc:
            logger.info(str(exc))
            self.retry(countdown=30)
        except Exception as e:
            logger.info(str(e))
            return None


@app.shared_task(bind=True, max_retries=3)
def patch_chat_user(self, query_opts, update_opts, retry: bool = True) -> None:
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
        chat_driver.login()

        try:
            chat_id = None
            if query_opts['chat_id'] is None and query_opts['handle']:
                try:
                    chat_user = chat_driver.users.get_user_by_username(query_opts['handle'])
                    chat_id = chat_user['id']
                    user_profile = Profile.objects.filter(handle=query_opts['handle'].lower())
                    user_profile.chat_id = chat_id
                    user_profile.save()
                except Exception as e:
                    logger.info(f"Unable to find chat user for {query_opts['handle']}")
            else:
                chat_id = query_opts['chat_id']
            chat_driver.users.patch_user(chat_id, options=update_opts)
        except ConnectionError as exc:
            logger.info(str(exc))
            self.retry(countdown=30)
        except Exception as e:
            logger.info(str(e))
