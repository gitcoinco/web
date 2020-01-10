from django.core.management.base import BaseCommand
from dashboard.models import Profile
from django.conf import settings

from chat.tasks import get_driver, create_channel, create_user, add_to_channel


class Command(BaseCommand):

    def handle(self, *args, **options):
        chat_driver = get_driver()

        try:

            # if bounty.chat_channel_id is None:
            # bounty_channel_name = slugify(f'{bounty.github_org_name}-{bounty.github_issue_number}')
            bounty_channel_name = "andrew-test-channel"
            channel_lookup = chat_driver.channels.get_channel_by_name(settings.GITCOIN_HACK_CHAT_TEAM_ID,
                                                                      bounty_channel_name)

            if 'message' in channel_lookup:
                options = {
                    'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                    'channel_display_name': f'{bounty_channel_name}'[:60],
                    'channel_name': bounty_channel_name[:60]
                }
                result = create_channel.apply_async(args=[options])
                bounty_channel_id_response = result.get()

                if 'message' in bounty_channel_id_response:
                    raise ValueError(bounty_channel_id_response['message'])

                # bounty.chat_channel_id = bounty_channel_id_response['id']
                bounty_channel_id = bounty_channel_id_response['id']
                # bounty.save()
            else:
                bounty_channel_id = channel_lookup['id']
                # bounty.chat_channel_id = bounty_channel_id
                # bounty.save()
            # else:
            # bounty_channel_id = bounty.chat_channel_id

            funder_profile = Profile.objects.get(handle="owocki")
            profile = Profile.objects.get(handle="androolloyd")
            if funder_profile is not None:
                if funder_profile.chat_id is None:

                    funder_chat_profile_lookup = chat_driver.users.get_users_by_usernames(
                        options=[funder_profile.handle]
                    )

                    if 'message' in funder_chat_profile_lookup:

                        result = create_user.apply_async(
                            args=[
                                {
                                    "email": funder_profile.user.email,
                                    "username": funder_profile.handle,
                                    "first_name": funder_profile.user.first_name,
                                    "last_name": funder_profile.user.last_name,
                                    "nickname": funder_profile.handle,
                                    "auth_data": f'{funder_profile.user.id}',
                                    "auth_service": "gitcoin",
                                    "locale": "en",
                                    "props": {},
                                    "notify_props": {
                                        "email": "false",
                                        "push": "mention",
                                        "desktop": "all",
                                        "desktop_sound": "true",
                                        "mention_keys": f'{funder_profile.handle}, @{funder_profile.handle}',
                                        "channel": "true",
                                        "first_name": "false"
                                    }
                                },
                                {
                                    "tid": settings.GITCOIN_HACK_CHAT_TEAM_ID
                                }
                            ]
                        )
                        funder_chat_profile_lookup = result.get()
                        if 'message' in funder_chat_profile_lookup:
                            raise ValueError(funder_chat_profile_lookup['message'])
                    elif len(funder_chat_profile_lookup) > 1:
                        raise ValueError("More than one username in chat")
                    funder_profile.chat_id = funder_chat_profile_lookup[0]['id']
                    funder_profile.save()

                if profile.chat_id is None:

                    profile_interest_lookup = chat_driver.users.get_users_by_usernames(
                        options=[profile.handle]
                    )

                    if 'message' in profile_interest_lookup:

                        result = create_user.apply_async(
                            args=[
                                {
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
                                },
                                {
                                    "tid": settings.GITCOIN_HACK_CHAT_TEAM_ID
                                }
                            ]
                        )

                        profile_interest_lookup = result.get()
                        if 'message' in profile_interest_lookup:
                            raise ValueError(profile_interest_lookup['message'])
                    elif len(profile_interest_lookup) > 1:
                        raise ValueError("More than one username in chat")

                    profile.chat_id = profile_interest_lookup[0]['id']
                    profile.save()

                profiles_to_connect = [
                    funder_profile.chat_id,
                    profile.chat_id
                ]

                add_to_channel.delay({
                    'channel_id': bounty_channel_id,
                    'profiles': profiles_to_connect
                })
        except Exception as e:
            print(str(e))
