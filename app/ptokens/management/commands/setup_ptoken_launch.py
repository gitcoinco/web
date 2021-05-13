'''
    Copyright (C) 2021 Gitcoin Core
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
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = "Setup pToken Permissions"

    def handle(self, *args, **options):
        pToken_group_name = "pToken-Seed-Round"
        pToken_group = Group.objects.get_or_create(name=pToken_group_name)[0]
        ct = ContentType.objects.get_for_model(model=User)
        add_pToken_auth = Permission.objects.get_or_create(name="Add pToken", codename="add_pToken_auth", content_type=ct)[0]
        pToken_group.permissions.add(add_pToken_auth)

        print('Adding seeded users to pToken Group')

        # TODO: How else will we determine which users should be added to the group
        valid_users = User.objects.filter(~Q(groups__name__in=[pToken_group_name]), profile__trust_profile=True)
        for user in valid_users:
            user.groups.add(pToken_group)

        print('Valid users added to pToken group')
