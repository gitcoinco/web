'''
    Copyright (C) 2019 Gitcoin Core

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
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from dashboard.models import Bounty


class Command(BaseCommand):

    help = 'expires featured bounties which have been featured for more than 14 days'

    def handle(self, *args, **options):

        expire_date = timezone.now() - timedelta(days=14) # Featured bounties expire in 14 days
        for bounty in Bounty.objects.filter(
            is_featured=True,
            web3_created__lte=expire_date
        ):
            if not bounty.featuring_date or \
                (bounty.featuring_date and bounty.featuring_date < expire_date):
                bounty.is_featured = False
                bounty.save()
