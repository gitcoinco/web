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

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group, Permission


class Command(BaseCommand):
    help = "Setup CLR Round 3"

    def handle(self, *args, **options):
        clr_group_r3 = Group.objects.get_or_create(name="Grants-CLR-Round-3")[0]
        add_clr_match = Permission.objects.get(codename="add_clrmatch")
        clr_group_r3.permissions.add(add_clr_match)

        valid_users = User.objects.filter(profile__data__created_at__lte="2019-03-01").select_related(
            'profile') | User.objects.filter(
            profile__trust_profile=True)
        for user in valid_users:
            user.groups.add(clr_group_r3)
