'''
    Copyright (C) 2018 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''
import logging

from django.conf import settings

from celery import group
from chat.tasks import add_to_channel, create_channel, create_user, get_driver, update_user
from dashboard.models import Profile
from mattermostdriver.exceptions import ResourceNotFound

logger = logging.getLogger(__name__)


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
                    "email": "false",
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
