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
from django.conf import settings
from django.core.management.base import BaseCommand

from grants.models import Contribution
from marketing.mails import grant_txn_failed


class Command(BaseCommand):
    help = 'sends emails for grant contributors whose contribution txns have failed'

    def handle(self, *args, **options):
        if settings.DEBUG:
            print("not active in non prod environments")
            return

        failed_contribs = Contribution.objects.exclude(validator_passed=True)

        for failed_contrib in failed_contribs:
            grant_txn_failed(failed_contrib)
