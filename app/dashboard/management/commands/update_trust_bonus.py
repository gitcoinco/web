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

from django.core.management.base import BaseCommand

from dashboard.models import Profile
from dashboard.tasks import update_trust_bonus


class Command(BaseCommand):

    help = 'Update every users trust_bonus score'

    def add_arguments(self, parser):
        parser.add_argument(
            '--call-now',
            type=int,
            help="disable execution on celery and call now"
        )

    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        print(profiles.count())
        for profile in profiles.iterator():
            if (options['call_now']):
                update_trust_bonus(profile.pk)
            else:
                update_trust_bonus.delay(profile.pk)
