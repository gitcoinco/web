"""Define the mint all kudos management command.

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

"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'updates popularity of all tokens'

    def handle(self, *args, **options):
        from kudos.models import KudosTransfer
        for kt in KudosTransfer.objects.all():
            kt.save()
