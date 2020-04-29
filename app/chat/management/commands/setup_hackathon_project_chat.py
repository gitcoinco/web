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
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from chat.tasks import create_channel_if_not_exists, associate_chat_to_profile, add_to_channel
from dashboard.models import HackathonEvent, HackathonProject, Profile

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create Project channels for active hackathons"

    def handle(self, *args, **options):
        try:

            today = timezone.now()

            projects_to_setup = HackathonProject.objects.filter(
                hackathon__start_date__lte=today,
                hackathon__end_date__gte=today
            )
            print("Projects to Setup **************")
            print(projects_to_setup)
            hackathon_admins = Profile.objects.filter(user__groups__name='hackathon-admin')
            admin_profiles = []
            try:
                for hack_admin in hackathon_admins:
                    if hack_admin.chat_id is '' or hack_admin.chat_id is None:
                        created, hack_admin = associate_chat_to_profile(hack_admin)
                    admin_profiles.append(hack_admin.chat_id)

            except Exception as e:
                logger.debug('Error with adding admin')

            for project in projects_to_setup:
                profiles_to_connect = admin_profiles
                if project.bounty.bounty_owner_githuB_username.lower() == 'consensyshealth':
                    handles = [
                        'midknyt',
                        'jcw-telemed',
                        'njallah',
                        'sherazo',
                        'niccieisenhauer',
                        'manalba',
                        'pvigi',
                        'mattsaavha',
                        'kalyaniyerra',
                        'tshine-netts',
                        'gkaissis',
                        'adham-bardeesi',
                        'mbmarchant',
                        'ehtadvisors',
                        'ingridvasiliufeltesmdmba',
                        'bluesteens',
                        'interceptor-x',
                        'randall-mitchell'
                        'consensyshealth-nicole'
                    ]
                    mentors = [profile.chat_id for profile in Profile.objects.filter(handle__in=handles)]
                    profiles_to_connect = profiles_to_connect + mentors

                project_channel_name = slugify(f'{project.name}')

                created, channel_details = create_channel_if_not_exists({
                    'team_id': settings.GITCOIN_HACK_CHAT_TEAM_ID,
                    'channel_purpose': project.summary[:255],
                    'channel_display_name': f'project-{project_channel_name}'[:60],
                    'channel_name': project_channel_name[:60],
                    'channel_type': 'P'
                })
                if project.chat_channel_id is '' or project.chat_channel_id is None:
                    project.chat_channel_id = channel_details['id']
                    project.save()

                try:
                    bounty_profile = Profile.objects.get(handle__icontains=project.bounty.bounty_owner_github_username)
                    if bounty_profile.chat_id is '' or bounty_profile.chat_id is None:
                        created, bounty_profile = associate_chat_to_profile(bounty_profile)
                    profiles_to_connect.append(bounty_profile.chat_id)

                except Exception as e:
                        logger.error('Error creating project channel', e)

                for team_m_profile in project.project_profiles.all():
                    if team_m_profile.chat_id is '' or team_m_profile.chat_id is None:
                        created, team_m_profile = associate_chat_to_profile(team_m_profile)
                    profiles_to_connect.append(team_m_profile.chat_id)

                try:
                    add_to_channel.delay({'id': project.chat_channel_id}, profiles_to_connect)
                except Exception as e:
                    logger.error(str(e))
                    continue

        except Exception as e:
            logger.error(str(e))
