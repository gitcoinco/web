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

from django.core import management
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):

    help = 'runs all mgmt commands for https://github.com/gitcoinco/web/pull/5093'

    def handle(self, *args, **options):

        # one
        management.call_command('create_rep_records', verbosity=0, interactive=False)

        # two
        for instance in Profile.objects.filter(hide_profile=False):
            instance.calculate_all()
            instance.save()

        # three
        management.call_command('create_earnings', verbosity=0, interactive=False)
